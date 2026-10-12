---
type: project
status: active
tags: [skepticism, assumptions]
---
# Challenges to the Brief

These are where I think the brief's assumptions are weak or need narrowing. Each item links to the note or test that resolves it.

## 1. "Order flow" here means trade-sign imbalance, not order flow in the microstructure sense
The literature's strongest short-horizon results (e.g. Cont–Kukanov–Stoikov "order flow imbalance") use **quote and depth changes**. We have **executed trades** with an aggressor flag and the best bid/ask *at the moment of each trade* (the SCID High/Low fields). That is a sparse L1 sample: no sizes, no depth, no cancels. Signals built from it are trade-imbalance and trade-size signals. That is a narrower thing, and we should name it accurately. → [[Data - SCID Record Format]], [[Data - Depth and Level 3 (MBO)]]

## 2. The horizon at which trade imbalance works is the horizon we can't trade
Trade-sign predictability is strongest over seconds and decays fast. Our round trip costs about **0.725 NQ points** (base model: $4.50 fees + 1 tick slippage per side), so the horizon must be minutes or longer, where the published predictability is weak. Prior: H01/H02 fail after costs. They are still worth running, because a clean negative closes the question. → [[Transaction Cost Model]], [[H00 - Baselines and cost hurdle]]

## 3. DEV (2011–2018) is a different market from TEST (2023+)
Things that change across the sample:
- **MNQ launched in May 2019.** Retail-size flow moved to the micro, so NQ trade-size distributions and "large trade" thresholds are not stationary.
- Changes in the feed or in unbundling alter record counts per trade.
- **QQQ Tuesday/Thursday expiries were added in 2022** (exact effective date to verify). This created a 0DTE-dominated options regime that exists only in VAL/TEST.

Mitigations: use scale-free features (imbalance ratios, z-scores against trailing sessions), report yearly tables, and have the audit look for regime breaks. → [[E001 - SCID integrity audit]]

## 4. OI-based GEX structurally misses 0DTE gamma
Open interest is an end-of-day snapshot. A same-day-expiry position opened and closed (or expired) within the session **never appears in any OI snapshot**. In the 0DTE era, OI-based GEX therefore omits a large and growing share of the gamma that is actually traded intraday. Estimating that share would need trade-level data with open/close indicators (e.g. Cboe Open-Close), and that is still only partial: it covers Cboe venues only and still involves inference. Any intraday "gamma wall" built from yesterday's OI is stale by construction. → [[GEX Estimation Spec]]

## 5. Dealer sign is an assumption with first-order effects
The common convention (dealers long calls, short puts) is a modelling choice. Under "customers net long everything", the GEX sign flips. Every GEX result is reported under all scenarios in `gex.SIGN_SCENARIOS`, and a hypothesis must state in advance which scenario it needs. → [[GEX Estimation Spec]]

## 6. GEX is mainly a volatility hypothesis, not a direction hypothesis
The hedging mechanism predicts **damped moves and mean reversion** (positive dealer gamma) or **amplified moves and momentum** (negative). It does not predict up versus down. Directional use has to go through a conditional mechanism such as H05 (momentum stronger when gamma is negative). And it must beat VXN and lagged RV, because options activity, OI and volatility move together. → [[H03 - Estimated GEX and next-session realized volatility]], [[H05 - Gamma-conditioned intraday momentum]]

## 7. Which options market? Probably not CME NQ options alone
The hedging flow that could move NQ comes from wherever the largest gamma sits: QQQ (very large, retail-heavy, 0DTE), NDX (index, cash-settled, large notional), and CME NQ options. Their relative gamma share should be **measured** before choosing. → [[Options Market Choice - NQ options vs NDX vs QQQ]]

## 8. Multiple testing in order-flow folklore
"Absorption", "exhaustion", "imbalance stacks", "delta divergence" and similar ideas each have many variants. We pre-register two (H01, H02), log every grid point, and require each to beat a price-only control. Anything added later starts a new hypothesis with its own trial count.

## 9. Things I could not verify from this session
The SCID, manifest and quality report live on your `D:` drive. This cloud session can't reach them. Every number about them in this vault comes from your brief until [[E001 - SCID integrity audit]] runs locally. Several vendor websites were also blocked from this session, so vendor facts come from search results and are marked [unverified] where relevant.
