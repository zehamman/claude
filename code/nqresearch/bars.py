"""Build 1-minute bars with signed executed-trade flow, per contract segment.

Bars never mix contracts: the group key is (segment, minute). Bars carry
the actual traded prices of the contract that was front by the causal roll
rule; NOTHING is back-adjusted. Any return or level computed across a
segment boundary is invalid and must be dropped by the caller (helpers in
``features.py`` do this).

Timestamp convention: ``ts`` = bar START in Unix microseconds (UTC). A bar
with ts = 09:31:00 contains trades with 09:31:00.000 <= t < 09:32:00.000 and
is only known at 09:32:00.000 (its close). Signals computed from a bar may
only trade at or after ``ts + 60s``.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from . import flow, manifest as mf, scid

MIN_US = 60_000_000

BAR_COLUMNS = [
    "segment", "ts", "open", "high", "low", "close", "volume", "n_rec",
    "buy_vol", "sell_vol", "amb_vol", "buy_n", "sell_n",
    "buy_vol_q", "sell_vol_q",  # quote-rule fill-in for ambiguous flags (sensitivity only)
    "big_buy_vol", "big_sell_vol",  # clean-flag trades with size >= big_size
    "pv", "last_bid", "last_ask", "first_us", "last_us",
]


def _aggregate(us: np.ndarray, seg: np.ndarray, rec: np.ndarray, big_size: int) -> pd.DataFrame:
    minute = us // MIN_US
    key_change = np.flatnonzero((np.diff(minute) != 0) | (np.diff(seg) != 0)) + 1
    starts = np.concatenate([[0], key_change])
    ends = np.concatenate([key_change, [len(us)]]) - 1

    px = rec["close"].astype(np.float64)
    v = rec["volume"].astype(np.int64)
    fs = flow.flag_side(rec)
    qs = flow.quote_side(rec)
    eff = np.where(fs != 0, fs, qs)  # quote-rule fill-in only where flag is ambiguous
    big = v >= big_size

    def s(x):
        return np.add.reduceat(x, starts)

    out = {
        "segment": seg[starts],
        "ts": minute[starts] * MIN_US,
        "open": px[starts],
        "high": np.maximum.reduceat(px, starts),
        "low": np.minimum.reduceat(px, starts),
        "close": px[ends],
        "volume": s(v),
        "n_rec": (ends - starts + 1).astype(np.int64),
        "buy_vol": s(np.where(fs > 0, v, 0)),
        "sell_vol": s(np.where(fs < 0, v, 0)),
        "amb_vol": s(np.where(fs == 0, v, 0)),
        "buy_n": s((fs > 0).astype(np.int64)),
        "sell_n": s((fs < 0).astype(np.int64)),
        "buy_vol_q": s(np.where(eff > 0, v, 0)),
        "sell_vol_q": s(np.where(eff < 0, v, 0)),
        "big_buy_vol": s(np.where((fs > 0) & big, v, 0)),
        "big_sell_vol": s(np.where((fs < 0) & big, v, 0)),
        "pv": s(px * v),
        "last_bid": rec["low"][ends].astype(np.float64),
        "last_ask": rec["high"][ends].astype(np.float64),
        "first_us": us[starts],
        "last_us": us[ends],
    }
    return pd.DataFrame(out, columns=BAR_COLUMNS)


def build(
    scid_path: str,
    manifest: pd.DataFrame,
    chunk_records: int = 10_000_000,
    big_size: int = 10,
    stop: int | None = None,
    progress: bool = True,
) -> tuple[pd.DataFrame, dict]:
    parts: list[pd.DataFrame] = []
    carry: np.ndarray | None = None
    stats = {"records_outside_segments": 0, "records": 0}
    prev_last = None
    t0 = time.time()
    for start, rec in scid.iter_chunks(scid_path, chunk_records, stop=stop):
        us_new = scid.to_unix_us(rec["dt"])
        if (np.diff(us_new) < 0).any() or (prev_last is not None and us_new[0] < prev_last):
            raise ValueError(
                f"Timestamps decrease in chunk starting at record {start}; "
                "run the audit and repair ordering before building bars."
            )
        prev_last = int(us_new[-1])
        if carry is not None:
            rec = np.concatenate([carry, rec])
        us = scid.to_unix_us(rec["dt"])
        seg = mf.assign_segment(manifest, us)
        outside = seg < 0
        if outside.any():
            stats["records_outside_segments"] += int(outside.sum())
            keep = ~outside
            rec, us, seg = rec[keep], us[keep], seg[keep]
        if len(rec) == 0:
            carry = None
            continue
        # hold back the final (possibly incomplete) minute for the next chunk
        last_min = us[-1] // MIN_US
        cut = np.searchsorted(us // MIN_US, last_min, side="left")
        carry = rec[cut:].copy()
        if cut > 0:
            parts.append(_aggregate(us[:cut], seg[:cut], rec[:cut], big_size))
            stats["records"] += cut
        if progress:
            print(f"  bars through record {start + chunk_records:,}  {time.time() - t0:7.0f}s", flush=True)
    if carry is not None and len(carry):
        us = scid.to_unix_us(carry["dt"])
        seg = mf.assign_segment(manifest, us)
        parts.append(_aggregate(us, seg, carry, big_size))
        stats["records"] += len(carry)
    bars = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=BAR_COLUMNS)
    dup = bars.duplicated(["segment", "ts"]).sum()
    if dup:
        raise AssertionError(f"{dup} duplicate (segment, minute) bars - chunk carry logic failed")
    bars = bars.merge(manifest[["segment", "symbol"]], on="segment", how="left")
    stats["bars"] = len(bars)
    stats["big_size"] = big_size
    return bars, stats
