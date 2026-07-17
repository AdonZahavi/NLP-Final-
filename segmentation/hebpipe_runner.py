"""Segment sample_50.txt with HebPipe.

Prereq (use a SEPARATE venv/Colab — HebPipe pins heavy deps that may conflict):
    pip install hebpipe
    # first run downloads models (~2GB)

This runs HebPipe as a subprocess on the sample file and parses its CoNLL-U
output: supertoken ranges (`i-j  form  ...`) are the original tokens, the rows
inside the range are the morphemes.

Usage:
    python segmentation/hebpipe_runner.py
Output:
    segmentation/out_hebpipe.jsonl  (same schema as out_yap.jsonl)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_TXT = ROOT / "segmentation" / "sample_50.txt"
OUT = ROOT / "segmentation" / "out_hebpipe.jsonl"


def run_hebpipe() -> str:
    cmd = [sys.executable, "-m", "hebpipe", "-o", "conllu", str(IN_TXT)]
    print("running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        sys.exit(f"hebpipe failed:\n{proc.stderr[-2000:]}")
    conllu = IN_TXT.with_suffix(".conllu")
    if conllu.exists():
        return conllu.read_text(encoding="utf-8")
    return proc.stdout  # some versions print to stdout


def parse_conllu(conllu: str) -> list[dict]:
    sentences, current, i = [], [], 0
    rows = [l for l in conllu.splitlines()]
    idx = 0
    tokens: list[dict] = []
    pending_range: tuple[int, int] | None = None
    pending_form = ""
    pending_morphs: list[str] = []

    def flush_pending():
        nonlocal pending_range, pending_form, pending_morphs
        if pending_range:
            tokens.append({"token": pending_form, "morphemes": pending_morphs})
            pending_range, pending_form, pending_morphs = None, "", []

    for line in rows + [""]:
        if not line.strip():
            flush_pending()
            if tokens:
                sentences.append(tokens)
                tokens = []
            continue
        if line.startswith("#"):
            continue
        cols = line.split("\t")
        tid = cols[0]
        if "-" in tid:  # supertoken: morphemes follow
            flush_pending()
            a, b = tid.split("-")
            pending_range, pending_form, pending_morphs = (int(a), int(b)), cols[1], []
        elif "." in tid:
            continue  # empty nodes
        else:
            n = int(tid)
            if pending_range and pending_range[0] <= n <= pending_range[1]:
                pending_morphs.append(cols[1])
                if n == pending_range[1]:
                    flush_pending()
            else:
                flush_pending()
                tokens.append({"token": cols[1], "morphemes": [cols[1]]})
    return sentences


def main() -> None:
    source_sentences = IN_TXT.read_text(encoding="utf-8").strip().splitlines()
    parsed = parse_conllu(run_hebpipe())
    if len(parsed) != len(source_sentences):
        print(
            f"[WARN] sentence count mismatch: {len(parsed)} parsed vs "
            f"{len(source_sentences)} input (HebPipe may re-split sentences); "
            "aligning by order."
        )
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for i, toks in enumerate(parsed):
            text = source_sentences[i] if i < len(source_sentences) else ""
            f.write(json.dumps({"text": text, "tokens": toks}, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
