---
type: vendor
status: parked
checked: 2026-10-12
tags: [vendor, cme, mbo]
---
# Vendor — Databento

- CME Globex MDP 3.0 (`GLBX.MDP3`) schemas: MBO, MBP-1, MBP-10, TBBO, trades, OHLCV, statistics (incl. OI for options on futures) [verify the statistics schema contents].
- Historical: usage-based, "from $0.50/GB" on the futures page (dated). Subscription prices changed **2026-06-22**: Standard $199/mo, Plus $1,750/mo, Unlimited $4,500/mo (annual for the top two).
- **Free cost-estimation and metadata endpoints**: always price a request before pulling it.

**Two potential uses:**
1. Targeted MBO samples, if a depth hypothesis is ever pre-registered ([[Data - Depth and Level 3 (MBO)]]).
2. **CME NQ options** trades/statistics history, as an alternative to DataMine for direct NQ-option OI. Price it with the estimator.

Parked: the brief judged full MBO too expensive, and nothing pre-registered needs it.

Sources: [Databento futures](https://databento.com/futures), [GLBX.MDP3](https://databento.com/datasets/GLBX.MDP3), [pricing update](https://databento.com/blog/updates-to-subscription-pricing).
