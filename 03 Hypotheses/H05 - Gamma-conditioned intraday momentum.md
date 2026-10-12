---
type: hypothesis
id: H05
status: parked
data: [nq-scid, options-eod-oi-iv (not yet acquired)]
baseline: "[[H04 - Market intraday momentum (NQ-only)]]"
experiment: "[[E040 - Intraday momentum]]"
tags: [gex, intraday-momentum, options-increment]
---
# H05 — Gamma-conditioned intraday momentum

> [!warning] Parked (2026-10-12)
> Written ahead of schedule in session 1. Not to be run or extended until strategy research is explicitly started. See [[Working Agreement]] and [[Session Log]].


## Mechanism
Short-gamma dealers rebalance hedges toward the close in the direction of the day's move. When estimated dealer gamma is **negative**, last-half-hour momentum should be **stronger**. When positive, it should be weaker or reversed (Baltussen et al. 2021 report this for gamma imbalance).

## Prediction
Mean gross P&L of the H04 trade is higher on sessions with GEX < 0 than on sessions with GEX ≥ 0. GEX is computed from OI/IV at the close of D−1 (usable for session D).

## Options-increment test (the core question of the project)
- **Rule A (baseline):** H04 every eligible day.
- **Rule B:** trade H04 only when GEX < 0 (or size ×2 when GEX < 0 and ×0 when ≥ 0; pick **one** before data: **trade only when GEX < 0**).
- Compare A and B on the **same TEST days**: net Sharpe, net P&L, and the t-stat of the difference in mean gross P&L between regimes.
- Declared sign scenario: `dealer_long_calls_short_puts`. Also report `dealer_short_all` (which is always ≤ 0, so the conditioning would be degenerate — a reminder that the sign convention drives the result) and the ex-≤1DTE variant.

## Confounds to control
- GEX is negative mostly when volatility is high, and momentum may simply be stronger in high-vol regimes. **Also condition on VXN terciles**: the GEX split must survive within VXN terciles.
- Few regime switches: count independent negative-GEX episodes, not just days.

## Falsification
Difference t < 1.5 in options-DEV, or the effect disappears within VXN terciles → options information adds nothing beyond volatility. Rejected.
