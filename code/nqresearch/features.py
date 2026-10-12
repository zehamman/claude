"""Leakage-safe features on 1-minute bars.

Rules enforced here:
* Every feature at row t uses bars <= t only (bar t is complete at ts+60s).
* Forward returns start at the OPEN of bar t+1 (first trade after the
  decision time) and end at the OPEN of bar t+1+h - the same prices the
  backtester trades at.
* All rolling windows and forward windows are computed INSIDE one
  (segment, session_date) RTH group, so nothing crosses a contract roll,
  an overnight gap, or a session boundary.
* Rows whose window would need a missing minute are NaN, not interpolated.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import sessions

MIN_US = 60_000_000


def rth_frame(bars: pd.DataFrame) -> pd.DataFrame:
    df = sessions.annotate(bars)
    df = df[df["is_rth"]].sort_values(["segment", "ts"], kind="stable").reset_index(drop=True)
    df["grp"] = df.groupby(["segment", "session_date"], sort=False).ngroup().to_numpy()
    df["rth_min"] = df["et_minute"] - sessions.RTH_START_MIN
    return df


def _lag_ok(ts: np.ndarray, grp: np.ndarray, k: int) -> np.ndarray:
    """True where bars t-k..t are k+1 consecutive minutes within one group."""
    ok = np.zeros(len(ts), dtype=bool)
    if k < len(ts):
        ok[k:] = (grp[k:] == grp[:-k]) & (ts[k:] - ts[:-k] == k * MIN_US)
    return ok


def _lead_ok(ts: np.ndarray, grp: np.ndarray, k: int) -> np.ndarray:
    ok = np.zeros(len(ts), dtype=bool)
    if k < len(ts):
        ok[:-k] = (grp[:-k] == grp[k:]) & (ts[k:] - ts[:-k] == k * MIN_US)
    return ok


def rolling_sum(x: np.ndarray, ts: np.ndarray, grp: np.ndarray, k: int) -> np.ndarray:
    """Sum of x over bars t-k+1..t; NaN unless they are k consecutive minutes in one group."""
    c = np.concatenate([[0.0], np.cumsum(x, dtype=np.float64)])
    out = np.full(len(x), np.nan)
    if k <= len(x):
        s = c[k:] - c[:-k]  # sum of x[i-k+1..i] at position i-k+1 -> align to i
        out[k - 1 :] = s
    ok = _lag_ok(ts, grp, k - 1) if k > 1 else np.ones(len(x), dtype=bool)
    out[~ok] = np.nan
    return out


def add_flow_features(df: pd.DataFrame, ks=(5, 15, 30)) -> pd.DataFrame:
    ts = df["ts"].to_numpy(np.int64)
    grp = df["grp"].to_numpy()
    buy = df["buy_vol"].to_numpy(np.float64)
    sell = df["sell_vol"].to_numpy(np.float64)
    vol = df["volume"].to_numpy(np.float64)
    close = df["close"].to_numpy(np.float64)
    out = {}
    for k in ks:
        ofi = rolling_sum(buy - sell, ts, grp, k)
        clean = rolling_sum(buy + sell, ts, grp, k)
        out[f"ofi_{k}"] = ofi
        out[f"imb_{k}"] = np.where(clean > 0, ofi / np.where(clean > 0, clean, 1), np.nan)
        out[f"vol_{k}"] = rolling_sum(vol, ts, grp, k)
        out[f"amb_share_{k}"] = 1 - clean / np.where(out[f"vol_{k}"] > 0, out[f"vol_{k}"], np.nan)
        r = np.full(len(close), np.nan)
        ok = _lag_ok(ts, grp, k)
        r[k:] = close[k:] - close[:-k]
        r[~ok] = np.nan
        out[f"ret_{k}"] = r
    return df.assign(**out)


def add_forward_returns(df: pd.DataFrame, hs=(5, 15, 30)) -> pd.DataFrame:
    """fwd_h = open[t+1+h] - open[t+1] in points (what a trade decided at t's close earns)."""
    ts = df["ts"].to_numpy(np.int64)
    grp = df["grp"].to_numpy()
    op = df["open"].to_numpy(np.float64)
    out = {}
    for h in hs:
        r = np.full(len(op), np.nan)
        ok = _lead_ok(ts, grp, h + 1)
        r[: -(h + 1)] = op[h + 1 :] - op[1 : -h]
        r[~ok] = np.nan
        out[f"fwd_{h}"] = r
    return df.assign(**out)


def add_trailing_vol(df: pd.DataFrame, k: int = 30) -> pd.DataFrame:
    """Trailing within-session std of 1-min close changes (points), for normalisation."""
    ts = df["ts"].to_numpy(np.int64)
    grp = df["grp"].to_numpy()
    c = df["close"].to_numpy(np.float64)
    d = np.full(len(c), np.nan)
    ok1 = _lag_ok(ts, grp, 1)
    d[1:] = c[1:] - c[:-1]
    d[~ok1] = np.nan
    dz = np.nan_to_num(d)
    n = rolling_sum((~np.isnan(d)).astype(float), ts, grp, k)
    s1 = rolling_sum(dz, ts, grp, k)
    s2 = rolling_sum(dz * dz, ts, grp, k)
    var = (s2 - s1 * s1 / n) / (n - 1)
    return df.assign(**{f"sd1m_{k}": np.sqrt(np.where(n >= k // 2, var, np.nan))})
