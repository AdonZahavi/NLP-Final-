"""Issue #5: build the ~50-sentence comparison sample for YAP vs HebPipe.

Draws from the committed eval subsets (data/subsets/), preferring sentences rich
in the morphological phenomena we care about (prefixes ו/ש/כש/ה/ל/ב/מ, plausible
pronominal suffixes), so the manual comparison actually exercises them.

Usage:
    python segmentation/make_sample.py
Outputs:
    segmentation/sample_50.txt    one sentence per line (input to both tools)
    segmentation/sample_50.jsonl  id, source task, text
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
SUBSETS = ROOT / "data" / "subsets"
OUT_TXT = ROOT / "segmentation" / "sample_50.txt"
OUT_JSONL = ROOT / "segmentation" / "sample_50.jsonl"

# words starting with common clitic prefixes (incl. combinations like וכש, ומה)
PREFIX_RE = re.compile(r"(?:^|\s)(?:ו?כש|ו?ש|ו?ה|ו?ל|ו?ב|ו?מ|ו)[א-ת]{2,}")
QUOTA = {"sentiment": 20, "nli": 15, "qa": 15}


def richness(text: str) -> float:
    words = text.split()
    if not (6 <= len(words) <= 30):  # readable for manual review
        return -1.0
    return len(PREFIX_RE.findall(text)) / len(words)


def candidates() -> dict[str, list[dict]]:
    pools: dict[str, list[dict]] = {"sentiment": [], "nli": [], "qa": []}
    with open(SUBSETS / "sentiment_500.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            pools["sentiment"].append({"id": r["id"], "text": r["text"]})
    with open(SUBSETS / "nli_884.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            pools["nli"].append({"id": r["id"] + "-prem", "text": r["premise"]})
            pools["nli"].append({"id": r["id"] + "-hyp", "text": r["hypothesis"]})
    with open(SUBSETS / "qa_500.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            pools["qa"].append({"id": r["id"] + "-q", "text": r["question"]})
    return pools


def main() -> None:
    rng = random.Random(SEED)
    pools = candidates()
    picked: list[dict] = []
    for task, quota in QUOTA.items():
        pool = [dict(c, score=richness(c["text"])) for c in pools[task]]
        pool = [c for c in pool if c["score"] >= 0]
        # top-3*quota by morphological richness, then random pick for variety
        pool.sort(key=lambda c: (-c["score"], c["id"]))
        top = pool[: 3 * quota]
        rng.shuffle(top)
        for c in top[:quota]:
            picked.append({"id": c["id"], "task": task, "text": " ".join(c["text"].split())})

    seen, unique = set(), []
    for c in picked:
        if c["text"] not in seen:
            seen.add(c["text"])
            unique.append(c)

    OUT_TXT.write_text("\n".join(c["text"] for c in unique) + "\n", encoding="utf-8")
    with open(OUT_JSONL, "w", encoding="utf-8", newline="\n") as f:
        for c in unique:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"wrote {len(unique)} sentences to {OUT_TXT.name} / {OUT_JSONL.name}")


if __name__ == "__main__":
    main()
