---
type: project
updated: 2026-10-12
tags: [environment, setup]
---
# Environment and Access

## Where things live
| Thing | Location |
|---|---|
| Vault + code (git repo) | `D:\Trading Bot` (clone of the GitHub repo `zehamman/claude`; branch `claude/affectionate-franklin-eh6a6l` until merged) |
| NQ SCID, manifest, quality JSON | `D:\SierraChartData\` (your machine only) |
| Derived data (bars, audit outputs) | `D:\Trading Bot\code\work\` (git-ignored) |
| Local paths config | `code\config.toml` (copy from `config.example.toml`; git-ignored) |

## Cloud sessions with Claude
- Can read and write the repo, run code on synthetic data, and do web research.
- **Cannot** access your `D:` drive or Sierra Chart. Anything that touches the real data runs on your machine; you then commit the generated result notes (or paste the output) so the next session can read them.
- Some sites are blocked by the environment's network policy (seen: sierrachart.com, thetadata.net, massive.com). Facts from those sites are marked unverified.
- The container is temporary. Anything not committed and pushed is lost.

## Your machine
- Python 3.11+, `pip install -r code\requirements.txt`.
- The full audit reads ~50 GB once. Lower `chunk_records` in `config.toml` if memory is tight.
