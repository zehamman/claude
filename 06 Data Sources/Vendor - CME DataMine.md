---
type: vendor
status: candidate
checked: 2026-10-12
tags: [vendor, cme, options, eod]
---
# Vendor — CME DataMine (and free CME daily files)

**Covers:** the only **direct** source for options on E-mini Nasdaq-100 futures.

## What exists (per CME Client Systems wiki, via search)
- **End-of-Day historical**: back to 1982 or contract inception. Official closing values: OHLC, OI, volume, settlement and **implied volatilities** for options, puts and calls. Bought from the DataMine page, card or invoice. **Price not found.**
- **End of Market Summary** files (Basic / Basic Plus / Premium): OHLC, OI, volume by venue, settlement, **delta**, IV. History starts **2024-04-03**. Delivered T+1. An old CME FAQ (~2023) quoted $105/month (or $2,100/month for one variant). Treat as outdated.
- **OI timing:** preliminary settlements around 18:00 CT; **OI can be revised the next morning** (an "F" file flags it). A GEX value is usable for session D+1 only.
- Strikes that didn't trade and have no OI are absent from settlement files.

## Free, forward-only
- CME Daily Bulletin, *Section 40 – Nasdaq 100 and E-mini Nasdaq-100 Options*: strike-level volume and OI each day. Capture it daily from now to build a forward NQ-options OI series. Builds slowly; never history.

**Fit:** direct NQ-option OI/IV for H03/H05 as a robustness check against QQQ-based GEX. Doesn't give intraday flow.

**To verify:** EOD historical price for the Nasdaq-100 options product group; exact fields (is delta/IV in the historical EOD set or only in EOMS?); licence and redistribution terms.

Sources: [End of Market Summary – Standard](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457225547/End+of+Market+Summary+-+Standard), [CME DataMine support](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457319709/CME+DataMine+Support), [Settlement data FAQ](https://www.cmegroup.com/articles/faqs/access-to-cme-group-settlement-data-faq.html), [Daily Bulletin Section 40](https://www.cmegroup.com/daily_bulletin/current/Section40_Nasdaq_100_And_E_Mini_Nasdaq_100_Options.pdf).
