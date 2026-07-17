"""Segment sample_50.txt with YAP via its local HTTP API.

Prereq (Linux/WSL/Colab — YAP is painful on native Windows):
    git clone https://github.com/OnlpLab/yap.git && cd yap
    bunzip2 data/*.bz2 && go get . && go build .
    ./yap api          # serves on http://localhost:8000

Usage:
    python segmentation/yap_client.py [--host http://localhost:8000]
Output:
    segmentation/out_yap.jsonl  {"text", "tokens": [{"token", "morphemes": [...]}]}
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_TXT = ROOT / "segmentation" / "sample_50.txt"
OUT = ROOT / "segmentation" / "out_yap.jsonl"

# minimal tokenization: split punctuation off words (YAP expects whitespace tokens)
TOKENIZE_RE = re.compile(r"[א-ת0-9a-zA-Z\"'׳״]+|[^\s]")


def yap_joint(host: str, sentence: str) -> dict:
    tokens = TOKENIZE_RE.findall(sentence)
    # YAP protocol: tokens separated by spaces, sentence terminated by two spaces
    payload = json.dumps({"text": " ".join(tokens) + "  "}).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/yap/heb/joint", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_md_lattice(md: str, tokens: list[str]) -> list[dict]:
    """md_lattice rows: start end form lemma cpos pos feats token_id"""
    per_token: dict[int, list[str]] = defaultdict(list)
    for line in md.strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= 8:
            per_token[int(parts[7])].append(parts[2])
    return [
        {"token": tok, "morphemes": per_token.get(i + 1, [tok])}
        for i, tok in enumerate(tokens)
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:8000")
    args = ap.parse_args()

    sentences = IN_TXT.read_text(encoding="utf-8").strip().splitlines()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for i, sent in enumerate(sentences, 1):
            tokens = TOKENIZE_RE.findall(sent)
            try:
                resp = yap_joint(args.host, sent)
                toks = parse_md_lattice(resp.get("md_lattice", ""), tokens)
            except Exception as e:  # noqa: BLE001
                print(f"  [{i}] ERROR: {e}")
                toks = [{"token": t, "morphemes": [t], "error": True} for t in tokens]
            f.write(json.dumps({"text": sent, "tokens": toks}, ensure_ascii=False) + "\n")
            print(f"  [{i}/{len(sentences)}] ok")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
