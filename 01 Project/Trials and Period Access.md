---
type: project
tags: [audit-trail, multiple-testing]
---
# Trials and Period Access

Two machine-written logs, committed to git, are the audit trail:

- `code/logs/trials.jsonl`: every configuration evaluated, by hypothesis family. The cumulative count feeds the deflated Sharpe ratio. **Never delete lines.**
- `code/logs/period_access.jsonl`: every request for DEV / VAL / TEST data, with the spec hash. TEST access with a changed spec is refused unless explicitly overridden, and the override is logged.

## Summary (update after each run)
| Hypothesis family | DEV trials | VAL accesses | TEST accesses | Notes |
|---|---|---|---|---|
| H01/H02/P01/P02 | 0 | 0 | 0 | |
| H04 | 0 | 0 | 0 | |
| H03 | 0 | 0 | 0 | |
| H05 | 0 | 0 | 0 | |

To view the logs: `python -c "import pandas as pd; print(pd.read_json('code/logs/trials.jsonl', lines=True).groupby(['hypothesis','period']).size())"`
