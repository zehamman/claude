---
type: data
status: documented
tags: [data, timestamps, sessions]
---
# Data — Timestamps and Sessions

## Timestamps
- Stored as UTC microseconds since 1899-12-30. Converted to Unix µs in code.
- **Resolution policy:** Sierra can use the sub-millisecond part as a **uniqueness counter** for trades in the same millisecond. Treat analysis time as **milliseconds** (`scid.ts_ms`). Never sequence or time events with the µs digits.
  - The audit reports `pct_us_nonzero` and `pct_eq_ms_prev` per year. If µs digits are nonzero mainly where the previous trade had the same ms, they are a counter.
- The brief notes that 978 reversals (max 10 s) were repaired upstream. The bar builder **refuses** to run if it finds any decrease.
- Equal-ms trades are legitimate (one aggressor sweeping several levels). Their order within the ms is the file order, which is not a measured time.

## Sessions (code: `sessions.py`)
- Research time zone is America/New_York with DST.
- `session_date`: a Globex session opening at 18:00 ET belongs to the **next** calendar date.
- RTH = 09:30–16:00 ET. v1 strategies decide 09:45–15:30 and are flat by 15:55 (H04: exit at 16:00).
- Historical schedule changes (maintenance halts, holiday hours) are **not** hard-coded. The audit lists gaps and missing weekdays so that holidays and outages are seen, not assumed.

## Decision-time rule
A 1-minute bar with start `ts` is known at `ts + 60 s`. A decision on bar *t* trades at the **open of bar t+1**, the first trade after the decision time. With the data's millisecond precision and no measured latency, this is the latency assumption. It is acceptable at minute horizons and not at second horizons.
