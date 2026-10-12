---
type: experiment
id: E001
status: ready-to-run
tags: [data-audit]
---
# E001 — SCID integrity audit (plan)

**Goal:** verify the inventory and characterise data quality **by year** before any research uses the file.

## Run (on your machine)
```powershell
cd "D:\Trading Bot\code"
python scripts\inspect_manifest.py
python scripts\run_audit.py --stop 20000000   # ~1 min smoke run
python scripts\run_audit.py                   # full pass, 1.33B records
```
Memory: about 2–3 GB per 10M-record chunk. Lower `chunk_records` in `config.toml` if needed. The run is I/O-bound and reads 50 GB once.

## Output
`code/work/audit/*` plus the generated note **[[E001 - SCID integrity audit (results)]]**.

## Checks and pass criteria (fixed before running)
| Check | Pass |
|---|---|
| Header magic/sizes; trailing bytes | SCID / 56 / 40; 0 |
| Record count, size, first/last date vs brief | equal, or difference explained (e.g. file extended) |
| Timestamp reversals | 0 (the brief says they were repaired) |
| Zero-volume, bad-price, off-tick records | 0 |
| NumTrades ≠ 1 | 0 |
| Aggressor flag per year | see policy in [[Data - Aggressor Side Reliability]] |
| µs digits | classify as counter vs real |
| Roll switches | at 18:00 ET; plausible gaps |
| RTH gaps > 60 s | near 0 outside known halts (e.g. 2020 limit-down episodes) |
| Missing weekday sessions | holidays only |

## After running
Fill in the *Interpretation* checklist in the results note, then update [[Data Inventory - NQ SCID]], [[Data - Aggressor Side Reliability]] and the [[Decision Log]] (e.g. which years are excluded from signed-flow studies).
