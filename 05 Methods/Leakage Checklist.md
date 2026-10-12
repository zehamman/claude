---
type: method
status: active
tags: [leakage, checklist]
---
# Leakage Checklist (tick each in every experiment note)

- [ ] Every feature at decision time *t* uses data with timestamp < t + 0 (bar closes ≤ t).
- [ ] Execution starts at the first trade **after** the decision (next bar open), never at the signal bar's close.
- [ ] Normalisers (z-score scales, terciles, thresholds) are computed from **prior** sessions or from DEV only.
- [ ] Daily external data (VXN, OI, GEX) is lagged to the first session after it became public.
- [ ] No feature or position crosses a contract roll or a session boundary.
- [ ] No back-adjusted prices in P&L.
- [ ] Ambiguous aggressor records are excluded from signed flow (not imputed) in the primary run.
- [ ] VAL/TEST accessed only with a frozen spec (logged hash).
- [ ] The trial count includes every variant actually looked at, including ones abandoned early.
- [ ] Random-entry control shows no positive gross edge (engine sanity).
