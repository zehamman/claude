---
type: experiment
id: E010
status: parked
hypotheses: ["[[H01 - Order-flow imbalance continuation]]", "[[H02 - Absorption reversal]]"]
---
# E010 — Order-flow DEV grid (plan)

> [!warning] Parked (2026-10-12)
> Written ahead of schedule in session 1. Not to be run or extended until strategy research is explicitly started. See [[Working Agreement]] and [[Session Log]].


```powershell
python scripts\run_flow_study.py --period dev
```
- Runs 72 configs (H01, P01, H02, P02 × 18), all logged to `code/logs/trials.jsonl`.
- Writes **[[E010 - Order-flow DEV grid (results)]]**: daily rank-IC tables, the grid, the DEV gate, candidates and deflated-Sharpe probability.

**Before running:** confirm from E001 which years have a usable aggressor flag. If any DEV year fails the policy, pass `--exclude-years 2011,2012` (example) **before** the run and record it in the [[Decision Log]]. The exclusion becomes part of the frozen spec.

**If a candidate passes:** copy `work/flow_study/H0x.candidate.json` to `code/specs/H0x.frozen.json`, commit it (the git timestamp proves the freeze), then:
```powershell
python scripts\run_flow_study.py --period val --spec specs\H01.frozen.json
```
TEST only after the VAL gate passes, once.
