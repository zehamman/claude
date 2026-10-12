"""Daily realized volatility and HAR-RV forecasting, for testing whether a
daily feature (e.g. estimated GEX) adds information BEYOND known volatility
predictors (lagged RV and implied vol). Options activity and volatility rise
together, so a GEX effect that disappears once VXN and lagged RV are in the
model is not evidence of a dealer-hedging mechanism.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .stats import newey_west_t


def daily_rv(rth: pd.DataFrame, step: int = 5) -> pd.DataFrame:
    """Per session: RTH realized variance from ``step``-minute close-to-close log returns
    (within one segment/session group), plus first-order autocorrelation of those returns."""
    rows = []
    for (sd, g), df in rth.groupby(["session_date", "grp"], sort=True):
        c = df["close"].to_numpy(float)[::step]
        if len(c) < 20:
            continue
        r = np.diff(np.log(c))
        ac1 = np.corrcoef(r[1:], r[:-1])[0, 1] if len(r) > 3 and r.std() > 0 else np.nan
        rows.append({"session_date": sd, "rv": float(r @ r), "ac1": ac1, "n_ret": len(r),
                     "oc_ret": float(np.log(df["close"].iloc[-1] / df["open"].iloc[0]))})
    out = pd.DataFrame(rows)
    # if a session has two segments (should not happen for an 18:00 ET roll) keep the larger
    out = out.sort_values("n_ret").drop_duplicates("session_date", keep="last")
    return out.set_index("session_date").sort_index()


def har_design(rv: pd.Series, extra: pd.DataFrame | None = None) -> pd.DataFrame:
    """Target: log RV of session t+1. Regressors known at end of session t."""
    lrv = np.log(rv.clip(lower=1e-12))
    X = pd.DataFrame({
        "y": lrv.shift(-1),
        "lrv_d": lrv,
        "lrv_w": lrv.rolling(5).mean(),
        "lrv_m": lrv.rolling(22).mean(),
    })
    if extra is not None:
        X = X.join(extra, how="left")
    return X


def expanding_oos(X: pd.DataFrame, cols: list[str], start: str, refit_every: int = 21,
                  min_train: int = 500) -> pd.Series:
    """Expanding-window OLS forecasts for dates >= start; refit every ``refit_every`` rows."""
    d = X.dropna(subset=["y", *cols])
    preds = pd.Series(np.nan, index=d.index)
    test_idx = np.flatnonzero(d.index >= pd.Timestamp(start))
    beta = None
    for j, i in enumerate(test_idx):
        if beta is None or j % refit_every == 0:
            tr = d.iloc[:i]
            if len(tr) < min_train:
                continue
            A = np.column_stack([np.ones(len(tr)), tr[cols].to_numpy(float)])
            beta, *_ = np.linalg.lstsq(A, tr["y"].to_numpy(float), rcond=None)
        preds.iloc[i] = beta[0] + d.iloc[i][cols].to_numpy(float) @ beta[1:]
    return preds.dropna()


def diebold_mariano(y: pd.Series, f_base: pd.Series, f_new: pd.Series, lags: int = 5) -> dict:
    """Squared-error loss. Positive t => new model has LOWER loss than base."""
    idx = y.index.intersection(f_base.index).intersection(f_new.index)
    e0 = (y[idx] - f_base[idx]) ** 2
    e1 = (y[idx] - f_new[idx]) ** 2
    d = (e0 - e1).to_numpy()
    return {"n": len(d), "mse_base": float(e0.mean()), "mse_new": float(e1.mean()),
            "oos_r2_vs_base": float(1 - e1.mean() / e0.mean()), "dm_t": newey_west_t(d, lags)}
