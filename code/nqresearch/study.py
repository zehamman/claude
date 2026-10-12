"""Shared loading for the bar-based studies."""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from . import costs, backtest, features, periods, signals, stats

KS = (5, 15, 30)
HS = (5, 15, 30)


def load_rth(work_dir: str, rebuild: bool = False) -> pd.DataFrame:
    cache = os.path.join(work_dir, "rth_features.parquet")
    if os.path.exists(cache) and not rebuild:
        return pd.read_parquet(cache)
    bars = pd.read_parquet(os.path.join(work_dir, "bars_1m.parquet"))
    df = features.rth_frame(bars)
    df = features.add_flow_features(df, KS)
    df = features.add_forward_returns(df, HS)
    df = features.add_trailing_vol(df, 30)
    for k in (5, 15):
        df = signals.prepare(df, k)
    df["period"] = periods.label(df["session_date"]).to_numpy()
    df = df.drop(columns=["et"])
    df.to_parquet(cache, index=False)
    return df


def evaluate(df: pd.DataFrame, name: str, k: int, theta: float, h: int, cost_name: str = "base") -> tuple:
    sig = signals.SIGNALS[name](df, k, theta)
    cm = costs.SCENARIOS[cost_name]
    tr = backtest.run(df, sig, h, cm)
    daily = backtest.daily_pnl(tr, df["session_date"].unique())
    rth_min = float(len(df))
    return tr, daily, stats.summarize(tr, daily, rth_min, boot=False)


def daily_sharpe_per_period(daily: pd.Series) -> float:
    d = daily.to_numpy(float)
    return float(d.mean() / d.std(ddof=1)) if d.std(ddof=1) > 0 else np.nan
