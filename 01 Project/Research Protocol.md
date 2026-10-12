---
type: method
status: active
tags: [protocol, pre-registration]
---
# Research Protocol

## Pre-registration (before touching data for a hypothesis)
Each hypothesis note in `03 Hypotheses` (use [[Hypothesis Template]]) must state:
1. **Mechanism** and a **directional, forward-looking prediction**, not a same-bar explanation.
2. **Observables**: exact fields and timestamps, each marked observed / inferred / unavailable.
3. **Signal**: calculation, decision time, holding horizon, entry/exit, session and roll handling.
4. **Falsification criterion**, **benchmark** and the **trade-only baseline** it must beat.
5. **Parameter grid** (small) and the DEV selection rule. Every grid point is logged as a trial.

## Chronological splits (enforced in `code/nqresearch/periods.py`)
| Period | Dates (session date) | Use |
|---|---|---|
| DEV | 2011-01-01 → 2018-12-31 | exploration, parameter choice |
| VAL | 2019-01-01 → 2022-12-31 | frozen spec only; every access logged |
| TEST | 2023-01-01 → end of data | **one shot per frozen spec**; a changed spec is refused by code |

- Splits are by session date. Bars never cross a contract segment or a session.
- **Options studies:** options history from affordable vendors starts years after 2011, so options hypotheses get their own DEV window (start of options data → 2018 or 2021, fixed in the hypothesis note *before* the data arrives). They share the same untouched TEST (2023+) so that the "with options" vs "without options" comparison is made on identical, unseen data.
- The access log (`code/logs/period_access.jsonl`) and trials log (`code/logs/trials.jsonl`) are committed to git. They are the audit trail. Summarised in [[Trials and Period Access]].

## Gates
- **DEV gate** (per hypothesis): ≥300 trades; net-positive (base costs) in ≥5 of 8 DEV years; and it must beat its price-only control at the same parameters. Fail → status `rejected`, no VAL access.
- **VAL gate**: net Sharpe (base costs) > 0.5; positive in ≥3 of 4 VAL years; stress-cost Sharpe > 0; deflated-Sharpe probability reported with all logged trials.
- **TEST**: report whatever happens. No retuning. If TEST is negative, the hypothesis is rejected even if VAL was good.
- **Options increment**: the options-augmented rule must beat the identical rule **without** the options feature on the same TEST days, with the difference's t-stat reported, under **every** pre-declared dealer-sign scenario that the hypothesis says should work.

## Reporting standard (every results note)
Trade count, trades/day, exposure, average gross and net points per trade, hit rate, net P&L, annualised Sharpe with a stationary-bootstrap 95% CI, Newey–West t of daily P&L, max drawdown and longest underwater stretch, results by year, and results under optimistic / base / stress costs. Negative results are written up with the same care.

## What is never allowed
- Retuning on VAL/TEST and calling it out-of-sample.
- Back-adjusted prices for P&L. We trade actual contract prices.
- Using sub-millisecond timestamp digits as information.
- Calling QQQ/NDX activity "NQ options flow", or calling a GEX estimate a dealer position.
