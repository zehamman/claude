"""Single-pass integrity audit of the NQ SCID file.

Everything is accumulated per calendar year (UTC) so that regime changes in
data quality (feed changes, aggressor-flag availability, unbundling) show up
as breaks in the yearly tables rather than being averaged away.
"""

from __future__ import annotations

import heapq
import json
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import flow, scid, sessions

Y0, Y1 = 2000, 2040
NY = Y1 - Y0
SIZE_EDGES = np.array([1, 2, 3, 6, 11, 26, 51, 101, 2**32], dtype=np.int64)
SIZE_LABELS = ["1", "2", "3-5", "6-10", "11-25", "26-50", "51-100", ">100"]
TOPK = 200
RTH_GAP_US = 60_000_000  # a >60 s gap between trades inside RTH is suspicious for NQ
BIG_JUMP_PTS = 20.0


@dataclass
class _TopK:
    k: int
    heap: list = field(default_factory=list)

    def push_many(self, keys: np.ndarray, payload: list[tuple]) -> None:
        for key, p in zip(keys.tolist(), payload):
            if len(self.heap) < self.k:
                heapq.heappush(self.heap, (key, p))
            elif key > self.heap[0][0]:
                heapq.heapreplace(self.heap, (key, p))

    def sorted(self) -> list:
        return sorted(self.heap, key=lambda x: -x[0])


