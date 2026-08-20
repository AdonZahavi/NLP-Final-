# Project Background — Catch-Up for Team Members

Everything you need to understand, explain, and defend this project — even if
you weren't in the day-to-day. Read this, then the report
(`report/report_draft.docx`), and you're fully up to speed.

---

## 1. The linguistic background (why Hebrew is special)

Hebrew is a *morphologically rich language*: one written word often packs
several grammatical units together. The word וכשהלכתי is four units in one:
ו (and) + כש (when) + הלכ (walked) + תי (I) — an entire English clause.
Prefixes like ו, ש, ה, ל, ב, מ, כש attach to the front of words; pronoun
suffixes attach to the end (ביתו = "his house" = בית + his); and construct
state (סמיכות) chains nouns together.

Because of this, Hebrew NLP historically had a golden rule: **before any
model touches the text, run a morphological analyzer that splits every word
into its morphemes**. The standard open-source tool for this is **YAP**
(Yet Another Parser, Open University / ONLP lab). This preprocessing step
was considered mandatory for ~30 years.

## 2. The question we asked

Modern LLMs (GPT, Claude, LLaMA, Mistral) read text through **subword
tokenizers** (BPE): they automatically break every word into learned
sub-pieces, trained on raw, unsegmented internet text. So:

- **RQ1:** Does explicit morphological segmentation *still* improve LLM
  performance on Hebrew tasks — or do LLMs already handle morphology
  internally?
- **RQ2 (our novel idea):** Instead of preprocessing, can we just *tell* the
  model in the prompt "Hebrew words bundle prefixes and suffixes — mentally
  decompose each word before answering"? If prompting could substitute for
  a preprocessing pipeline, that would be a much cheaper alternative.

## 3. What we built

A 4 × 3 × 3 experiment grid:

- **4 models:** GPT-4o and Claude (commercial APIs), LLaMA 3.2 3B and
  Mistral 7B (open weights, run ourselves on a Colab GPU).
- **3 tasks:** sentiment analysis (Facebook comments about Israel's
  president — labels are positive/negative/off-topic), NLI (does a premise
  entail a hypothesis — 884 human-verified pairs), and extractive QA
  (answer a question by copying a span from a Hebrew Wikipedia paragraph).
- **3 conditions:** **raw** (text as written), **segmented** (same text
  pre-split by YAP into morphemes), **prompt_guided** (raw text + the
  morphology instruction — our RQ2).

Everything else is held identical — same 1,884 examples per model per
condition, same prompts, deterministic (greedy) decoding, answers parsed
strictly. ~22,600 predictions total. Every single prediction is saved with
its exact prompt and raw model output, all API calls are cached (never pay
twice), and every run is resumable after a crash. Total API cost: $10.65.

The prompt instruction for RQ2 wasn't arbitrary: we wrote 5 variants and
piloted them on held-out dev data (never the test set); the best variant
(a rich linguistic explanation) was used for all main runs.

## 4. What happened along the way (the war stories)

Worth knowing because they show the project's rigor — and they come up in
the report and video:

- **YAP was hard to build** (old Go code) and its segmentation isn't
  perfect: validated against a gold standard, it gets 0.875 token-F1;
  we documented its error classes.
- **Colab fought us**: GPU quota cuts, out-of-memory crashes (Mistral barely
  fits a T4), VM recycles. The crash-safe, resumable pipeline meant we never
  lost a single completed prediction through all of it.
- **Our evaluation lied to us twice — and we caught it both times:**
  1. *QA spacing artifact:* under segmentation, QA scores seemed to collapse
     (GPT-4o 0.628 → 0.424 exact match). Inspecting outputs showed models
     answering CORRECTLY but in segmented spelling (ב ירושלים vs בירושלים) —
     our scorer was punishing the spaces we ourselves inserted. Rescoring
     space-insensitively: 0.424 → 0.600. ~80% of the "collapse" was fake.
  2. *Thinking-budget artifact:* Claude first looked devastated by
     segmentation (−18.8 NLI points). But Claude is a reasoning model — on
     unusual input it "thought" so long it consumed its whole answer-token
     budget and returned EMPTY answers (26.2% of segmented NLI vs 5.3% raw),
     which scored as errors. After disabling thinking and re-running, the
     real drop is only −2.3 points. Bonus insight: manipulated input made
     the model measurably think harder.

## 5. The findings (the corrected, final numbers)

1. **Raw Hebrew wins everywhere.** No model on any task is significantly
   improved by either intervention. Segmentation significantly hurts NLI
   for 3 of 4 models (all 4 directionally) and QA for all 4; sentiment is
   unaffected.
2. **Harm scales inversely with model strength.** Frontier models lose a
   little (GPT-4o −3.8, Claude −2.3 NLI points); small models lose more —
   and the prompt instruction is LLaMA's *worst* condition (−8.3 NLI,
   −11.4 QA, p<0.0001). The instruction was tuned on GPT-4o and doesn't
   transfer down: prompt scaffolding is model-dependent.
3. **RQ2 answer: prompting can't substitute** — because there's nothing to
   substitute, and the instruction itself can hurt.
4. **The mechanism (tokenizer analysis):** English ≈ 1.06 tokens/word;
   Hebrew is 1.79 (GPT-4o), 3.58 (Claude), ~4.4–4.6 (LLaMA/Mistral — near
   character level). Models never see whole Hebrew words anyway; their
   tokenizer already "segments", just not on linguistic lines. Explicit
   segmentation adds no information, shifts the input away from the training
   distribution, and makes inputs 12–20% longer (= more cost).
5. **Flip analysis:** examples that changed from right→wrong under
   segmentation are morphologically *ordinary* on NLI/QA — the damage is a
   uniform distribution shift, not confusion on hard morphology. We verified
   4 qualitative examples by hand (a meaning-changing split, a destroyed
   content word, a mangled celebrity name, and a perfectly-segmented example
   that still flipped).

**One-line conclusion: feed LLMs raw Hebrew. The preprocessing wisdom of the
statistical era does not transfer to LLMs — "helping" them with linguistic
structure can actively hurt.**

## 6. Questions you might be asked (and answers)

- *"Maybe YAP's errors, not segmentation itself, caused the harm?"* —
  Partially possible (0.875 F1 vs gold), but the flip analysis shows damage
  is uniform, not concentrated where segmentation is wrong; and the
  perfectly-segmented control example still flipped.
- *"Maybe your prompt for the segmented condition was bad?"* — The only
  addition was one explanatory sentence; task templates were identical
  across conditions by design, so differences are attributable to the input.
- *"Why only one prompt formulation per condition?"* — Cost control; we
  mitigated with a 5-variant pilot on dev data. Listed as a limitation.
- *"Is the QA result trustworthy given the artifact?"* — We report both
  scorings (strict and space-insensitive) and base conclusions on the
  corrected one.
- *"Why these models?"* — Two frontier APIs + two small open models spans
  the capability range and lets us test whether weaker models benefit more
  (they don't — they're hurt more).
- *"Could fine-tuning change the answer?"* — Out of scope (zero-shot by
  design); plausible future work, noted in the report.

## 7. Where everything lives

- Report: `report/report_draft.docx` / `.pdf` · Slides: `report/slides.pptx`
- Video guide: `report/video_brief.docx` (has a slide-by-slide timing map)
- All numbers: `analysis/comparison.md` · Flips: `analysis/flips.md`,
  `analysis/flip_annotations.md` · Tokenizers: `analysis/tokenizers.md`
- Repo: https://github.com/AdonZahavi/NLP-Final-
