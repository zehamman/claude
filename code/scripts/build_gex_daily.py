"""Build a daily GEX table from standardized option-chain snapshots.

Input: a folder of CSV/parquet files, one per snapshot date, with columns
    date        trade date D whose closing OI / IV the row describes
    strike, right ('C'/'P'), expiry (ISO timestamp incl. timezone, actual settlement time)
    oi          open interest as of the close of D (OCC/CME publish it the next morning)
    iv          implied vol at the close of D (vendor field - record which one in the vault)
    spot        underlying close on D (QQQ / NDX index / NQ futures price for 'black76')
Vendor files must be converted to this schema by a small adapter; document the adapter in the
vendor's vault note.

Output (work_dir/gex_daily.csv): one row per USABLE session (= first trading session after D,
because OI is only public the morning after D), one column per sign scenario, plus an
'ex_le1dte' variant that drops contracts expiring within 1 day (0DTE/1DTE regime-shift check).

    python scripts/build_gex_daily.py --chains D:\\options\\qqq_chains --underlying QQQ --multiplier 100
"""
import argparse
import glob
import os

import _bootstrap  # noqa: F401
import pandas as pd

from nqresearch import config, gex

ap = argparse.ArgumentParser()
ap.add_argument("--chains", required=True)
ap.add_argument("--underlying", required=True)
ap.add_argument("--multiplier", type=float, default=100.0)
ap.add_argument("--model", default="bsm", choices=["bsm", "black76"])
ap.add_argument("--r", type=float, default=0.0, help="flat rate if no 'r' column (document it!)")
ap.add_argument("--q", type=float, default=0.0, help="flat dividend yield if no 'q' column")
ap.add_argument("--close-time", default="16:00", help="ET time of the as-of snapshot")
a = ap.parse_args()
cfg = config.load()

files = sorted(glob.glob(os.path.join(a.chains, "*.csv")) + glob.glob(os.path.join(a.chains, "*.parquet")))
rows = []
for f in files:
    ch = pd.read_parquet(f) if f.endswith(".parquet") else pd.read_csv(f)
    ch["expiry"] = pd.to_datetime(ch["expiry"], utc=True)
    for D, c in ch.groupby("date"):
        asof = pd.Timestamp(f"{D} {a.close_time}", tz="America/New_York")
        spot = float(c["spot"].iloc[0])
        r = float(c["r"].iloc[0]) if "r" in c else a.r
        q = float(c["q"].iloc[0]) if "q" in c else a.q
        row = {"asof_date": pd.Timestamp(D), "spot": spot, "n_contracts": len(c)}
        for sc in gex.SIGN_SCENARIOS:
            kw = dict(r=r, q=q, multiplier=a.multiplier, scenario=sc, model=a.model)
            row[sc] = gex.total_gex(c, spot, asof, **kw)
            row[f"{sc}__ex_le1dte"] = gex.total_gex(c, spot, asof, exclude_expiring_within_hours=24 * 1.5, **kw)
        rows.append(row)
out = pd.DataFrame(rows).sort_values("asof_date")
# usable for the NEXT session (business-day approximation; holidays are reconciled when joined to sessions)
out["session_date"] = out["asof_date"] + pd.offsets.BDay(1)
path = os.path.join(cfg["work_dir"], f"gex_daily_{a.underlying}.csv")
cols = ["session_date"] + [c for c in out.columns if c not in ("session_date",)]
out[cols].to_csv(path, index=False)
print(f"{len(out)} days -> {path}")
print("Helper columns asof_date/spot/n_contracts are ignored by the study scripts.")