class Auditor:
    def __init__(self) -> None:
        z = lambda *s: np.zeros(s, dtype=np.int64)  # noqa: E731
        self.n = z(NY)
        self.vol = z(NY)
        self.flag_n = z(NY, 3)  # sell, ambiguous, buy
        self.flag_vol = z(NY, 3)
        self.sum_cls = z(NY, 3)  # below, equal, above
        self.quote_ok = z(NY)
        self.agree = z(NY, 3, 3)  # [flag+1, quote+1]
        self.open_cat = z(NY, 4)
        self.multi_trade = z(NY)
        self.zero_vol = z(NY)
        self.off_tick = z(NY)
        self.bad_price = z(NY)
        self.us_nonzero = z(NY)
        self.eq_us = z(NY)
        self.eq_ms = z(NY)
        self.reversals = z(NY)
        self.max_reversal_us = 0
        self.rth_gaps = z(NY)
        self.big_jumps = z(NY)
        self.size_hist = z(NY, len(SIZE_LABELS))
        self.pmin = np.full(NY, np.inf)
        self.pmax = np.full(NY, -np.inf)
        self.sess = {}  # session day -> [n, vol, first_us, last_us]
        self.top_gaps = _TopK(TOPK)
        self.top_jumps = _TopK(TOPK)
        self.first_us: int | None = None
        self.last_us: int | None = None
        self._prev: np.ndarray | None = None
        self.records = 0

    # ------------------------------------------------------------------
    def update(self, start_index: int, rec: np.ndarray) -> None:
        if len(rec) == 0:
            return
        us = scid.to_unix_us(rec["dt"])
        yr = us.astype("datetime64[us]").astype("datetime64[Y]").astype(np.int64) + 1970 - Y0
        yr = np.clip(yr, 0, NY - 1)
        price = rec["close"].astype(np.float64)
        v = rec["volume"].astype(np.int64)

        bc = lambda w=None, y=yr: np.bincount(y, weights=w, minlength=NY)  # noqa: E731
        self.n += bc().astype(np.int64)
        self.vol += bc(v).astype(np.int64)

        fs = flow.flag_side(rec)
        for j, s in enumerate((-1, 0, 1)):
            m = fs == s
            self.flag_n[:, j] += bc(None, yr[m]).astype(np.int64)
            self.flag_vol[:, j] += bc(v[m], yr[m]).astype(np.int64)
        sc = flow.side_sum_class(rec)
        for j, s in enumerate((-1, 0, 1)):
            self.sum_cls[:, j] += bc(None, yr[sc == s]).astype(np.int64)

        qv = flow.quote_valid(rec)
        self.quote_ok += bc(None, yr[qv]).astype(np.int64)
        qs = flow.quote_side(rec)
        cell = yr * 9 + (fs.astype(np.int64) + 1) * 3 + (qs.astype(np.int64) + 1)
        self.agree += np.bincount(cell[qv], minlength=NY * 9).reshape(NY, 3, 3)

        oc = flow.open_category(rec)
        self.open_cat += np.bincount(yr * 4 + oc, minlength=NY * 4).reshape(NY, 4)
        self.multi_trade += bc(None, yr[rec["num_trades"] != 1]).astype(np.int64)
        self.zero_vol += bc(None, yr[v == 0]).astype(np.int64)
        good_p = np.isfinite(price) & (price > 0)
        self.bad_price += bc(None, yr[~good_p]).astype(np.int64)
        self.off_tick += bc(None, yr[good_p & ~flow.on_tick(price)]).astype(np.int64)
        self.us_nonzero += bc(None, yr[(us % 1000) != 0]).astype(np.int64)
        sb = np.clip(np.searchsorted(SIZE_EDGES, v, side="right") - 1, 0, len(SIZE_LABELS) - 1)
        self.size_hist += np.bincount(yr * len(SIZE_LABELS) + sb, minlength=NY * len(SIZE_LABELS)).reshape(
            NY, len(SIZE_LABELS)
        )
        for y in np.unique(yr[good_p]):
            py = price[good_p & (yr == y)]
            self.pmin[y] = min(self.pmin[y], py.min())
            self.pmax[y] = max(self.pmax[y], py.max())

        # ---- consecutive-record checks (include the record before this chunk)
        if self._prev is not None:
            p_us = np.concatenate([scid.to_unix_us(self._prev["dt"]), us])
            p_px = np.concatenate([self._prev["close"].astype(np.float64), price])
            off = 1
        else:
            p_us, p_px, off = us, price, 0
        d = np.diff(p_us)
        dy = yr[1 - off :]  # year of the later record in each consecutive pair
        self.reversals += bc(None, dy[d < 0]).astype(np.int64)
        if (d < 0).any():
            self.max_reversal_us = max(self.max_reversal_us, int(-d.min()))
        self.eq_us += bc(None, dy[d == 0]).astype(np.int64)
        dms = np.diff(p_us // 1000)
        self.eq_ms += bc(None, dy[dms == 0]).astype(np.int64)

        et_min, sess_day = sessions.et_minute_and_session(p_us)
        in_rth = (et_min[1:] >= sessions.RTH_START_MIN) & (et_min[1:] < sessions.RTH_END_MIN)
        same_sess = sess_day[1:] == sess_day[:-1]
        self.rth_gaps += bc(None, dy[in_rth & same_sess & (d > RTH_GAP_US)]).astype(np.int64)

        dp = np.abs(np.diff(p_px))
        self.big_jumps += bc(None, dy[dp > BIG_JUMP_PTS]).astype(np.int64)

        base = start_index - off
        gi = np.argpartition(d, -min(TOPK, len(d)))[-min(TOPK, len(d)) :] if len(d) else []
        self.top_gaps.push_many(
            d[gi], [(int(p_us[i]), int(p_us[i + 1]), base + int(i) + 1) for i in gi]
        )
        dpv = np.nan_to_num(dp, nan=0.0)
        ji = np.argpartition(dpv, -min(TOPK, len(dpv)))[-min(TOPK, len(dpv)) :] if len(dpv) else []
        self.top_jumps.push_many(
            dpv[ji], [(int(p_us[i + 1]), float(p_px[i]), float(p_px[i + 1]), base + int(i) + 1) for i in ji]
        )

        # ---- per-session coverage
        sd = sess_day[off:]
        uniq, first_idx, cnt = np.unique(sd, return_index=True, return_counts=True)
        sv = np.add.reduceat(v, first_idx)
        last_idx = first_idx + cnt - 1
        for s_, c_, v_, f_, l_ in zip(uniq.tolist(), cnt.tolist(), sv.tolist(), us[first_idx].tolist(), us[last_idx].tolist()):
            cur = self.sess.get(s_)
            if cur is None:
                self.sess[s_] = [c_, v_, f_, l_]
            else:
                cur[0] += c_
                cur[1] += v_
                cur[2] = min(cur[2], f_)
                cur[3] = max(cur[3], l_)

        if self.first_us is None:
            self.first_us = int(us[0])
        self.last_us = int(us[-1])
        self._prev = rec[-1:].copy()
        self.records += len(rec)

    # ------------------------------------------------------------------
    def yearly_table(self) -> pd.DataFrame:
        rows = []
        for i in np.flatnonzero(self.n):
            n = self.n[i]
            ag = self.agree[i]
            q = self.quote_ok[i]
            clean_q = ag[[0, 2]][:, [0, 2]].sum()  # flag clean & quote at bid/ask
            agree = ag[0, 0] + ag[2, 2]
            rows.append(
                {
                    "year": Y0 + i,
                    "records": n,
                    "volume": self.vol[i],
                    "pct_flag_buy": 100 * self.flag_n[i, 2] / n,
                    "pct_flag_sell": 100 * self.flag_n[i, 0] / n,
                    "pct_flag_ambiguous": 100 * self.flag_n[i, 1] / n,
                    "pct_vol_ambiguous": 100 * self.flag_vol[i, 1] / max(self.vol[i], 1),
                    "side_sum_below": self.sum_cls[i, 0],
                    "side_sum_above": self.sum_cls[i, 2],
                    "pct_quote_valid": 100 * q / n,
                    "pct_quote_inside_spread": 100 * ag[:, 1].sum() / max(q, 1),
                    "flag_vs_quote_agree_pct": 100 * agree / max(clean_q, 1),
                    "pct_open_single": 100 * self.open_cat[i, 0] / n,
                    "pct_open_unbundled": 100 * self.open_cat[i, 1:3].sum() / n,
                    "pct_open_other": 100 * self.open_cat[i, 3] / n,
                    "num_trades_ne_1": self.multi_trade[i],
                    "zero_volume": self.zero_vol[i],
                    "bad_price": self.bad_price[i],
                    "off_tick": self.off_tick[i],
                    "pct_us_nonzero": 100 * self.us_nonzero[i] / n,
                    "pct_eq_ms_prev": 100 * self.eq_ms[i] / n,
                    "eq_us_prev": self.eq_us[i],
                    "reversals": self.reversals[i],
                    "rth_gaps_gt_60s": self.rth_gaps[i],
                    "jumps_gt_20pts": self.big_jumps[i],
                    "price_min": self.pmin[i],
                    "price_max": self.pmax[i],
                    **{f"size_{lab}": 100 * self.size_hist[i, j] / n for j, lab in enumerate(SIZE_LABELS)},
                }
            )
        return pd.DataFrame(rows)

    def session_table(self) -> pd.DataFrame:
        s = pd.DataFrame.from_dict(self.sess, orient="index", columns=["records", "volume", "first_us", "last_us"])
        s.index = pd.to_datetime(s.index.astype(np.int64), unit="D")
        s.index.name = "session_date"
        s = s.sort_index()
        s["first_utc"] = pd.to_datetime(s.pop("first_us"), unit="us", utc=True)
        s["last_utc"] = pd.to_datetime(s.pop("last_us"), unit="us", utc=True)
        s["weekday"] = s.index.day_name()
        return s

    def missing_weekdays(self) -> list[str]:
        s = self.session_table()
        if s.empty:
            return []
        all_wd = pd.bdate_range(s.index.min(), s.index.max())
        return [d.date().isoformat() for d in all_wd.difference(s.index)]

    def gaps_table(self) -> pd.DataFrame:
        rows = []
        for gap, (a, b, idx) in self.top_gaps.sorted():
            ea = sessions.to_et(np.array([a]))[0]
            rows.append({"gap_minutes": gap / 6e7, "from_et": ea.isoformat(), "to_et": sessions.to_et(np.array([b]))[0].isoformat(),
                         "weekday_from": ea.day_name(), "record_index": idx})
        return pd.DataFrame(rows)

    def jumps_table(self) -> pd.DataFrame:
        rows = []
        for jump, (t, p0, p1, idx) in self.top_jumps.sorted():
            rows.append({"abs_jump_pts": jump, "at_et": sessions.to_et(np.array([t]))[0].isoformat(),
                         "from_px": p0, "to_px": p1, "record_index": idx})
        return pd.DataFrame(rows)


def run(path: str, chunk_records: int = 10_000_000, stop: int | None = None, progress: bool = True) -> tuple[Auditor, dict]:
    inf = scid.info(path)
    a = Auditor()
    t0 = time.time()
    for start, rec in scid.iter_chunks(path, chunk_records, stop=stop):
        a.update(start, rec)
        if progress:
            el = time.time() - t0
            done = (start + len(rec)) / (stop or inf.n_records)
            print(f"  {start + len(rec):,} records  {100 * done:5.1f}%  {el:7.0f}s", flush=True)
    summary = {
        "path": path,
        "file_size_bytes": inf.file_size,
        "header": {"version": inf.header.version, "utc_start_index": inf.header.utc_start_index},
        "n_records": inf.n_records,
        "records_audited": a.records,
        "trailing_bytes": inf.trailing_bytes,
        "first_utc": pd.Timestamp(a.first_us, unit="us", tz="UTC").isoformat() if a.first_us is not None else None,
        "last_utc": pd.Timestamp(a.last_us, unit="us", tz="UTC").isoformat() if a.last_us is not None else None,
        "timestamp_reversals": int(a.reversals.sum()),
        "max_reversal_seconds": a.max_reversal_us / 1e6,
        "sessions_with_data": len(a.sess),
        "missing_weekday_sessions": len(a.missing_weekdays()),
        "runtime_seconds": round(time.time() - t0, 1),
    }
    return a, summary


def boundary_report(m: pd.DataFrame, path: str) -> pd.DataFrame:
    """For each manifest boundary: ET time of switch and the price gap across it."""
    mm = scid.open_records(path)  # binary search on the memmap; nothing is loaded
    n = mm.shape[0]

    def find(t_us: int) -> int:
        lo, hi = 0, n
        target = scid.from_unix_us(t_us)
        while lo < hi:
            mid = (lo + hi) // 2
            if mm["dt"][mid] < target:
                lo = mid + 1
            else:
                hi = mid
        return lo

    rows = []
    for i in range(1, len(m)):
        s = int(m.loc[i, "start_us"])
        j = find(s)
        if j <= 0 or j >= n:
            continue
        before, after = mm[j - 1], mm[j]
        e_prev = sessions.to_et(np.array([int(scid.to_unix_us(np.array([before["dt"]]))[0])]))[0]
        e_next = sessions.to_et(np.array([s]))[0]
        rows.append({
            "segment": i, "from_symbol": m.loc[i - 1, "symbol"], "to_symbol": m.loc[i, "symbol"],
            "switch_et": e_next.isoformat(), "switch_et_hhmm": e_next.strftime("%H:%M"),
            "last_trade_prev_et": e_prev.isoformat(),
            "px_before": float(before["close"]), "px_after": float(after["close"]),
            "gap_pts": float(after["close"]) - float(before["close"]),
            "manifest_end_prev_matches": int(m.loc[i - 1, "end_us"]) == int(scid.to_unix_us(np.array([before["dt"]]))[0]),
        })
    return pd.DataFrame(rows)


def write_outputs(a: Auditor, summary: dict, out_dir: str, boundaries: pd.DataFrame | None = None) -> dict[str, str]:
    import os

    os.makedirs(out_dir, exist_ok=True)
    paths = {
        "summary": os.path.join(out_dir, "audit_summary.json"),
        "yearly": os.path.join(out_dir, "audit_yearly.csv"),
        "sessions": os.path.join(out_dir, "audit_sessions.csv"),
        "gaps": os.path.join(out_dir, "audit_top_gaps.csv"),
        "jumps": os.path.join(out_dir, "audit_top_jumps.csv"),
        "missing": os.path.join(out_dir, "audit_missing_weekdays.txt"),
    }
    with open(paths["summary"], "w") as fh:
        json.dump(summary, fh, indent=2, default=str)
    a.yearly_table().to_csv(paths["yearly"], index=False)
    a.session_table().to_csv(paths["sessions"])
    a.gaps_table().to_csv(paths["gaps"], index=False)
    a.jumps_table().to_csv(paths["jumps"], index=False)
    with open(paths["missing"], "w") as fh:
        fh.write("\n".join(a.missing_weekdays()))
    if boundaries is not None:
        paths["boundaries"] = os.path.join(out_dir, "audit_roll_boundaries.csv")
        boundaries.to_csv(paths["boundaries"], index=False)
    return paths
