import numpy as np
import pandas as pd
import pytest

from nqresearch import audit, bars, flow, manifest as mf, scid, sessions
from synth import make_records


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    d = tmp_path_factory.mktemp("d")
    rec, man = make_records()
    p = str(d / "x.scid")
    scid.write_scid(p, rec)
    mp = str(d / "m.csv")
    man.to_csv(mp, index=False)
    return p, mp, rec


def test_header_and_roundtrip(data):
    p, _, rec = data
    inf = scid.info(p)
    assert inf.n_records == len(rec) and inf.trailing_bytes == 0
    mm = scid.open_records(p)
    assert np.array_equal(np.asarray(mm), rec)


def test_epoch():
    # 2021-01-04 00:00 UTC is 44200 days after 1899-12-30
    us = pd.Timestamp("2021-01-04", tz="UTC").value // 1000
    assert scid.from_unix_us(us) == 44200 * 86400 * 1_000_000


def test_flag_side():
    r = np.zeros(4, dtype=scid.RECORD_DTYPE)
    r["volume"] = [3, 3, 3, 3]
    r["ask_volume"] = [3, 0, 1, 0]
    r["bid_volume"] = [0, 3, 2, 0]
    assert flow.flag_side(r).tolist() == [1, -1, 0, 0]
    assert flow.side_sum_class(r).tolist() == [0, 0, 0, -1]


def test_audit_counts(data):
    p, _, rec = data
    a, summary = audit.run(p, chunk_records=7_777, progress=False)
    assert summary["records_audited"] == len(rec)
    fs = flow.flag_side(rec)
    yt = a.yearly_table()
    assert yt["records"].sum() == len(rec)
    assert np.isclose(yt["pct_flag_ambiguous"].iloc[0], 100 * (fs == 0).mean())
    assert summary["timestamp_reversals"] == 0
    # synthetic data: flag and quote rule agree on clean records by construction
    assert np.isclose(yt["flag_vs_quote_agree_pct"].iloc[0], 100.0)
    # equal-ms pairs carry the sub-ms counter
    assert yt["pct_us_nonzero"].iloc[0] > 0
    us = scid.to_unix_us(rec["dt"])
    assert a.yearly_table()["eq_us_prev"].sum() == int((np.diff(us) == 0).sum())


def test_audit_detects_reversal(tmp_path):
    rec, _ = make_records(n_days=2)
    rec = rec.copy()
    i = len(rec) // 2
    rec["dt"][i] = rec["dt"][i - 1] - 5_000_000  # 5 s backwards
    p = str(tmp_path / "r.scid")
    scid.write_scid(p, rec)
    a, s = audit.run(p, chunk_records=1000, progress=False)
    assert s["timestamp_reversals"] == 1
    assert s["max_reversal_seconds"] >= 5.0


def test_manifest_and_segments(data):
    p, mp, rec = data
    m = mf.load(mp)
    assert list(m.columns[:4]) == ["segment", "symbol", "start_us", "end_us"]
    seg = mf.assign_segment(m, scid.to_unix_us(rec["dt"]))
    assert (seg >= 0).all() and set(seg.tolist()) == {0, 1}
    br = audit.boundary_report(m, p)
    assert len(br) == 1
    assert br["switch_et_hhmm"].iloc[0] == "18:00"
    assert abs(br["gap_pts"].iloc[0] - 60.0) < 5


@pytest.mark.parametrize("chunk", [997, 50_000, 10_000_000])
def test_bars_chunk_invariant(data, chunk):
    p, mp, rec = data
    m = mf.load(mp)
    ref, _ = bars.build(p, m, chunk_records=10_000_000, progress=False)
    b, stats = bars.build(p, m, chunk_records=chunk, progress=False)
    pd.testing.assert_frame_equal(ref, b)
    assert b["volume"].sum() == rec["volume"].astype(np.int64).sum()
    assert (b["buy_vol"] + b["sell_vol"] + b["amb_vol"] == b["volume"]).all()
    assert (b["buy_vol_q"] + b["sell_vol_q"] <= b["volume"]).all()
    # no bar straddles a contract segment
    assert not b.duplicated(["segment", "ts"]).any()
    assert (b.groupby("segment")["symbol"].nunique() == 1).all()


def test_bars_refuse_unsorted(tmp_path):
    rec, man = make_records(n_days=2)
    rec = rec.copy()
    rec["dt"][100] = rec["dt"][99] - 10
    p = str(tmp_path / "u.scid")
    scid.write_scid(p, rec)
    mp = str(tmp_path / "m.csv")
    man.to_csv(mp, index=False)
    with pytest.raises(ValueError):
        bars.build(p, mf.load(mp), progress=False)


def test_session_annotation():
    ts = pd.to_datetime(["2021-03-09 14:30", "2021-03-09 23:00", "2021-03-09 21:00"], utc=True).as_unit("us").asi8
    a = sessions.annotate(pd.DataFrame({"ts": ts}))
    assert a["is_rth"].tolist() == [True, False, False]
    assert [d.date().isoformat() for d in a["session_date"]] == ["2021-03-09", "2021-03-10", "2021-03-09"]
