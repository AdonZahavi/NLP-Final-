"""Unified experiment runner: any (model × task × condition) combination.

Usage (from repo root):
    PYTHONPATH=src python -m heb_morph.harness.runner \
        --model gpt-4 --task sentiment --condition raw [--limit 20]

Guarantees:
- every prompt goes through the SQLite response cache (never pay twice);
- per-example JSONL records follow CONTRACT.md exactly and are appended
  incrementally -> fully resumable (already-answered ids are skipped);
- transient API errors are retried with exponential backoff; persistent
  failure aborts loudly (never silently skips paid work).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from heb_morph.harness import metrics, parsing, prompts

ROOT = Path(__file__).resolve().parents[3]
SUBSETS = ROOT / "data" / "subsets"
RESULTS = ROOT / "results"

TASK_FILES = {"sentiment": "sentiment_500.jsonl",
              "nli": "nli_884.jsonl",
              "qa": "qa_500.jsonl"}
MODELS = ("gpt-4", "claude", "llama-3.2", "mistral-7b")
MAX_TOKENS = {"sentiment": 8, "nli": 8, "qa": 64}
RETRY_DELAYS = (2, 8, 30, 60)


def make_client(model_key: str):
    """Instantiate the cached client for a contract model key."""
    sys.path.insert(0, str(ROOT / "src"))
    from heb_morph.clients import (AnthropicClient, CachedModelClient,
                                   OpenAIClient, SqliteResponseCache)
    cache = SqliteResponseCache(ROOT / "cache" / "responses.sqlite")
    if model_key == "gpt-4":
        return CachedModelClient(OpenAIClient(), cache)
    if model_key == "claude":
        return CachedModelClient(AnthropicClient(), cache)
    if model_key in ("llama-3.2", "mistral-7b"):
        from heb_morph.clients.hf_client import HFLocalClient
        hf_id = ("meta-llama/Llama-3.2-3B-Instruct" if model_key == "llama-3.2"
                 else "mistralai/Mistral-7B-Instruct-v0.3")
        return CachedModelClient(HFLocalClient(hf_id), cache)
    raise ValueError(f"unknown model key: {model_key}")


def load_records(task: str, condition: str) -> list[dict]:
    """Segmented condition needs the *_seg fields -> segmented files."""
    base = SUBSETS / "segmented" if condition == "segmented" else SUBSETS
    with open(base / TASK_FILES[task], encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def gold_of(task: str, record: dict) -> str:
    if task == "qa":
        return json.dumps(record["answers"]["text"], ensure_ascii=False)
    return record["label"]


def complete_with_retry(client, prompt: str, **params) -> str:
    last: Exception | None = None
    for delay in (0,) + RETRY_DELAYS:
        if delay:
            time.sleep(delay)
        try:
            return client.complete(prompt, **params)
        except Exception as e:  # noqa: BLE001
            last = e
            import traceback
            print(f"    [retry] {type(e).__name__}: {e!r}")
            traceback.print_exc()
    raise RuntimeError(f"model call failed after retries: {last}")


def run(model_key: str, task: str, condition: str, limit: int = 0,
        morph_instruction: str | None = None, client=None,
        results_dir: Path | None = None) -> Path:
    records = load_records(task, condition)
    if limit:
        records = records[:limit]
    client = client or make_client(model_key)

    out_dir = (results_dir or RESULTS) / condition
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{task}_{model_key}.jsonl"

    done_ids = set()
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            done_ids = {json.loads(l)["id"] for l in f}
    todo = [r for r in records if r["id"] not in done_ids]
    print(f"[{model_key}|{task}|{condition}] {len(records)} examples, "
          f"{len(done_ids)} done, {len(todo)} to run")

    t0 = time.time()
    with open(out_path, "a", encoding="utf-8", newline="\n") as f:
        for i, rec in enumerate(todo, 1):
            prompt = prompts.build_prompt(task, rec, condition, morph_instruction)
            raw_output = complete_with_retry(
                client, prompt, max_tokens=MAX_TOKENS[task])
            row = {
                "id": rec["id"],
                "task": task,
                "model": model_key,
                "condition": condition,
                "input": prompt,
                "raw_output": raw_output,
                "parsed_label": parsing.parse(task, raw_output),
                "gold": gold_of(task, rec),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            if i % 25 == 0 or i == len(todo):
                rate = i / max(time.time() - t0, 1)
                print(f"  {i}/{len(todo)} ({rate:.2f} ex/s)")

    print(f"wrote {out_path}")
    print("scores:", json.dumps(metrics.score_file(out_path), ensure_ascii=False))
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=MODELS)
    ap.add_argument("--task", required=True, choices=list(TASK_FILES))
    ap.add_argument("--condition", required=True, choices=prompts.CONDITIONS)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--morph-instruction-file", default=None,
                    help="text file with the winning prompt-guided instruction (#8)")
    args = ap.parse_args()

    morph = None
    if args.morph_instruction_file:
        morph = Path(args.morph_instruction_file).read_text(encoding="utf-8").strip()
    run(args.model, args.task, args.condition, args.limit, morph)


if __name__ == "__main__":
    main()
