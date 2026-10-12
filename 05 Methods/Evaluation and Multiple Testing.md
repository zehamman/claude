---
type: method
status: active
tags: [statistics, multiple-testing]
code: code/nqresearch/stats.py
---
# Evaluation and Multiple Testing

## Inference
- **Unit of observation:** the session. Intraday trades within a day are dependent; t-stats come from **daily** P&L with Newey–West (5 lags).
- **Sharpe CI:** stationary bootstrap (Politis–Romano, mean block 5 days), 95%.
- **Predictive content without a trading rule:** daily Spearman rank IC on **non-overlapping** samples (every h+1 bars), then a NW t across days. A feature with no IC can't make a strategy. A feature with IC can still fail after costs.
- **Volatility forecasts:** out-of-sample MSE on log RV, Diebold–Mariano t vs the nested baseline.

## Multiple testing
- Every evaluated configuration is appended to `code/logs/trials.jsonl`.
- **Deflated Sharpe Ratio** (Bailey & López de Prado 2014) for every DEV candidate, using the cumulative trial count and the variance of trial Sharpes.
- Controls (price-only P01/P02, random entry, fixed-time long) are reported side by side, so "edge" isn't confused with beta or price momentum.

## Overlap and regime traps
- Overlapping forward returns inflate t-stats → non-overlapping sampling or daily aggregation.
- Options activity rises with volatility → always control for VXN and lagged RV.
- Few regime switches (e.g. long stretches of negative GEX in 2022) → count **episodes**, not days.
- Report by year. A result carried by one year (2020, 2022) isn't robust.
