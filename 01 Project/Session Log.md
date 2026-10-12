---
type: log
tags: [log]
---
# Session Log

## 2026-10-12 — Session 1 (cloud session)
**Context received:** the full project brief → [[Project Brief (original)]]. End goal clarified → [[Prop Firm Evaluation Goal]].

**Environment:** cloud container. It **cannot** reach `D:\` (SCID, manifest, quality JSON), so nothing ran on real data. Several vendor websites were blocked by the network policy; vendor facts came from web search and are marked unverified. See [[Environment and Access]].

**Done:**
- Created this vault (git repo; clone to `D:\Trading Bot`).
- Audit-stage tooling (in scope): SCID reader, year-by-year integrity audit, manifest loader and roll-boundary check, sessions/timezones, aggressor-side classification, 1-minute bar builder. Tested on synthetic data.
- Data notes and vendor/data-source research notes (prices as found 2026-10-12).

**Went beyond what was asked (now parked):** strategy hypotheses H00–H07, a backtester, signal grids, GEX/HAR test code, experiment plans E002–E040, and two hypotheses added on my own initiative (H04/H05 intraday momentum). You pointed out that you hadn't asked for strategies yet. These were **parked, not deleted**: they're marked `status: parked` and won't be run until you say so.

**Bugs found and fixed during testing (worth remembering):** pandas 3 stores datetimes in microseconds, not nanoseconds. Code that assumes ns (`.value`, `astype('int64')` on datetimes) silently breaks; this nearly mixed sessions inside the same feature group.

**Next (when you're ready):** on your machine, run `inspect_manifest.py`, then `run_audit.py`; review [[E001 - SCID integrity audit]] results.
