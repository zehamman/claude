---
type: index
tags: [home]
---
# NQ Order-Flow & Options Research — Home

**End goal:** a prop-firm eval/funded-account passer that is also a statistically proven profitable algorithm → [[Prop Firm Evaluation Goal]].

**Current stage: data audit.** Strategy work is parked until you start it. Start each session with [[Working Agreement]] and [[Session Log]].

**Research question:** Does a clearly defined, timestamp-valid options feature (options flow or model-estimated GEX) improve a pre-specified NQ decision **after costs**, on **untouched** periods, robustly to data and dealer-sign assumptions — beyond what NQ executed-trade flow and price alone already give?

A robust "no" is a successful outcome. See [[Research Charter]].

## Status board (update by hand)
| Stage | Item | Status |
|---|---|---|
| 0 | Vault + audit toolkit built, tested on synthetic data | ✅ 2026-10-12 |
| 1 | Manifest format confirmed ([[Data - Contract Rolls and Manifest]]) | ⏳ run `inspect_manifest.py` locally |
| 1 | [[E001 - SCID integrity audit]] on the real file | ⏳ run locally |
| 1 | Aggressor-flag reliability by year ([[Data - Aggressor Side Reliability]]) | ⏳ from E001 |
| 1 | Timestamp / session / coverage review ([[Data - Timestamps and Sessions]]) | ⏳ from E001 |
| — | Prop firm choice and rules ([[Prop Firm Evaluation Goal]]) | ⏳ your input |
| — | Options data purchase decision ([[Data Acquisition Plan]]) | later |
| P | Strategy hypotheses H00–H07 and experiments E002–E040 | 🅿️ parked |

## Map
- **Project:** [[Project Brief (original)]] · [[Working Agreement]] · [[Session Log]] · [[Prop Firm Evaluation Goal]] · [[Environment and Access]] · [[Research Charter]] · [[Research Protocol]] · [[Challenges to the Brief]] · [[Decision Log]] · [[Open Questions]] · [[Trials and Period Access]]
- **Data (what we have):** [[Data Inventory - NQ SCID]] · [[Data - SCID Record Format]] · [[Data - Contract Rolls and Manifest]] · [[Data - Aggressor Side Reliability]] · [[Data - Timestamps and Sessions]]
- **Data (what we might get):** [[Data - Depth and Level 3 (MBO)]] · [[Options Market Choice - NQ options vs NDX vs QQQ]] · [[Data Acquisition Plan]] · vendors in `06 Data Sources`
- **Hypotheses (parked):** `03 Hypotheses` (one note each, pre-registered before data is touched)
- **Experiments:** `04 Experiments` (a plan note per experiment; scripts write a separate "(results)" note per run)
- **Methods:** [[Transaction Cost Model]] · [[Backtest Engine Conventions]] · [[Evaluation and Multiple Testing]] · [[GEX Estimation Spec]] · [[Leakage Checklist]]
- **Literature:** [[Literature - Prior Evidence]]
- **Reference:** [[Glossary]]
- **Code:** `code/` — see [[README]] for setup and run order.

## Conventions
- One note per hypothesis, experiment, data source, method. Results notes are generated, never hand-edited except the "Interpretation" section.
- Frontmatter `status:` one of `draft → pre-registered → frozen → dev-done → val-done → test-done → rejected/accepted`.
- Facts are tagged **[observed]**, **[inferred]**, **[assumption]** or **[unverified]** where it matters.
