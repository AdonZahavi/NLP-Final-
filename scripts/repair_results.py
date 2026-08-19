"""Repair result files: remove duplicate records and empty-output records.

Two bugs corrupted some Claude/GPT-4 result files:
1. Concurrent/restarted API sweeps appended DUPLICATE records (same id).
2. Claude returned EMPTY completions (thinking consumed the max_tokens
   budget); these were saved and cached, silently scoring as wrong.

This script rewrites every results/<condition>/<task>_<model>.jsonl keeping
ONE record per id (preferring a non-empty raw_output; last occurrence wins
among equals) and DROPPING records whose raw_output is empty — so a normal
runner invocation afterwards re-runs exactly the missing examples.

It also purges empty responses from the SQLite response cache.

Usage (from repo root):  python scripts/repair_results.py
Then re-run the affected sweeps, e.g.:
    PYTHONPATH=src python scripts/run_all.py --condition raw --models claude
    PYTHONPATH=src python scripts/run_all.py --condition segmented --models claude
    PYTHONPATH=src python scripts/run_all.py --condition prompt_guided --models claude,gpt-4
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def repair_file(path: Path) -> tuple[int, int, int]:
    recs = [json.loads(l) for l in open(path, encoding="utf-8")]
    best: dict = {}
    order: list = []
    for r in recs:
        i = r["id"]
        if i not in best:
            order.append(i)
            best[i] = r
        else:
            old_empty = not (best[i]["raw_output"] or "").strip()
            new_empty = not (r["raw_output"] or "").strip()
            if old_empty or not new_empty:  # prefer non-empty; else newest
                best[i] = r
    kept = [best[i] for i in order
            if (best[i]["raw_output"] or "").strip()]
    dropped_empty = len(order) - len(kept)
    dups = len(recs) - len(order)
    if dups or dropped_empty:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in kept:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(recs), dups, dropped_empty


def purge_cache_empties() -> None:
    db = ROOT / "cache" / "responses.sqlite"
    if not db.exists():
        print("no cache db found — skipping cache purge")
        return
    con = sqlite3.connect(db)
    try:
        # find the table and response column generically
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        purged = 0
        for t in tables:
            cols = [c[1] for c in con.execute(f"PRAGMA table_info({t})")]
            resp_col = next((c for c in cols if "resp" in c.lower()
                             or "value" in c.lower() or "output" in c.lower()),
                            None)
            if resp_col:
                cur = con.execute(
                    f"DELETE FROM {t} WHERE TRIM({resp_col}) = ''")
                purged += cur.rowcount
        con.commit()
        print(f"cache: purged {purged} empty responses")
    finally:
        con.close()


def main() -> None:
    total_dups = total_empty = 0
    for path in sorted((ROOT / "results").glob("*/*.jsonl")):
        n, dups, empty = repair_file(path)
        total_dups += dups
        total_empty += empty
        if dups or empty:
            print(f"{path}: {n} records -> removed {dups} duplicates, "
                  f"dropped {empty} empty")
    print(f"\ntotal: {total_dups} duplicates removed, "
          f"{total_empty} empty records dropped (will be re-run)")
    purge_cache_empties()


if __name__ == "__main__":
    main()
