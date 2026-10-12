---
type: vendor
status: candidate
checked: 2026-10-12
tags: [vendor, options, open-close, dealer-sign]
---
# Vendor — Cboe DataShop Open-Close Volume Summary

**Why it matters:** this is the only affordable class of data that addresses the **dealer-sign problem**. It splits volume by participant type (customer, professional customer, broker-dealer, market maker), **buy/sell** and **open/close**.

- Coverage: Cboe's own exchanges only (C1, C2, BZX, EDGX). **Not the whole market.**
- EOD history: C1 from 2005-01-03; BZX, C2, EDGX from 2018-01-02. Intraday 10-minute and 1-minute snapshots from 2019-03-01.
- Monthly or annual subscriptions, or ad-hoc month purchases. One forum user reported ~$3K/month for C1 10-minute data [anecdotal].
- **NDX options are a Nasdaq-listed product** [verify]. If so, NDX flow isn't here. Nasdaq's own open/close product (reportedly "Nasdaq Options Trade Outline") is a lead to check.

**Fit:** builds a *customer-positioning-based* dealer sign (the `dealer_sign` column in `gex.chain_gex`) instead of a convention. That's the strongest robustness check for H03/H05 and the core of H07. **Expensive; buy only if H03/H05 show something under the conventional scenarios.**

Sources: [Open-Close on DataShop](https://datashop.cboe.com/open-close-cboe-c2-exchange), [Elite Trader thread](https://www.elitetrader.com/et/threads/cboe-open-close-volume-summary.390301/).
