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
        params.pop("temperature", None)
        params.pop("max_input_tokens", None)  # HF-client-only knob
        params.setdefault("max_tokens", 256)
        # claude-sonnet-5 thinks before answering; with small max_tokens the
        # thinking consumes the whole budget and the visible text is EMPTY.
        # Disable thinking (fall back gracefully if the API rejects it).
        try:
            resp = self._client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                thinking={"type": "disabled"},
                **params,
            )
        except Exception:  # noqa: BLE001 — older SDK/API without the param
            bigger = dict(params)
            bigger["max_tokens"] = max(params.get("max_tokens", 256), 1024)
            resp = self._client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **bigger,
            )
        text = "".join(b.text for b in resp.content if b.type == "text")
        if not text.strip():
            raise RuntimeError(
                "empty completion from Anthropic API (thinking consumed the "
                "token budget?) — not caching, will retry")
        return text
