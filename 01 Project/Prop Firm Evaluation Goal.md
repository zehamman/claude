---
type: project
status: active
updated: 2026-10-12
tags: [goal, prop-firm, evaluation, risk]
---
# Prop Firm Evaluation Goal

## End goal (as stated, 2026-10-12)
1. An algorithm that **passes prop-firm evaluations** and keeps **funded accounts**.
2. A trading algorithm that is **statistically proven profitable**.

These are related but **not the same target**, and the research must track both.

## Why they differ
| | Long-run edge | Eval pass |
|---|---|---|
| Question | Is expected P&L after costs > 0 on untouched data? | What is the probability of hitting the profit target before breaching any rule? |
| Driven by | Mean and stability of returns | Mean **and** path: drawdown depth, daily loss clustering, time to target |
| Failure mode | No edge | Real edge, but drawdowns too deep for the rules |
| Luck | Small over many trades | Large: a no-edge strategy can pass sometimes by variance |

So: **first** establish a real edge (statistical proof). **Then** fit sizing and risk rules to a specific firm and estimate the pass probability. Never the other way round. Tuning for eval passes on historical data, without an edge, is curve-fitting to luck.

## Firm rules to capture (one note per firm when chosen)
| Rule | Why it matters |
|---|---|
| Account size and profit target | sets required return |
| Max loss: **trailing** vs static; trails on intraday equity or end-of-day balance? | the biggest driver of failures |
| Daily loss limit | caps bad days; interacts with intraday volatility |
| Consistency rule (max share of profit from one day) | penalises lumpy strategies |
| Minimum trading days / time limits | affects low-frequency strategies |
| Max contracts / scaling plan | caps size; NQ vs MNQ |
| Allowed hours, news restrictions, overnight/weekend holding | may forbid parts of a strategy |
| **Automated trading / bot policy** | some firms ban or restrict bots or require approval; check before building automation |
| Fees: eval cost, reset cost, activation, data, commissions per round trip | costs to include in the backtest and in pass economics |
| Funded-account rules (payout rules, buffer, scaling, drawdown) | often differ from eval rules; model both |

## Implications for the research
- **Contract size:** NQ ≈ $20/point, MNQ ≈ $2/point. With tight trailing drawdowns, MNQ granularity may be what makes a strategy fit. Results should be reportable per contract and scaled.
- **Costs:** use the actual commission schedule of the target firm. One firm publishes $3.78 per NQ round trip all-in (Topstep, seen 2026-10-12). See [[Transaction Cost Model]].
- **Statistics to report later** (when strategy work starts): worst daily loss, worst intraday drawdown (not just end-of-day), longest losing streak, and distribution of time to reach a profit target.
- **Pass probability (future method, parked):** replay the strategy's out-of-sample daily/intraday P&L paths against the firm's exact rules many times (block bootstrap of days), to estimate pass rate, expected time to pass, and expected cost per funded account. Done only on a strategy that already has a statistically supported edge.

## Open questions for you
- [ ] Which firm(s) and account size(s)?
- [ ] Do they allow fully automated trading for evals **and** funded accounts?
- [ ] NQ or MNQ?
- [ ] Budget per eval attempt (resets included)?
