# Morphological segmentation — tool choice (issue #5)

## Candidates

| | YAP (OnlpLab) | HebPipe (amir-zeldes) |
|---|---|---|
| Type | Go, lexicon-based joint morph-syntactic parser | Python pipeline, neural components |
| Install | git clone + `go build`; run `./yap api` (port 8000) | `pip install hebpipe` (separate venv! heavy pinned deps, ~2GB models on first run) |
| Platform | Linux/WSL/Colab recommended (painful on native Windows) | anywhere Python + torch runs |
| Interface | HTTP API (`/yap/heb/joint`), needs pre-tokenized input | CLI on text files, CoNLL-U output |

Fallback if both disappoint on our noisy sentiment text: DICTA's neural
segmenter (dictabert-seg on HuggingFace) — not in the proposal, but trivial to
run; document the deviation if used.

## Workflow

```bash
python segmentation/make_sample.py          # 50 sentences from the eval subsets
# terminal A: ./yap api                     # after building YAP
python segmentation/yap_client.py
python segmentation/hebpipe_runner.py       # in the hebpipe venv
python segmentation/compare_segmenters.py   # -> comparison.md + stats
```

The sample is drawn from our own eval subsets and biased toward
prefix-rich sentences (ו/ש/כש/ה/ל/ב/מ) so the comparison exercises the
phenomena from the proposal.

## Comparison rubric (fill after reviewing comparison.md)

| Criterion | YAP | HebPipe | Notes |
|---|---|---|---|
| Prefix detachment (ל/ב/מ, ש/ו, ה) | | | |
| Combined prefixes (וכש, ומש...) | | | |
| Pronominal suffixes (ביתו, ספריהם) | | | |
| Smichut NOT over-split | | | |
| Noisy social-media text (sentiment) | | | |
| Speed on 50 sentences | | | |
| Install/operational pain | | | |

## Decision

**Chosen tool:** _TBD after manual review_

**Rationale:** _TBD — cite agreement stats and rubric rows above. Reference
point: the omilab sentiment dataset ships a gold `morph` variant
(data/raw/morph_test.tsv); spot-check the chosen tool against it._

## Gold sanity check

`data/raw/morph_test.tsv` is expert-segmented text of the exact sentences in
`data/raw/token_test.tsv` — compare the chosen tool's output on a few sentiment
sentences against it before signing off (helps catch systematic errors, e.g.,
definite-article ה under-splitting after ל/ב).
