"""Sanity report per condition: metrics + parse-failure rate per model/task.

Usage:
    PYTHONPATH=src python scripts/summarize_results.py --condition raw
    PYTHONPATH=src python scripts/summarize_results.py            # all conditions

Writes results/<condition>/summary.md and prints it. Safe to run anytime —
it only reads prediction files that exist and reports coverage.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from heb_morph.harness import metrics  # noqa: E402
from heb_morph.harness.runner import MODELS, TASK_FILES  # noqa: E402

RESULTS = ROOT / "results"
EXPECTED_N = {"sentiment": 500, "nli": 884, "qa": 500}


def summarize(condition: str) -> Path | None:
    cond_dir = RESULTS / condition
    lines = [f"# Sanity report — condition: {condition}\n",
             "| model | task | n | coverage | accuracy | macro-F1 | QA EM | QA token-F1 | parse-fail % |",
             "|---|---|---|---|---|---|---|---|---|"]
    found = 0
    warnings: list[str] = []
    for model in MODELS:
        for task in TASK_FILES:
            path = cond_dir / f"{task}_{model}.jsonl"
            if not path.exists() or path.stat().st_size == 0:
                lines.append(f"| {model} | {task} | — | missing | | | | | |")
                continue
            found += 1
            s = metrics.score_file(path)
            n, exp = s["n"], EXPECTED_N[task]
            cov = f"{n}/{exp}"
            if n < exp:
                warnings.append(f"{model}×{task}: only {n}/{exp} examples — resume the run")
            if s["parse_failure_rate"] > 0.05:
                warnings.append(f"{model}×{task}: parse-failure rate "
                                f"{s['parse_failure_rate']:.1%} > 5% — inspect raw outputs")
            if task == "qa":
                lines.append(f"| {model} | {task} | {n} | {cov} | | | "
                             f"{s['em']:.3f} | {s['f1']:.3f} | "
                             f"{100 * s['parse_failure_rate']:.1f} |")
            else:
                lines.append(f"| {model} | {task} | {n} | {cov} | "
                             f"{s['accuracy']:.3f} | {s['macro_f1']:.3f} | | | "
                             f"{100 * s['parse_failure_rate']:.1f} |")
    if not found:
        print(f"[{condition}] no result files yet — skipping")
        return None

    lines.append(f"\nFiles found: {found}/{len(MODELS) * len(TASK_FILES)}")
    if warnings:
        lines.append("\n## ⚠ Warnings\n")
        lines.extend(f"- {w}" for w in warnings)
    else:
        lines.append("\nAll present files complete, parse-failure ≤ 5% ✔")

    out = cond_dir / "summary.md"
    text = "\n".join(lines) + "\n"
    out.write_text(text, encoding="utf-8")
    sys.stdout.buffer.write(text.encode("utf-8"))
    print(f"\nwrote {out}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", default=None,
                    choices=("raw", "segmented", "prompt_guided"))
    args = ap.parse_args()
    conds = [args.condition] if args.condition else ["raw", "segmented", "prompt_guided"]
    for c in conds:
        summarize(c)


if __name__ == "__main__":
    main()
