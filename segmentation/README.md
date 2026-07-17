# Morphological segmentation — tool choice (issue #5)

## Candidates

| | YAP (OnlpLab) | HebPipe (amir-zeldes) |
|---|---|---|
| Type | Go, lexicon-based joint morph-syntactic parser | Python, character-wise xgboost segmenter |
| Install | git clone + `go build`; run `./yap api` (port 8000) | `pip install rftokenizer` + `heb.sm3` model (auto-downloaded) |
| Platform | Linux/WSL/Colab recommended (painful on native Windows) | anywhere Python runs |
| Interface | HTTP API (`/yap/heb/joint`), needs pre-tokenized input | Python API, one word-form per item, pipe-separated output |

**Note on "HebPipe":** the full `hebpipe` package is unusable on modern stacks
(fails at import via its coref module, interactive model prompts, forced Stanza
pass). Its segmentation engine is **RFTokenizer** (same author, same `heb.sm3`
model; `heb_pipe.py -wt` just calls `rf_tokenize`), so `hebpipe_runner.py` runs
that component directly — segmentation output is identical to HebPipe's `-wt`.

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

## Comparison results (50 sentences, 564 shared tokens)

Token-level agreement: **70.4%** overall — sentiment 71.5%, NLI 63.6%, QA 75.0%.
Split rates: YAP segments 42.0% of tokens, RFTokenizer 57.0%.

| Criterion | YAP | HebPipe/RFTokenizer | Evidence (comparison.md) |
|---|---|---|---|
| Prefix detachment (ל/ב/מ, ש/ו, ה) | good, lexicon-backed | over-detaches heavily | RF: כל→כ+ל, מול→מ+ול, ממש→מ+מש, מאוד→מ+אוד, הצלחה→ה+צלחה |
| Proper names left intact | yes | no | RF: ביבי→ב+יבי, בוזי→ב+וזי |
| Verb templates not split as prefixes | mostly (one error: התברר→ה+תברר) | frequent errors | RF: מעריכה→מ+עריכה, מקובלת→מ+קובלת, מאוכזבים→מ+אוכזבים |
| Pronominal suffixes | normalized to base pronoun (בך→ב+אתה) | mixed: whole (אותך) or surface (ל+ך); error ש+לך | design difference, see note below |
| Covert definite article | reconstructed (במקום→ב+ה+מקום) | surface only (ב+מקום) | design difference |
| Noisy social-media text | robust | weakest here (most spurious splits are in sentiment sentences) | rows 1–8 of the table |
| Speed on 50 sentences | minutes (server + joint parse) | seconds | |
| Install/operational pain | high (Go, GOPATH, vendored deps, 6GB RAM server) | trivial (`pip install rftokenizer`) | see colab notebook |

## Decision

**Chosen tool: YAP.**

**Rationale:** RFTokenizer's spurious prefix detachments (57% split rate vs.
YAP's 42%) corrupt ordinary words and proper names — exactly the noise we must
not inject into the *segmented* experimental condition, since it would confound
"morphological decomposition" with "text corruption". YAP's errors are rarer and
of a different kind: occasional wrong disambiguation (התברר→ה+תברר) and two
systematic *normalizations* that are linguistically informative rather than
wrong: it reconstructs the covert definite article (ב+ה+מקום) and maps
pronominal suffixes to base pronouns (בך→ב+אתה). Both must be documented in the
report as properties of the segmented condition (the segmented text is a
morphological analysis, not a pure surface split). Operational cost (Colab-only,
slow) is acceptable: issue #6 runs it once over ~1,900 fixed examples.

Caveat for fairness: our RFTokenizer runs fed it punctuation-split tokens
without HebPipe's own whitespace_tokenize conventions, which may hurt it
somewhat; the observed failure pattern (prefix-lookalike over-splitting on
OOV/names) is nonetheless inherent to its character-windowed approach.

**Follow-up before closing issue #6:** spot-check YAP output against the gold
morph variant of the sentiment data (data/raw/morph_test.tsv) on ~20 sentences,
and have a Hebrew speaker skim comparison.md to confirm the table above.

## Gold sanity check

`data/raw/morph_test.tsv` is expert-segmented text of the exact sentences in
`data/raw/token_test.tsv` — compare the chosen tool's output on a few sentiment
sentences against it before signing off (helps catch systematic errors, e.g.,
definite-article ה under-splitting after ל/ב).
