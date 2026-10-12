"""Pre-registered signal definitions. These must match the hypothesis notes in
``03 Hypotheses``. Change them only by creating a NEW hypothesis version."""

from __future__ import annotations

import numpy as np
import pandas as pd


def trailing_session_scale(df: pd.DataFrame, col: str, n_sessions: int = 20) -> np.ndarray:
    """Std of ``col`` over the previous ``n_sessions`` sessions (excluding the current one).
    Uses only information available before the session starts."""
    per = df.groupby("session_date")[col].agg(["sum", lambda s: (s * s).sum(), "count"])
    per.columns = ["s1", "s2", "n"]
    roll = per.rolling(n_sessions, min_periods=n_sessions).sum().shift(1)
    var = (roll["s2"] - roll["s1"] ** 2 / roll["n"]) / (roll["n"] - 1)
    return df["session_date"].map(np.sqrt(var)).to_numpy(float)


def prepare(df: pd.DataFrame, k: int) -> pd.DataFrame:
    """Adds z_imb_k (flow) and z_ret_k (price-only control)."""
    out = {}
    out[f"z_imb_{k}"] = df[f"imb_{k}"].to_numpy() / trailing_session_scale(df, f"imb_{k}")
    out[f"z_ret_{k}"] = df[f"ret_{k}"].to_numpy() / (df["sd1m_30"].to_numpy() * np.sqrt(k))
    return df.assign(**out)


def h01_flow_continuation(df, k, theta):
    z = df[f"z_imb_{k}"].to_numpy()
    return np.where(np.abs(z) >= theta, np.sign(z), 0).astype(np.int8)


def h02_absorption_reversal(df, k, theta, absorb=0.5):
    z = df[f"z_imb_{k}"].to_numpy()
    zr = df[f"z_ret_{k}"].to_numpy()
    cond = (np.abs(z) >= theta) & (np.abs(zr) <= absorb)
    return np.where(cond, -np.sign(z), 0).astype(np.int8)


def p01_price_momentum(df, k, theta):
    """Price-only control for H01: same k/theta/h, trades sign of the past k-minute move."""
    z = df[f"z_ret_{k}"].to_numpy()
    return np.where(np.abs(z) >= theta, np.sign(z), 0).astype(np.int8)


def p02_price_reversal(df, k, theta):
    return (-p01_price_momentum(df, k, theta)).astype(np.int8)


SIGNALS = {
    "H01": h01_flow_continuation,
    "H02": h02_absorption_reversal,
    "P01": p01_price_momentum,
    "P02": p02_price_reversal,
}

HYPOTHESIS_NOTES = {
    "H01": "H01 - Order-flow imbalance continuation",
    "H02": "H02 - Absorption reversal",
}

GRID = {"k": [5, 15], "theta": [1.5, 2.0, 2.5], "h": [5, 15, 30]}
