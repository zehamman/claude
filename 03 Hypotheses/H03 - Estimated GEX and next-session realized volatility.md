---
type: hypothesis
id: H03
status: pre-registered
data: [nq-scid, vxn, options-eod-oi-iv (not yet acquired)]
experiment: "[[E030 - HAR increment test]]"
tags: [gex, volatility, options]
---
# H03 — Estimated GEX and next-session realized volatility

## Mechanism
Delta-hedging dealers who are **long gamma** sell rallies and buy dips, which damps realized volatility. **Short-gamma** dealers hedge in the direction of the move, which amplifies it.

## Prediction
Higher estimated GEX at the close of D → **lower** RTH realized variance on session D+1, **after controlling for** log VXN at D and HAR lags of RV (1, 5, 22 sessions).

## Observables
| Field | Status |
|---|---|
| RV(D+1) from 5-min NQ RTH returns | observed |
| VXN close (FRED VXNCLS) | observed, free |
| Option OI per contract at D close | observed (vendor), published next morning |
| IV per contract | vendor model or derived → state which |
| Dealer sign | **assumption**: run all of `gex.SIGN_SCENARIOS` |
| GEX | **model-derived** ([[GEX Estimation Spec]]) |

## Test
`code/scripts/run_har.py`. Expanding-window OLS on log RV, refit every 21 sessions.
- Model A: HAR. Model B: HAR + log VXN. Model C: B + GEX feature (signed log-magnitude).
- Primary statistic: Diebold–Mariano t of C vs B (squared error, NW 5 lags), and the OOS R² of C vs B.
- Feature variants (all logged as trials): each sign scenario × {all expiries, ex ≤1DTE}.
- Options-DEV window: start of purchased OI history → 2018-12-31 (or → 2021-12-31 if history starts after 2016; fix this **before** the data arrives and record it in the [[Decision Log]]).

## Falsification
DM t for C vs B ≤ 1 in options-DEV under the convention scenario → rejected. Also rejected if the result **only** appears under one sign scenario that wasn't pre-declared. Declared scenario: `dealer_long_calls_short_puts`. Its flip (`dealer_short_all`) should give the opposite sign, which is a consistency check.

## Why this is first among the options tests
It is the most direct test of the hedging mechanism, and the cheapest (daily EOD data). If GEX can't improve a volatility forecast beyond VXN, directional uses of GEX have no plausible footing.
