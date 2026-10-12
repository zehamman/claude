---
type: index
tags: [home]
---
# NQ Order-Flow & Options Research — Home

**Question:** Does a clearly defined, timestamp-valid options feature (options flow or model-estimated GEX) improve a pre-specified NQ decision **after costs**, on **untouched** periods, robustly to data and dealer-sign assumptions — beyond what NQ executed-trade flow and price alone already give?

A robust "no" is a successful outcome. See [[Research Charter]].

## Status board (update by hand)
| Stage | Item | Status |
|---|---|---|
| 0 | Vault + toolkit built and tested on synthetic data | ✅ 2026-10-12 |
| 1 | [[E001 - SCID integrity audit]] on the real file | ⏳ run locally |
| 1 | Manifest format confirmed ([[Data - Contract Rolls and Manifest]]) | ⏳ |
| 1 | Aggressor-flag reliability by year ([[Data - Aggressor Side Reliability]]) | ⏳ |
| 2 | 1-minute bars built | ⏳ |
| 2 | [[E002 - Baselines on DEV]] ([[H00 - Baselines and cost hurdle]]) | ⏳ |
| 3 | [[E040 - Intraday momentum]] ([[H04 - Market intraday momentum (NQ-only)]]) | ⏳ |
| 3 | [[E010 - Order-flow DEV grid]] ([[H01 - Order-flow imbalance continuation]], [[H02 - Absorption reversal]]) | ⏳ |
| 4 | Free VXN download → [[E030 - HAR increment test]] VXN-only | ⏳ |
| 5 | Options data decision ([[Data Acquisition Plan]]) | ⏳ needs your budget call |
| 6 | [[H03 - Estimated GEX and next-session realized volatility]], [[H05 - Gamma-conditioned intraday momentum]], [[H06 - Gamma-conditioned order-flow signal]] | blocked on data |
| — | [[H07 - Intraday options flow leads NQ]] | deferred (cost) |

## Map
- **Project:** [[Research Charter]] · [[Research Protocol]] · [[Challenges to the Brief]] · [[Decision Log]] · [[Open Questions]] · [[Trials and Period Access]]
- **Data (what we have):** [[Data Inventory - NQ SCID]] · [[Data - SCID Record Format]] · [[Data - Contract Rolls and Manifest]] · [[Data - Aggressor Side Reliability]] · [[Data - Timestamps and Sessions]]
- **Data (what we might get):** [[Data - Depth and Level 3 (MBO)]] · [[Options Market Choice - NQ options vs NDX vs QQQ]] · [[Data Acquisition Plan]] · vendors in `06 Data Sources`
- **Hypotheses:** `03 Hypotheses` (one note each, pre-registered before data is touched)
- **Experiments:** `04 Experiments` (a plan note per experiment; scripts write a separate "(results)" note per run)
- **Methods:** [[Transaction Cost Model]] · [[Backtest Engine Conventions]] · [[Evaluation and Multiple Testing]] · [[GEX Estimation Spec]] · [[Leakage Checklist]]
- **Literature:** [[Literature - Prior Evidence]]
- **Code:** `code/` — see [[README]] for setup and run order.

## Conventions
- One note per hypothesis, experiment, data source, method. Results notes are generated, never hand-edited except the "Interpretation" section.
- Frontmatter `status:` one of `draft → pre-registered → frozen → dev-done → val-done → test-done → rejected/accepted`.
- Facts are tagged **[observed]**, **[inferred]**, **[assumption]** or **[unverified]** where it matters.
