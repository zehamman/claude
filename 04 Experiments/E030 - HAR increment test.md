---
type: experiment
id: E030
status: parked
hypothesis: "[[H03 - Estimated GEX and next-session realized volatility]]"
---
# E030 — HAR increment test (plan)

> [!warning] Parked (2026-10-12)
> Written ahead of schedule in session 1. Not to be run or extended until strategy research is explicitly started. See [[Working Agreement]] and [[Session Log]].


Step 1 (free, now): download VXNCLS from FRED into `code/work/VXNCLS.csv`, then
```powershell
python scripts\run_har.py --vxn work\VXNCLS.csv --period dev
```
Establishes how much VXN adds to HAR. That is the bar GEX must clear.

Step 2 (after options data): convert chains to the standard schema, then
```powershell
python scripts\build_gex_daily.py --chains <folder> --underlying QQQ --multiplier 100
python scripts\run_har.py --vxn work\VXNCLS.csv --gex work\gex_daily_QQQ.csv --period dev --oos-start <options-DEV pseudo-OOS start>
```
Every GEX column is a logged variant. The declared primary is `dealer_long_calls_short_puts`.
