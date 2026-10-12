# NQ Order-Flow & Options Research

This repository is both an **Obsidian vault** (open the folder as a vault; start at `00 Home.md`) and a **Python research toolkit** (`code/`). It tests whether options information (flow or model-estimated GEX) adds out-of-sample value to an NQ futures strategy built on executed-trade order flow, under a pre-registered, chronologically split protocol.

## Setup (Windows, on the machine that has the data)
```powershell
git clone <this repo> "D:\Trading Bot"
cd "D:\Trading Bot\code"
python -m pip install -r requirements.txt     # Python 3.11+
copy config.example.toml config.toml           # edit paths if they differ
python -m pytest -q tests                      # 21 tests on synthetic data
```

## Run order
Current stage is the **data audit** (steps 1–2). Steps 3–7 belong to strategy research, which is **parked** until it's explicitly started (see `01 Project/Working Agreement.md`).

| Step | Command (from `code/`) | Writes vault note |
|---|---|---|
| 1 | `python scripts\inspect_manifest.py` | — (paste the header into *Data - Contract Rolls and Manifest*) |
| 2 | `python scripts\run_audit.py` | `04 Experiments/E001 … (results)` |
| 3 | `python scripts\build_bars.py` | — (`work/bars_1m.parquet`) |
| 4 | `python scripts\run_baselines.py` | E002 results |
| 5 | `python scripts\run_intraday_momentum.py --period dev` | E040 results |
| 6 | `python scripts\run_flow_study.py --period dev` | E010 results |
| 7 | download FRED `VXNCLS` → `work\VXNCLS.csv`; `python scripts\run_har.py --vxn work\VXNCLS.csv` | E030 results |

VAL/TEST runs need a frozen spec, and every access is logged in `code/logs/` (commit these logs). See `01 Project/Research Protocol.md`.

## Layout
```
00 Home.md            index and status board
01 Project/           charter, protocol, challenges, decisions, open questions
02 Data/              what the data is and how far it can be trusted
03 Hypotheses/        one pre-registered note per hypothesis
04 Experiments/       plan notes; scripts add one "(results)" note per run
05 Methods/           costs, engine conventions, statistics, GEX spec, leakage checklist
06 Data Sources/      vendor notes (prices checked 2026-10-12, many unverified) + acquisition plan
07 Literature/        prior evidence
Templates/            note templates
code/nqresearch/      library (scid reader, audit, bars, features, backtest, stats, gex, rv, periods)
code/scripts/         runnable studies
code/tests/           synthetic-data tests
```
Market data and derived files are never committed (`code/work/` is git-ignored).
