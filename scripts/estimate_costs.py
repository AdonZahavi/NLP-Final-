"""Cost estimator for the commercial-API experiments.

Scenario (proposal §4.5): ~500 examples x 3 tasks x 3 conditions x 2 API models.

Prices are USD per 1M tokens (verified July 2026 — re-check before running,
they change):
  - gpt-4o:            $2.50 in / $10.00 out
  - gpt-4.1:           $2.00 in /  $8.00 out
  - claude-sonnet:     $3.00 in / $15.00 out (Sonnet 5 intro: $2.00/$10.00 until 2026-09-01)
  - claude-haiku-4.5:  $1.00 in /  $5.00 out
Batch API is ~50% cheaper for both providers if latency doesn't matter.

Usage:
    python scripts/estimate_costs.py
    python scripts/estimate_costs.py --examples 500 --overhead 1.15
"""

from __future__ import annotations

import argparse

# USD per 1M tokens: (input, output)
PRICES = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4.1": (2.00, 8.00),
    "claude-sonnet": (3.00, 15.00),
    "claude-haiku-4.5": (1.00, 5.00),
}

# Rough average tokens per example: (input, output).
# Hebrew is token-expensive in most tokenizers (~2-4 tokens/word).
# Segmented condition adds ~30% input tokens; prompt_guided adds a fixed instruction.
TASK_TOKENS = {
    "sentiment": (250, 10),
    "nli": (350, 10),
    "qa": (1500, 60),
}

CONDITION_INPUT_FACTOR = {
    "raw": 1.00,
    "segmented": 1.30,
    "prompt_guided": 1.15,
}

API_MODELS = ["gpt-4o", "claude-sonnet"]  # the two paid models in the experiment


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--examples", type=int, default=500, help="examples per task")
    p.add_argument(
        "--overhead",
        type=float,
        default=1.15,
        help="multiplier for pilots/retries/prompt iterations",
    )
    args = p.parse_args()

    grand_total = 0.0
    print(f"{'model':<16} {'task':<10} {'condition':<14} {'cost':>8}")
    print("-" * 52)
    for model in API_MODELS:
        in_price, out_price = PRICES[model]
        model_total = 0.0
        for task, (in_tok, out_tok) in TASK_TOKENS.items():
            for cond, factor in CONDITION_INPUT_FACTOR.items():
                cost = args.examples * (
                    in_tok * factor * in_price + out_tok * out_price
                ) / 1_000_000
                model_total += cost
                print(f"{model:<16} {task:<10} {cond:<14} ${cost:>7.2f}")
        print(f"{model:<16} {'TOTAL':<10} {'':<14} ${model_total:>7.2f}\n")
        grand_total += model_total

    print(f"Subtotal (both API models):        ${grand_total:.2f}")
    print(f"With {args.overhead:.0%} overhead factor:         ${grand_total * args.overhead:.2f}")
    print(f"Total paid API calls:              {args.examples * len(TASK_TOKENS) * len(CONDITION_INPUT_FACTOR) * len(API_MODELS):,}")
    print("\nCost guards: response cache (no duplicate calls), fixed subsets,")
    print("consider Batch API (-50%) for the full runs.")


if __name__ == "__main__":
    main()
