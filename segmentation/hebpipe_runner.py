"""Segment sample_50.txt with RFTokenizer — HebPipe's morphological segmenter.

Why not the full hebpipe package: on modern Python/transformers stacks it fails
at import time (its xrenner/coref module), requires an interactive model-download
prompt, and forces a Stanza tagging pass even for segmentation-only runs.
Its actual segmentation engine is RFTokenizer (same author, same heb.sm3 model
— heb_pipe.py -wt just calls rf_tokenize), so we run that component directly.

Prereq:
    pip install rftokenizer

Usage:
    python segmentation/hebpipe_runner.py
Output:
    segmentation/out_hebpipe.jsonl  (same schema as out_yap.jsonl)
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_TXT = ROOT / "segmentation" / "sample_50.txt"
OUT = ROOT / "segmentation" / "out_hebpipe.jsonl"
MODEL = ROOT / "segmentation" / "heb.sm3"
# same model file the hebpipe package downloads for itself
MODEL_URL = "http://gucorpling.org/amir/download/heb_models_v4/heb.sm3"

# same minimal tokenization as yap_client.py, so both tools see identical tokens
TOKENIZE_RE = re.compile(r"[א-ת0-9a-zA-Z\"'׳״]+|[^\s]")


def main() -> None:
    if not MODEL.exists():
        print(f"downloading {MODEL_URL} …")
        urllib.request.urlretrieve(MODEL_URL, MODEL)

    from rftokenizer import RFTokenizer

    tok = RFTokenizer(model=str(MODEL))
    sentences = IN_TXT.read_text(encoding="utf-8").strip().splitlines()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for i, sent in enumerate(sentences, 1):
            words = TOKENIZE_RE.findall(sent)
            segged = tok.rf_tokenize(words)
            tokens = [
                {"token": w, "morphemes": s.split("|")}
                for w, s in zip(words, segged)
            ]
            f.write(json.dumps({"text": sent, "tokens": tokens}, ensure_ascii=False) + "\n")
            print(f"  [{i}/{len(sentences)}] ok")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
