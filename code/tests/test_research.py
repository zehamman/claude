import numpy as np
import pandas as pd
import pytest

from nqresearch import backtest, bars, costs, features, manifest as mf, periods, scid
from synth import make_records


@pytest.fixture(scope="module")
def rth(tmp_path_factory):
    d = tmp_path_factory.mktemp("r")
    rec, man = make_records(n_days=5)
    p = str(d / "x.scid")
    scid.write_scid(p, rec)
    mp = str(d / "m.csv")
    man.to_csv(mp, index=False)
    b, _ = bars.build(p, mf.load(mp), progress=False)
    df = features.rth_frame(b)
    df = features.add_flow_features(df, (5,))
    df = features.add_forward_returns(df, (5,))
    return df


def test_rth_groups_do_not_mix_contracts(rth):
    assert (rth.groupby("grp")["segment"].nunique() == 1).all()
    assert (rth.groupby("grp")["session_date"].nunique() == 1).all()
    assert rth["rth_min"].between(0, 389).all()


def test_forward_return_alignment(rth):
    g = rth[rth.grp == 0].reset_index(drop=True)
    t = 20
    assert np.isclose(g.loc[t, "fwd_5"], g.loc[t + 6, "open"] - g.loc[t + 1, "open"])
    # last 6 rows of a session have no forward return
    assert g["fwd_5"].tail(6).isna().all()


def test_rolling_features_use_past_only(rth):
    g = rth[rth.grp == 0].reset_index(drop=True)
    t = 30
    manual = (g.loc[t - 4:t, "buy_vol"] - g.loc[t - 4:t, "sell_vol"]).sum()
    assert g.loc[t, "ofi_5"] == manual
    assert g.loc[:3, "ofi_5"].isna().all()


def test_backtest_prices_and_forced_flat(rth):
    sig = np.zeros(len(rth), dtype=np.int8)
    g0 = np.flatnonzero(rth.grp.to_numpy() == 0)
    d = g0[20]
    sig[d] = 1
    late = g0[-10]  # decision after 15:30 -> must be ignored
    sig[late] = -1
    t = backtest.run(rth, sig, h=5, cost=costs.SCENARIOS["zero"], first_decision_min=15, last_decision_min=360)
    assert len(t) == 1
    assert t.entry_px.iloc[0] == rth.open.iloc[d + 1]
    assert t.exit_px.iloc[0] == rth.open.iloc[d + 6]
    assert np.isclose(t.gross_pts.iloc[0], rth.open.iloc[d + 6] - rth.open.iloc[d + 1])
    # forced flat: decision at 15:30 with h=60 must exit by 15:55 open
    sig2 = np.zeros(len(rth), dtype=np.int8)
    d2 = g0[np.flatnonzero(rth.rth_min.to_numpy()[g0] == 360)[0]]
    sig2[d2] = 1
    t2 = backtest.run(rth, sig2, h=60, cost=costs.SCENARIOS["zero"])
    assert pd.Timestamp(t2.exit_ts.iloc[0], unit="us", tz="UTC").tz_convert("America/New_York").strftime("%H:%M") == "15:55"


def test_costs():
    c = costs.SCENARIOS["base"]
    assert np.isclose(c.rt_dollars, 4.50 + 2 * 5.0)


def test_period_lock(tmp_path):
    log = str(tmp_path / "a.jsonl")
    periods.request("test", "HX", {"a": 1}, "first", log_path=log)
    periods.request("test", "HX", {"a": 1}, "same spec rerun ok", log_path=log)
    with pytest.raises(PermissionError):
        periods.request("test", "HX", {"a": 2}, "retuned", log_path=log)
    periods.request("test", "HX", {"a": 2}, "flagged", log_path=log, i_understand_this_is_not_oos=True)
