---
type: vendor
status: candidate
checked: 2026-10-12
tags: [vendor, options, opra]
---
# Vendor — ORATS

**Covers:** US equity/ETF options (QQQ; NDX [verify]) with ORATS-smoothed IV and Greeks.

- **1-minute** options data from **August 2020** (S3 delivery); a **2-minute** archive from **2015**; near-EOD and EOD products. A hard-drive delivery of intraday history is offered.
- OPRA-level intraday via API only from **January 2022**, for 1,270 tickers.
- Historical data can be a one-time purchase; recurring subscriptions start at the purchase date.
- Price: a 2022 blog listed the intraday API at $399/month. **Outdated**; get a quote.

**Fit:** good if we want **intraday GEX** (IV/Greeks through the day) from 2015/2020 onward. IV is ORATS-smoothed, which is a modelling choice to record in [[GEX Estimation Spec]].

Sources: [ORATS one-minute data](https://orats.com/one-minute-data), [historical data](https://orats.com/university/historical-data), [intraday API](https://orats.com/intraday-data-api), [llms.txt](https://orats.com/llms.txt).
