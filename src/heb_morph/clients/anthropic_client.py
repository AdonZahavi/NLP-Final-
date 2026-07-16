"""Anthropic client implementing the ModelClient protocol (CONTRACT.md)."""

from __future__ import annotations

import os


class AnthropicClient:
    """Contract model key: "claude" (results/<condition>/<task>_claude.jsonl)."""

    def __init__(self, model: str = "claude-sonnet-5", api_key: str | None = None):
        import anthropic  # lazy import

        self.model = model
        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ["ANTHROPIC_API_KEY"]
        )

    def complete(self, prompt: str, **params) -> str:
        params.setdefault("temperature", 0)
        params.setdefault("max_tokens", 256)
        resp = self._client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        return "".join(b.text for b in resp.content if b.type == "text")
