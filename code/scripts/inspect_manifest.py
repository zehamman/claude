"""Show the manifest's raw layout and whether the loader can map it.

    python scripts/inspect_manifest.py [--manifest PATH]
"""
import argparse

import _bootstrap  # noqa: F401
import pandas as pd

from nqresearch import config, manifest as mf

ap = argparse.ArgumentParser()
ap.add_argument("--manifest")
a = ap.parse_args()
cfg = config.load()
path = a.manifest or cfg["manifest"]
raw = pd.read_csv(path)
print(f"{path}\nrows={len(raw)} columns={list(raw.columns)}\n")
print(raw.head(5).to_string())
print("...")
print(raw.tail(3).to_string())
try:
    m = mf.load(path)
    print("\nParsed OK:")
    print(m.head().to_string())
    print(f"segments={len(m)} first={pd.Timestamp(m.start_us.iloc[0], unit='us')} last={pd.Timestamp(m.end_us.iloc[-1], unit='us')}")
except Exception as e:  # noqa: BLE001
    print(f"\nLoader could not map this manifest: {e}")
