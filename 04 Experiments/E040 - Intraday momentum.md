---
type: experiment
id: E040
status: ready-after-bars
hypotheses: ["[[H04 - Market intraday momentum (NQ-only)]]", "[[H05 - Gamma-conditioned intraday momentum]]"]
---
# E040 — Intraday momentum (plan)

```powershell
python scripts\run_intraday_momentum.py --period dev
python scripts\run_intraday_momentum.py --period val
python scripts\run_intraday_momentum.py --period test     # one shot; the rule has no parameters
```
With options data (H05):
```powershell
python scripts\run_intraday_momentum.py --period dev --gex work\gex_daily_QQQ.csv --vxn work\VXNCLS.csv
```
The VXN-tercile breakdown (the H05 confound control) is built in. It uses the previous day's VXN close, so there is no same-day look-ahead. Without `--vxn`, the results note says H05 can't be accepted.
