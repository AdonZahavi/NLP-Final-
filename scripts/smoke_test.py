"""Smoke test: verify OpenAI + Anthropic API keys with a Hebrew call, and that caching works.

Usage:
    pip install -r requirements-a.txt
    cp .env.example .env   # fill in keys
    python scripts/smoke_test.py

Each model is called twice with the same prompt; the second call MUST be a cache hit
(free). Exits non-zero if any API call or the cache guarantee fails.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv

from heb_morph.clients import (
    AnthropicClient,
    CachedModelClient,
    OpenAIClient,
    SqliteResponseCache,
)

# Morphologically rich Hebrew: וכשהלכתי = ו+כש+הלכ+תי
PROMPT = (
    "סווג את הסנטימנט של המשפט הבא כ'חיובי', 'שלילי' או 'נייטרלי'. "
    "ענה במילה אחת בלבד.\n"
    "משפט: וכשהלכתי אתמול למסעדה החדשה, האוכל היה מצוין והשירות היה מהיר."
)


def run(name: str, client: CachedModelClient) -> bool:
    try:
        t0 = time.time()
        first = client.complete(PROMPT)
        t_first = time.time() - t0
        hit_first = client.last_was_cache_hit

        t0 = time.time()
        second = client.complete(PROMPT)
        t_second = time.time() - t0
        hit_second = client.last_was_cache_hit

        ok = bool(first.strip()) and hit_second and first == second
        print(f"[{name}] response: {first.strip()!r}")
        print(
            f"[{name}] 1st call: {t_first:.2f}s (cache hit: {hit_first}) | "
            f"2nd call: {t_second:.3f}s (cache hit: {hit_second})"
        )
        print(f"[{name}] {'PASS' if ok else 'FAIL'}")
        return ok
    except Exception as e:  # noqa: BLE001
        print(f"[{name}] FAIL: {type(e).__name__}: {e}")
        return False


def main() -> int:
    load_dotenv()
    cache = SqliteResponseCache()
    results = [
        run("openai", CachedModelClient(OpenAIClient(), cache)),
        run("anthropic", CachedModelClient(AnthropicClient(), cache)),
    ]
    print("cache stats:", cache.stats())
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
