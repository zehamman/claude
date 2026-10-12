"""Model-derived gamma exposure (GEX) estimates - NOT observed dealer positions.

Everything a GEX number depends on is an explicit argument, so that every
estimate can be reproduced and stress-tested:

* contract universe and snapshot time (``asof``) and when it is usable
* underlying / forward price, rate ``r``, dividend yield ``q``
* volatility source (per-contract implied vol column)
* contract multiplier (100 for QQQ/NDX equity options; for options on NQ
  futures 1 option = 1 future -> multiplier 20 with ``model='black76'``)
* expiration timestamps (PM vs AM settlement matters; pass the actual time)
* DEALER SIGN ASSUMPTION - the big one. Open interest does not reveal who is
  long. Run every study under all of SIGN_SCENARIOS and report each.

Units: ``gex_usd_1pct`` = change in dealer delta-dollars for a +1% move in
the underlying = sign * gamma * OI * multiplier * S^2 * 0.01.
"""

from __future__ import annotations


import numpy as np
import pandas as pd
from scipy.stats import norm

YEAR_SECONDS = 365.25 * 86400

SIGN_SCENARIOS = {
    # Common vendor convention: customers sell calls (overwriting) and buy puts,
    # so dealers are long calls and short puts.
    "dealer_long_calls_short_puts": {"C": +1.0, "P": -1.0},
    # Customers net long all options (dealers short gamma everywhere).
    "dealer_short_all": {"C": -1.0, "P": -1.0},
    # Bounding case: dealers long everything.
    "dealer_long_all": {"C": +1.0, "P": +1.0},
}


def gamma(S, K, T, sigma, r=0.0, q=0.0, model: str = "bsm"):
    """Per-unit gamma. ``bsm``: spot S with yield q. ``black76``: S is the futures price."""
    S, K, T, sigma = (np.asarray(a, dtype=float) for a in (S, K, T, sigma))
    sqrtT = np.sqrt(T)
    if model == "bsm":
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrtT)
        disc = np.exp(-q * T)
    elif model == "black76":
        d1 = (np.log(S / K) + 0.5 * sigma**2 * T) / (sigma * sqrtT)
        disc = np.exp(-r * T)
    else:
        raise ValueError(model)
    return disc * norm.pdf(d1) / (S * sigma * sqrtT)


def chain_gex(
    chain: pd.DataFrame,
    spot: float,
    asof: pd.Timestamp,
    r: float = 0.0,
    q: float = 0.0,
    multiplier: float = 100.0,
    scenario: str | dict = "dealer_long_calls_short_puts",
    model: str = "bsm",
    min_T_hours: float = 1.0,
    exclude_expiring_within_hours: float | None = None,
    max_dte_days: float | None = None,
) -> pd.DataFrame:
    """Per-contract GEX. ``chain`` columns: strike, right ('C'/'P'), expiry (tz-aware ts),
    oi, iv. Optional ``dealer_sign`` column overrides the scenario (e.g. from open/close data)."""
    c = chain.copy()
    asof = pd.Timestamp(asof)
    T_sec = (pd.to_datetime(c["expiry"]) - asof).dt.total_seconds().to_numpy()
    keep = T_sec > 0
    if exclude_expiring_within_hours is not None:
        keep &= T_sec > exclude_expiring_within_hours * 3600
    if max_dte_days is not None:
        keep &= T_sec <= max_dte_days * 86400
    keep &= (c["iv"].to_numpy() > 0) & (c["oi"].to_numpy() > 0)
    c = c[keep].copy()
    T = np.maximum(T_sec[keep], min_T_hours * 3600) / YEAR_SECONDS
    if "dealer_sign" in c:
        sign = c["dealer_sign"].to_numpy(float)
    else:
        sc = SIGN_SCENARIOS[scenario] if isinstance(scenario, str) else scenario
        sign = c["right"].map(sc).to_numpy(float)
    g = gamma(spot, c["strike"].to_numpy(float), T, c["iv"].to_numpy(float), r, q, model)
    c["T_years"] = T
    c["gamma"] = g
    c["gex_usd_1pct"] = sign * g * c["oi"].to_numpy(float) * multiplier * spot**2 * 0.01
    return c


def total_gex(chain: pd.DataFrame, spot: float, asof, **kw) -> float:
    return float(chain_gex(chain, spot, asof, **kw)["gex_usd_1pct"].sum())


def gex_profile(chain: pd.DataFrame, spot: float, asof, rel_grid=np.linspace(-0.05, 0.05, 41), **kw) -> pd.DataFrame:
    """Total GEX if spot moved to spot*(1+x), IVs held per strike (sticky-strike assumption)."""
    rows = [(spot * (1 + x), total_gex(chain, spot * (1 + x), asof, **kw)) for x in rel_grid]
    return pd.DataFrame(rows, columns=["spot", "gex_usd_1pct"])


def zero_gamma_level(profile: pd.DataFrame, spot: float) -> float:
    """Sign-change level of the profile closest to spot (NaN if none in the grid)."""
    s = profile["spot"].to_numpy()
    g = profile["gex_usd_1pct"].to_numpy()
    idx = np.flatnonzero(np.sign(g[1:]) != np.sign(g[:-1]))
    if len(idx) == 0:
        return float("nan")
    lv = [s[i] - g[i] * (s[i + 1] - s[i]) / (g[i + 1] - g[i]) for i in idx]
    return float(min(lv, key=lambda v: abs(v - spot)))


def to_nq_contracts(gex_usd_1pct: float, nq_price: float, point_value: float = 20.0) -> float:
    """Express a dollar-gamma figure as NQ contracts of hedge per 1% move.

    Uses notional, so no fixed QQQ:NDX ratio is assumed."""
    return gex_usd_1pct / (nq_price * point_value)
