"""Issue #12: cross-condition analysis.

Reads all results/<condition>/<task>_<model>.jsonl files and produces:

- analysis/comparison.md — the paper's core results:
  * full metric matrix (model × task × condition)
  * deltas vs the raw baseline
  * McNemar exact significance tests (paired, per model × task)
  * flip counts (helpful: wrong→right, harmful: right→wrong)
  * QA alternative metric (space-insensitive EM) that neutralizes the
    segmentation artifact where models copy segmented spans (ב ירושלים)
    that fail exact-match against raw gold (בירושלים)
- analysis/correctness.json — per-example correctness by model × task ×
  condition, consumed by the flip categorization (issue #13)

Usage (from repo root):
    PYTHONPATH=src python analysis/compare_conditions.py
"""

from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from heb_morph.harness import metrics  # noqa: E402

RESULTS = ROOT / "results"
OUT_MD = ROOT / "analysis" / "comparison.md"
OUT_JSON = ROOT / "analysis" / "correctness.json"

MODELS = ("gpt-4", "claude", "llama-3.2", "mistral-7b")
TASKS = ("sentiment", "nli", "qa")
CONDITIONS = ("raw", "segmented", "prompt_guided")


def load(condition: str, task: str, model: str) -> list[dict]:
    path = RESULTS / condition / f"{task}_{model}.jsonl"
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def qa_golds(rec: dict) -> list[str]:
    g = rec["gold"]
    return json.loads(g) if isinstance(g, str) else g


def is_correct(task: str, rec: dict) -> bool:
    if task == "qa":
        return metrics.qa_em(rec["parsed_label"], qa_golds(rec)) == 1.0
    return rec["parsed_label"] == rec["gold"]


def is_correct_nospace(rec: dict) -> bool:
    """QA EM ignoring ALL spaces — neutralizes segmentation spacing."""
    pred = rec["parsed_label"]
    if pred is None:
        return False
    p = metrics.normalize_answer(pred).replace(" ", "")
    return any(p == metrics.normalize_answer(g).replace(" ", "")
               for g in qa_golds(rec))


def mcnemar_p(b: int, c: int) -> float:
    """Exact two-sided McNemar test on discordant pairs (b, c)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def fmt_p(p: float) -> str:
    s = f"{p:.4f}" if p >= 0.0001 else "<0.0001"
    if p < 0.001:
        return f"**{s}**"
    if p < 0.05:
        return f"*{s}*"
    return s


def main() -> None:
    correctness: dict = {}   # model -> task -> condition -> {id: bool}
    scores: dict = {}        # model -> task -> condition -> score dict

    for model in MODELS:
        correctness[model], scores[model] = {}, {}
        for task in TASKS:
            correctness[model][task], scores[model][task] = {}, {}
            for cond in CONDITIONS:
                recs = load(cond, task, model)
                s = metrics.score_records(recs)
                if task == "qa":
                    s["em_nospace"] = sum(
                        is_correct_nospace(r) for r in recs) / len(recs)
                scores[model][task][cond] = s
                correctness[model][task][cond] = {
                    r["id"]: is_correct(task, r) for r in recs}

    lines = ["# Cross-condition comparison (issue #12)", "",
             "Primary metric: accuracy (sentiment/NLI), exact match (QA).",
             "Deltas are vs the raw baseline. p-values: exact two-sided",
             "McNemar test on paired predictions; `*` p<0.05, `**` p<0.001.",
             ""]

    # ---------------- main table per task
    for task in TASKS:
        metric_name = "EM" if task == "qa" else "accuracy"
        lines += [f"## {task} ({metric_name})", "",
                  "| model | raw | segmented | Δseg | p(seg) | prompt_guided | Δpg | p(pg) |",
                  "|---|---|---|---|---|---|---|---|"]
        for model in MODELS:
            def acc(cond):
                s = scores[model][task][cond]
                return s["em"] if task == "qa" else s["accuracy"]
            raw_c = correctness[model][task]["raw"]
            row = [model, f"{acc('raw'):.3f}"]
            for cond in ("segmented", "prompt_guided"):
                cond_c = correctness[model][task][cond]
                ids = sorted(set(raw_c) & set(cond_c))
                b = sum(raw_c[i] and not cond_c[i] for i in ids)  # harmful
                c = sum(not raw_c[i] and cond_c[i] for i in ids)  # helpful
                delta = acc(cond) - acc("raw")
                row += [f"{acc(cond):.3f}", f"{delta:+.3f}",
                        fmt_p(mcnemar_p(b, c))]
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # ---------------- macro-F1 table (classification)
    lines += ["## Macro-F1 (classification tasks)", "",
              "| model | task | raw | segmented | prompt_guided |",
              "|---|---|---|---|---|"]
    for model in MODELS:
        for task in ("sentiment", "nli"):
            f1 = [f"{scores[model][task][c]['macro_f1']:.3f}"
                  for c in CONDITIONS]
            lines.append(f"| {model} | {task} | " + " | ".join(f1) + " |")
    lines.append("")

    # ---------------- QA artifact check
    lines += ["## QA: exact match vs space-insensitive exact match", "",
              "If EM(nospace) − EM is large in the segmented condition only,",
              "part of the segmented QA drop is the spacing artifact (model",
              "copies segmented spans), not real comprehension loss.", "",
              "| model | condition | EM | EM (nospace) | gap |",
              "|---|---|---|---|---|"]
    for model in MODELS:
        for cond in CONDITIONS:
            s = scores[model]["qa"][cond]
            gap = s["em_nospace"] - s["em"]
            lines.append(f"| {model} | {cond} | {s['em']:.3f} | "
                         f"{s['em_nospace']:.3f} | {gap:+.3f} |")
    lines.append("")

    # ---------------- flip summary
    lines += ["## Flip analysis (vs raw)", "",
              "helpful = wrong→right under the condition; harmful = right→wrong.", "",
              "| model | task | condition | helpful | harmful | net |",
              "|---|---|---|---|---|---|"]
    flips: dict = {}
    for model in MODELS:
        flips[model] = {}
        for task in TASKS:
            flips[model][task] = {}
            raw_c = correctness[model][task]["raw"]
            for cond in ("segmented", "prompt_guided"):
                cond_c = correctness[model][task][cond]
                ids = sorted(set(raw_c) & set(cond_c))
                helpful = [i for i in ids if not raw_c[i] and cond_c[i]]
                harmful = [i for i in ids if raw_c[i] and not cond_c[i]]
                flips[model][task][cond] = {"helpful": helpful,
                                            "harmful": harmful}
                lines.append(f"| {model} | {task} | {cond} | {len(helpful)} | "
                             f"{len(harmful)} | {len(helpful)-len(harmful):+d} |")
    lines.append("")

    OUT_MD.parent.mkdir(exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"correctness": correctness, "flips": flips}, f,
                  ensure_ascii=False)
    print("\n".join(lines))
    print(f"\nwrote {OUT_MD}\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
