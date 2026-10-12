---
type: hypothesis
id: H04
status: parked
data: [nq-scid]
experiment: "[[E040 - Intraday momentum]]"
tags: [intraday-momentum, baseline, trades-only]
---
# H04 — Market intraday momentum (NQ-only)

> [!warning] Parked (2026-10-12)
> Written ahead of schedule in session 1. Not to be run or extended until strategy research is explicitly started. See [[Working Agreement]] and [[Session Log]].


## Mechanism
Published in index ETFs and futures (Gao, Han, Li & Zhou 2018; Baltussen, Da, Lammers & Martens 2021): the return earlier in the day predicts the **last half-hour** return. Proposed drivers are late-day hedging by short-gamma intermediaries and leveraged-ETF rebalancing, plus infrequent rebalancers and late-informed traders. See [[Literature - Prior Evidence]].

## Prediction
sign(r_rod) predicts the sign of the 15:30→16:00 ET return, where r_rod = price at 15:30 − previous session's 16:00 price (same contract).

## Rule (zero free parameters)
At the close of the 15:29 bar: long if r_rod > 0, short if < 0. Enter at the 15:30 bar open, exit at the 15:59 bar close. Sessions without a same-contract previous session (roll days, data holes) are skipped. Secondary predictor `r_first30` (10:00 price − previous 16:00) is reported and counts as a trial.

## Benchmarks
H00 fixed-time long over the same 30 minutes (beta); random sign.

## Falsification
- DEV: average gross per trade ≤ the 0.725-pt cost, or NW t of sign × return < 1.5 → no tradable effect (the effect may still exist gross; report both).
- Because nothing is tuned, the same spec runs on DEV → VAL → TEST in sequence. **Decay after publication (2018+) is a live possibility.** Compare DEV with VAL and TEST.

## Role
This is the **NQ-only baseline** that H05 tries to improve with options information.
