"""Issue #3: download the three benchmarks, validate them, and generate data/README.md.

Usage:
    pip install datasets pandas
    python scripts/explore_datasets.py

Notes:
- omilab/hebrew_sentiment uses a legacy HF loading script that modern `datasets`
  (>=3.0) cannot load, so we fetch the raw TSVs from the source GitHub repo instead.
  Labels: 0=pos, 1=neg, 2=off-topic ("neutral" in the card summary means off-topic!).
  The repo also provides a *morph* (pre-segmented) variant — useful for issue #6.
- HebNLI / HeQ load normally via `datasets`.
"""

from __future__ import annotations

import io
import json
import statistics
import urllib.request
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
README = ROOT / "data" / "README.md"

SENTIMENT_BASE = (
    "https://github.com/omilab/Neural-Sentiment-Analyzer-for-Modern-Hebrew"
    "/raw/master/data/{name}.tsv"
)
SENTIMENT_FILES = ["token_train", "token_test", "morph_train", "morph_test"]
SENTIMENT_LABELS = {0: "pos", 1: "neg", 2: "off-topic"}


def _download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        print(f"  downloading {url}")
        urllib.request.urlretrieve(url, dest)
    return dest


def text_stats(texts: list[str]) -> dict:
    words = [len(t.split()) for t in texts]
    chars = [len(t) for t in texts]
    return {
        "n": len(texts),
        "words_mean": round(statistics.mean(words), 1),
        "words_median": statistics.median(words),
        "words_p95": sorted(words)[int(0.95 * len(words))],
        "words_max": max(words),
        "chars_mean": round(statistics.mean(chars), 1),
        "empty": sum(1 for t in texts if not t.strip()),
        "dupes": len(texts) - len(set(texts)),
    }


def fmt_dist(counter: Counter) -> str:
    total = sum(counter.values())
    return ", ".join(
        f"{k}: {v:,} ({100 * v / total:.1f}%)" for k, v in counter.most_common()
    )


def explore_sentiment(lines: list[str]) -> None:
    print("== omilab/hebrew_sentiment (via source GitHub TSVs)")
    frames = {}
    for name in SENTIMENT_FILES:
        path = _download(SENTIMENT_BASE.format(name=name), RAW_DIR / f"{name}.tsv")
        df = pd.read_csv(
            path, sep="\t", names=["text", "label"], quoting=3, dtype={"label": int}
        )
        frames[name] = df
    lines.append("## 1. Sentiment — omilab/hebrew_sentiment (MIT)\n")
    lines.append(
        "Facebook comments on President Rivlin's page (2014). Loaded from the "
        "source GitHub repo (the HF repo's loading script is incompatible with "
        "datasets>=3). Two variants: `token` (raw) and `morph` (pre-segmented "
        "morphemes — reusable for issue #6).\n"
    )
    lines.append("**Label mapping: 0=pos, 1=neg, 2=off-topic.** The dataset card's "
                 "'370 neutral' actually means off-topic — the proposal's "
                 "positive/negative/neutral framing needs this caveat.\n")
    for name, df in frames.items():
        dist = Counter(SENTIMENT_LABELS[l] for l in df["label"])
        st = text_stats(df["text"].astype(str).tolist())
        lines.append(f"### {name} ({st['n']:,} rows)\n")
        lines.append(f"- Labels: {fmt_dist(dist)}")
        lines.append(
            f"- Words/example: mean {st['words_mean']}, median {st['words_median']}, "
            f"p95 {st['words_p95']}, max {st['words_max']}"
        )
        lines.append(f"- Quality: {st['empty']} empty, {st['dupes']} duplicate texts\n")
        print(f"  {name}: {st['n']:,} rows | {fmt_dist(dist)}")


