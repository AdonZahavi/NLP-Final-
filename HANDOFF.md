# Project Handoff — Hebrew Morphological Decomposition & LLMs

**Last updated:** July 16, 2026
**Repo:** AdonZahavi/NLP-Final- | **Proposal:** see project PDF / README summary

We're testing whether explicit morphological segmentation still helps LLMs on Hebrew tasks (sentiment / NLI / QA), across three input conditions — **raw**, **segmented** (YAP/HebPipe), and **prompt_guided** (novel: instruct the model to decompose morphology itself) — on GPT-4o, Claude Sonnet 5, LLaMA 3.2, and Mistral 7B.

## How we work

- **One branch per GitHub issue** (`issue-N-short-name`), merged via PR. The full issue list with dependencies lives in the repo's GitHub Issues (16 issues).
- **CONTRACT.md is the source of truth** for interfaces: the prediction-record JSONL schema, `ModelClient`/`ResponseCache` protocols, and per-lane directory ownership under `src/heb_morph/`. Read it before writing code.
- Lane-specific deps go in `requirements-<lane>.txt`, merged into `requirements.txt` at integration.
- Results land in `results/<condition>/<task>_<model>.jsonl` — per-example records, never just aggregate scores.

## Setup (5 minutes)

```bash
python -m venv .venv && .venv\Scripts\activate      # or source .venv/bin/activate
pip install -r requirements.txt -r requirements-a.txt
copy .env.example .env                               # fill in your own keys — NEVER commit .env
python scripts/smoke_test.py                         # verifies OpenAI + Anthropic + cache
python scripts/check_hf_access.py                    # verifies HF gated-model access
python scripts/explore_datasets.py                   # downloads datasets, regenerates data/README.md
```

## Done so far

**Issue #1 — Scaffolding (merged).** Folder structure, `requirements.txt`, `.gitignore`, README, `.env.example`.

**Issue #2 — API access + cost guards (merged).** `src/heb_morph/clients/`: OpenAI + Anthropic clients (contract `ModelClient` protocol), SQLite response cache + `CachedModelClient` wrapper — **every API call goes through the cache, no prompt is ever paid for twice**. Smoke tests pass in Hebrew for both APIs; HF access confirmed for LLaMA 3.2 1B/3B and Mistral 7B v0.3. Cost estimate (`scripts/estimate_costs.py`): **~$23–26 total** for 9,000 paid calls (500 examples × 3 tasks × 3 conditions × 2 API models, July 2026 prices). Note: Claude Sonnet 5 rejects the `temperature` param (deprecated) — the Anthropic client strips it.

**Issue #3 — Datasets (this branch).** `scripts/explore_datasets.py` downloads and validates all three benchmarks and auto-generates `data/README.md` with label distributions, text lengths, and quality checks. Verified counts:

| Task | Dataset | Splits | Notes |
|------|---------|--------|-------|
| sentiment | omilab/hebrew_sentiment | 10,244 train / 2,560 test | pos 66.5% / neg 30.6% / off-topic 2.9% |
| nli | HebArabNlpProject/HebNLI | 300K train / 2K val / **884 gold test** | balanced 3-way; eval on gold test only |
| qa | Etelis/HeQ_v1 | 27,142 / 1,501 / 1,504 | SQuAD-style, long contexts |

## Gotchas (read before coding)

1. **Sentiment labels are 0=pos, 1=neg, 2=off-topic — NOT neutral.** The proposal says positive/negative/neutral; prompts must say "off-topic". Heavy imbalance → macro-F1 + stratified sampling in issue #4.
2. **hebrew_sentiment can't be loaded with `datasets>=3`** (legacy loading script). We pull raw TSVs from the omilab GitHub repo. Bonus: its `morph` variant is gold pre-segmented morphemes — a free reference for issue #6 segmentation QA.
3. **HebNLI Hebrew text is in `translation1`/`translation2`** (label in `hebrew_label`/`original_label` — the explore script auto-detects). Train is machine-translated; only the 884-pair test set is human-verified.
4. **Keys:** each member uses their own `.env` (copy from `.env.example`). Keys were never committed — keep it that way.
5. `data/raw/`, `cache/`, `.env` are gitignored. Committed data lives in `data/subsets/` (issue #4).

## Next up (dependency order)

- **#4 Fixed eval subsets** (~500/task, stratified, fixed seed; likely all 884 for NLI) — unblocks most things
- **#5 YAP vs HebPipe** comparison → **#6 segment the subsets**
- **#7 evaluation harness** (Lane B) → **#8 prompt variants** (Lane C) → **#9–11 experiment runs**
- **#12–14 analysis** (Lane D; #14 tokenizer analysis can start any time after #4)
- **#15 report → #16 slides/video**

#5 and #7 are independent of each other — good candidates for parallel work.
