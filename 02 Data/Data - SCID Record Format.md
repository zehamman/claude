---
type: data
status: documented
tags: [data, scid, format]
---
# Data — SCID Record Format

Implemented in `code/nqresearch/scid.py`. Sources: Sierra Chart "Intraday Data File Format" documentation (via search; the page itself was blocked in this session), cross-checked against the open-source Go reader `RileyR387/sc-data-util`.

## Header (56 bytes)
`"SCID"` · HeaderSize u32 (=56) · RecordSize u32 (=40) · Version u16 · Unused u16 · UTCStartIndex u32 · 36 reserved bytes

## Record (40 bytes)
| Field | Type | Meaning for 1-tick trade records |
|---|---|---|
| DateTime | int64 | **microseconds since 1899-12-30 00:00 UTC** (offset to Unix epoch = 25,569 days) |
| Open | float32 | record-type marker: `0.0` = single trade with bid/ask; `-1.99900095e37` = first sub-trade of an unbundled trade; `-1.99900197e37` = last sub-trade |
| High | float32 | ask at the time of the trade |
| Low | float32 | bid at the time of the trade |
| Close | float32 | trade price |
| NumTrades | uint32 | 1 for tick records |
| TotalVolume | uint32 | contracts |
| BidVolume | uint32 | volume traded **at the bid** → seller-initiated |
| AskVolume | uint32 | volume traded **at the ask** → buyer-initiated |

## Interpretation rules [assumption → verified by audit]
- High and Low hold bid and ask only on tick records. The audit's `pct_quote_valid` and `flag_vs_quote_agree_pct` columns test this year by year.
- float32 prices are exact for NQ's 0.25 tick at these price levels (24-bit mantissa).
- Sub-millisecond digits: see [[Data - Timestamps and Sessions]].
- "Unbundled" markers mean one exchange aggressor event was split into fills. Whether the file has them, and in which years, is reported by the audit (`pct_open_unbundled`). It matters for trade counts and trade-size features, not for volume.
