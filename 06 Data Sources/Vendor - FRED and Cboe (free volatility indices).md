---
type: vendor
status: use-now
checked: 2026-10-12
tags: [vendor, free, vxn, control]
---
# Free — FRED / Cboe volatility indices

- **VXN** (Cboe Nasdaq-100 Volatility Index): FRED series `VXNCLS`, daily close, free CSV download from fred.stlouisfed.org. Cboe also publishes historical VXN.
- **Use:** mandatory control in H03 and a regime variable everywhere. The VXN close on date D is used only for session D+1.
- **Download:** `https://fred.stlouisfed.org/series/VXNCLS` → "Download CSV" → save as `code/work/VXNCLS.csv`.

Without this control, any "GEX predicts volatility" result is suspect: options OI and activity are themselves functions of volatility.
