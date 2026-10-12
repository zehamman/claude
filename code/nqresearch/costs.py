"""Transaction cost model for NQ (E-mini Nasdaq-100), per contract.

Point value $20, tick 0.25 pt = $5.

Defaults are deliberately not optimistic. Verify fees against your broker
statement and CME Fee Finder; see vault note "Transaction Cost Model".

* fees_rt: commission + exchange + clearing + NFA, round trip. A prop-firm
  all-in figure seen Oct 2026 was $3.78 RT; retail brokers are commonly
  $4-5 RT. Base $4.50.
* slip_ticks_per_side: adverse slippage vs the reference price (first trade
  after the decision time). Base 1 tick/side for marketable orders: NQ RTH
  spread is usually 1 tick, and the reference trade could be on either side.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

POINT_VALUE = 20.0
TICK = 0.25


@dataclass(frozen=True)
class CostModel:
    fees_rt: float = 4.50
    slip_ticks_per_side: float = 1.0

    @property
    def rt_points(self) -> float:
        return self.fees_rt / POINT_VALUE + 2 * self.slip_ticks_per_side * TICK

    @property
    def rt_dollars(self) -> float:
        return self.rt_points * POINT_VALUE

    def asdict(self) -> dict:
        return asdict(self)


SCENARIOS = {
    "zero": CostModel(0.0, 0.0),  # diagnostic only - never report as a result
    "optimistic": CostModel(3.78, 0.5),
    "base": CostModel(4.50, 1.0),
    "stress": CostModel(6.00, 2.0),
}
