---
type: data
status: unverified
tags: [data, nq, scid]
---
# Data Inventory — NQ SCID

> **Everything below comes from the brief (snapshot of 2026-07-13) and is [unverified]** until [[E001 - SCID integrity audit]] runs on your machine. This cloud session can't see `D:`.

| Item | Recorded value | Verified? |
|---|---|---|
| File | `D:\SierraChartData\NQ_CONTINUOUS_CAUSAL_2011_2026.scid` | ⏳ |
| Size | 53,339,396,536 bytes (~49.7 GiB) | ⏳ |
| Records | 1,333,484,912 executed-trade records | ⏳ check: (size − 56) / 40 = 1,333,484,912.0 ✔ arithmetic consistent |
| Segments | 63 contract segments (manifest) | ⏳ |
| Dates | 2011-01-02 → 2026-07-13 | ⏳ |
| Manifest | `…manifest.csv` — causal contract identity; roll = completed-session volume crossover | ⏳ format unknown |
| Quality report | `…quality.json`: 978 timestamp reversals repaired (max 10 s); 13,984 side-volume < total; 896 side-volume > total; output nondecreasing, one trade per record, nonzero volume, on-tick prices | ⏳ |
| Not the archive | `NQ_1tick_2011_2026.txt` (~635 MB) covered only 2026-06-16 → 07-13 | — |

**Consistency check done here:** a 56-byte header plus 40-byte records gives exactly 1,333,484,912 records for 53,339,396,536 bytes, with no remainder. Size and count agree.

## What this data is
- Executed trades (time and sales) with Sierra's per-trade bid/ask volume split and the best bid/ask at trade time.
- **Not** Level 2 depth history and **not** Level 3 / MBO. [[Data - Depth and Level 3 (MBO)]]

## What it supports
Price, volume and trade-size analysis in every year. Signed-flow analysis only in years where the aggressor flag proves reliable ([[Data - Aggressor Side Reliability]]).

## Related
[[Data - SCID Record Format]] · [[Data - Contract Rolls and Manifest]] · [[Data - Timestamps and Sessions]]
