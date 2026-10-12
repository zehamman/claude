"""Minimal, explicit fixed-horizon backtester on 1-minute bars.

* Decision at the close of bar t (signal in {-1, 0, +1}).
* Entry at OPEN of bar t+1, which must be the next consecutive minute in the
  same (segment, session) group; otherwise the signal is skipped.
* Exit at OPEN of bar entry+h, or earlier at the first bar whose ET minute
  >= flat_by_min (forced flat), or at the last bar's CLOSE if the group ends.
* One position at a time, 1 contract. No pyramiding, no overnight holding,
  no position across a contract roll (groups are per segment).
* Costs: CostModel round trip, applied per trade, in points.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .costs import POINT_VALUE, CostModel

MIN_US = 60_000_000


def run(df: pd.DataFrame, signal: np.ndarray, h: int, cost: CostModel,
        first_decision_min: int = 15, last_decision_min: int = 360, flat_by_min: int = 385) -> pd.DataFrame:
    """``df`` from features.rth_frame (sorted by segment, ts). Minutes are RTH minutes
    (0 = 09:30 ET). Defaults: decide 09:45-15:30, flat by 15:55."""
    sig = np.asarray(signal, dtype=np.int8)
    ts = df["ts"].to_numpy(np.int64)
    grp = df["grp"].to_numpy()
    op = df["open"].to_numpy(np.float64)
    cl = df["close"].to_numpy(np.float64)
    rm = df["rth_min"].to_numpy()
    sd = df["session_date"].to_numpy()
    sym = df["symbol"].to_numpy() if "symbol" in df else np.full(len(df), "")

    eligible = (sig != 0) & (rm >= first_decision_min) & (rm <= last_decision_min)
    cand = np.flatnonzero(eligible)
    bounds = np.flatnonzero(np.diff(grp)) + 1
    g_end = np.concatenate([bounds, [len(grp)]])  # exclusive end per group id order
    g_start = np.concatenate([[0], bounds])
    gid_end = dict(zip(grp[g_start].tolist(), g_end.tolist()))

    trades = []
    next_ok = -1
    for d in cand:
        if d < next_ok:
            continue
        e = d + 1
        g = grp[d]
        end = gid_end[g]
        if e >= end or ts[e] - ts[d] != MIN_US:
            continue
        x = e + h
        flat = np.flatnonzero(rm[e:min(x, end)] >= flat_by_min)
        if len(flat):
            x = e + int(flat[0])
            if x == e:
                continue
        if x < end:
            exit_px, exit_ts = op[x], ts[x]
        else:
            x = end
            exit_px, exit_ts = cl[end - 1], ts[end - 1] + MIN_US
        side = int(sig[d])
        gross = side * (exit_px - op[e])
        trades.append((sd[d], sym[d], ts[d], ts[e], exit_ts, side, op[e], exit_px, gross,
                       (exit_ts - ts[e]) / MIN_US))
        next_ok = x - 1  # may decide again at the close of the bar before the exit open
    cols = ["session_date", "symbol", "decision_ts", "entry_ts", "exit_ts", "side", "entry_px",
            "exit_px", "gross_pts", "hold_min"]
    t = pd.DataFrame(trades, columns=cols)
    t["cost_pts"] = cost.rt_points
    t["net_pts"] = t["gross_pts"] - t["cost_pts"]
    t["net_usd"] = t["net_pts"] * POINT_VALUE
    return t


def daily_pnl(trades: pd.DataFrame, sessions_index, col: str = "net_usd") -> pd.Series:
    """Daily P&L over ALL sessions in the evaluated period (zero on no-trade days)."""
    idx = pd.DatetimeIndex(pd.to_datetime(pd.Index(sessions_index).unique())).sort_values()
    if trades.empty:
        return pd.Series(0.0, index=idx)
    s = trades.groupby(pd.to_datetime(trades["session_date"]))[col].sum()
    return s.reindex(idx, fill_value=0.0)
