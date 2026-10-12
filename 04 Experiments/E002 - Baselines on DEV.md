---
type: experiment
id: E002
status: ready-after-bars
hypothesis: "[[H00 - Baselines and cost hurdle]]"
---
# E002 — Baselines on DEV (plan)

```powershell
python scripts\build_bars.py          # once, after E001
python scripts\run_baselines.py
```
Writes **[[E002 - Baselines on DEV (results)]]**. The first run also builds `work/rth_features.parquet`, the feature cache.

Engine sanity: random-entry gross P&L should be about 0. Net should be about −0.725 pt per trade.
