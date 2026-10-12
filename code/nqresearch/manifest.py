"""Roll / contract manifest for the stitched NQ continuous SCID.

The exact column layout of ``NQ_CONTINUOUS_CAUSAL_2011_2026.manifest.csv``
was not available when this code was written, so the loader maps common
column names onto a canonical schema and FAILS LOUDLY if it cannot. Run
``python -m scripts.inspect_manifest`` first and, if needed, pass an
explicit ``column_map``.

Canonical schema (one row per contract segment, chronological)::

    segment       int     0..N-1
    symbol        str     e.g. NQH11 / NQH2011
    start_us      int64   Unix us (UTC), first record of the segment (inclusive)
    end_us        int64   Unix us (UTC), last record of the segment (inclusive)
    first_record  int64   optional: record index in the SCID
    last_record   int64   optional

Timestamps without a timezone are assumed to be UTC (Sierra's storage
convention). The audit checks this assumption: a session-based roll should
switch contracts at a Globex session open (18:00 ET); boundaries that land
mid-session suggest a timezone mismatch.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ALIASES = {
    "symbol": ["symbol", "contract", "contract_symbol", "ticker", "instrument", "sc_symbol"],
    "start": ["start_us", "start_utc", "start", "start_time", "start_timestamp", "first_timestamp",
              "first_ts", "from", "from_utc", "segment_start", "begin"],
    "end": ["end_us", "end_utc", "end", "end_time", "end_timestamp", "last_timestamp",
            "last_ts", "to", "to_utc", "segment_end", "until"],
    "first_record": ["first_record", "start_record", "start_index", "record_start", "first_index"],
    "last_record": ["last_record", "end_record", "end_index", "record_end", "last_index"],
}


def _find(cols: list[str], names: list[str]) -> str | None:
    low = {c.lower().strip(): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    return None


def _to_unix_us(s: pd.Series) -> np.ndarray:
    if pd.api.types.is_integer_dtype(s.dtype):
        v = s.to_numpy(np.int64)
        # Heuristic on magnitude: seconds / ms / us since 1970
        mx = np.abs(v).max()
        if mx < 10**11:
            return v * 1_000_000
        if mx < 10**14:
            return v * 1_000
        return v
    t = pd.to_datetime(s, utc=False, format="mixed")
    if t.dt.tz is None:
        t = t.dt.tz_localize("UTC")
    naive_utc = t.dt.tz_convert("UTC").dt.tz_localize(None)
    return naive_utc.to_numpy().astype("datetime64[us]").astype(np.int64)


def load(path: str, column_map: dict[str, str] | None = None) -> pd.DataFrame:
    raw = pd.read_csv(path)
    cols = list(raw.columns)
    cmap = dict(column_map or {})
    for key in ALIASES:
        if key not in cmap:
            found = _find(cols, ALIASES[key])
            if found is not None:
                cmap[key] = found
    missing = [k for k in ("symbol", "start", "end") if k not in cmap]
    if missing:
        raise ValueError(
            f"Manifest {path}: could not identify columns {missing}. Columns present: {cols}. "
            "Pass column_map={'symbol': ..., 'start': ..., 'end': ...}."
        )
    out = pd.DataFrame(
        {
            "symbol": raw[cmap["symbol"]].astype(str),
            "start_us": _to_unix_us(raw[cmap["start"]]),
            "end_us": _to_unix_us(raw[cmap["end"]]),
        }
    )
    for k in ("first_record", "last_record"):
        if k in cmap:
            out[k] = raw[cmap[k]].astype(np.int64)
    out = out.sort_values("start_us", kind="stable").reset_index(drop=True)
    out.insert(0, "segment", np.arange(len(out), dtype=np.int32))
    validate(out)
    return out


def validate(m: pd.DataFrame) -> None:
    if (m["end_us"] < m["start_us"]).any():
        bad = m[m["end_us"] < m["start_us"]]
        raise ValueError(f"Manifest has segments ending before they start:\n{bad}")
    overlap = m["start_us"].to_numpy()[1:] <= m["end_us"].to_numpy()[:-1]
    if overlap.any():
        idx = np.flatnonzero(overlap)
        raise ValueError(f"Manifest segments overlap at rows {idx.tolist()}")
    if m["symbol"].duplicated().any():
        raise ValueError(f"Duplicate symbols in manifest: {m.loc[m.symbol.duplicated(), 'symbol'].tolist()}")


def assign_segment(m: pd.DataFrame, unix_us: np.ndarray) -> np.ndarray:
    """Segment id per timestamp; -1 for timestamps outside every segment."""
    starts = m["start_us"].to_numpy()
    ends = m["end_us"].to_numpy()
    idx = np.searchsorted(starts, unix_us, side="right") - 1
    ok = idx >= 0
    ok[ok] &= unix_us[ok] <= ends[idx[ok]]
    return np.where(ok, idx, -1).astype(np.int32)
