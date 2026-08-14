"""Issues #9-11: orchestrate runner.run over models × tasks for one condition.

Usage (from repo root, .env populated):
    # issue #9 — API models, raw condition, local machine:
    PYTHONPATH=src python scripts/run_all.py --condition raw --models gpt-4,claude

    # smoke test first (STRONGLY recommended before full spend):
    PYTHONPATH=src python scripts/run_all.py --condition raw \
        --models gpt-4,claude --limit 20

    # GPU models (run in Colab via experiments/colab_run_hf_models.ipynb):
    PYTHONPATH=src python scripts/run_all.py --condition raw --models llama-3.2
    PYTHONPATH=src python scripts/run_all.py --condition raw --models mistral-7b

    # issues #10/#11 are the same command with --condition segmented /
    # --condition prompt_guided (the winning instruction loads automatically).

Properties:
- one client per model, reused across tasks (HF models load weights ONCE);
- fully resumable: runner skips finished ids, cache prevents double payment;
- a model failure doesn't kill the sweep — remaining combos still run,
  the failure is reported and the exit code is nonzero;
- after each sweep, refreshes results/<condition>/summary.md.
"""

from __future__ import annotations

import argparse
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from heb_morph.harness import runner  # noqa: E402

WINNING_INSTRUCTION = ROOT / "experiments" / "winning_instruction.txt"
TASKS = ("sentiment", "nli", "qa")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True,
                    choices=("raw", "segmented", "prompt_guided"))
    ap.add_argument("--models", default="gpt-4,claude",
                    help="comma-separated subset of: gpt-4,claude,llama-3.2,mistral-7b")
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--limit", type=int, default=0,
                    help="cap examples per task (smoke test); 0 = full run")
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]
    for m in models:
        if m not in runner.MODELS:
            sys.exit(f"unknown model: {m}")
    for t in tasks:
        if t not in TASKS:
            sys.exit(f"unknown task: {t}")

    morph = None
    if args.condition == "prompt_guided":
        if not WINNING_INSTRUCTION.exists():
            sys.exit("missing experiments/winning_instruction.txt — run issue #8 pilot first")
        morph = WINNING_INSTRUCTION.read_text(encoding="utf-8").strip()
        print(f"prompt_guided instruction loaded ({len(morph)} chars)")

    failures: list[tuple[str, str, str]] = []
    t0 = time.time()
    for model_key in models:
        print(f"\n=== {model_key} ({args.condition}) ===")
        try:
            client = runner.make_client(model_key)  # once per model
        except Exception as e:  # noqa: BLE001
            print(f"!! client init failed for {model_key}: {e}")
            failures.append((model_key, "*", str(e)))
            continue
        for task in tasks:
            try:
                runner.run(model_key, task, args.condition,
                           limit=args.limit, morph_instruction=morph,
                           client=client)
            except Exception as e:  # noqa: BLE001
                traceback.print_exc()
                failures.append((model_key, task, str(e)))

    print(f"\nsweep finished in {(time.time() - t0) / 60:.1f} min")

    # refresh the sanity report
    from summarize_results import summarize
    summarize(args.condition)

    if failures:
        print("\nFAILED combos (rerun the same command — it resumes):")
        for m, t, e in failures:
            print(f"  {m} × {t}: {e[:200]}")
        sys.exit(1)
    print("all requested combos complete")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts"))
    main()
