"""Build 1-minute bars (per contract segment) with signed flow -> work_dir/bars_1m.parquet

    python scripts/build_bars.py [--big-size 10]
"""
import argparse
import json
import os

import _bootstrap  # noqa: F401

from nqresearch import bars, config, manifest as mf

ap = argparse.ArgumentParser()
ap.add_argument("--big-size", type=int, default=10)
ap.add_argument("--stop", type=int)
a = ap.parse_args()
cfg = config.load()
m = mf.load(cfg["manifest"])
b, stats = bars.build(cfg["scid"], m, chunk_records=int(cfg["chunk_records"]), big_size=a.big_size, stop=a.stop)
out = os.path.join(cfg["work_dir"], "bars_1m.parquet")
b.to_parquet(out, index=False)
with open(os.path.join(cfg["work_dir"], "bars_1m.stats.json"), "w") as fh:
    json.dump(stats, fh, indent=2, default=int)
print(stats, "->", out)
