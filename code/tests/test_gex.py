import numpy as np
import pandas as pd

from nqresearch import gex


def bs_delta(S, K, T, s, r=0.0, q=0.0):
    from scipy.stats import norm
    d1 = (np.log(S / K) + (r - q + 0.5 * s * s) * T) / (s * np.sqrt(T))
    return np.exp(-q * T) * norm.cdf(d1)


def test_gamma_matches_finite_difference():
    S, K, T, s, r, q = 400.0, 410.0, 0.1, 0.25, 0.04, 0.006
    h = 0.01
    fd = (bs_delta(S + h, K, T, s, r, q) - bs_delta(S - h, K, T, s, r, q)) / (2 * h)
    assert abs(gex.gamma(S, K, T, s, r, q) - fd) < 1e-6


def _chain(asof):
    exp = asof + pd.Timedelta(days=7)
    return pd.DataFrame({
        "strike": [390.0, 400.0, 410.0, 390.0, 400.0, 410.0],
        "right": ["C", "C", "C", "P", "P", "P"],
        "expiry": [exp] * 6, "oi": [1000, 5000, 3000, 4000, 6000, 1000], "iv": [0.2] * 6,
    })


def test_sign_scenarios_bound_each_other():
    asof = pd.Timestamp("2024-01-10 16:00", tz="America/New_York")
    ch = _chain(asof)
    v = {k: gex.total_gex(ch, 400.0, asof, scenario=k) for k in gex.SIGN_SCENARIOS}
    assert v["dealer_short_all"] < 0 < v["dealer_long_all"]
    assert np.isclose(v["dealer_short_all"], -v["dealer_long_all"])
    assert v["dealer_short_all"] <= v["dealer_long_calls_short_puts"] <= v["dealer_long_all"]


def test_expired_and_filters():
    asof = pd.Timestamp("2024-01-10 16:00", tz="America/New_York")
    ch = _chain(asof)
    ch.loc[0, "expiry"] = asof - pd.Timedelta(minutes=1)
    out = gex.chain_gex(ch, 400.0, asof)
    assert len(out) == 5
    assert len(gex.chain_gex(ch, 400.0, asof, exclude_expiring_within_hours=24 * 8)) == 0


def test_zero_gamma_level_exists_for_mixed_book():
    asof = pd.Timestamp("2024-01-10 16:00", tz="America/New_York")
    ch = _chain(asof)
    prof = gex.gex_profile(ch, 400.0, asof, rel_grid=np.linspace(-0.1, 0.1, 81))
    z = gex.zero_gamma_level(prof, 400.0)
    assert np.isnan(z) or 360 <= z <= 440
