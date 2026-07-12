# Interface Contract (all lanes code against this)

## Prediction record (JSONL, one object per line)

```json
{
  "id": "string — stable example id within its dataset",
  "task": "sentiment | nli | qa",
  "model": "gpt-4 | claude | llama-3.2 | mistral-7b",
  "condition": "raw | segmented | prompt_guided",
  "input": "string — the exact text sent (post-templating)",
  "raw_output": "string — verbatim model response",
  "parsed_label": "string | null — null on parse failure",
  "gold": "string — gold label / answer"
}
```

Results live under `results/<condition>/` as `<task>_<model>.jsonl`.

## Model client interface (Lane B implements, Lane A's cache plugs in)

```python
class ModelClient(Protocol):
    def complete(self, prompt: str, **params) -> str: ...
```

## Cache interface (Lane A implements, Lane B consumes via injection)

```python
class ResponseCache(Protocol):
    def get(self, model: str, prompt: str, params: dict) -> str | None: ...
    def put(self, model: str, prompt: str, params: dict, response: str) -> None: ...
```

## Directory ownership (do not write outside your lane)

| Lane | Issue | Owns |
|------|-------|------|
| A | #2  | `src/heb_morph/clients/`, `scripts/` |
| B | #7  | `src/heb_morph/harness/`, `tests/harness/` |
| C | #8  | `experiments/prompts.md` |
| D | #12 | `src/heb_morph/analysis/`, `tests/analysis/`, `tests/fixtures/` |

Shared namespace package: `src/heb_morph/` (PEP 420, no top-level `__init__.py` conflicts —
each lane creates only its own subpackage).

## Dependencies

Each lane records its deps in `requirements-<lane>.txt` (e.g. `requirements-a.txt`)
at repo root. They get merged into one `requirements.txt` at integration.

## Tasks and label spaces

- sentiment: labels `positive | negative | neutral` (dataset: omilab/hebrew_sentiment)
- nli: labels `entailment | contradiction | neutral` (dataset: HebArabNlpProject/HebNLI, gold test set)
- qa: extractive span answers, metrics EM + token F1 (dataset: Etelis/HeQ_v1)
