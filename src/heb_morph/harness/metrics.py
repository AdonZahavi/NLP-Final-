"""Metrics: accuracy + macro-F1 (classification), EM + token-F1 (QA).

No sklearn dependency — implemented directly so results are auditable.
Parse failures (parsed_label is None/null) count as WRONG and are reported.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

_PUNCT_RE = re.compile(r"[^\wא-ת0-9]+", re.UNICODE)


def normalize_answer(s: str) -> str:
    """SQuAD-style normalization adapted for Hebrew: strip punctuation,
    collapse whitespace, lowercase latin."""
    return " ".join(_PUNCT_RE.sub(" ", str(s)).lower().split())


def qa_em(pred: str | None, golds: list[str]) -> float:
    if pred is None:
        return 0.0
    p = normalize_answer(pred)
    return float(any(p == normalize_answer(g) for g in golds))


def qa_token_f1(pred: str | None, golds: list[str]) -> float:
    if pred is None:
        return 0.0
    p_toks = normalize_answer(pred).split()
    best = 0.0
    for g in golds:
        g_toks = normalize_answer(g).split()
        if not p_toks or not g_toks:
            best = max(best, float(p_toks == g_toks))
            continue
        common = Counter(p_toks) & Counter(g_toks)
        overlap = sum(common.values())
        if overlap == 0:
            continue
        prec, rec = overlap / len(p_toks), overlap / len(g_toks)
        best = max(best, 2 * prec * rec / (prec + rec))
    return best


def accuracy(preds: list[str | None], golds: list[str]) -> float:
    return sum(p == g for p, g in zip(preds, golds)) / max(len(golds), 1)


def macro_f1(preds: list[str | None], golds: list[str]) -> float:
    classes = sorted(set(golds))
    f1s = []
    for c in classes:
        tp = sum(1 for p, g in zip(preds, golds) if p == c and g == c)
        fp = sum(1 for p, g in zip(preds, golds) if p == c and g != c)
        fn = sum(1 for p, g in zip(preds, golds) if p != c and g == c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return sum(f1s) / len(f1s) if f1s else 0.0


def score_records(records: list[dict]) -> dict:
    """Score a list of contract-schema prediction records (one task)."""
    task = records[0]["task"]
    n = len(records)
    failures = sum(1 for r in records if r["parsed_label"] in (None, ""))
    out = {"task": task, "n": n, "parse_failure_rate": failures / n}
    if task in ("sentiment", "nli"):
        preds = [r["parsed_label"] for r in records]
        golds = [r["gold"] for r in records]
        out["accuracy"] = accuracy(preds, golds)
        out["macro_f1"] = macro_f1(preds, golds)
    elif task == "qa":
        golds_list = [json.loads(r["gold"]) if isinstance(r["gold"], str) else r["gold"]
                      for r in records]
        out["em"] = sum(qa_em(r["parsed_label"], g)
                        for r, g in zip(records, golds_list)) / n
        out["f1"] = sum(qa_token_f1(r["parsed_label"], g)
                        for r, g in zip(records, golds_list)) / n
    return out


def score_file(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        records = [json.loads(l) for l in f]
    result = score_records(records)
    result["file"] = str(path)
    return result