def explore_hebnli(lines: list[str]) -> None:
    from datasets import load_dataset

    print("== HebArabNlpProject/HebNLI")
    splits = {}
    file_map = {
        "train": "HebNLI_train.jsonl",
        "validation": "HebNLI_val.jsonl",
        "test": "HebNLI_test.jsonl",
    }
    for split_name, fname in file_map.items():
        try:
            splits[split_name] = load_dataset(
                "HebArabNlpProject/HebNLI",
                data_files=fname,
                split="train",  # single-file loads as 'train'
            )
        except Exception as e:
            print(f"  [WARN] could not load split '{split_name}': {e}")
    lines.append("## 2. NLI — HebArabNlpProject/HebNLI (CC BY 4.0)\n")
    lines.append(
        "MultiNLI machine-translated to Hebrew. Per the proposal we evaluate on "
        "the test split (manually verified gold set).\n"
    )
    for split, d in splits.items():
        cols = d.column_names
        # Hebrew fields are translation1/translation2 when present
        prem = "translation1" if "translation1" in cols else cols[0]
        hyp = "translation2" if "translation2" in cols else cols[1]
        label_col = next(
            (c for c in ("hebrew_label", "gold_label", "original_label", "label") if c in cols),
            None,
        )
        dist = Counter(d[label_col]) if label_col else Counter()
        st = text_stats([f"{a} {b}" for a, b in zip(d[prem], d[hyp])])
        lines.append(f"### {split} ({d.num_rows:,} pairs)\n")
        lines.append(f"- Columns: {cols} (premise=`{prem}`, hypothesis=`{hyp}`, label=`{label_col}`)")
        lines.append(f"- Labels: {fmt_dist(dist)}")
        lines.append(
            f"- Words/pair: mean {st['words_mean']}, median {st['words_median']}, "
            f"p95 {st['words_p95']}"
        )
        lines.append(f"- Quality: {st['empty']} empty, {st['dupes']} duplicate pairs\n")
        print(f"  {split}: {d.num_rows:,} | label=`{label_col}` | {fmt_dist(dist)}")


def explore_heq(lines: list[str]) -> None:
    from datasets import load_dataset

    print("== Etelis/HeQ_v1")
    ds = load_dataset("Etelis/HeQ_v1")
    lines.append("## 3. QA — Etelis/HeQ_v1 (CC BY 4.0)\n")
    lines.append(
        "SQuAD-style extractive QA over Hebrew Wikipedia + Geektime "
        "(30,147 questions total).\n"
    )
    import ast

    def parse_answers(raw):
        return ast.literal_eval(raw) if isinstance(raw, str) else raw

    for split in ds:
        d = ds[split]
        cols = d.column_names
        pick = lambda *names: next((c for c in names if c in cols), None)  # noqa: E731
        ctx_col = pick("Context", "context")
        q_col = pick("Question", "question")
        ans_col = pick("Answers", "answers")
        ctx_st = text_stats([str(c) for c in d[ctx_col]])
        q_st = text_stats([str(q) for q in d[q_col]])
        n_unans = 0
        if ans_col:
            n_unans = sum(
                1 for a in d[ans_col] if not parse_answers(a).get("text")
            )
        lines.append(f"### {split} ({d.num_rows:,} questions)\n")
        lines.append(f"- Columns: {cols}")
        lines.append(
            f"- Context words: mean {ctx_st['words_mean']}, p95 {ctx_st['words_p95']} "
            f"| Question words: mean {q_st['words_mean']}"
        )
        lines.append(
            f"- Quality: {n_unans} unanswerable, {ctx_st['dupes']} duplicate contexts "
            f"(multiple Qs per paragraph is expected)\n"
        )
        print(f"  {split}: {d.num_rows:,} questions")


def main() -> None:
    lines = [
        "# Datasets\n",
        "_Auto-generated by `scripts/explore_datasets.py` (issue #3). "
        "Raw files land in `data/raw/` (gitignored)._\n",
    ]
    explore_sentiment(lines)
    explore_hebnli(lines)
    explore_heq(lines)
    lines.append("## Cross-cutting notes for the experiments\n")
    lines.append(
        "- **Sentiment is heavily imbalanced** (~66% pos / ~31% neg / ~3% off-topic): "
        "report macro-F1, and stratify the ~500-example subset (issue #4).\n"
        "- **Sentiment 'neutral' is actually off-topic** — prompt wording must say "
        "off-topic, not neutral.\n"
        "- **HebNLI train is machine-translated**; only the test split is "
        "human-verified — evaluate on test only.\n"
        "- **HeQ contexts are long** — dominant driver of API cost (see "
        "scripts/estimate_costs.py).\n"
        "- The sentiment `morph` variant is gold pre-segmented morphemes: a useful "
        "upper-bound/sanity reference for our own segmentation in issue #6.\n"
    )
    README.parent.mkdir(parents=True, exist_ok=True)
    README.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {README}")


if __name__ == "__main__":
    main()
