"""Synthetic NQ-like tick data for testing the pipeline (NOT for research)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from nqresearch import scid


def make_records(n_days: int = 6, seed: int = 0, start: str = "2021-03-08", trades_per_min: int = 20,
                 ambiguous_frac: float = 0.02, symbols=("NQH21", "NQM21")):
    """Return (records, manifest DataFrame). Trades only during 09:30-16:00 ET and
    a thin overnight; contract switches at the 18:00 ET open of the middle day."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range(start, periods=n_days)
    ts_list = []
    for d in days:
        # overnight 18:00 prev day -> 09:30 thin; RTH dense
        on = pd.date_range(d - pd.Timedelta(hours=6), d + pd.Timedelta(hours=9, minutes=30), freq="1min", inclusive="left")
        rth = pd.date_range(d + pd.Timedelta(hours=9, minutes=30), d + pd.Timedelta(hours=16), freq="1min", inclusive="left")
        for mins, k in ((on, 2), (rth, trades_per_min)):
            base = mins.tz_localize("America/New_York").tz_convert("UTC").as_unit("us").asi8
            off = np.sort(rng.integers(0, 60_000_000, size=(len(base), k)), axis=1)
            off = (off // 1000) * 1000  # ms precision
            ts_list.append((base[:, None] + off).ravel())
    us = np.sort(np.concatenate(ts_list))
    # Sierra-like uniqueness counter in the sub-ms digits for equal ms
    ms = us // 1000
    dup = np.concatenate([[False], ms[1:] == ms[:-1]])
    grp = np.cumsum(~dup) - 1
    first = np.flatnonzero(~dup)
    rank = np.arange(len(us)) - first[grp]
    us = ms * 1000 + np.minimum(rank, 999)

    n = len(us)
    side = rng.choice([-1, 1], size=n)
    steps = rng.choice([-1, 0, 0, 1], size=n) * 0.25
    mid = 13000 + np.cumsum(steps)
    bid = np.round(mid * 4) / 4
    ask = bid + 0.25
    price = np.where(side > 0, ask, bid)

    switch_day = days[n_days // 2]
    switch_us = pd.Timestamp(switch_day - pd.Timedelta(hours=6), tz="America/New_York").value // 1000
    seg = (us >= switch_us).astype(int)
    roll_gap = 60.0
    price = price + seg * roll_gap
    bid = bid + seg * roll_gap
    ask = ask + seg * roll_gap

    vol = rng.geometric(0.35, size=n).astype(np.uint32)
    rec = np.zeros(n, dtype=scid.RECORD_DTYPE)
    rec["dt"] = scid.from_unix_us(us)
    rec["open"] = 0.0
    rec["high"] = ask
    rec["low"] = bid
    rec["close"] = price
    rec["num_trades"] = 1
    rec["volume"] = vol
    rec["ask_volume"] = np.where(side > 0, vol, 0)
    rec["bid_volume"] = np.where(side < 0, vol, 0)
    amb = (rng.random(n) < ambiguous_frac) & (vol >= 2)
    half = (vol[amb] // 2).astype(np.uint32)
    rec["bid_volume"][amb] = half
    rec["ask_volume"][amb] = vol[amb] - half

    man = pd.DataFrame({
        "contract": list(symbols),
        "start_utc": [pd.Timestamp(us[0], unit="us").isoformat(), pd.Timestamp(switch_us, unit="us").isoformat()],
        "end_utc": [pd.Timestamp(us[seg == 0][-1], unit="us").isoformat(), pd.Timestamp(us[-1], unit="us").isoformat()],
    })
    return rec, man
