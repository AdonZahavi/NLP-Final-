"""Issue #5/#6 follow-up: validate YAP segmentation against gold morphemes.

The omilab sentiment benchmark ships expert gold segmentation (morph_test.tsv)
of the exact sentences in token_test.tsv. Our sentiment subset ids are
`sent-<row>` — row indexes into both files — so after segment_subsets.py has
run we can score YAP's output against gold with zero extra YAP calls.

Reports sentence-level exact match and token-level (bag) F1, plus the most
common YAP-vs-gold diffs so a human can eyeball whether mismatches are real
errors or representation differences (e.g., covert-ה insertion conventions).

Usage:
    python segmentation/gold_check.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEGMENTED = ROOT / "data" / "subsets" / "segmented" / "sentiment_500.jsonl"
MORPH_TSV = ROOT / "data" / "raw" / "morph_test.tsv"


def main() -> None:
    gold_df = pd.read_csv(
        MORPH_TSV, sep="\t", names=["text", "label"], quoting=3
    )
    with open(SEGMENTED, encoding="utf-8") as f:
        records = [json.loads(l) for l in f]

    exact = 0
    p_num = p_den = r_num = r_den = 0
    diff_examples = []
    per_morph_miss = Counter()

    for r in records:
        row = int(r["id"].split("-")[1])
        gold = str(gold_df.at[row, "text"]).split()
        pred = str(r["text_seg"]).split()
        if gold == pred:
            exact += 1
        else:
            gc, pc = Counter(gold), Counter(pred)
            overlap = sum((gc & pc).values())
            p_num += overlap; p_den += len(pred)
            r_num += overlap; r_den += len(gold)
            for m in (gc - pc):
                per_morph_miss[m] += 1
            if len(diff_examples) < 15:
                diff_examples.append((r["id"], " ".join(gold), " ".join(pred)))

    n = len(records)
    print(f"sentences: {n}")
    print(f"sentence-level exact match: {exact}/{n} ({100*exact/n:.1f}%)")
    if p_den and r_den:
        p, rc = p_num / p_den, r_num / r_den
        f1 = 2 * p * rc / (p + rc)
        print(f"token-bag P/R/F1 on non-exact sentences: {p:.3f}/{rc:.3f}/{f1:.3f}")
    print("\nmost-missed gold morphemes:", per_morph_miss.most_common(15))
    print("\nsample diffs (gold vs YAP):")
    for id_, g, p_ in diff_examples:
        print(f"\n[{id_}]\n  gold: {g}\n  yap : {p_}")


if __name__ == "__main__":
    main()
