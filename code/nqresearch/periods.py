"""Chronological split + enforced access discipline.

DEV   2011-01-01 .. 2018-12-31   free use
VAL   2019-01-01 .. 2022-12-31   only for FROZEN specs; every access logged
TEST  2023-01-01 .. end          one shot per hypothesis spec; logged; a second
                                 access with a DIFFERENT spec hash is refused

The spec hash is a hash of the full parameter dict that defines a strategy
(signal, thresholds, horizon, costs, filters). Changing anything after a TEST
look means the result is no longer out-of-sample, and the code refuses unless
``i_understand_this_is_not_oos=True`` - in which case the log records it and
the vault note must say so.
"""

from __future__ import annotations

import hashlib
import json
import os
import time

import pandas as pd

PERIODS = {
    "dev": ("2011-01-01", "2018-12-31"),
    "val": ("2019-01-01", "2022-12-31"),
    "test": ("2023-01-01", "2100-01-01"),
}

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "period_access.jsonl")


def spec_hash(spec: dict) -> str:
    blob = json.dumps(spec, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def _read_log(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def request(period: str, hypothesis: str, spec: dict, reason: str, log_path: str = LOG_PATH,
            i_understand_this_is_not_oos: bool = False) -> str:
    """Register an access to a period. Returns the spec hash. Raises on violations."""
    if period not in PERIODS:
        raise ValueError(period)
    h = spec_hash(spec)
    if period == "test":
        prior = [r for r in _read_log(log_path) if r["period"] == "test" and r["hypothesis"] == hypothesis]
        changed = [r for r in prior if r["spec_hash"] != h]
        if changed and not i_understand_this_is_not_oos:
            raise PermissionError(
                f"{hypothesis}: TEST already accessed with spec(s) {[r['spec_hash'] for r in changed]}; "
                f"new spec {h} would not be out-of-sample."
            )
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as fh:
        fh.write(json.dumps({
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"), "period": period, "hypothesis": hypothesis,
            "spec_hash": h, "reason": reason, "not_oos_override": bool(i_understand_this_is_not_oos),
            "spec": spec,
        }, default=str) + "\n")
    return h


def select(df: pd.DataFrame, period: str, date_col: str = "session_date") -> pd.DataFrame:
    a, b = PERIODS[period]
    d = pd.to_datetime(df[date_col])
    return df[(d >= a) & (d <= b)]


def label(dates: pd.Series) -> pd.Series:
    d = pd.to_datetime(dates)
    out = pd.Series("dev", index=dates.index)
    out[d >= PERIODS["val"][0]] = "val"
    out[d >= PERIODS["test"][0]] = "test"
    return out
