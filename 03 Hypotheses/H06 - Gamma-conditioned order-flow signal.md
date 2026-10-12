---
type: hypothesis
id: H06
status: draft
data: [nq-scid, options-eod-oi-iv]
depends_on: ["[[H01 - Order-flow imbalance continuation]]", "[[H02 - Absorption reversal]]"]
tags: [gex, order-flow, options-increment]
---
# H06 — Gamma-conditioned order-flow signal (draft)

## Idea
In negative-gamma regimes, hedging amplifies flow-driven moves (continuation, H01). In positive-gamma regimes, dealers absorb them (reversal, H02).

## Status
**Draft.** It becomes pre-registered only after E010 DEV results exist, so that the conditioning is fixed in advance:
- If both H01 and H02 are rejected unconditionally, H06 may still be tested, but **only** as the single pre-declared rule "H01 when GEX < 0, H02 when GEX ≥ 0" at one fixed k/θ/h chosen from DEV **without** looking at GEX. Grid search inside regimes is not allowed.
- Same VXN-tercile control as [[H05 - Gamma-conditioned intraday momentum]].
