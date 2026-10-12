"""Paths. Copy config.example.toml to config.toml (git-ignored) and edit."""

from __future__ import annotations

import os
import tomllib

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../code
VAULT = os.path.dirname(HERE)

DEFAULTS = {
    "scid": r"D:\SierraChartData\NQ_CONTINUOUS_CAUSAL_2011_2026.scid",
    "manifest": r"D:\SierraChartData\NQ_CONTINUOUS_CAUSAL_2011_2026.manifest.csv",
    "quality_json": r"D:\SierraChartData\NQ_CONTINUOUS_CAUSAL_2011_2026.quality.json",
    "work_dir": os.path.join(HERE, "work"),  # derived data (bars parquet etc.), git-ignored
    "vault": VAULT,
    "chunk_records": 10_000_000,
}


def load(path: str | None = None) -> dict:
    cfg = dict(DEFAULTS)
    path = path or os.environ.get("NQR_CONFIG") or os.path.join(HERE, "config.toml")
    if os.path.exists(path):
        with open(path, "rb") as fh:
            cfg.update(tomllib.load(fh).get("paths", {}))
    os.makedirs(cfg["work_dir"], exist_ok=True)
    return cfg
