---
type: project
status: reference
received: 2026-10-12
tags: [brief, source]
---
# Project Brief (original)

> The brief exactly as given at the start of the project (2026-10-12). It is **background and context**, not a list of build instructions. See [[Working Agreement]]. The vault root moved to `D:\Trading Bot` (see the last line).

---

## Research Objective

I want to research and potentially build a systematic strategy for Nasdaq-100 futures (NQ), using executed-trade order flow and options-related information such as options flow and gamma exposure (GEX). We should do serious empirical research and extensive backtesting; a finished automated system is not required if the useful outcome is a well-tested strategy or a clear finding that a hypothesis does not work.

Do not use ICT concepts. Be quantitatively rigorous and candid: challenge my assumptions, identify data limitations, distinguish evidence from speculation, and do not agree just to be agreeable. Start from a simple NQ-only baseline and test whether options data adds measurable out-of-sample value over order flow alone.

## Existing NQ Trade Data

The canonical Sierra Chart file was recorded at:

`D:\SierraChartData\NQ_CONTINUOUS_CAUSAL_2011_2026.scid`

Related files:

- Roll/contract mapping: `D:\SierraChartData\NQ_CONTINUOUS_CAUSAL_2011_2026.manifest.csv`
- Data quality report: `D:\SierraChartData\NQ_CONTINUOUS_CAUSAL_2011_2026.quality.json`

These are paths from the previous workspace and may need to be located or copied to the current machine. The latest recorded inventory was a July 13, 2026 snapshot, not a live check: the SCID was 53,339,396,536 bytes (about 49.7 GiB), with 1,333,484,912 executed-trade records across 63 contract segments, dated January 2, 2011 through July 13, 2026. Verify the current file size, date range, and integrity before relying on those counts.

Important distinction: the 49.7 GiB SCID is the full-history candidate. A separate export, `D:\SierraChartData\NQ_1tick_2011_2026.txt`, was only about 635 MB and contained June 16 through July 13, 2026 in the last inspection. Despite its name, that text export was recent-only, not the full historical tick archive.

The SCID represents executed trades. It is not historical Level 3 order-by-order data or a full historical order book. The 63-segment manifest records causal contract identity and a roll rule based on completed-session volume crossover. Use the manifest to avoid treating stitched contract changes as continuous tradable prices; do not silently back-adjust prices if the research needs actual execution levels.

Known quality notes from the saved report: 978 timestamp reversals were repaired, with a maximum reversal of 10 seconds. There were 13,984 side-volume exceptions below total volume and 896 above it. The produced output had nondecreasing timestamps, one-trade records, nonzero volume, and on-tick prices. Equal millisecond timestamps can occur; do not invent finer timestamp precision. For signed flow, establish which records have trustworthy aggressor-side information and exclude or separately handle ambiguous cases. Price/volume analyses may still be possible where trade-side classification is not trustworthy.

## Depth / Level 3 Data

"Level 3" should mean individual order-level events, usually with order identifiers and add/modify/cancel/execute activity. It is different from Level 2 market-by-price depth, which aggregates size at price levels. A footprint built from trades is not Level 3.

The prior investigation found that Sierra Chart can display CME Market-by-Order data for eligible real-time services/packages, but it does not provide a long historical archive of that order-level feed. Sierra historical depth is aggregate market-by-price data and retention is limited (the previously checked CME limit was up to 180 days). Treat these as leads to recheck against current Sierra documentation and your exact service/package. A forward capture may be feasible, but it would not create a decade of historical L3.

Databento's CME MBO product is a candidate for comprehensive order-level history, but it was considered too expensive for this project. Before buying anything, compare a short, targeted sample against the actual research question. Rithmic/Bookmap or other services may offer live MBO access, but verify whether they allow recording, export, and later research use; do not assume they provide a usable historical archive. If full MBO is unaffordable, test hypotheses that can be addressed with executed trades or available aggregate depth rather than treating L2 as L3.

## Options, Flow, and GEX

First decide which options market is relevant:

