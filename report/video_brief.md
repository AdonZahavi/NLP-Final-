# 5-Minute Video — Briefing for Alon & Rafael

Everything you need to prepare the video: the project story in 2 minutes of
reading, a minute-by-minute script skeleton with the exact numbers, what to
show on screen, and production tips. The full details are in
`report/report_draft.docx` — read it once before recording.

---

## The project in one paragraph (know this cold)

For decades, Hebrew NLP required morphological segmentation as preprocessing:
splitting words like וכשהלכתי into ו + כש + הלכתי before any model touches
the text. We asked whether modern LLMs still need this. We evaluated 4 models
(GPT-4o, Claude, LLaMA 3.2 3B, Mistral 7B) on 3 Hebrew tasks (sentiment, NLI,
question answering) under 3 input conditions: **raw** text, **YAP-segmented**
text, and a novel **prompt-guided** condition where we instruct the model to
mentally decompose Hebrew words. ~22,600 predictions total. **The answer is
no**: raw Hebrew wins everywhere, segmentation significantly *hurts* (on NLI:
three of four models, all four directionally), and the prompting trick
doesn't help either. The
reason: LLM tokenizers already split Hebrew into subword pieces, so explicit
morphology is redundant — it just makes the text look unlike anything the
model saw in training.

## The three punchiest facts (use them verbatim)

1. **Our evaluation lied to us TWICE — and we caught it both times.**
   (a) QA looked like it collapsed under segmentation (GPT-4o: 0.628→0.424
   exact match), but models were answering correctly *in segmented spelling*
   (ב ירושלים vs בירושלים); space-insensitive scoring recovers most of it
   (0.424→0.600). (b) Claude first looked devastated by segmentation (−18.8
   NLI points) — but it's a reasoning model, and unusual input made it THINK
   so long it ran out of answer tokens, returning empty responses (26.2% on
   segmented NLI vs 5.3% raw). After disabling thinking, the real drop is
   only −2.3 points. Frame this as detective work — it's the best story in
   the project.
2. **No model benefits, and small models are hurt most by the prompting
   trick**: LLaMA loses 8.3 NLI points and 11.4 QA points under the
   morphology instruction (both p<0.0001) — the instruction was tuned on
   GPT-4o and doesn't transfer down. Segmentation significantly degrades NLI
   for 3 of 4 models; sentiment is unaffected for all.
3. **The mechanism**: tokenizer fertility. English ≈ 1.06 tokens/word.
   Hebrew: GPT-4o 1.79, Claude 3.58, LLaMA/Mistral ≈ 4.4–4.6 (near character
   level). The models never see whole Hebrew words anyway — their tokenizer
   already "segments". And YAP segmentation makes inputs 12–20% longer, so it
   costs more money for worse accuracy.

---

## Minute-by-minute script skeleton

### 0:00–0:50 — The question (hook first, then setup)
- Open with the example: write וכשהלכתי on screen, break it apart live:
  "one Hebrew word — an entire English clause: *and-when-I-walked*."
- "For 30 years, Hebrew NLP said you MUST split words like this before a
  model can understand them. We asked: do LLMs still care?"
- State RQ1 (does segmentation still help?) and RQ2 (can prompting replace
  it? — our novel condition).

### 0:50–1:50 — What we did (the experiment matrix)
- Show the 4×3×3 matrix graphic: 4 models × 3 tasks × 3 conditions.
- One sentence per condition; show the SAME example sentence rendered three
  ways (raw / segmented / raw+instruction) — this visual carries the minute.
- Mention scale + rigor fast: "identical fixed subsets for every cell,
  ~22,600 predictions, greedy decoding, everything cached and reproducible
  on GitHub."
- Mention the pilot: 5 instruction variants tested on held-out dev data
  (never on test), winner used everywhere.

### 1:50–3:20 — Results (the core; spend the most time here)
- Show the NLI table (Table 3 in the report). Punch line: "no model got
  better — three of four got significantly worse."
- The two-artifacts detective story (fact #1 above) — spend ~40 seconds here;
  it demonstrates rigor better than anything else.
- Prompt-guided verdict: "for the frontier models — nothing. For LLaMA — its
  worst condition. Prompting can't substitute for segmentation because
  there's nothing to substitute, and the instruction itself can hurt."

### 3:20–4:20 — Why (the mechanism)
- Tokenizer fertility table (Table 6). Show English 1.06 vs Hebrew numbers.
- "The tokenizer already segments — just not along linguistic lines. Adding
  YAP's segmentation doesn't inform the model; it makes Hebrew look like
  text it never saw in training. It's a distribution shift, and we showed
  the damage is uniform, not concentrated in morphologically hard examples."
- Cost angle: "and it makes every request 12–20% more expensive."

### 4:20–5:00 — Conclusion
- "The answer to our title: no. Feed LLMs raw Hebrew."
- One nuance sentence: "the one hint of benefit was small models on
  sentiment — not significant, but the right direction for future work."
- Close: "preprocessing wisdom from the statistical era doesn't transfer to
  LLMs — and 'helping' them with linguistic structure can actively hurt."
- End slide: names, GitHub link.

---

## What to show on screen (slides/visuals checklist)

1. Title slide (title, names, course).
2. וכשהלכתי decomposition animation/build.
3. 4×3×3 matrix graphic.
4. Same sentence in 3 conditions (side by side).
5. NLI results table (from report Table 3) — highlight the Δ column in red.
6. QA artifact before/after bar pair (0.424 vs 0.600, next to raw 0.628).
7. Tokenizer fertility bar chart (English vs 4 models) — most intuitive
   visual in the project; build it from report Table 6.
8. Conclusion slide with the one-line answer.

## Production tips

- 5 minutes ≈ 700–750 spoken words. The skeleton above fits; time yourselves
  per section and cut words, not content.
- Record narration over slides (screen recording is fine); no need to appear
  on camera unless the course requires it.
- Numbers on slides, sentences in narration — never read a table aloud.
- Rehearse the Hebrew example out loud once; it's the opening hook.
- Export 1080p, check audio levels, keep a 5–10 second buffer under the
  limit (4:50 is safer than 5:05).

## Where everything lives

- Full report: `report/report_draft.docx`
- All result tables: `analysis/comparison.md`
- Tokenizer table: `analysis/tokenizers.md`
- Flip analysis + Hebrew examples: `analysis/flips.md`, `analysis/flip_examples.md`
- Prompt variants + pilot: `experiments/prompts.md`
- Repo: https://github.com/AdonZahavi/NLP-Final-
