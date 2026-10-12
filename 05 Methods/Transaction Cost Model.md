---
type: method
status: active
tags: [costs]
code: code/nqresearch/costs.py
---
# Transaction Cost Model

NQ: $20 per point. Tick 0.25 = $5. Costs are per contract per round trip, applied to every trade.

| Scenario | Fees RT | Slippage per side | Total RT (pts) | Total RT ($) |
|---|---|---|---|---|
| zero (diagnostic only) | $0 | 0 | 0 | 0 |
| optimistic | $3.78 | 0.5 tick | 0.439 | $8.78 |
| **base** | **$4.50** | **1 tick** | **0.725** | **$14.50** |
| stress | $6.00 | 2 ticks | 1.300 | $26.00 |

## Rationale
- **Fees:** one prop-firm all-in NQ round trip is published at $3.78 (Topstep help centre, accessed 2026-10-12). Retail brokers are commonly $4–5 all-in. **Replace with your broker statement.** NFA fee $0.02/side. Exchange and clearing fees from CME Fee Finder.
- **Slippage:** the reference price is the first trade after the decision (next bar open), which may sit on either side of the spread. A marketable order pays about the spread relative to the far side. NQ RTH spread is usually 1 tick, wider around news and the open. 1 tick per side is a fair base; 2 ticks is the stress case for size or fast markets.
- **Latency:** decisions at minute boundaries. The assumed latency is "fill at the next bar's open". Not valid for second-scale strategies.
- **Not modelled:** market impact beyond one contract, partial fills, limit-order queue position. Limit-order strategies are out of scope without depth data.

## Rule
A result counts only if it's positive under **base**. Optimistic-only results are reported as "not robust to costs".
