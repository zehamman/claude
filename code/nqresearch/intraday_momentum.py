"""H04 market intraday momentum (NQ-only) and its GEX-conditioned version (H05).

Primary predictor (zero free parameters): r_rod = price at 15:30 ET (close of
the 15:29 bar) minus the previous session's 16:00 ET price (close of its 15:59
bar), same contract segment only. Trade sign(r_rod) at the 15:30 bar open,
exit at the close of the 15:59 bar. Secondary predictor: r_first30 = 10:00
price minus previous 16:00 price.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def session_points(rth: pd.DataFrame) -> pd.DataFrame:
    """One row per (segment, session) with the prices the rule needs."""
    def at(minute, col):
        s = rth[rth["rth_min"] == minute].set_index("grp")[col]
        return s

    g = rth.groupby("grp").agg(segment=("segment", "first"), session_date=("session_date", "first"),
                               symbol=("symbol", "first"))
    g["close_1559"] = at(389, "close")
    g["close_0959"] = at(29, "close")
    g["close_1529"] = at(359, "close")
    g["open_1530"] = at(360, "open")
    g = g.sort_values(["segment", "session_date"])
    prev = g.groupby("segment")["close_1559"].shift(1)
    prev_date = g.groupby("segment")["session_date"].shift(1)
    # only use the previous session if it is the immediately preceding trading session
    gap_days = (g["session_date"] - prev_date).dt.days
    prev = prev.where(gap_days <= 4)  # weekend / single holiday allowed
    g["r_rod"] = g["close_1529"] - prev
    g["r_first30"] = g["close_0959"] - prev
    g["r_last30"] = g["close_1559"] - g["open_1530"]  # what the trade earns gross (before slippage)
    return g.reset_index()


def signal_from_points(rth: pd.DataFrame, pts: pd.DataFrame, col: str) -> np.ndarray:
    """Place sign(col) on the 15:29 bar of each group (decision at its close)."""
    s = pts.set_index("grp")[col]
    sig = np.zeros(len(rth), dtype=np.int8)
    rows = np.flatnonzero(rth["rth_min"].to_numpy() == 359)
    vals = s.reindex(rth["grp"].to_numpy()[rows]).to_numpy()
    sig[rows] = np.where(np.isnan(vals), 0, np.sign(vals)).astype(np.int8)
    return sig
