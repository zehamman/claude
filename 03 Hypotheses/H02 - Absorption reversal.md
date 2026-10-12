---
type: hypothesis
id: H02
status: pre-registered
data: [nq-scid]
control: P02 price reversal
experiment: "[[E010 - Order-flow DEV grid]]"
tags: [order-flow, trades-only]
---
# H02 — Absorption reversal

## Mechanism
When heavy one-sided aggression fails to move price, a large passive participant (possibly informed, or a liquidity provider with inventory capacity) is absorbing it. Once the aggressive side is exhausted, price moves **against** the aggressors.

H01 and H02 are competing hypotheses. At a given horizon at most one can hold in the "imbalance with small price move" region. Both may well be false.

## Prediction
After a k-minute window with |z_imb_k| ≥ θ **and** a small price move (|z_ret_k| ≤ 0.5), the next-h-minute return is **opposite** to the imbalance sign.

## Observables
Same as [[H01 - Order-flow imbalance continuation]], plus `sd1m_30` (trailing 30-minute std of 1-min price changes, within session).

## Signal
- Short (long) if z_imb_k ≥ θ (≤ −θ) and |z_ret_k| ≤ 0.5. The absorption threshold 0.5 is fixed, not tuned.
- Entry, exit, window and grid as in H01 (18 configs).

## Benchmarks
**P02 price reversal** (same k/θ/h, sign of −z_ret_k when |z_ret_k| ≥ θ). H02 must beat P02 and H00.

## Falsification
DEV gate fails or H02 ≤ P02 → rejected. Note: "absorption" folklore is usually shown on hand-picked charts; that is no evidence here.
