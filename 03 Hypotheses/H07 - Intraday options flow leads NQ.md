---
type: hypothesis
id: H07
status: deferred
data: [opra-trades-quotes or cme-options-trades (not acquired)]
tags: [options-flow, deferred]
---
# H07 — Intraday options flow leads NQ (deferred)

## Idea
Aggressive, delta-weighted QQQ/NDX (or NQ-option) customer buying over the last N minutes precedes NQ moves in the same direction, as dealers hedge the delta they just took on.

## Why deferred
- Needs trade-level options data with NBBO, to classify aggressor side by quote rule, and ideally open/close indicators. Expensive ([[Data Acquisition Plan]] stages 2–3).
- Volume alone doesn't reveal opening vs closing trades or intent, and quote-rule classification of options trades is noisy (many trades print inside the spread).
- QQQ options flow is not NQ options flow. Label it as related-market flow.

## Entry condition
Pre-register only if H03 or H05 shows the options channel carries information at all. Then run a cheap pilot first (e.g. one month of data) for timestamp alignment and classification quality.
