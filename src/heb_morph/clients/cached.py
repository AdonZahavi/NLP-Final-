"""Cache-wrapping ModelClient: checks the cache before paying for an API call."""

from __future__ import annotations


class CachedModelClient:
    """Wraps any ModelClient with a ResponseCache (both protocols in CONTRACT.md).

    Usage:
        client = CachedModelClient(OpenAIClient(), SqliteResponseCache())
        text = client.complete(prompt)          # API call, cached
        text = client.complete(prompt)          # cache hit, free
    """

    def __init__(self, client, cache):
        self._client = client
        self._cache = cache
        self.model = client.model
        self.last_was_cache_hit: bool = False

    def complete(self, prompt: str, **params) -> str:
        cached = self._cache.get(self.model, prompt, params)
        if cached is not None:
            self.last_was_cache_hit = True
            return cached
        self.last_was_cache_hit = False
        response = self._client.complete(prompt, **params)
        self._cache.put(self.model, prompt, params, response)
        return response
