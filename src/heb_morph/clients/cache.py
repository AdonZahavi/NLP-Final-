"""SQLite-backed response cache.

Implements the ResponseCache protocol from CONTRACT.md:

    get(model, prompt, params) -> str | None
    put(model, prompt, params, response) -> None

Guarantee: no identical (model, prompt, params) request is ever paid for twice.
The cache file lives in cache/ (gitignored).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

DEFAULT_CACHE_PATH = Path("cache") / "responses.sqlite"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS responses (
    key        TEXT PRIMARY KEY,
    model      TEXT NOT NULL,
    prompt     TEXT NOT NULL,
    params     TEXT NOT NULL,
    response   TEXT NOT NULL,
    created_at REAL NOT NULL
);
"""


def _cache_key(model: str, prompt: str, params: dict) -> str:
    payload = json.dumps(
        {"model": model, "prompt": prompt, "params": params},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class SqliteResponseCache:
    def __init__(self, path: str | Path = DEFAULT_CACHE_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def get(self, model: str, prompt: str, params: dict) -> str | None:
        row = self._conn.execute(
            "SELECT response FROM responses WHERE key = ?",
            (_cache_key(model, prompt, params),),
        ).fetchone()
        return row[0] if row else None

    def put(self, model: str, prompt: str, params: dict, response: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO responses VALUES (?, ?, ?, ?, ?, ?)",
            (
                _cache_key(model, prompt, params),
                model,
                prompt,
                json.dumps(params, sort_keys=True, ensure_ascii=False),
                response,
                time.time(),
            ),
        )
        self._conn.commit()

    def stats(self) -> dict:
        n, = self._conn.execute("SELECT COUNT(*) FROM responses").fetchone()
        per_model = dict(
            self._conn.execute(
                "SELECT model, COUNT(*) FROM responses GROUP BY model"
            ).fetchall()
        )
        return {"total": n, "per_model": per_model}
