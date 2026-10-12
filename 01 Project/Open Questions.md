---
type: project
tags: [todo, verify]
---
# Open Questions (to resolve locally or with vendors)

## On your machine
- [ ] Are the SCID / manifest / quality JSON still at `D:\SierraChartData\`? Current size and mtime? → `python code/scripts/run_audit.py`
- [ ] Manifest column layout → `python code/scripts/inspect_manifest.py`. If the loader can't map it, paste the header row into [[Data - Contract Rolls and Manifest]].
- [ ] Are manifest timestamps UTC? (The audit checks whether roll switches land at 18:00 ET.)
- [ ] Which Sierra data service and settings recorded the file (Denali? "Combine records"? tick storage)? This determines what BidVolume/AskVolume mean in each era.
- [ ] Is the SCID's sub-millisecond part a uniqueness counter? (Audit: `pct_us_nonzero` vs `pct_eq_ms_prev`.)
- [ ] Your actual broker fees per NQ round turn (for [[Transaction Cost Model]]).
- [ ] Extend the SCID past 2026-07-13?

## With vendors / exchanges (the session couldn't open these sites)
- [ ] ThetaData: exact start dates per tier for QQQ and NDX options trades, quotes, OI and Greeks; personal-use licence terms. [[Vendor - ThetaData]]
- [ ] CME DataMine: price and fields of historical EOD for E-mini Nasdaq-100 options (settlement, OI, volume, delta, IV); licence. [[Vendor - CME DataMine]]
- [ ] Cboe DataShop Open-Close: does it cover QQQ/NDX, from which date, at what price? [[Vendor - Cboe DataShop (Open-Close)]]
- [ ] Massive options tiers: history depth, quotes, OI. [[Vendor - Massive (formerly Polygon)]]
- [ ] Exact effective date of QQQ Tue/Thu expirations; launch dates of CME E-mini Nasdaq-100 Tue/Thu weeklies and the Micro daily options.
- [ ] Sierra historical depth retention for CME on your package (the brief's 180 days; forum reports ~6 months). [[Data - Depth and Level 3 (MBO)]]
