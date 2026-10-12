"""H04 intraday momentum (NQ-only) and, with --gex, H05 GEX conditioning.

    python scripts/run_intraday_momentum.py --period dev
    python scripts/run_intraday_momentum.py --period dev --gex work/gex_daily.csv

The H04 rule has no tunable parameters, so the same spec is run on dev, val, test.
GEX CSV columns: session_date (the session the value is USABLE for) + one column per sign scenario.
"""
import argparse
import os

import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd

from nqresearch import backtest, config, costs, intraday_momentum as im, periods, report, stats, study

ap = argparse.ArgumentParser()
ap.add_argument("--period", choices=["dev", "val", "test"], required=True)
ap.add_argument("--gex")
ap.add_argument("--vxn", help="FRED VXNCLS csv; required with --gex for the VXN-tercile control")
a = ap.parse_args()
cfg = config.load()
full = study.load_rth(cfg["work_dir"])
SPEC = {"hypothesis": "H04", "version": 1, "predictor": "r_rod", "entry": "15:30 open", "exit": "15:59 bar close",
        "costs": "optimistic/base/stress reported", "gex_file": os.path.basename(a.gex) if a.gex else None}
h = periods.request(a.period, "H04" if not a.gex else "H05", SPEC, "intraday momentum")
df = periods.select(full, a.period)
pts = im.session_points(df)
sessions = df["session_date"].unique()

rows, trades_base = [], {}
for pred in ("r_rod", "r_first30"):
    sig = im.signal_from_points(df, pts, pred)
    for cname in ("optimistic", "base", "stress"):
        tr = backtest.run(df, sig, h=30, cost=costs.SCENARIOS[cname], first_decision_min=359,
                          last_decision_min=359, flat_by_min=400)
        daily = backtest.daily_pnl(tr, sessions)
        s = stats.summarize(tr, daily, float(len(df)), boot=(cname == "base"))
        if cname == "base":
            trades_base[pred] = (tr, daily)
        rows.append({"predictor": pred, "costs": cname, **{k: s.get(k) for k in (
            "trades", "avg_gross_pts", "avg_net_pts", "hit_rate_net", "sharpe", "sharpe_ci95", "nw_t_daily_mean",
            "max_dd_usd", "long_share")}})
res = pd.DataFrame(rows)
tr0, d0 = trades_base["r_rod"]
yr = stats.by_year(tr0, d0)

# Unconditional regression of last-30 return on r_rod scaled (pooled, NW t across days)
p = pts.dropna(subset=["r_rod", "r_last30"])
beta_t = stats.newey_west_t((np.sign(p["r_rod"]) * p["r_last30"]).to_numpy(), 5)

gex_section = "_No GEX file supplied; H05 not run._"
if a.gex:
    g = pd.read_csv(a.gex, parse_dates=["session_date"]).set_index("session_date")
    g = g.drop(columns=[c for c in ("asof_date", "spot", "n_contracts") if c in g.columns])
    t = tr0.assign(session_date=pd.to_datetime(tr0["session_date"]))
    t = t.join(g, on="session_date", how="left")
    grows = []
    for c in g.columns:
        x = t.dropna(subset=[c])
        for name, m in (("gex<0", x[c] < 0), ("gex>=0", x[c] >= 0)):
            sub = x[m]
            grows.append({"scenario": c, "regime": name, "trades": len(sub),
                          "avg_gross_pts": sub["gross_pts"].mean(), "avg_net_pts": sub["net_pts"].mean(),
                          "t_net": stats.newey_west_t(sub["net_pts"].to_numpy(), 5)})
        neg, pos = x[x[c] < 0]["gross_pts"], x[x[c] >= 0]["gross_pts"]
        diff = neg.mean() - pos.mean()
        se = np.sqrt(neg.var(ddof=1) / max(len(neg), 1) + pos.var(ddof=1) / max(len(pos), 1))
        grows.append({"scenario": c, "regime": "difference neg-pos", "trades": len(x), "avg_gross_pts": diff,
                      "avg_net_pts": np.nan, "t_net": diff / se if se > 0 else np.nan})
    gex_section = report.md_table(pd.DataFrame(grows))
    if a.vxn:
        v = pd.read_csv(a.vxn)
        v.columns = ["date", "vxn"]
        v["date"] = pd.to_datetime(v["date"])
        v["vxn"] = pd.to_numeric(v["vxn"], errors="coerce")
        v = v.dropna().set_index("date")["vxn"].sort_index()
        # VXN close of the PREVIOUS calendar day available before session D (no same-day look-ahead)
        t["vxn_prev"] = v.shift(1).reindex(t["session_date"], method="ffill").to_numpy()
        t["vxn_tercile"] = pd.qcut(t["vxn_prev"], 3, labels=["low", "mid", "high"])
        trows = []
        for c in g.columns:
            for terc, x in t.dropna(subset=[c, "vxn_tercile"]).groupby("vxn_tercile", observed=True):
                neg, pos = x[x[c] < 0]["gross_pts"], x[x[c] >= 0]["gross_pts"]
                se = np.sqrt(neg.var(ddof=1) / max(len(neg), 1) + pos.var(ddof=1) / max(len(pos), 1))
                trows.append({"scenario": c, "vxn_tercile": terc, "n_neg": len(neg), "n_pos": len(pos),
                              "gross_neg": neg.mean(), "gross_pos": pos.mean(),
                              "t_diff": (neg.mean() - pos.mean()) / se if se > 0 else np.nan})
        gex_section += "\n\n### Within VXN terciles (confound control: the split must survive here)\n" + report.md_table(pd.DataFrame(trows))
    else:
        gex_section += "\n\n**VXN-tercile control not run (pass --vxn). H05 cannot be accepted without it.**"

body = f"""# {"E040 - H04" if not a.gex else "E050 - H05"} intraday momentum {a.period.upper()} (results)

Pre-registration: [[H04 - Market intraday momentum (NQ-only)]]{", [[H05 - Gamma-conditioned intraday momentum]]" if a.gex else ""}.
Spec hash `{h}`. Period {a.period.upper()} {periods.PERIODS[a.period]}. The rule has no tuned parameters.

## Results (r_rod is primary; r_first30 is secondary and counts as an extra trial)
{report.md_table(res)}

NW t of sign(r_rod) x last-30 gross return (points, no costs): **{beta_t:.2f}**

## By year, primary, base costs
{report.md_table(yr)}

## GEX conditioning (H05)
Prediction (Baltussen et al. mechanism): momentum stronger when estimated dealer gamma < 0.
Must hold under the scenario(s) declared in the hypothesis note, not just the most convenient one.

{gex_section}
"""
title = f"{'E040 - H04' if not a.gex else 'E050 - H05'} intraday momentum {a.period.upper()} (results)"
note = report.write_note(cfg["vault"], "04 Experiments", title,
                         {"type": "experiment-result", "hypothesis": "H04" if not a.gex else "H05", "period": a.period,
                          "spec_hash": h, "tags": ["intraday-momentum", "baseline" if not a.gex else "gex"]}, body)
print(res.to_string())
print("Wrote", note)
