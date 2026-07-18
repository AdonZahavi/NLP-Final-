# Issue #8 — Prompt-guided morphology instruction: variants and pilot

The `prompt_guided` condition prepends a morphology instruction to the same
task template used by `raw`. This file documents the candidate instructions,
the pilot protocol, and the pilot results that selected the winner.

## Design constraints

Only the instruction prefix varies between variants — the task template,
answer format, and parser are identical (see `src/heb_morph/harness/prompts.py`),
so any pilot difference is attributable to the instruction itself.
The winning instruction is written to `experiments/winning_instruction.txt`
and passed to the runner via `--morph-instruction-file` for all main runs.

## Pilot protocol (no tuning on test data)

Variants are compared on dev slices **disjoint from the fixed eval subsets**:

- **sentiment**: 50 examples (20 pos / 20 neg / 10 off-topic) sampled with
  SEED=42 from `token_test.tsv` rows NOT in `data/subsets/sentiment_500.jsonl`.
- **nli**: 50 examples from the HebNLI **validation** split (`HebNLI_val.jsonl`);
  the eval subset uses the test split, so overlap is impossible.
- **qa**: excluded from the pilot — the span-copy answer format is unchanged by
  the instruction, and the two classification tasks are cheaper, more sensitive
  probes. The winner is applied to QA unchanged in the main runs.

Slices are deterministic and committed under `experiments/dev_slices/`.
Pilot model: GPT-4o (cheap, capable; one model to avoid tuning per-model).
Baseline: the same dev slices under the `raw` condition, for reference.
Selection: highest mean accuracy across the two tasks; ties break toward the
simpler (earlier-numbered) variant.

Run: `PYTHONPATH=src python experiments/pilot_prompts.py --model gpt-4`
(add `--mock` for a no-API dry run).

## Variants

Full text in `experiments/prompt_variants.py`.

### v1_brief — minimal note
One sentence listing the common clitic prefixes (ו, ש, ה, ל, ב, מ, כש) and
pronominal suffixes, asking the model to "mentally decompose each word into
its morphemes" before reasoning. This is also `DEFAULT_MORPH_INSTRUCTION`
in the harness. Hypothesis: a light nudge is enough; minimal prompt overhead.

### v2_linguistic — rich linguistic framing
A short lesson: Hebrew as a morphologically rich language, a worked lexical
example (וכשהלכתי = ו+כש+הלכ+תי), the full prefix inventory with glosses, and
suffix examples (ביתו = בית + שלו). Hypothesis: more explicit knowledge
activation helps smaller models (LLaMA/Mistral) most.

### v3_worked_example — example-driven
Minimal explanation; instead shows one full decomposition of a two-word
phrase with glosses and says "apply this kind of decomposition mentally."
Hypothesis: demonstration beats description.

### v4_hebrew — instruction in Hebrew
Same content as v1 but written in Hebrew (אותיות שימוש, כינויי שייכות).
Hypothesis: matching the instruction language to the text language may prime
Hebrew processing; risk: weaker instruction-following in Hebrew for some models.

### v5_decompose_first — explicit two-step output
Asks the model to first (silently, but in practice in its output) rewrite the
text morpheme-by-morpheme, then answer; final answer must be the last line.
Needs a larger max_tokens budget (250) and last-line parsing. This is the
closest prompt-only analogue of the `segmented` condition — the model produces
its own segmentation. Hypothesis: strongest effect, but highest cost and
parse-failure risk.

## Results

(Appended automatically by `pilot_prompts.py`.)

## Pilot results (model: gpt-4, 50 dev examples/task)

| variant | sentiment acc | sentiment F1 | nli acc | nli F1 | parse fails |
|---|---|---|---|---|---|
| baseline_raw | 0.780 | 0.733 | 0.820 | 0.813 | 0 |
| v1_brief | 0.820 | 0.773 | 0.800 | 0.778 | 0 |
| v2_linguistic **← winner** | 0.820 | 0.769 | 0.820 | 0.795 | 0 |
| v3_worked_example | 0.800 | 0.754 | 0.760 | 0.734 | 0 |
| v4_hebrew | 0.800 | 0.749 | 0.780 | 0.758 | 0 |
| v5_decompose_first | 0.720 | 0.646 | 0.760 | 0.725 | 0 |
