"""Issue #4: create the fixed evaluation subsets used by every model and condition.

Usage:
    python scripts/explore_datasets.py   # first (downloads raw data)
    python scripts/make_subsets.py

Decisions (documented in data/subsets/README.md):
- SEED = 42 everywhere; sampling is fully deterministic.
- sentiment: 500 from the test split, stratified proportionally but with a
  MINIMUM of 30 off-topic examples (proportional would give only ~15 — too few
  to estimate per-class F1). The extra slots come out of the majority class.
- nli: ALL 884 gold-test pairs. Rationale: the set is balanced, human-verified,
  and only 76% larger than 500 — the extra statistical power is worth the
  marginal API cost (~$2).
- qa: 500 from the test split, answerable questions only, uniform sample.
- Output is NORMALIZED JSONL (stable `id`, canonical field names) so the
  harness (#7) and segmentation (#6) never touch raw dataset quirks.
- data/subsets/ is committed; checksums.txt pins the exact bytes.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

import pandas as pd

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "subsets"

SENTIMENT_LABELS = {0: "pos", 1: "neg", 2: "off-topic"}
SENTIMENT_N, SENTIMENT_MIN_PER_CLASS = 500, 30
QA_N = 500


def write_jsonl(path: Path, records: list[dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"  wrote {path.name}: {len(records):,} records  sha256={digest[:16]}…")
    return digest


def make_sentiment() -> tuple[list[dict], str]:
    df = pd.read_csv(
        RAW_DIR / "token_test.tsv", sep="\t", names=["text", "label"],
        quoting=3, dtype={"label": int},
    )
    df["label_name"] = df["label"].map(SENTIMENT_LABELS)
    rng = random.Random(SEED)

    # proportional allocation, then enforce the minimum for rare classes
    counts = df["label_name"].value_counts()
    alloc = {c: round(SENTIMENT_N * n / len(df)) for c, n in counts.items()}
    for c in alloc:
        alloc[c] = max(alloc[c], SENTIMENT_MIN_PER_CLASS)
    while sum(alloc.values()) != SENTIMENT_N:  # trim/pad from the majority class
        major = counts.idxmax()
        alloc[major] += SENTIMENT_N - sum(alloc.values())

    records = []
    for cls, k in alloc.items():
        idxs = df.index[df["label_name"] == cls].tolist()
        for i in sorted(rng.sample(idxs, k)):
            records.append(
                {
                    "id": f"sent-{i}",
                    "task": "sentiment",
                    "text": str(df.at[i, "text"]),
                    "label": cls,
                }
            )
    return records, "sentiment_500.jsonl"


def make_nli() -> tuple[list[dict], str]:
    from datasets import load_dataset

    d = load_dataset(
        "HebArabNlpProject/HebNLI", data_files="HebNLI_test.jsonl", split="train"
    )
    cols = d.column_names
    prem = "translation1" if "translation1" in cols else cols[0]
    hyp = "translation2" if "translation2" in cols else cols[1]
    label_col = next(
        c for c in ("hebrew_label", "gold_label", "original_label", "label") if c in cols
    )
    records = [
        {
            "id": f"nli-{i}",
            "task": "nli",
            "premise": str(row[prem]),
            "hypothesis": str(row[hyp]),
            "label": str(row[label_col]).strip().lower(),
        }
        for i, row in enumerate(d)
    ]
    bad = [r for r in records if r["label"] not in ("entailment", "contradiction", "neutral")]
    if bad:
        raise ValueError(f"unexpected NLI labels: {Counter(r['label'] for r in bad)}")
    return records, "nli_884.jsonl"


def make_qa() -> tuple[list[dict], str]:
    from datasets import load_dataset

    import ast

    d = load_dataset("Etelis/HeQ_v1", split="test")
    rng = random.Random(SEED)

    def parse_answers(raw):
        if isinstance(raw, str):
            return ast.literal_eval(raw)
        return raw

    answerable = [
        i for i, a in enumerate(d["Answers"])
        if (parsed := parse_answers(a)).get("text") and any(str(t).strip() for t in parsed["text"])
    ]
    chosen = sorted(rng.sample(answerable, QA_N))
    records = []
    for i in chosen:
        row = d[i]
        ans = parse_answers(row["Answers"])
        records.append(
            {
                "id": f"qa-{i}",
                "task": "qa",
                "context": str(row["Context"]),
                "question": str(row["Question"]),
                "answers": {
                    "text": [str(t) for t in ans["text"]],
                    "answer_start": [int(s) for s in ans["answer_start"]],
                },
            }
        )
    return records, "qa_500.jsonl"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    checksums, readme = [], [
        "# Fixed evaluation subsets (issue #4)\n",
        f"Deterministic, SEED={SEED}. Generated by `scripts/make_subsets.py`. "
        "These exact files are used by every model and every condition. "
        "Do not regenerate without bumping a version note here.\n",
    ]
    for maker in (make_sentiment, make_nli, make_qa):
        records, fname = maker()
        digest = write_jsonl(OUT_DIR / fname, records)
        checksums.append(f"{digest}  {fname}")
        label_key = "label" if "label" in records[0] else None
        dist = Counter(r[label_key] for r in records) if label_key else None
        readme.append(f"## {fname} — {len(records):,} records\n")
        if dist:
            total = sum(dist.values())
            readme.append(
                "- Label balance: "
                + ", ".join(f"{k}: {v} ({100*v/total:.1f}%)" for k, v in dist.most_common())
            )
        readme.append(f"- sha256: `{digest}`\n")
    readme.append(
        "## Decisions\n\n"
        "- **sentiment**: stratified 500 with a floor of "
        f"{SENTIMENT_MIN_PER_CLASS} off-topic examples (proportional would yield ~15; "
        "slots taken from the majority class). Note: label 2 = off-topic, NOT neutral.\n"
        "- **nli**: all 884 gold-test pairs kept (balanced, human-verified; "
        "extra cost over 500 is negligible).\n"
        "- **qa**: uniform 500 from answerable test questions.\n"
    )
    (OUT_DIR / "checksums.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    (OUT_DIR / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(f"\nWrote {OUT_DIR / 'README.md'} and checksums.txt")


if __name__ == "__main__":
    main()
