"""H01 / H02 order-flow studies with price-only controls (P01 / P02).

DEV (exploration, full pre-registered grid; every config is logged as a trial):
    python scripts/run_flow_study.py --period dev

VAL / TEST (one frozen spec per hypothesis; access is logged and TEST is one-shot):
    python scripts/run_flow_study.py --period val  --spec specs/H01.frozen.json
    python scripts/run_flow_study.py --period test --spec specs/H01.frozen.json
"""
import argparse
import itertools
import json
import os

import _bootstrap  # noqa: F401
import pandas as pd

from nqresearch import config, costs, periods, report, signals, stats, study

ap = argparse.ArgumentParser()
ap.add_argument("--period", choices=["dev", "val", "test"], required=True)
ap.add_argument("--spec")
ap.add_argument("--rebuild", action="store_true")
ap.add_argument("--exclude-years", default="", help="comma list of years whose aggressor flag failed E001, e.g. 2011,2012")
a = ap.parse_args()
cfg = config.load()
full = study.load_rth(cfg["work_dir"], a.rebuild)
EXCL = sorted(int(y) for y in a.exclude_years.split(",") if y.strip())
if EXCL:
    full = full[~pd.to_datetime(full["session_date"]).dt.year.isin(EXCL)]
out_dir = os.path.join(cfg["work_dir"], "flow_study")
os.makedirs(out_dir, exist_ok=True)

MIN_TRADES = 300
MIN_POS_YEARS_DEV = 5


def ic_table(df):
    rows = []
    for k, h in itertools.product((5, 15), (5, 15, 30)):
        for feat in (f"z_imb_{k}", f"z_ret_{k}"):
            ic = stats.daily_ic(df, feat, f"fwd_{h}", step=h + 1)
            if len(ic) == 0:
                continue
            by_y = ic.groupby(pd.to_datetime(ic.index).year).mean()
            rows.append({"feature": feat, "h": h, "days": len(ic), "mean_ic": ic.mean(),
                         "t_days": stats.newey_west_t(ic.to_numpy(), 5),
                         "years_ic_pos": int((by_y > 0).sum()), "years": len(by_y)})
    return pd.DataFrame(rows)


if a.period == "dev":
    periods.request("dev", "H01/H02/P01/P02", {"grid": signals.GRID, "exclude_years": EXCL}, "dev exploration")
    df = periods.select(full, "dev")
    ic = ic_table(df)
    rows, trials = [], []
    for name in ("H01", "P01", "H02", "P02"):
        for k, th, h in itertools.product(signals.GRID["k"], signals.GRID["theta"], signals.GRID["h"]):
            tr, daily, s = study.evaluate(df, name, k, th, h, "base")
            yr = stats.by_year(tr, daily)
            row = {"signal": name, "k": k, "theta": th, "h": h, **{x: s[x] for x in (
                "trades", "avg_gross_pts", "avg_net_pts", "hit_rate_net", "sharpe", "nw_t_daily_mean",
                "max_dd_usd", "exposure")}, "years_pos": int((yr["net_usd"] > 0).sum()),
                "daily_sr": study.daily_sharpe_per_period(daily)}
            rows.append(row)
            trials.append({"signal": name, "k": k, "theta": th, "h": h, "cost": "base",
                           "sharpe": s["sharpe"], "trades": s["trades"]})
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(out_dir, "dev_grid.csv"), index=False)
    n_trials = report.log_trials("H01/H02/P01/P02", "dev", trials)

    picks = []
    for name in ("H01", "H02"):
        r = res[(res.signal == name) & (res.trades >= MIN_TRADES) & (res.years_pos >= MIN_POS_YEARS_DEV)]
        if len(r) == 0:
            picks.append({"signal": name, "status": "REJECTED at DEV: no config met the pre-registered DEV gate"})
            continue
        best = r.sort_values("sharpe", ascending=False).iloc[0]
        ctrl = res[(res.signal == "P0" + name[-1]) & (res.k == best.k) & (res.theta == best.theta) & (res.h == best.h)].iloc[0]
        sr_var = res[res.signal.isin(["H01", "H02", "P01", "P02"])]["daily_sr"].var()
        dsr = stats.deflated_sharpe(best.daily_sr, int(len(df.session_date.unique())), n_trials, sr_var)
        spec = {"hypothesis": name, "version": 1, "k": int(best.k), "theta": float(best.theta), "h": int(best.h),
                "cost_model": "base", "decision_window_rth_min": [15, 360], "flat_by_rth_min": 385,
                "signal_def": f"signals.{signals.SIGNALS[name].__name__}", "exclude_years": EXCL}
        with open(os.path.join(out_dir, f"{name}.candidate.json"), "w") as fh:
            json.dump(spec, fh, indent=2)
        picks.append({"signal": name, "status": "candidate", "k": best.k, "theta": best.theta, "h": best.h,
                      "dev_sharpe": best.sharpe, "control_sharpe_same_params": ctrl.sharpe,
                      "dsr_prob": dsr, "trials_logged": n_trials})
    picks = pd.DataFrame(picks)
    body = f"""# E010 - Order-flow DEV grid (results)

Pre-registration: [[H01 - Order-flow imbalance continuation]], [[H02 - Absorption reversal]].
Controls: P01 price momentum, P02 price reversal (same k/theta/h, no flow information).
Period: DEV only ({periods.PERIODS['dev'][0]} .. {periods.PERIODS['dev'][1]}). Cost model: base
({costs.SCENARIOS['base'].rt_points:.3f} pts = ${costs.SCENARIOS['base'].rt_dollars:.2f} round trip).
Trials logged for this family so far: **{n_trials}**. Years excluded (aggressor flag failed E001): {EXCL or 'none'}.

## 1. Is there any predictive content? (daily rank IC, non-overlapping samples)
`t_days` is a Newey-West t-stat across daily ICs. A flow feature only matters if it beats the price-only
feature (`z_ret`) at the same k/h.

{report.md_table(ic, "{:.4f}")}

## 2. Pre-registered grid, base costs
{report.md_table(res.sort_values(['signal', 'sharpe'], ascending=[True, False]))}

## 3. DEV gate and candidates
Gate: trades >= {MIN_TRADES}, net-positive in >= {MIN_POS_YEARS_DEV} of the DEV years; best Sharpe among those.
Then a candidate must also beat its price-only control - otherwise the "order flow" is just price.
`dsr_prob` = deflated-Sharpe probability given all trials logged.

{report.md_table(picks)}

## Interpretation (fill in by hand)
- Does flow add over price? ____
- Freeze? If yes, copy `work/flow_study/H0x.candidate.json` to `code/specs/H0x.frozen.json` and commit
  BEFORE running VAL. Record the decision in [[Decision Log]].
"""
    note = report.write_note(cfg["vault"], "04 Experiments", "E010 - Order-flow DEV grid (results)",
                             {"type": "experiment-result", "experiment": "E010", "period": "dev",
                              "tags": ["order-flow", "H01", "H02"]}, body)
    print(picks.to_string())
    print("Wrote", note)

