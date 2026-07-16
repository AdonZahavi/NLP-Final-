# Does Morphological Decomposition Still Help LLMs Understand Hebrew?

NLP Course Final Project, RUNI 2026.
Or Zahavi, Alon Kremerman, Rafael Yzgeav.

We compare LLM performance on Hebrew downstream tasks (sentiment, NLI, QA) under three input conditions:

1. **raw** — unsegmented Hebrew text
2. **segmented** — morphologically segmented via YAP/HebPipe
3. **prompt_guided** — raw text + a prompt instruction to decompose morphology mentally (novel condition)

Models: GPT-4, Claude, LLaMA 3.2 Instruct, Mistral 7B Instruct.

## Repo layout

```
data/                  datasets; fixed eval subsets in data/subsets/ (raw + segmented)
segmentation/          YAP/HebPipe setup, comparison, and segmentation scripts
experiments/         