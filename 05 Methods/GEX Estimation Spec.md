---
type: method
status: active
tags: [gex, options, assumptions]
code: code/nqresearch/gex.py
---
# GEX Estimation Spec

> GEX is a **model output**, not an exchange-reported dealer position. Every number states its assumptions.

## Formula
Per contract: `gex_usd_1pct = sign × Γ × OI × multiplier × S² × 0.01`. This is the change in hedgers' delta-dollars for a +1% move. Summed over the chain.
- Γ: Black–Scholes–Merton (equity/ETF/index options, dividend yield q) or Black-76 (options on NQ futures, S = futures price).
- Conversion to NQ hedge contracts: `gex_usd_1pct / (NQ price × $20)`. Notional-based, so no fixed QQQ:NDX ratio.
- Profile vs spot and the zero-gamma level: reprice gamma over a ±5% spot grid holding each strike's IV fixed (sticky strike, an assumption).

## Required metadata for each GEX series (record in the vendor/experiment note)
| Item | Choice |
|---|---|
| Contract universe (underlying(s), expiries, strikes) | |
| Snapshot time and **usable-from** time (OI published next morning → usable for the next session) | |
| Underlying / forward price source | |
| Rate r, dividend yield q | |
| IV source (vendor model? our own from mid quotes?) | |
| Multiplier (100 for QQQ/NDX; 20 per NQ point for NQ options) | |
| Expiration timestamps (AM vs PM settlement) | |
| Minimum T floor (default 1 hour) | |
| **Dealer sign scenario** | all of: `dealer_long_calls_short_puts` (convention), `dealer_short_all`, `dealer_long_all`, data-based `dealer_sign` if open/close data exist |
| 0DTE handling | all expiries **and** an ex-≤1DTE variant |

## Known limitations
- OI does **not** reveal who is long. Signs are assumptions.
- OI is end-of-day. **Intraday-opened 0DTE positions never appear in OI.** OI-based GEX understates (and may mis-sign) 0DTE-era gamma.
- Vendors' published GEX numbers use different conventions. Never mix vendor GEX with our estimates.
- Sticky-strike profiles ignore spot-vol dynamics. The zero-gamma level is fragile; don't trade it literally without a pre-registered test.
