"""Performance statistics with dependence-aware inference."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats as sps

TRADING_DAYS = 252


def newey_west_t(x: np.ndarray, lags: int = 5) -> float:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 3:
        return float("nan")
    e = x - x.mean()
    lr = e @ e / n
    for l in range(1, min(lags, n - 1) + 1):
        w = 1 - l / (lags + 1)
        lr += 2 * w * (e[l:] @ e[:-l]) / n
    se = math.sqrt(max(lr, 1e-300) / n)
    return x.mean() / se


def sharpe(daily: np.ndarray) -> float:
    d = np.asarray(daily, dtype=float)
    sd = d.std(ddof=1)
    return float(d.mean() / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")


def stationary_bootstrap_sharpe(daily: np.ndarray, n_boot: int = 2000, mean_block: float = 5.0,
                                seed: int = 0) -> tuple[float, float]:
    """95% CI of annualised Sharpe via Politis-Romano stationary bootstrap."""
    d = np.asarray(daily, dtype=float)
    n = len(d)
    rng = np.random.default_rng(seed)
    p = 1.0 / mean_block
    out = np.empty(n_boot)
    pos = np.arange(n)
    for b in range(n_boot):
        new = rng.random(n) < p
        new[0] = True
        bstart = np.maximum.accumulate(np.where(new, pos, 0))  # index where current block began
        idx = (rng.integers(n, size=n)[bstart] + pos - bstart) % n
        out[b] = sharpe(d[idx])
    return float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))


def max_drawdown(daily: np.ndarray) -> tuple[float, int]:
    eq = np.cumsum(np.asarray(daily, dtype=float))
    peak = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    dd = eq - peak
    mdd = float(dd.min()) if len(dd) else 0.0
    # longest underwater stretch in days
    longest = cur = 0
    for v in dd:
        cur = cur + 1 if v < 0 else 0
        longest = max(longest, cur)
    return mdd, longest


def deflated_sharpe(sr_daily: float, n_obs: int, n_trials: int, sr_var_trials: float,
                    skew: float = 0.0, kurt: float = 3.0) -> float:
    """Bailey & Lopez de Prado (2014) DSR: P(true SR > expected max of N null trials).

    All Sharpe ratios here are PER-PERIOD (daily, not annualised).
    """
    if n_trials < 1 or n_obs < 3:
        return float("nan")
    g = 0.5772156649
    if n_trials == 1:
        sr0 = 0.0
    else:
        sr0 = math.sqrt(max(sr_var_trials, 0.0)) * (
            (1 - g) * sps.norm.ppf(1 - 1 / n_trials) + g * sps.norm.ppf(1 - 1 / (n_trials * math.e))
        )
    denom = math.sqrt(max(1 - skew * sr_daily + (kurt - 1) / 4 * sr_daily ** 2, 1e-12))
    return float(sps.norm.cdf((sr_daily - sr0) * math.sqrt(n_obs - 1) / denom))


def summarize(trades: pd.DataFrame, daily: pd.Series, rth_minutes_total: float | None = None,
              boot: bool = True) -> dict:
    d = daily.to_numpy(dtype=float)
    mdd, uw = max_drawdown(d)
    out = {
        "sessions": int(len(d)),
        "trades": int(len(trades)),
        "trades_per_day": len(trades) / max(len(d), 1),
        "avg_gross_pts": float(trades["gross_pts"].mean()) if len(trades) else float("nan"),
        "avg_net_pts": float(trades["net_pts"].mean()) if len(trades) else float("nan"),
        "hit_rate_net": float((trades["net_pts"] > 0).mean()) if len(trades) else float("nan"),
        "total_net_usd": float(d.sum()),
        "ann_mean_usd": float(d.mean() * TRADING_DAYS),
        "ann_vol_usd": float(d.std(ddof=1) * math.sqrt(TRADING_DAYS)),
        "sharpe": sharpe(d),
        "nw_t_daily_mean": newey_west_t(d),
        "max_dd_usd": mdd,
        "longest_underwater_days": uw,
        "worst_day_usd": float(d.min()) if len(d) else 0.0,
        "skew_daily": float(sps.skew(d)) if len(d) > 2 else float("nan"),
        "kurt_daily": float(sps.kurtosis(d, fisher=False)) if len(d) > 3 else float("nan"),
        "long_share": float((trades["side"] > 0).mean()) if len(trades) else float("nan"),
    }
    if rth_minutes_total:
        out["exposure"] = float(trades["hold_min"].sum() / rth_minutes_total) if len(trades) else 0.0
    if boot and len(d) > 20 and np.std(d) > 0:
        out["sharpe_ci95"] = stationary_bootstrap_sharpe(d, n_boot=500)
    return out


def by_year(trades: pd.DataFrame, daily: pd.Series) -> pd.DataFrame:
    rows = []
    t_year = pd.to_datetime(trades["session_date"]).dt.year if len(trades) else pd.Series(dtype=int)
    for y, d in daily.groupby(daily.index.year):
        t = trades[t_year == y] if len(trades) else trades
        mdd, _ = max_drawdown(d.to_numpy())
        rows.append({
            "year": y, "trades": len(t), "net_usd": d.sum(), "sharpe": sharpe(d.to_numpy()),
            "avg_net_pts": t["net_pts"].mean() if len(t) else np.nan,
            "hit_rate": (t["net_pts"] > 0).mean() if len(t) else np.nan, "max_dd_usd": mdd,
        })
    return pd.DataFrame(rows)


def daily_ic(df: pd.DataFrame, x: str, y: str, step: int, day_col: str = "session_date",
             min_obs: int = 8) -> pd.Series:
    """Spearman IC per session on non-overlapping samples (every ``step`` rows of each group)."""
    sub = df[[day_col, "grp", x, y]].dropna()
    sub = sub[sub.groupby("grp").cumcount() % step == 0]

    def f(g):
        if len(g) < min_obs or g[x].nunique() < 3:
            return np.nan
        return sps.spearmanr(g[x], g[y]).statistic

    return sub.groupby(day_col)[[x, y]].apply(f).dropna()
