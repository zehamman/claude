---
type: data
status: documented
tags: [data, depth, mbo, level3]
---
# Data — Depth and Level 3 (MBO)

## Definitions (use precisely)
- **Level 1**: best bid/ask (and sizes). The SCID stores best bid/ask **prices at trade times only**, with no sizes.
- **Level 2 / market-by-price (MBP)**: aggregated resting size per price level.
- **Level 3 / market-by-order (MBO)**: individual order events (add / modify / cancel / execute) with order IDs. Needed for queue position, iceberg detection and order-level cancellation behaviour.
- A trade **footprint** is built from executed trades. It is neither L2 nor L3.

## What is realistically available
| Source | Type | History | Notes |
|---|---|---|---|
| Our SCID | trades + L1 at trade times | 2011–2026 | what we have |
| Sierra Chart historical depth | MBP (aggregate) | limited retention: ~180 days for CME per the brief; ~6 months per a NexusFi user [unverified] | recheck against your package; forward capture possible |
| Sierra Chart MBO display | MBO real-time | no long archive | display/recording terms need checking |
| Databento GLBX.MDP3 | MBO, MBP-10, trades… | MBO from ~2017 per third-party comparison [unverified] | historical is usage-based: "from $0.50/GB" per the futures page (dated); subscriptions changed 2026-06-22: Standard $199/mo, Plus $1,750/mo, Unlimited $4,500/mo [from search, verify] |
| Rithmic / Bookmap | live MBO | not a historical archive | check whether recording and research use are permitted |

## Recommendation
**Don't buy MBO now.** None of the pre-registered hypotheses need it, and the horizon our costs allow (minutes) is where depth adds the least. If a later hypothesis truly requires depth or queue information:
1. Write the hypothesis note first.
2. Use Databento's free cost-estimation endpoint to price a **targeted** sample (e.g. NQ front month, RTH only, 20 trading days in different regimes).
3. Run the hypothesis on that sample. Only extend if it survives.

A forward capture of Sierra MBP depth costs nothing extra and gives an L2 sample. It accumulates slowly and is never history.

Sources: [Databento futures](https://databento.com/futures), [Databento pricing update](https://databento.com/blog/updates-to-subscription-pricing), [NexusFi thread](https://nexusfi.com/showthread.php?p=773050) — accessed 2026-10-12 via search.
