"""Issue #13: linguistic categorization of answer flips.

For every example we compute morphological features from the YAP segmentation
(how many clitic prefixes were split off, expansion ratio, covert-ה
insertions), then ask: do examples that FLIPPED under a condition differ
morphologically from examples that stayed stable?

Outputs:
- analysis/flips.md          — feature means for helpful/harmful/stable groups
                               per model × task × condition + category counts
- analysis/flip_examples.md  — concrete Hebrew examples of the biggest effect
                               (harmful NLI flips), for the report's
                               qualitative analysis

Usage (from repo root):
    PYTHONPATH=src python analysis/categorize_flips.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBSETS = ROOT / "data" / "subsets"
CORRECTNESS = ROOT / "analysis" / "correctness.json"
OUT_MD = ROOT / "analysis" / "flips.md"
OUT_EX = ROOT / "analysis" / "flip_examples.md"

MODELS = ("gpt-4", "claude", "llama-3.2", "mistral-7b")
TASKS = ("sentiment", "nli", "qa")
TASK_FILES = {"sentiment": "sentiment_500.jsonl",
              "nli": "nli_884.jsonl",
              "qa": "qa_500.jsonl"}
TEXT_FIELDS = {"sentiment": ("text",),
               "nli": ("premise", "hypothesis"),
               "qa": ("context", "question")}

# clitic prefixes YAP splits off (single tokens after segmentation)
PREFIX_TOKENS = {"ו", "ש", "ה", "ל", "ב", "מ", "כ", "כש", "וש", "וכש",
                 "לכש", "מש", "וה", "ול", "וב", "ומ"}


def load_pair(task: str) -> dict:
    """id -> {raw: str, seg: str} concatenated over the task's text fields."""
    raw = {r["id"]: r for r in
           (json.loads(l) for l in open(SUBSETS / TASK_FILES[task],
                                        encoding="utf-8"))}
    seg = {r["id"]: r for r in
           (json.loads(l) for l in open(SUBSETS / "segmented" / TASK_FILES[task],
                                        encoding="utf-8"))}
    out = {}
    for i, r in raw.items():
        s = seg.get(i, {})
        out[i] = {
            "raw": " ".join(str(r[f]) for f in TEXT_FIELDS[task]),
            "seg": " ".join(str(s.get(f + "_seg", r[f]))
                            for f in TEXT_FIELDS[task]),
        }
    return out


def features(raw: str, seg: str) -> dict:
    rt, st = raw.split(), seg.split()
    n_prefix = sum(1 for t in st if t in PREFIX_TOKENS)
    # covert-ה proxy: standalone ה tokens in seg beyond ה-initial raw words
    he_seg = sum(1 for t in st if t == "ה")
    return {
        "expansion": len(st) / max(len(rt), 1),
        "prefix_splits": n_prefix,
        "prefix_density": n_prefix / max(len(rt), 1),
        "he_tokens": he_seg,
    }


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main() -> None:
    with open(CORRECTNESS, encoding="utf-8") as f:
        data = json.load(f)
    flips = data["flips"]
    correctness = data["correctness"]

    texts = {t: load_pair(t) for t in TASKS}
    feats = {t: {i: features(v["raw"], v["seg"]) for i, v in texts[t].items()}
             for t in TASKS}

    lines = ["# Flip categorization by morphological features (issue #13)", "",
             "For each model × task × condition: mean morphological features of",
             "examples that flipped helpfully (wrong→right), harmfully",
             "(right→wrong), or stayed stable. `prefix_density` = clitic",
             "prefixes split per raw token; `expansion` = seg/raw token ratio.",
             ""]

    lines += ["| model | task | condition | group | n | expansion | prefix_density | he_tokens |",
              "|---|---|---|---|---|---|---|---|"]
    for model in MODELS:
        for task in TASKS:
            all_ids = set(feats[task])
            for cond in ("segmented", "prompt_guided"):
                fl = flips[model][task][cond]
                groups = {
                    "helpful": fl["helpful"],
                    "harmful": fl["harmful"],
                    "stable": sorted(all_ids - set(fl["helpful"])
                                     - set(fl["harmful"])),
                }
                for gname, ids in groups.items():
                    fs = [feats[task][i] for i in ids if i in feats[task]]
                    if not fs:
                        continue
                    lines.append(
                        f"| {model} | {task} | {cond} | {gname} | {len(fs)} | "
                        f"{mean([x['expansion'] for x in fs]):.3f} | "
                        f"{mean([x['prefix_density'] for x in fs]):.3f} | "
                        f"{mean([x['he_tokens'] for x in fs]):.2f} |")
    lines.append("")

    # aggregate: harmful vs stable across all models (segmented condition)
    lines += ["## Aggregate (segmented condition, all models pooled)", "",
              "| task | group | n | expansion | prefix_density |",
              "|---|---|---|---|---|"]
    for task in TASKS:
        pooled = {"helpful": [], "harmful": [], "stable": []}
        for model in MODELS:
            fl = flips[model][task]["segmented"]
            stable = set(feats[task]) - set(fl["helpful"]) - set(fl["harmful"])
            pooled["helpful"] += [feats[task][i] for i in fl["helpful"]]
            pooled["harmful"] += [feats[task][i] for i in fl["harmful"]]
            pooled["stable"] += [feats[task][i] for i in stable]
        for g, fs in pooled.items():
            lines.append(f"| {task} | {g} | {len(fs)} | "
                         f"{mean([x['expansion'] for x in fs]):.3f} | "
                         f"{mean([x['prefix_density'] for x in fs]):.3f} |")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    # ------- qualitative examples: Claude NLI harmful flips (biggest effect)
    ex_lines = ["# Qualitative flip examples (issue #13)", "",
                "Claude × NLI × segmented — the largest harmful effect",
                "(−166 net flips). First 10 harmful flips:", ""]
    raw_recs = {r["id"]: r for r in
                (json.loads(l) for l in
                 open(ROOT / "results" / "raw" / "nli_claude.jsonl",
                      encoding="utf-8"))}
    seg_recs = {r["id"]: r for r in
                (json.loads(l) for l in
                 open(ROOT / "results" / "segmented" / "nli_claude.jsonl",
                      encoding="utf-8"))}
    for i in flips["claude"]["nli"]["segmented"]["harmful"][:10]:
        t = texts["nli"][i]
        ex_lines += [f"### {i}",
                     f"- raw premise+hypothesis: {t['raw'][:300]}",
                     f"- segmented: {t['seg'][:300]}",
                     f"- gold: {raw_recs[i]['gold']}",
                     f"- raw answer: {raw_recs[i]['parsed_label']} ✓",
                     f"- segmented answer: {seg_recs[i]['parsed_label']} ✗", ""]
    OUT_EX.write_text("\n".join(ex_lines), encoding="utf-8")

    print("\n".join(lines[:40]))
    print(f"...\nwrote {OUT_MD}\nwrote {OUT_EX}")


if __name__ == "__main__":
    main()
