"""Write experiment results as Obsidian notes (one note per run)."""

from __future__ import annotations

import datetime as _dt
import json
import os

import numpy as np
import pandas as pd

TRIALS_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "trials.jsonl")


def md_table(df: pd.DataFrame, floatfmt: str = "{:.3f}", max_rows: int = 200) -> str:
    if df is None or len(df) == 0:
        return "_(empty)_"
    d = df.head(max_rows)
    cols = [str(c) for c in d.columns]

    def fmt(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else floatfmt.format(v)
        if isinstance(v, tuple):
            return "(" + ", ".join(fmt(x) for x in v) + ")"
        return str(v)

    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in d.iterrows():
        lines.append("| " + " | ".join(fmt(v) for v in row.tolist()) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_{len(df) - max_rows} more rows in the CSV output._")
    return "\n".join(lines)


def write_note(vault: str, folder: str, title: str, frontmatter: dict, body: str) -> str:
    d = os.path.join(vault, folder)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{title}.md")
    fm = {"created": _dt.datetime.now().strftime("%Y-%m-%d %H:%M"), **frontmatter}
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, (list, tuple)):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + body.rstrip() + "\n")
    return path


def log_trials(hypothesis: str, period: str, configs: list[dict], log_path: str = TRIALS_LOG) -> int:
    """Append every evaluated configuration; returns the cumulative count for the hypothesis."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as fh:
        for c in configs:
            fh.write(json.dumps({"time": _dt.datetime.now().isoformat(timespec="seconds"),
                                 "hypothesis": hypothesis, "period": period, **c}, default=str) + "\n")
    with open(log_path) as fh:
        return sum(1 for line in fh if json.loads(line)["hypothesis"] == hypothesis)
