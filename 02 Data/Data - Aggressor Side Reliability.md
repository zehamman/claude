---
type: data
status: needs-verification
tags: [data, aggressor, order-flow]
---
# Data — Aggressor Side Reliability

## Why this matters
Every flow signal (H01, H02, H06) depends on correctly signing trades. If the flag is wrong or inconsistent across years, we would be measuring feed artefacts.

## Background
- CME's MDP 3.0 Trade Summary carries an **AggressorSide** field (tag 5797: 0 = none, 1 = buy, 2 = sell). The tag number dates back to 2008 FIX notices. It is legitimately **0** at the open, after a pre-open or pause, and for trades against implied orders. Those trades have no aggressor and must stay unsigned.
- How Sierra filled BidVolume/AskVolume historically (exchange flag vs. a bid/ask comparison) may differ by data service and era. **[unverified]**: find out which service recorded each era.

## Pre-registered policy (D003)
1. **Clean flag**: TotalVolume entirely in AskVolume (buy) or entirely in BidVolume (sell). Primary signed flow uses only these.
2. **Ambiguous** (split, empty, or Bid+Ask ≠ Total): excluded from signed flow. Its share is reported per bar (`amb_share_k`) and per year.
3. **Quote-rule fill-in** (trade ≥ ask → buy, ≤ bid → sell, using the bid/ask stored in the record) is a sensitivity check (`buy_vol_q`, `sell_vol_q`), never the default.
4. A year is **excluded from flow studies** if any of these hold: ambiguous volume > 5%; flag-vs-quote agreement on at-quote trades < 95%; or a visible break in buy/sell shares. Thresholds were fixed before seeing the audit.

## Audit outputs (E001 → fill in)
| Year | % ambiguous vol | flag/quote agreement % | usable? |
|---|---|---|---|
| … | | | |

Known from the brief: 13,984 records with Bid+Ask < Total and 896 with Bid+Ask > Total, out of 1.33B records (~0.001%). That is negligible in count, but check whether they cluster in specific days.
