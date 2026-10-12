"""H00 - benchmarks every strategy must beat (DEV only by default).

    python scripts/run_baselines.py [--period dev]
"""
import argparse
import os

import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd

from nqresearch import backtest, config, costs, periods, report, stats, study

ap = argparse.ArgumentParser()
ap.add_argument("--period", default="dev", choices=["dev"])
a = ap.parse_args()
cfg = config.load()
full = study.load_rth(cfg["work_dir"])
periods.request("dev", "H00", {"baselines": 1}, "benchmarks")
df = periods.select(full, "dev")
sessions = df["session_date"].unique()

# 1. Unconditional forward returns by half-hour of RTH (gross, points), daily-clustered t
rows = []
df = df.assign(bucket=(df["rth_min"] // 30) * 30)
for h in (5, 15, 30):
    sub = df[df.groupby("grp").cumcount() % (h + 1) == 0]
    for b, g in sub.groupby("bucket"):
        daily = g.groupby("session_date")[f"fwd_{h}"].mean().dropna()
        rows.append({"h": h, "bucket_start": f"{9 + (30 + b) // 60:02d}:{(30 + b) % 60:02d}",
                     "mean_pts": g[f"fwd_{h}"].mean(), "t_daily": stats.newey_west_t(daily.to_numpy()),
                     "n_days": len(daily)})
tod = pd.DataFrame(rows)

# 2. Fixed-time long: enter 09:45, exit 15:55 (intraday beta)
sig = np.where(df["rth_min"].to_numpy() == 15, 1, 0).astype(np.int8)
fixed = []
for cname in ("base",):
    tr = backtest.run(df, sig, h=400, cost=costs.SCENARIOS[cname])
    daily = backtest.daily_pnl(tr, sessions)
    s = stats.summarize(tr, daily, float(len(df)))
    fixed.append({"rule": "long 09:45->15:55", "costs": cname, **{k: s[k] for k in ("trades", "avg_net_pts", "sharpe", "nw_t_daily_mean", "max_dd_usd")}})
    yr = stats.by_year(tr, daily)

# 3. Random-entry benchmark: no skill, same machinery, ~4 trades/day
rnd = []
rng = np.random.default_rng(42)
p = 4 / 345
for h in (5, 15, 30):
    for seed in range(20):
        r = rng.random(len(df))
        sgn = np.where(r < p / 2, 1, np.where(r < p, -1, 0)).astype(np.int8)
        tr = backtest.run(df, sgn, h, costs.SCENARIOS["base"])
        daily = backtest.daily_pnl(tr, sessions)
        s = stats.summarize(tr, daily, float(len(df)), boot=False)
        rnd.append({"h": h, "seed": seed, "trades": s["trades"], "avg_gross_pts": s["avg_gross_pts"],
                    "avg_net_pts": s["avg_net_pts"], "sharpe": s["sharpe"]})
rnd = pd.DataFrame(rnd)
rnd_sum = rnd.groupby("h").agg(trades=("trades", "mean"), avg_gross=("avg_gross_pts", "mean"),
                               avg_net=("avg_net_pts", "mean"), sharpe_mean=("sharpe", "mean"),
                               sharpe_p05=("sharpe", lambda x: np.percentile(x, 5)),
                               sharpe_p95=("sharpe", lambda x: np.percentile(x, 95))).reset_index()

out_dir = os.path.join(cfg["work_dir"], "baselines")
os.makedirs(out_dir, exist_ok=True)
tod.to_csv(os.path.join(out_dir, "time_of_day.csv"), index=False)
rnd.to_csv(os.path.join(out_dir, "random_entry.csv"), index=False)
cm = costs.SCENARIOS["base"]
body = f"""# E002 - Baselines on DEV (results)

Pre-registration: [[H00 - Baselines and cost hurdle]]. Period: DEV. Base round-trip cost
{cm.rt_points:.3f} pts (${cm.rt_dollars:.2f}).

## Cost hurdle
Any signal must earn more than **{cm.rt_points:.3f} points per trade gross** just to break even.

## Random entry (no skill), base costs, 20 seeds per horizon
{report.md_table(rnd_sum)}

## Fixed-time long 09:45 -> 15:55 (intraday market exposure)
{report.md_table(pd.DataFrame(fixed))}

{report.md_table(yr)}

## Unconditional forward return by time of day (gross points)
{report.md_table(tod)}
"""
note = report.write_note(cfg["vault"], "04 Experiments", "E002 - Baselines on DEV (results)",
                         {"type": "experiment-result", "experiment": "E002", "period": "dev", "tags": ["baseline", "H00"]}, body)
print("Wrote", note)
