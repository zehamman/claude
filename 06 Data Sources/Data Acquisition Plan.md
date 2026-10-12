---
type: plan
status: proposed
tags: [data, budget, plan]
---
# Data Acquisition Plan

Principle: buy the **cheapest data that can falsify** the next hypothesis, and nothing more. Every price below must be re-checked on the vendor page before paying. See the vendor notes for sources.

| Stage | What | Cost (indicative) | Unblocks | Trigger |
|---|---|---|---|---|
| 0 | VXN from FRED; your SCID; CME Daily Bulletin Sec. 40 forward capture | free | H00, H01, H02, H04, H03 control | now |
| 1 | **QQQ (and NDX if available) daily OI + IV/Greeks history**, e.g. one or two months of ThetaData Standard/Pro for bulk download | ~$80–$320 total [verify] | H03, H05, H06 under convention-based dealer signs | after E001 + E040 DEV |
| 1b | CME NQ-options EOD (DataMine EOD, or Databento statistics, priced via estimator) | quote needed | direct-NQ robustness check of H03/H05 | if Stage 1 shows anything |
| 2 | Customer open/close data (Cboe Open-Close; Nasdaq equivalent for NDX) | likely $$$ | data-based dealer sign; H07 | only if H03/H05 survive VAL under conventional signs |
| 3 | Intraday OPRA trades+quotes (Massive Advanced $199/mo from 2014; ThetaData tick) | $199+/mo | H07 intraday options flow | only after a pre-registered H07 passes a cheap pilot |
| — | Databento MBO | targeted samples only | none pre-registered | parked |

## Before any purchase, write down
1. The hypothesis and the exact fields it needs (contract-level OI? IV source? timestamps?).
2. The first date needed, given the hypothesis's options-DEV window.
3. The licence: personal research use, no redistribution. Vendor data never goes into git (`code/work/` is ignored).
4. Adapter plan into the `build_gex_daily.py` schema (`date, strike, right, expiry, oi, iv, spot`).
