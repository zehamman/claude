---
type: data
status: open
tags: [options, market-choice]
---
# Options Market Choice — NQ options vs NDX vs QQQ

| | CME options on E-mini Nasdaq-100 futures | NDX index options | QQQ ETF options |
|---|---|---|---|
| Underlying | NQ futures (1 option = 1 future, $20/pt) | Nasdaq-100 index (cash-settled, $100 multiplier) | QQQ ETF (physically settled, 100 shares) |
| Data feed | CME MDP 3.0 / DataMine | OPRA | OPRA |
| Direct link to NQ | **direct** (hedged in NQ) | indirect (hedged in NQ, QQQ, baskets) | indirect (hedged in QQQ, NQ, baskets) |
| Expiries | quarterly, monthly, weeklies (Mon–Fri incl. Tue/Thu weeklies); Micro E-mini options with daily expiries | AM/PM monthlies, weeklies, dailies [verify] | daily (Mon–Fri) since Tue/Thu were added in 2022 [verify date] |
| OI | CME daily, revised next morning | OCC daily | OCC daily |

## Labelling rule
Only CME NQ options flow is "NQ options flow". QQQ/NDX features are **related-market options features** and must be named that way.

## Decision procedure (before buying)
The hedging pressure that could move NQ comes from where the gamma is. So, before choosing:
1. For a few sample dates in 2018, 2021 and 2024, compute **notional dollar gamma per 1% move** for each market from EOD OI (`gex.chain_gex` with `scenario='dealer_long_all'`, i.e. gross magnitude).
2. Pick the market(s) holding most of the gamma. If QQQ dominates, the primary H03/H05 feature is QQQ-based and CME NQ options are a secondary check.
3. Aggregating across markets needs one common unit: dollar gamma per 1% move, converted to NQ-contract equivalents with `gex.to_nq_contracts`. No fixed QQQ:NDX ratio.

Prior (unverified): QQQ carries a very large share of gross gamma since the 0DTE era, and CME NQ options a comparatively small one. Measure it; don't assume it.
