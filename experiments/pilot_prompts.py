"""Issue #8: pilot the morphology-instruction variants on DEV slices.

The dev slices are DISJOINT from the fixed eval subsets (no prompt tuning on
test data): sentiment uses token_test rows NOT selected in issue #4; NLI uses
the HebNLI validation split. QA is excluded from the pilot (span format is
unchanged by the instruction; classification tasks are the cheap, sensitive
probes).

Usage (needs .env with API keys; ~600 short calls ≈ under $1, all cached):
    PYTHONPATH=src python experiments/pilot_prompts.py --model gpt-4
    PYTHONPATH=src python experiments/pilot_prompts.py --model gpt-4 --mock  # dry run

Outputs:
    experiments/dev_slices/{sentiment,nli}_dev50.jsonl  (deterministic, committed)
    experiments/prompts.md            <- results table appended
    experiments/winning_instruction.txt  <- consumed by the runner via
                                            --morph-instruction-file
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from heb_morph.harness import metrics, parsing, prompts  # noqa: E402
from prompt_variants import VARIANTS  # noqa: E402

SEED = 42
DEV_DIR = ROOT / "experiments" / "dev_slices"
N_PER_TASK = 50
SENTIMENT_LABELS = {0: "pos", 1: "neg", 2: "off-topic"}
DEFAULT_MAX_TOKENS = 8


# ------------------------------------------------------------ dev slices
def build_dev_slices() -> dict[str, list[dict]]:
    DEV_DIR.mkdir(parents=True, exist_ok=True)
    slices = {}
    for task in ("sentiment", "nli"):
        path = DEV_DIR / f"{task}_dev50.jsonl"
        if path.exists() and path.stat().st_size > 0:
            slices[task] = [json.loads(l) for l in open(path, encoding="utf-8")]
            continue
        records = (_build_sentiment_dev() if task == "sentiment"
                   else _build_nli_dev())
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"built {path} ({len(records)} examples)")
        slices[task] = records
    return slices


def _build_sentiment_dev() -> list[dict]:
    import pandas as pd

    eval_ids = {json.loads(l)["id"]
                for l in open(ROOT / "data" / "subsets" / "sentiment_500.jsonl",
                              encoding="utf-8")}
    df = pd.read_csv(ROOT / "data" / "raw" / "token_test.tsv", sep="\t",
                     names=["text", "label"], quoting=3, dtype={"label": int})
    rng = random.Random(SEED)
    records = []
    for label_val, quota in ((0, 20), (1, 20), (2, 10)):  # pos/neg/off-topic
        pool = [i for i in df.index[df["label"] == label_val]
                if f"sent-{i}" not in eval_ids]
        for i in sorted(rng.sample(pool, quota)):
            records.append({"id": f"dev-sent-{i}", "task": "sentiment",
                            "text": str(df.at[i, "text"]),
                            "label": SENTIMENT_LABELS[label_val]})
    return records


def _build_nli_dev() -> list[dict]:
    from datasets import load_dataset

    d = load_dataset("HebArabNlpProject/HebNLI",
                     data_files="HebNLI_val.jsonl", split="train")
    cols = d.column_names
    prem = "translation1" if "translation1" in cols else cols[0]
    hyp = "translation2" if "translation2" in cols else cols[1]
    label_col = next(c for c in ("hebrew_label", "gold_label",
                                 "original_label", "label") if c in cols)
    rng = random.Random(SEED)
    idxs = sorted(rng.sample(range(len(d)), N_PER_TASK))
    records = []
    for i in idxs:
        row = d[i]
        records.append({"id": f"dev-nli-{i}", "task": "nli",
                        "premise": str(row[prem]),
                        "hypothesis": str(row[hyp]),
                        "label": str(row[label_col]).strip().lower()})
    return [r for r in records
            if r["label"] in ("entailment", "contradiction", "neutral")]


# ------------------------------------------------------------ pilot
class MockClient:
    model = "mock"

    def complete(self, prompt, **params):
        return "positive" if "off-topic" in prompt else "neutral"


def make_client(model_key: str, mock: bool):
    if mock:
        return MockClient()
    from heb_morph.clients import (AnthropicClient, CachedModelClient,
                                   OpenAIClient, SqliteResponseCache)
    cache = SqliteResponseCache(ROOT / "cache" / "responses.sqlite")
    base = OpenAIClient() if model_key == "gpt-4" else AnthropicClient()
    return CachedModelClient(base, cache)


def eval_variant(client, records: list[dict], task: str,
                 condition: str, instruction: str | None,
                 max_tokens: int | None) -> dict:
    preds, golds, failures = [], [], 0
    for rec in records:
        prompt = prompts.build_prompt(task, rec, condition, instruction)
        raw = client.complete(prompt,
                              max_tokens=max_tokens or DEFAULT_MAX_TOKENS)
        # for v5 the answer is on the LAST line; try last line first
        parsed = (parsing.parse(task, raw.strip().splitlines()[-1])
                  if raw.strip() else None) or parsing.parse(task, raw)
        preds.append(parsed)
        golds.append(rec["label"])
        failures += parsed is None
    return {"accuracy": metrics.accuracy(preds, golds),
            "macro_f1": metrics.macro_f1(preds, golds),
            "parse_failures": failures, "n": len(records)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-4", choices=["gpt-4", "claude"])
    ap.add_argument("--mock", action="store_true", help="dry run, no API calls")
    args = ap.parse_args()

    if not args.mock:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")

    slices = build_dev_slices()
    client = make_client(args.model, args.mock)

    conditions: list[tuple[str, str, str | None, int | None]] = [
        ("baseline_raw", "raw", None, None)]
    conditions += [(name, "prompt_guided", v["instruction"], v["max_tokens"])
                   for name, v in VARIANTS.items()]

    results: dict[str, dict[str, dict]] = {}
    for name, condition, instruction, max_tok in conditions:
        results[name] = {}
        for task, records in slices.items():
            r = eval_variant(client, records, task, condition, instruction, max_tok)
            results[name][task] = r
            print(f"{name:<22} {task:<10} acc={r['accuracy']:.3f} "
                  f"f1={r['macro_f1']:.3f} fails={r['parse_failures']}")

    # winner = best mean accuracy across tasks (ties -> earlier/simpler variant)
    def mean_acc(name: str) -> float:
        return sum(v["accuracy"] for v in results[name].values()) / len(results[name])

    winner = max(VARIANTS, key=mean_acc)
    print(f"\nWINNER: {winner} (mean acc {mean_acc(winner):.3f} vs "
          f"baseline {mean_acc('baseline_raw'):.3f})")

    if not args.mock:
        (ROOT / "experiments" / "winning_instruction.txt").write_text(
            VARIANTS[winner]["instruction"], encoding="utf-8")
        _append_results(args.model, results, winner)
        print("wrote winning_instruction.txt and appended results to prompts.md")


def _append_results(model: str, results: dict, winner: str) -> None:
    lines = [f"\n## Pilot results (model: {model}, 50 dev examples/task)\n",
             "| variant | sentiment acc | sentiment F1 | nli acc | nli F1 | parse fails |",
             "|---|---|---|---|---|---|"]
    for name, per_task in results.items():
        s, n = per_task.get("sentiment", {}), per_task.get("nli", {})
        fails = s.get("parse_failures", 0) + n.get("parse_failures", 0)
        mark = " **← winner**" if name == winner else ""
        lines.append(f"| {name}{mark} | {s.get('accuracy', 0):.3f} | "
                     f"{s.get('macro_f1', 0):.3f} | {n.get('accuracy', 0):.3f} | "
                     f"{n.get('macro_f1', 0):.3f} | {fails} |")
    with open(ROOT / "experiments" / "prompts.md", "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
