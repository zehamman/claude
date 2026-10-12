"""Aggressor-side classification for executed-trade records.

Two independent classifications are computed so they can be cross-checked:

1. ``flag_side`` -- from Sierra's BidVolume / AskVolume split. A record is
   "clean" only when the whole TotalVolume sits on exactly one side.
   +1 = buy aggressor (traded at ask), -1 = sell aggressor (traded at bid),
   0 = ambiguous (split, missing, or BidVolume+AskVolume != TotalVolume).

2. ``quote_side`` -- quote rule from the bid/ask stored in Low/High at the
   time of the trade: +1 if price >= ask, -1 if price <= bid, 0 inside the
   spread or when the quote is unusable.

Pre-registered policy (see vault note "Data - Aggressor Side Reliability"):
the primary signed-flow series uses ``flag_side`` clean records only and
reports the excluded (ambiguous) volume alongside. Quote-rule fill-in is a
sensitivity analysis, never the default.
"""

from __future__ import annotations

import numpy as np

from .scid import OPEN_FIRST_SUB_TRADE, OPEN_LAST_SUB_TRADE, OPEN_SINGLE_TRADE

NQ_TICK = 0.25

# Open-field categories
OPEN_CAT_SINGLE = 0
OPEN_CAT_FIRST_SUB = 1
OPEN_CAT_LAST_SUB = 2
OPEN_CAT_OTHER = 3  # a real price in Open, i.e. not a 1-tick record
OPEN_CAT_NAMES = ["single_with_bid_ask", "first_sub_unbundled", "last_sub_unbundled", "other"]


def flag_side(rec: np.ndarray) -> np.ndarray:
    v = rec["volume"]
    b = rec["bid_volume"]
    a = rec["ask_volume"]
    side = np.zeros(len(rec), dtype=np.int8)
    side[(a == v) & (b == 0) & (v > 0)] = 1
    side[(b == v) & (a == 0) & (v > 0)] = -1
    return side


def side_sum_class(rec: np.ndarray) -> np.ndarray:
    """-1 if Bid+Ask < Total, 0 if equal, +1 if Bid+Ask > Total."""
    s = rec["bid_volume"].astype(np.int64) + rec["ask_volume"].astype(np.int64)
    t = rec["volume"].astype(np.int64)
    return np.sign(s - t).astype(np.int8)


def quote_valid(rec: np.ndarray) -> np.ndarray:
    bid = rec["low"]
    ask = rec["high"]
    return np.isfinite(bid) & np.isfinite(ask) & (bid > 0) & (ask > bid) & (ask - bid < 1000)


def quote_side(rec: np.ndarray) -> np.ndarray:
    p = rec["close"]
    bid = rec["low"]
    ask = rec["high"]
    ok = quote_valid(rec)
    side = np.zeros(len(rec), dtype=np.int8)
    side[ok & (p >= ask)] = 1
    side[ok & (p <= bid)] = -1
    return side


def open_category(rec: np.ndarray) -> np.ndarray:
    o = rec["open"]
    cat = np.full(len(rec), OPEN_CAT_OTHER, dtype=np.int8)
    cat[o == OPEN_SINGLE_TRADE] = OPEN_CAT_SINGLE
    cat[o == OPEN_FIRST_SUB_TRADE] = OPEN_CAT_FIRST_SUB
    cat[o == OPEN_LAST_SUB_TRADE] = OPEN_CAT_LAST_SUB
    return cat


def on_tick(price: np.ndarray, tick: float = NQ_TICK) -> np.ndarray:
    q = price.astype(np.float64) / tick
    return np.abs(q - np.round(q)) < 1e-6