- CME options on E-mini Nasdaq-100 futures are directly tied to the futures contract, but their data products, history, and intraday quote/trade availability need to be checked with CME.
- NDX and QQQ options are listed equity-index/ETF options with OPRA data. They may be useful related markets, but they are not NQ futures options. Do not label QQQ/NDX exposure as direct NQ-option flow.

GEX is a model-derived estimate, not an exchange-reported dealer position. Open interest generally does not disclose whether dealers are net long or short, and it is often a daily snapshot rather than intraday positioning. Any "dealer sign," hedge behavior, or gamma-wall interpretation must be explicit as an assumption and tested for sensitivity. Options volume alone does not identify opening versus closing trades or the buyer/seller's intent.

Potential lower-cost starting points to investigate:

- CME daily reports and CME DataMine for NQ futures-options settlements, volume, and open interest. This may support daily or end-of-day studies; confirm the available fields, historical span, fees, and redistribution/license terms before assuming intraday options flow is included.
- For QQQ/NDX OPRA data, compare ThetaData, ORATS, Cboe DataShop, and Massive. These vendors differ materially in historical depth, quote/trade granularity, open-interest availability, Greeks, coverage, and licensing. Prior research found examples of lower-cost EOD or limited-history plans, but pricing and plans change; verify current prices and exact fields before subscribing.
- If estimating GEX, document the contract universe and timestamp, underlying/forward price, rates/dividends, volatility source, option multiplier, expiration handling, and dealer-position sign assumption. Prefer testing several plausible sign/positioning assumptions over presenting one estimated GEX series as ground truth.

No options, depth, or MBO subscription was confirmed purchased in the prior work. These are acquisition leads, not data already in hand.

## Suggested Research Discipline

For every proposed effect, write down before testing:

1. The mechanism and a directional, forward-looking prediction (not merely a same-bar explanation).
2. The exact observable fields and timestamps needed, and which are observed versus inferred or unavailable.
3. The signal calculation, decision time, holding horizon, entry/exit rules, and treatment of session boundaries and contract rolls.
4. A falsification criterion and a simple benchmark. Ask whether the effect adds value after costs and beyond a trade-only baseline.

Use chronological evaluation rather than random shuffling. A sensible initial protocol is development on 2011–2018, validation of the frozen method on 2019–2022, and a final untouched test on 2023 onward, subject to the actual coverage and data quality. Never retune on the later periods and then describe them as out-of-sample.

Model commissions, exchange fees, realistic spread/slippage, latency, and fills. Report trade count, exposure, drawdowns, turnover, and performance by year and market regime, not just a single aggregate Sharpe ratio. Guard against overlapping samples, multiple testing, survivorship/selection effects, timestamp leakage, stale options snapshots, and the tendency for options activity and volatility to rise together. Compare against simple baselines such as no signal, time-of-day behavior, and a price/trade-flow-only model.

The core question is not whether GEX or options flow looks compelling on a chart. It is whether a clearly defined, timestamp-valid options feature improves a pre-specified NQ decision after costs, across untouched periods, and remains robust to reasonable data and dealer-sign assumptions.

## Prompt to Continue the Work

> Help me research a systematic NQ futures strategy using executed-trade order flow and, if the data supports it, options flow or options-derived GEX. Be a skeptical quant collaborator, not a yes-man. Do not use ICT concepts. First audit the available data, timestamps, contract rolls, and market coverage. For each idea, state a plausible forward mechanism, exact measurable fields, assumptions, a falsification test, and realistic transaction costs. Separate observed facts from model-derived estimates, especially dealer positioning and GEX. Prefer affordable data sources and verify current pricing, history, fields, and licensing before recommending a purchase. Test whether options information adds out-of-sample value beyond an NQ trade-flow baseline; do not assume it does. Use chronological development, validation, and untouched test periods, and report null or negative results plainly. A viable strategy is a success; a robust finding that a hypothesis does not work is also a success.

We will also be using an Obsidian vault for this project; every individual research should have its own file/note. The file location will be: `D:\Trading Bot`.
