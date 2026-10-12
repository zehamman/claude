---
type: method
status: active
tags: [backtest, conventions]
code: code/nqresearch/backtest.py
---
# Backtest Engine Conventions

1. **Bars:** 1-minute, per contract segment, built from raw trades. `ts` = bar start (UTC µs). The bar is known at ts + 60 s.
2. **Groups:** each (segment, session) RTH block is a separate unit. Features, forward returns and positions never cross a group boundary, so there's nothing across rolls, overnight or holidays.
3. **Decision → entry:** decide at bar *t*'s close; enter at bar *t+1*'s **open**, which must be the next consecutive minute, otherwise skip.
4. **Exit:** open of bar entry + h; or forced flat at the first bar ≥ 15:55 ET (H04: 16:00); or the last bar's close if the session ends.
5. **Position:** one contract, one position at a time, no pyramiding. A new decision is allowed at the bar before the exit (stop-and-reverse is charged two round trips' worth via two trades).
6. **P&L:** points on actual contract prices, no back-adjustment. Costs from [[Transaction Cost Model]].
7. **Daily series:** P&L by session date over **all** sessions in the period (zeros on no-trade days) for Sharpe, t-stats and drawdown.
8. **Missing data:** windows needing a missing minute give NaN. No filling or interpolation.

Tests in `code/tests/test_research.py` check entry/exit prices, forced flat, the past-only feature windows and forward-return alignment.
