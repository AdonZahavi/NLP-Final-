"""OpenAI client implementing the ModelClient protocol (CONTRACT.md)."""

from __future__ import annotations

import os


class OpenAIClient:
    """Contract model key: "gpt-4" (results/<condition>/<task>_gpt-4.jsonl)."""

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        from openai import OpenAI  # lazy import

        self.model = model
        self._client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])

    def complete(self, prompt: str, **params) -> str:
        params.setdefault("temperature", 0)
        params.setdefault("max_tokens", 256)
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        return resp.choices[0].message.content or ""
