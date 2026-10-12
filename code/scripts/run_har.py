"""H03 - does a daily options feature (e.g. estimated GEX) improve next-session realized-vol
forecasts beyond HAR + implied vol? Runs with VXN alone until options data exist.

    python scripts/run_har.py --vxn VXNCLS.csv [--gex gex_daily.csv] --period dev

VXN: FRED series VXNCLS (CSV with columns observation_date, VXNCLS). Value for date D is the D close,
used to forecast the NEXT session.
GEX CSV: columns session_date (the session the value is USABLE for, i.e. already lagged so that the
input OI/IV were public before that session's open) plus one column per sign scenario.
"""
import argparse
import os

import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd

from nqresearch import config, periods, report, rv, study

ap = argparse.ArgumentParser()
ap.add_argument("--vxn", required=True)
ap.add_argument("--gex")
ap.add_argument("--period", default="dev", choices=["dev", "val", "test"])
ap.add_argument("--oos-start", default="2014-01-01", help="pseudo-OOS start inside DEV")
ap.add_argument("--min-train", type=int, default=500)
a = ap.parse_args()
cfg = config.load()
full = study.load_rth(cfg["work_dir"])
d = rv.daily_rv(full)

v = pd.read_csv(a.vxn)
v.columns = ["date", "vxn"]
v["date"] = pd.to_datetime(v["date"])
v["vxn"] = pd.to_numeric(v["vxn"], errors="coerce")
v = v.dropna().set_index("date")["vxn"]
extra = pd.DataFrame({"lvxn": np.log(v).reindex(d.index, method="ffill")})  # VXN close of session date D
cols_g = []
if a.gex:
    g = pd.read_csv(a.gex, parse_dates=["session_date"]).set_index("session_date")
    g = g.drop(columns=[c for c in ("asof_date", "spot", "n_contracts") if c in g.columns])
    # scale-free: signed log magnitude, so regime shifts in options volume do not dominate the fit
    g = np.sign(g) * np.log1p(g.abs() / 1e6)
    cols_g = list(g.columns)
    # Row D predicts session D+1, so it must carry the value USABLE FOR session D+1.
    extra = extra.join(g.reindex(d.index).shift(-1), how="left")

X = rv.har_design(d["rv"], extra)
X["period"] = periods.label(pd.Series(X.index, index=X.index)).to_numpy()
spec = {"model": "HAR(1,5,22) log RV", "extra": ["lvxn"] + cols_g, "refit_every": 21}
periods.request(a.period, "H03", spec, "HAR increment test")
if a.period == "dev":
    Xp = X[X["period"] == "dev"]
    start = a.oos_start
else:
    Xp = X[X["period"].isin(["dev", "val"] if a.period == "val" else ["dev", "val", "test"])]
    start = periods.PERIODS[a.period][0]

base_cols = ["lrv_d", "lrv_w", "lrv_m"]
f0 = rv.expanding_oos(Xp, base_cols, start, min_train=a.min_train)
f1 = rv.expanding_oos(Xp, base_cols + ["lvxn"], start, min_train=a.min_train)
y = Xp["y"]
rows = [{"comparison": "HAR+VXN vs HAR", **rv.diebold_mariano(y, f0, f1)}]
for c in cols_g:
    f2 = rv.expanding_oos(Xp, base_cols + ["lvxn", c], start, min_train=a.min_train)
    rows.append({"comparison": f"HAR+VXN+{c} vs HAR+VXN", **rv.diebold_mariano(y, f1, f2)})
res = pd.DataFrame(rows)
out = os.path.join(cfg["work_dir"], f"har_{a.period}.csv")
res.to_csv(out, index=False)
body = f"""# E030 - HAR realized-vol increment test, {a.period.upper()} (results)

Pre-registration: [[H03 - Estimated GEX and next-session realized volatility]].
Forecast target: log RTH realized variance (5-min returns) of the next session. Expanding-window OLS,
refit every 21 sessions, forecasts from {start}. `dm_t` > 0 means the richer model has lower squared error
(Newey-West, 5 lags). GEX columns tested: {cols_g or "none supplied (VXN-only run)"}.

{report.md_table(res, "{:.4f}")}
"""
note = report.write_note(cfg["vault"], "04 Experiments", f"E030 - HAR increment test {a.period.upper()} (results)",
                         {"type": "experiment-result", "experiment": "E030", "period": a.period, "tags": ["H03", "gex", "volatility"]}, body)
print(res.to_string())
print("Wrote", note)
