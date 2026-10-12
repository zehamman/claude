---
type: project
status: active
tags: [charter]
---
# Research Charter

## Objective
Build, or rule out, a systematic NQ futures strategy using executed-trade order flow, and test whether options information (flow or model-estimated GEX) adds **measurable out-of-sample value** over an NQ-only baseline.

## What counts as success
1. A strategy that passes the frozen-spec VAL gate and then the one-shot TEST, after base costs, with acceptable drawdown and stable yearly results, **or**
2. A well-documented negative: "feature X does not improve decision Y after costs on untouched data, under assumptions A–C." That is equally valuable and much more likely.

## Scope
- Instrument traded: NQ (E-mini Nasdaq-100) outright, 1 contract, intraday (no overnight holds in v1).
- Inputs: the causal-stitched Sierra Chart SCID of executed trades (2011–2026), with manifest; free macro/vol series (VXN); options data only after a deliberate purchase decision.
- No ICT concepts. No discretionary chart patterns. Each idea gets a mechanism, a forward-looking prediction and a falsification test **before** its data is examined.

## Non-goals (for now)
- Live automation and execution infrastructure.
- Sub-second / queue-position strategies. With executed trades only and no order-book history, these can't be tested honestly (see [[Data - Depth and Level 3 (MBO)]]).
- Buying full MBO history.

## Prior expectations (written before seeing any results)
- Trade-sign imbalance has well-documented **very short-horizon** predictability (seconds to a few minutes). At 5–30 minute horizons, after a ~0.7-point round-trip cost, the prior is that it **does not** survive. I expect H01/H02 to fail. [[Literature - Prior Evidence]]
- Intraday momentum into the close (H04) has published support in index futures and ETFs. The prior is that it is weak but real, and that it may have decayed after publication.
- GEX is most plausibly linked to **volatility and autocorrelation**, not direction. I expect any GEX effect to shrink a lot once implied vol (VXN) and lagged realized vol are controlled for.
- QQQ 0DTE listings changed the options landscape in late 2022 (to be date-verified), so options features may be non-stationary exactly across the VAL→TEST boundary.

## Working agreement
I am a skeptical collaborator. Expect "no" and "we can't know that from this data" often. Agreement is never a goal.
