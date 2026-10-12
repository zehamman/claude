---
type: vendor
status: candidate
checked: 2026-10-12
tags: [vendor, options, opra]
---
# Vendor — Massive (formerly Polygon.io)

| Plan | $/month | History | Trades | Quotes |
|---|---|---|---|---|
| Options Developer | $79 | 4 yrs (one page says 2) | 15-min delayed | **not included** |
| Options Advanced | $199 | all, since 2014-06-02 | real-time | included (flat files + websocket) |

- Developer reportedly returns previous-session OI per contract (third-party claim).
- Flat files (daily S3) for trades/quotes; day aggregates for options.
- Index (NDX) coverage is a separate product [verify].

**Fit:** Advanced gives QQQ options **trades + quotes back to mid-2014**, the longest affordable OPRA trade history. That's useful for H07 (flow) and for building IV ourselves. Historical **OI** coverage and depth must be confirmed: GEX needs OI.

Sources: [Massive options](https://massive.com/options), [quotes flat files](https://massive.com/docs/flat-files/options/quotes), [trades REST](https://massive.com/docs/rest/options/trades-quotes/trades) — via search; the site was blocked from this session.
