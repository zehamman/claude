---
type: hypothesis
id: H00
status: parked
data: [nq-scid]
experiment: "[[E002 - Baselines on DEV]]"
tags: [baseline]
---
# H00 — Baselines and cost hurdle

> [!warning] Parked (2026-10-12)
> Written ahead of schedule in session 1. Not to be run or extended until strategy research is explicitly started. See [[Working Agreement]] and [[Session Log]].


Not a trading idea. It's the yardstick every strategy is measured against.

## Components
1. **Cost hurdle.** Base round trip = 0.725 pt ($14.50). A signal needs average **gross** P&L per trade above this.
2. **Random entry.** Same engine, random long/short at ~4 trades/day, horizons 5/15/30 min, 20 seeds. Expected net ≈ −cost per trade. This validates the engine (no hidden positive bias) and shows the cost drag.
3. **Fixed-time long 09:45→15:55.** Intraday market exposure. Any directional strategy with a long bias must be judged against it.
4. **Time-of-day drift.** Unconditional forward returns by half-hour bucket, with daily-clustered t-stats.

## Falsification / sanity
If random entry shows a positive average gross P&L with |t| > 2, suspect the engine (leakage or a price-alignment bug) before suspecting the market.
