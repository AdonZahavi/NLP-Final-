# Does Morphological Decomposition Still Help LLMs Understand Hebrew?

NLP Course Final Project, RUNI 2026.
Or Zahavi, Alon Kremerman, Rafael Yzgeav.

We compare LLM performance on Hebrew downstream tasks (sentiment, NLI, QA)
under three input conditions:

1. **raw** — unsegmented Hebrew text
2. **segmented** — morphologically segmented via YAP
3. **prompt_guided** — raw text + a prompt instruction to decompose
   morphology mentally (novel condition)

Models: GPT-4o, Claude, LLaMA 3.2 3B Instruct, Mistral 7B Instruct.
Scale: 4 models × 3 tasks × 3 conditions, ~22,600 predictions.
Total API spend: $10.65.

## Results at a glance

**The answer is no.** No intervention ever significantly outperforms raw
Hebrew for any model on any task. Explicit YAP segmentation significantly
degrades NLI (3 of 4 models) and QA under strict exact match (all 4; 2 of 4
after artifact correction); the prompt-guided instruction never helps and
significantly harms models across the capability range (GPT-4o and Mistral
on NLI; LLaMA most severely). Mechanistically, subword tokenizers already
fragment Hebrew far beyond English (fertility 1.8–4.6 vs ≈1.1 tokens/word),
so explicit morphology is redundant and acts as a distribution shift — while
costing 6–18% more tokens. Models: gpt-4o, claude-sonnet-5,
Llama-3.2-3B-Instruct, Mistral-7B-Instruct-v0.3 (August 2026).

Along the way we caught and corrected two evaluation artifacts: a QA
span-spacing artifact (models answering correctly in segmented spelling) and
a thinking-budget artifact (a reasoning model returning empty answers on
unfamiliar input because internal thinking consumed the token budget).

Full write-up: `report/report_final.docx` (+ PDF). Slides: `report/slides.pptx`.
Core tables: `analysis/comparison.md`. Flip analysis: `analysis/flips.md`,
`analysis/flip_annotations.md` (native-speaker verified). Tokenizer analysis:
`analysis/tokenizers.md`.

## Repo layout

```
data/                  raw datasets; fixed eval subsets in data/subsets/ (raw + segmented, checksummed)
segmentation/          YAP build/setup, segmentation scripts, gold-standard check
experiments/           prompt variants, pilot, winning instruction, Colab notebooks for GPU runs
src/heb_morph/         clients (OpenAI/Anthropic/HF + SQLite cache) and evaluation harness
scripts/               run_all.py (experiment orchestrator), summarize_results.py, repair/audit tools
results/               per-example predictions: results/<condition>/<task>_<model>.jsonl + summaries
analysis/              cross-condition comparison, McNemar tests, flip analysis, tokenizer fertility
report/                report (.docx/.pdf), slides (.pptx), video brief, rubric notes
tests/                 harness unit tests
```

## Reproducing

```bash
pip install -r requirements.txt
cp .env.example .env            # fill in your API keys (never commit .env)
PYTHONPATH=src python -m pytest tests/ -q

# run one experiment cell (resumable; responses cached in SQLite):
PYTHONPATH=src python scripts/run_all.py --condition raw --models gpt-4 --limit 20

# GPU models run on Colab: experiments/colab_issue10_segmented.ipynb etc.

# regenerate all analyses from the committed results:
PYTHONPATH=src python analysis/compare_conditions.py
PYTHONPATH=src python analysis/categorize_flips.py
```

Everything is deterministic: fixed seeded subsets (SEED=42, SHA-256
checksums in `data/subsets/checksums.txt`), greedy decoding, per-example
JSONL records containing the exact prompt and raw model output.