else:
    if not a.spec:
        raise SystemExit("--spec is required for val/test")
    with open(a.spec) as fh:
        spec = json.load(fh)
    name = spec["hypothesis"]
    h = periods.request(a.period, name, spec, f"{a.period} evaluation of frozen spec")
    df = periods.select(full, a.period)
    if spec.get("exclude_years"):
        df = df[~pd.to_datetime(df["session_date"]).dt.year.isin(spec["exclude_years"])]
    out_rows, by_year = [], None
    for sig_name in (name, "P0" + name[-1]):
        for cname in ("optimistic", "base", "stress"):
            tr, daily, s = study.evaluate(df, sig_name, spec["k"], spec["theta"], spec["h"], cname)
            if sig_name == name and cname == "base":
                s = stats.summarize(tr, daily, float(len(df)), boot=True)
                by_year = stats.by_year(tr, daily)
                tr.to_csv(os.path.join(out_dir, f"{name}_{a.period}_trades.csv"), index=False)
            out_rows.append({"signal": sig_name, "costs": cname, **{x: s.get(x) for x in (
                "trades", "avg_gross_pts", "avg_net_pts", "hit_rate_net", "sharpe", "sharpe_ci95",
                "nw_t_daily_mean", "max_dd_usd", "longest_underwater_days", "exposure", "long_share")}})
    res = pd.DataFrame(out_rows)
    body = f"""# E01x - {name} {a.period.upper()} evaluation (results)

Frozen spec `{a.spec}` (hash `{h}`):
```json
{json.dumps(spec, indent=1)}
```
Period: {a.period.upper()} {periods.PERIODS[a.period]}. {"**TEST is one-shot. Do not retune after reading this.**" if a.period == "test" else ""}

## Results by cost scenario (with price-only control)
{report.md_table(res)}

## By year (base costs)
{report.md_table(by_year)}

## Verdict (fill in by hand against the pre-registered criteria in [[{signals.HYPOTHESIS_NOTES[name]}]])
"""
    note = report.write_note(cfg["vault"], "04 Experiments", f"{name} - {a.period.upper()} evaluation (results)",
                             {"type": "experiment-result", "hypothesis": name, "period": a.period, "spec_hash": h,
                              "tags": ["order-flow", name]}, body)
    print(res.to_string())
    print("Wrote", note)
