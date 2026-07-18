"""Unit tests for the evaluation harness (issue #7). Run from repo root:

    PYTHONPATH=src python -m pytest tests/harness -q
or  PYTHONPATH=src python tests/harness/test_harness.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from heb_morph.harness import metrics, parsing, prompts, runner  # noqa: E402


# ---------------------------------------------------------------- prompts
def test_prompt_conditions():
    rec = {"text": "טקסט גולמי", "text_seg": "טקסט מ פולח"}
    raw = prompts.build_prompt("sentiment", rec, "raw")
    seg = prompts.build_prompt("sentiment", rec, "segmented")
    pg = prompts.build_prompt("sentiment", rec, "prompt_guided")
    assert "טקסט גולמי" in raw and "morphologically segmented" not in raw
    assert "טקסט מ פולח" in seg and "morphologically segmented" in seg
    assert "טקסט גולמי" in pg and "decompose" in pg
    custom = prompts.build_prompt("sentiment", rec, "prompt_guided",
                                  morph_instruction="CUSTOM INSTRUCTION")
    assert "CUSTOM INSTRUCTION" in custom


def test_prompt_all_tasks():
    nli = {"premise": "P", "hypothesis": "H"}
    qa = {"context": "C", "question": "Q"}
    assert "Premise: P" in prompts.build_prompt("nli", nli, "raw")
    assert "Question: Q" in prompts.build_prompt("qa", qa, "raw")


# ---------------------------------------------------------------- parsing
def test_parse_classification():
    assert parsing.parse("sentiment", "Positive") == "pos"
    assert parsing.parse("sentiment", "  negative.  ") == "neg"
    assert parsing.parse("sentiment", "Off-topic") == "off-topic"
    assert parsing.parse("sentiment", "The sentiment is positive here") == "pos"
    assert parsing.parse("sentiment", "positive or negative") is None  # ambiguous
    assert parsing.parse("sentiment", "I cannot classify this") is None
    assert parsing.parse("sentiment", "חיובי") == "pos"
    assert parsing.parse("nli", "entailment") == "entailment"
    assert parsing.parse("nli", "NEUTRAL\nbecause...") == "neutral"


def test_parse_qa():
    assert parsing.parse("qa", "  ירושלים  ") == "ירושלים"
    assert parsing.parse("qa", 'Answer: "בשנת 1948"') == "בשנת 1948"
    assert parsing.parse("qa", "תשובה: דוד בן גוריון") == "דוד בן גוריון"
    assert parsing.parse("qa", "   \n  ") is None


# ---------------------------------------------------------------- metrics
def test_classification_metrics():
    preds = ["pos", "neg", "pos", None]
    golds = ["pos", "neg", "neg", "pos"]
    assert metrics.accuracy(preds, golds) == 0.5
    f1 = metrics.macro_f1(preds, golds)
    assert 0 < f1 < 1
    # perfect predictions
    assert metrics.macro_f1(["a", "b"], ["a", "b"]) == 1.0


def test_qa_metrics():
    assert metrics.qa_em("ירושלים", ["ירושלים"]) == 1.0
    assert metrics.qa_em('"ירושלים".', ["ירושלים"]) == 1.0  # normalization
    assert metrics.qa_em("תל אביב", ["ירושלים"]) == 0.0
    assert metrics.qa_token_f1("דוד בן גוריון", ["בן גוריון"]) > 0.7
    assert metrics.qa_token_f1(None, ["x"]) == 0.0


# ---------------------------------------------------------------- runner
class MockClient:
    """Deterministic fake model; counts calls to verify resume behavior."""
    model = "mock"

    def __init__(self, answer="positive"):
        self.answer = answer
        self.calls = 0

    def complete(self, prompt, **params):
        self.calls += 1
        return self.answer


def _fake_subsets(tmp: Path):
    (tmp / "subsets").mkdir(parents=True)
    rows = [{"id": f"sent-{i}", "task": "sentiment",
             "text": f"טקסט {i}", "label": "pos" if i % 2 else "neg"}
            for i in range(6)]
    with open(tmp / "subsets" / "sentiment_500.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return rows


def test_runner_end_to_end_and_resume(monkeypatch=None):
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _fake_subsets(tmp)
        # point the runner at the fake data dirs
        runner.SUBSETS = tmp / "subsets"
        results = tmp / "results"

        client = MockClient("positive")
        out = runner.run("gpt-4", "sentiment", "raw", client=client,
                         results_dir=results)
        recs = [json.loads(l) for l in open(out, encoding="utf-8")]
        assert len(recs) == 6 and client.calls == 6
        # contract schema
        assert set(recs[0]) == {"id", "task", "model", "condition", "input",
                                "raw_output", "parsed_label", "gold"}
        assert recs[0]["parsed_label"] == "pos"
        assert out.name == "sentiment_gpt-4.jsonl" and out.parent.name == "raw"

        # resume: second run makes ZERO new calls
        client2 = MockClient("positive")
        runner.run("gpt-4", "sentiment", "raw", client=client2,
                   results_dir=results)
        assert client2.calls == 0

        # scoring the file works
        s = metrics.score_file(out)
        assert s["n"] == 6 and 0 <= s["accuracy"] <= 1
        assert s["parse_failure_rate"] == 0.0


def _run_all():
    fns = [v for k, v in globals().items() if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} tests passed")


if __name__ == "__main__":
    _run_all()
