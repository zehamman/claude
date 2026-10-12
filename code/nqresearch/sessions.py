"""CME equity-index session conventions, all derived from UTC timestamps.

* Exchange time zone for research = America/New_York (handles DST).
* A Globex session that opens at 18:00 ET belongs to the NEXT calendar date
  (``session_date``). Implemented as ``(ET time + 6h).date``.
* RTH = 09:30 <= ET < 16:00 (cash-index hours). Futures trade until 17:00 ET.

Historic schedule changes (e.g. the former 16:15-16:30 CT maintenance halt)
are not hard-coded; the audit reports the observed intraday gap structure by
year instead, so that no session rule is assumed without evidence.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TZ = "America/New_York"
RTH_START_MIN = 9 * 60 + 30
RTH_END_MIN = 16 * 60


def to_et(unix_us: np.ndarray) -> pd.DatetimeIndex:
    return pd.to_datetime(np.asarray(unix_us, dtype=np.int64), unit="us", utc=True).tz_convert(TZ)


def annotate(df: pd.DataFrame, ts_col: str = "ts") -> pd.DataFrame:
    """Add et, session_date, et_minute (minutes after ET midnight), is_rth.

    ``ts_col`` holds Unix-epoch microseconds (UTC) of the bar START.
    """
    et = to_et(df[ts_col].to_numpy())
    out = df.copy()
    out["et"] = et
    out["session_date"] = (et + pd.Timedelta(hours=6)).tz_localize(None).normalize()
    out["et_minute"] = et.hour * 60 + et.minute
    out["is_rth"] = (out["et_minute"] >= RTH_START_MIN) & (out["et_minute"] < RTH_END_MIN)
    return out


# ---------------------------------------------------------------------------
# Fast per-record ET conversion for billion-row passes (lookup by UTC hour).
# ---------------------------------------------------------------------------
_HOUR_US = 3_600_000_000
_DAY_US = 86_400_000_000
_OFFSET_CACHE: dict[tuple[int, int], np.ndarray] = {}


def et_offset_us(unix_us: np.ndarray) -> np.ndarray:
    """UTC->ET offset (us, negative) per timestamp, DST-aware, via hourly table."""
    h = np.asarray(unix_us, dtype=np.int64) // _HOUR_US
    lo, hi = int(h.min()), int(h.max())
    key = (lo // 100_000, hi // 100_000 + 1)
    tab = _OFFSET_CACHE.get(key)
    base = key[0] * 100_000
    if tab is None:
        hours = np.arange(base, key[1] * 100_000, dtype=np.int64)
        idx = pd.to_datetime(hours * _HOUR_US, unit="us", utc=True).tz_convert(TZ)
        tab = (idx.tz_localize(None).as_unit("us").asi8 - hours * _HOUR_US).astype(np.int64)
        _OFFSET_CACHE[key] = tab
    return tab[h - base]


def et_minute_and_session(unix_us: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(minutes after ET midnight, session_date as days since 1970) per timestamp."""
    et_us = np.asarray(unix_us, dtype=np.int64) + et_offset_us(unix_us)
    et_min = (et_us % _DAY_US) // 60_000_000
    sess_day = (et_us + 6 * _HOUR_US) // _DAY_US
    return et_min.astype(np.int16), sess_day.astype(np.int32)
