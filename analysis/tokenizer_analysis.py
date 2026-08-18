"""Issue #14: tokenizer analysis — why does raw Hebrew win?

Measures subword *fertility* (tokens per whitespace word) of each model's
tokenizer on our actual evaluation text, in both conditions:

- raw Hebrew: how finely does each tokenizer already fragment Hebrew words?
  High fertility means the model effectively sees subword pieces anyway —
  its own implicit segmentation.
- segmented Hebrew: what does YAP segmentation do to the token stream?
  (tokens per RAW word, i.e. total sequence-length cost of segmentation)

Also includes an English baseline sample for scale.

Tokenizers:
- gpt-4o     : tiktoken o200k_base            (pip install tiktoken)
- llama-3.2  : HF AutoTokenizer (gated; needs HF_TOKEN in .env)
- mistral-7b : HF AutoTokenizer
- claude     : no public tokenizer -> Anthropic count_tokens API if
               ANTHROPIC_API_KEY is set (small sample), else skipped

Each tokenizer is optional — missing ones are reported and skipped.

Usage (from repo root, on a machine with internet + .env):
    PYTHONPATH=src python analysis/tokenizer_analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBSETS = ROOT / "data" / "subsets"
OUT_MD = ROOT / "analysis" / "tokenizers.md"

SAMPLE_N = 300  # sentiment examples used (short, representative UGC Hebrew)

ENGLISH_BASELINE = (
    "The president visited the school yesterday and spoke with the students "
    "about their plans for the future. Everyone agreed that the meeting was "
    "productive and that another visit should be scheduled soon."
) * 10


def load_texts() -> tuple[list[str], list[str]]:
    raw = [json.loads(l)["text"] for l in
           open(SUBSETS / "sentiment_500.jsonl", encoding="utf-8")][:SAMPLE_N]
    seg = [json.loads(l)["text_seg"] for l in
           open(SUBSETS / "segmented" / "sentiment_500.jsonl",
                encoding="utf-8")][:SAMPLE_N]
    return raw, seg


def get_tokenizers() -> dict:
    toks = {}
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        toks["gpt-4o (o200k)"] = lambda s: len(enc.encode(s))
    except Exception as e:  # noqa: BLE001
        print(f"[skip] tiktoken: {e}")
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except Exception:  # noqa: BLE001
        pass
    from os import environ
    for name, hf_id in (("llama-3.2", "meta-llama/Llama-3.2-3B-Instruct"),
                        ("mistral-7b", "mistralai/Mistral-7B-Instruct-v0.3")):
        try:
            from transformers import AutoTokenizer
            t = AutoTokenizer.from_pretrained(hf_id,
                                              token=environ.get("HF_TOKEN"))
            toks[name] = (lambda tt: (lambda s: len(tt.encode(
                s, add_special_tokens=False))))(t)
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {name}: {type(e).__name__}: {str(e)[:120]}")
    if environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            client = anthropic.Anthropic()

            def claude_count(s: str) -> int:
                r = client.messages.count_tokens(
                    model="claude-sonnet-5",
                    messages=[{"role": "user", "content": s}])
                return r.input_tokens
            toks["claude (API, sample)"] = claude_count
        except Exception as e:  # noqa: BLE001
            print(f"[skip] claude: {type(e).__name__}: {str(e)[:120]}")
    return toks


def fertility(count_fn, texts: list[str], word_texts: list[str],
              cap: int | None = None) -> float:
    """tokens(texts) per whitespace word of word_texts."""
    if cap:
        texts, word_texts = texts[:cap], word_texts[:cap]
    total_tokens = sum(count_fn(t) for t in texts)
    total_words = sum(len(t.split()) for t in word_texts)
    return total_tokens / max(total_words, 1)


def main() -> None:
    raw, seg = load_texts()
    toks = get_tokenizers()
    if not toks:
        sys.exit("no tokenizers available — install tiktoken/transformers "
                 "and set tokens in .env")

    lines = ["# Tokenizer analysis (issue #14)", "",
             f"Fertility = subword tokens per whitespace word, measured on "
             f"{SAMPLE_N} sentiment examples (user-generated Hebrew).",
             "`seg cost` = tokens of the SEGMENTED text per RAW word — the",
             "total sequence-length cost of feeding YAP output to the model.",
             "English baseline: simple news-register English text.", "",
             "| tokenizer | Hebrew raw | Hebrew segmented (per seg word) | "
             "seg cost (per raw word) | English |",
             "|---|---|---|---|---|"]

    for name, fn in toks.items():
        cap = 25 if "API" in name else None  # keep API usage tiny
        f_raw = fertility(fn, raw, raw, cap)
        f_seg = fertility(fn, seg, seg, cap)
        f_cost = fertility(fn, seg, raw, cap)
        f_en = fn(ENGLISH_BASELINE) / len(ENGLISH_BASELINE.split())
        lines.append(f"| {name} | {f_raw:.2f} | {f_seg:.2f} | "
                     f"{f_cost:.2f} | {f_en:.2f} |")
        print(lines[-1])

    lines += ["", "## Reading the table", "",
              "- Hebrew raw fertility >> English fertility: every tokenizer",
              "  already fragments Hebrew words into multiple pieces — the",
              "  models never see whole Hebrew words, with or without YAP.",
              "- If segmented fertility (per seg word) is close to 1-1.5, the",
              "  tokenizers largely recognize the split morphemes as units,",
              "  yet performance still DROPPED — evidence the harm is a",
              "  distribution shift (unfamiliar spacing), not a tokenization",
              "  failure.",
              "- `seg cost` shows segmentation also lengthens sequences,",
              "  raising compute/API cost for zero accuracy benefit."]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {OUT_MD}")


if __name__ == "__main__":
    main()
