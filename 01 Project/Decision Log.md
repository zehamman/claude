---
type: project
tags: [decisions]
---
# Decision Log

| ID | Date | Decision | Why | Revisit if |
|---|---|---|---|---|
| D001 | 2026-10-12 | The git repo **is** the vault. Clone it to `D:\Trading Bot`. Code lives in `code/`. Market data and derived files stay outside git (`code/work/`, ignored). | One place for notes, code and the audit trail. Obsidian ignores `.py` files. | Repo grows too large |
| D002 | 2026-10-12 | The research unit is 1-minute bars **per contract segment**, built from the SCID. No back-adjustment. v1 strategies are RTH-only and flat by 15:55 ET (H04: 16:00). | Executable prices; no roll contamination; RTH has the liquidity. | An overnight hypothesis is pre-registered |
| D003 | 2026-10-12 | Signed flow counts only clean-flag records (all volume on one side). Ambiguous volume is excluded and reported. Quote-rule fill-in is a sensitivity check only. | Don't manufacture aggressor information. | Audit shows the flag is unreliable in some years → those years are excluded from flow studies |
| D004 | 2026-10-12 | DEV 2011–18 / VAL 2019–22 / TEST 2023+. Options hypotheses get their own DEV but share the TEST. Enforced in code. | Chronological honesty, and an identical untouched comparison window. | Audit reveals unusable years |
| D005 | 2026-10-12 | Base cost: $4.50 RT fees + 1 tick/side slippage = 0.725 pt. Optimistic and stress variants always reported. | Conservative; refine from broker statements. | Real fills available |
| D006 | 2026-10-12 | (Now parked, see D008.) Added H04 (intraday momentum, NQ-only, zero parameters) and H05 (gamma-conditioned) as the main options test, ahead of the order-flow variants. | Most direct published link between dealer gamma and index futures returns, and few degrees of freedom. | — |
| D007 | 2026-10-12 | No data purchase until E001 (audit) is done and the free VXN HAR baseline has run. | The audit could change the plan; free controls come first. | — |
| D008 | 2026-10-12 | Strategy work (H00–H07, backtester, E002–E040) **parked**, not deleted. Current stage = data audit only. | You hadn't asked for strategies yet; background info isn't a go-ahead. | You say to start strategy research |
| D009 | 2026-10-12 | End goal recorded: prop-firm eval/funded passer + statistically proven profitable algorithm. Edge first, eval-rule fitting second. | Avoid fitting to eval rules by luck. | Firm chosen → per-firm rules note |
| D010 | 2026-10-12 | The vault is the project memory: everything worth keeping (context, decisions, research, lessons) goes in, plus a Session Log entry per session. | Your instruction. | — |
