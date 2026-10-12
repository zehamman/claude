---
type: vendor
status: candidate
checked: 2026-10-12
tags: [vendor, options, opra]
---
# Vendor — ThetaData

**Covers:** OPRA (QQQ; NDX via index/option tiers [verify]). Trades, NBBO quotes, EOD, OI, Greeks depending on tier. **Not** CME NQ options.

| Tier (retail) | $/month | History | Granularity |
|---|---|---|---|
| Options Value | $40 | 4 yrs (Aug–Sep 2026 sources) or 6 yrs (Oct 10, 2026 source) | 1-minute |
| Options Standard | $80 | 8 or 10 yrs | tick |
| Options Pro | $160 | 12 or 14 yrs | tick |
| Commercial | $1,600 | — | not for personal use |

The sources conflict on history depth, so the vendor's own page is authoritative (it was blocked from this session). **[unverified]**

**Fit for this project:** best value for **QQQ EOD OI + IV/Greeks** history (H03, H05) and potentially trade-level flow (H07). Standard/Pro depth reaches back to ~2016–2018, so the options DEV window starts there, not 2011.

**To verify before paying:** exact first date for QQQ and NDX OI/Greeks/quotes per tier; whether historical OI is per day per contract; personal-use licence (research use fine, no redistribution); bulk-download limits. A one- or two-month subscription to bulk-download history may be enough.

Sources: [QuantVPS (2026-10-10)](https://www.quantvps.com/blog/download-historical-options-data), [FlashAlpha comparison](https://flashalpha.com/articles/options-data-pricing-comparison-flashalpha-thetadata-polygon-spotgamma-squeezemetrics), [DeskTested review](https://desktested.com/posts/thetadata-review/), [ThetaData commercial](https://www.thetadata.net/commercial-use).
