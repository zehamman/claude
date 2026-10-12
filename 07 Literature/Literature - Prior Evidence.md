---
type: literature
status: draft
tags: [literature]
---
# Literature — Prior Evidence

> Summaries are from memory and meant for orientation. **Verify each claim against the paper before relying on it.**

## Trade flow and order flow
- **Lillo & Farmer (2004), "The long memory of the efficient market."** Trade signs are strongly persistent (long memory), consistent with order splitting. Motivates H01, and also why price impact must be resisted (prices stay efficient).
- **Chordia, Roll & Subrahmanyam (2002, JFE), "Order imbalance, liquidity, and market returns."** Aggregate imbalance relates to contemporaneous returns; forward predictability is short-lived.
- **Cont, Kukanov & Stoikov (2014, J. Fin. Econometrics), "The price impact of order book events."** Quote-based order flow imbalance explains short-horizon price changes, mostly **contemporaneously**. Needs L1 sizes, which we don't have.

## Intraday momentum and gamma
- **Gao, Han, Li & Zhou (2018, JFE), "Market intraday momentum."** The first half-hour return (from the previous close) predicts the last half-hour return for SPY; reported to be stronger on volatile days. → H04
- **Baltussen, Da, Lammers & Martens (2021, JFE), "Hedging demand and market intraday momentum."** Intraday momentum across many futures markets, linked to hedging demand by short-gamma intermediaries; stronger when gamma imbalance is negative. → H05
- **Ni, Pearson, Poteshman & White (2021, RFS), "Does option trading have a pervasive impact on underlying stock prices?"** Net gamma of option liquidity providers relates to underlying return volatility, using open/close data. → H03
- **Barbon & Buraschi, "Gamma Fragility" (working paper).** Dealer gamma imbalance and intraday momentum/reversal in equity markets. → H05/H06

## Statistics
- **Bailey & López de Prado (2014), "The deflated Sharpe ratio."** → [[Evaluation and Multiple Testing]]
- **Politis & Romano (1994), stationary bootstrap.**

## Implications for this project
1. The best-supported link between options positioning and index futures returns is **conditional intraday momentum into the close** (H05), not "gamma levels as support/resistance".
2. Published effects decay after publication. Gao et al. (2018) predates our VAL/TEST windows, which makes our VAL/TEST a genuine post-publication check.
