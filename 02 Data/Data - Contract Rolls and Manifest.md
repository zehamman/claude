---
type: data
status: needs-verification
tags: [data, rolls, manifest]
---
# Data — Contract Rolls and Manifest

## Facts from the brief
- 63 segments, causal contract identity, roll rule = **completed-session volume crossover**: the next contract becomes front only after it has out-traded the current one over a completed session. [unverified]
- Prices are **not** back-adjusted. Keep it that way: P&L must use the traded contract's actual prices.

## How the code uses it
- `manifest.load()` maps columns to `segment, symbol, start_us, end_us [, first_record, last_record]`. If it can't recognise the layout it fails loudly. Run `python code/scripts/inspect_manifest.py` and record the real header here:
  - Real header: `____` (fill in)
- Bars are keyed by (segment, minute). All features and forward returns are computed inside one (segment, session) group, so nothing crosses a roll. On the first session of a new segment, H04 has no "previous close" in the same contract and skips that day by design.

## Checks in the audit (E001)
- `audit_roll_boundaries.csv`: for each switch, the ET time and the price gap between the last old-contract trade and the first new-contract trade.
  - Expected: switches at **18:00 ET** (Globex open) if the rule acts on completed sessions. Switches at other times mean either a different rule or a **timezone mismatch** in the manifest.
  - Expected gap ≈ the calendar spread (a few to tens of points, depending on rates, dividends and the NDX level). Large or zero gaps are suspicious.
- `manifest_end_prev_matches`: the manifest's end of segment *i−1* equals the last record before segment *i*.
- Causality: confirm the roll decision for session *S* used volume through session *S−1* only. The manifest rows should show the decision date and the effective date. If they don't, recompute the crossover from the bars and compare.

## Open
- [ ] Paste the manifest header and three sample rows here.
- [ ] Record the roll-gap distribution from E001.
