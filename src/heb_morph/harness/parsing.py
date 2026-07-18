"""Strict output parsing. Returns the parsed label/span or None on failure
(per CONTRACT.md, parsed_label is null on parse failure — failures count as
wrong in metrics and are reported separately)."""

from __future__ import annotations

import re

_LABELS = {
    "sentiment": {
        "positive": "pos", "negative": "neg",
        "off-topic": "off-topic", "off topic": "off-topic", "offtopic": "off-topic",
        # common Hebrew answers as a fallback
        "חיובי": "pos", "שלילי": "neg", "לא רלוונטי": "off-topic",
    },
    "nli": {
        "entailment": "entailment", "contradiction": "contradiction",
        "neutral": "neutral",
    },
}


def parse_classification(task: str, raw_output: str) -> str | None:
    """Find exactly one known label in the output; None if zero or ambiguous."""
    text = raw_output.strip().lower()
    if not text:
        return None
    # fast path: the whole (first line of the) answer is a label
    first_line = text.splitlines()[0].strip().strip('."\'`:!،,')
    mapping = _LABELS[task]
    if first_line in mapping:
        return mapping[first_line]
    found = {canon for key, canon in mapping.items()
             if re.search(rf"(?<![a-zא-ת]){re.escape(key)}(?![a-zא-ת])", text)}
    return found.pop() if len(found) == 1 else None


def parse_qa_span(raw_output: str) -> str | None:
    """First non-empty line, stripped of quotes/labels; None if empty."""
    for line in raw_output.strip().splitlines():
        line = line.strip()
        line = re.sub(r"^(answer|תשובה)\s*[:：]\s*", "", line, flags=re.I)
        line = line.strip().strip('"\'"״`')
        if line:
            return line
    return None


def parse(task: str, raw_output: str) -> str | None:
    if task in ("sentiment", "nli"):
        return parse_classification(task, raw_output)
    if task == "qa":
        return parse_qa_span(raw_output)
    raise ValueError(f"unknown task: {task}")
