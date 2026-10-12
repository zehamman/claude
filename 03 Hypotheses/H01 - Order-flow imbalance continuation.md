---
type: hypothesis
id: H01
status: parked
data: [nq-scid]
control: P01 price momentum
experiment: "[[E010 - Order-flow DEV grid]]"
tags: [order-flow, trades-only]
---
# H01 — Order-flow imbalance continuation

> [!warning] Parked (2026-10-12)
> Written ahead of schedule in session 1. Not to be run or extended until strategy research is explicitly started. See [[Working Agreement]] and [[Session Log]].


## Mechanism
Large parents (institutional metaorders) are split into many child trades on the same side. Order flow is therefore persistent (long memory of trade signs), and price impact accumulates while the parent is being worked.

## Prediction (directional, forward-looking)
After an unusually one-sided k-minute window of aggressor volume, the NQ return over the next h minutes, measured from the next bar's open, has the **same sign** as the imbalance.

## Observables
| Field | Status |
|---|---|
| Clean-flag buy/sell volume per minute | observed (if the year passes [[Data - Aggressor Side Reliability]]) |
| Ambiguous volume | observed, excluded, reported |
| Trade prices (bar open/close) | observed |
| Trailing scale (20 prior sessions) | derived, causal |

## Signal
- `imb_k` = (buy − sell) / (buy + sell) over the last k 1-minute RTH bars, clean flags only. NaN if any minute is missing.
- `z_imb_k` = imb_k / std(imb_k over the previous 20 sessions).
- Decide at bar close, 09:45–15:30 ET. Long if z ≥ θ, short if z ≤ −θ. Enter at the next bar's open. Exit at open + h, or 15:55. One position at a time.
- Grid (18 configs): k ∈ {5, 15}, θ ∈ {1.5, 2.0, 2.5}, h ∈ {5, 15, 30}.

## Benchmarks
- **P01 price momentum**: identical rule using `z_ret_k` (past k-minute price change / (σ₁ₘ·√k)). H01 must beat P01 at the same k/θ/h. Otherwise the "flow" is just price.
- H00 random entry and fixed-time long.

## Falsification
- DEV: no config passes the gate in [[Research Protocol]], **or** the best config doesn't beat P01 → rejected.
- Daily rank-IC of `z_imb_k` on `fwd_h` ≤ 0, or not above `z_ret_k`'s IC → no evidence of content even before costs.

## Prior
Likely fails after costs at these horizons ([[Challenges to the Brief]] §2).
