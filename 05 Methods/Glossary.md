---
type: reference
tags: [glossary]
---
# Glossary

| Term | Meaning here |
|---|---|
| **NQ / MNQ** | E-mini / Micro E-mini Nasdaq-100 futures (CME). NQ $20 per index point, tick 0.25 = $5. MNQ $2 per point (launched May 2019). |
| **SCID** | Sierra Chart intraday data file. Here, one record per executed trade. [[Data - SCID Record Format]] |
| **Segment / roll** | Period in which one contract month is "front" in the stitched file. Prices aren't back-adjusted. [[Data - Contract Rolls and Manifest]] |
| **Aggressor side** | Whether the trade was initiated by a buyer (lifting the ask) or a seller (hitting the bid). |
| **Signed flow / imbalance** | Buy-aggressor volume minus sell-aggressor volume over a window (clean-flag records only). |
| **RTH / ETH** | Regular trading hours 09:30–16:00 ET / electronic (overnight) hours. |
| **Session date** | Globex session opening 18:00 ET belongs to the next calendar date. |
| **L1 / L2 / L3** | Best bid/ask / aggregated depth per price (market-by-price) / individual orders (market-by-order, MBO). [[Data - Depth and Level 3 (MBO)]] |
| **Footprint** | Volume at price split by aggressor side, built from trades. Not L2/L3. |
| **OI** | Open interest: contracts outstanding at end of day; published the next morning. |
| **Greeks / Γ (gamma)** | Sensitivity of an option's delta to the underlying price. |
| **GEX** | Gamma exposure: a **model estimate** of hedgers' delta change per 1% move, from OI × gamma × an **assumed dealer sign**. [[GEX Estimation Spec]] |
| **Dealer sign** | Assumption about whether dealers are long or short each option. Not observable from OI. |
| **0DTE** | Options expiring the same day. |
| **OPRA** | Consolidated US listed-options feed (QQQ, NDX options). CME options on futures are not on OPRA. |
| **VXN** | Cboe Nasdaq-100 volatility index (implied vol). Free on FRED as `VXNCLS`. |
| **DEV / VAL / TEST** | Development 2011–2018 / validation 2019–2022 / untouched test 2023+. [[Research Protocol]] |
| **Out-of-sample** | Data not used in any way to choose the strategy or its parameters. |
| **Sharpe / DSR** | Risk-adjusted return / deflated Sharpe ratio, which accounts for how many variants were tried. |
| **HAR** | Heterogeneous autoregressive model for forecasting realized volatility from its daily, weekly and monthly averages. |
| **Eval / funded account** | Prop-firm evaluation account with pass rules / account trading firm capital after passing. [[Prop Firm Evaluation Goal]] |
| **Trailing drawdown** | Max-loss limit that moves up with peak equity (rules differ by firm: intraday vs end-of-day). |
| **ICT** | "Inner Circle Trader" concepts. Excluded from this project. |
