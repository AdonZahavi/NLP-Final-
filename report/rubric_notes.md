# Report planning notes (from course rubric + exemplar projects)

## Course template (inferred from the two exemplar reports: AMI 2023, Hebrew Sentence BERT 2024)

~8 pages, paper-style PDF. Title + authors with IDs + "Submitted as final project
report for the NLP course, RUNI, 2026". Sections:

1. Introduction — problem statement, motivation, research questions (RQ1/RQ2 style)
2. Related Works
3. Datasets — with EDA (label distributions, length stats)
4. Solution / Experimental design — approach, code structure, platform (Colab/API), design decisions
5. Experiments & Results — numbered tables, per-experiment setup
6. Discussion — including failure/error analysis, limitations
7. Conclusion
8. References + GitHub link (footnote on page 1 in both exemplars)

## Grading rubric → what we must nail

- 15% problem definition — proposal framing is strong; state RQ explicitly:
  RQ1 does explicit segmentation still help LLMs? RQ2 can prompting substitute
  for pipeline segmentation? (RQ2 = our novelty)
- 5%  related work — NOT in any GitHub issue; must add. Cover: YAP/Hebrew
  morphological analysis, Hebrew PLMs (AlephBERT, DictaBERT — trained around
  exactly this segmentation question), subword tokenization in MRLs, prompting
  as linguistic scaffolding.
- 20% results & analysis — issues #12–14: deltas per model×task, McNemar
  significance, flip analysis (helpful/harmful), morphological-phenomenon
  categorization, tokenizer/fertility analysis.
- 10% methodology — report the engineering rigor: fixed seeded subsets with
  checksums, identical subset across conditions, response caching, greedy
  decoding, no tuning on test data (pilot on disjoint dev slices).
- 20% novelty — prompt-guided morphology condition; pilot finding that forcing
  explicit decomposition (v5) HURT GPT-4o is a headline nonobvious result.
- 10% report clarity, 5% presentation, 15% general impression.

## Known corrections to state explicitly in the report

- omilab/hebrew_sentiment label 2 = OFF-TOPIC (proposal said "neutral") — found
  during exploration, subsets stratified accordingly (min 30 off-topic).
- Proposal said "YAP or HebPipe"; HebPipe was unusable (dependency rot:
  TransfoXLTokenizer removed from transformers) → YAP chosen; gold check on
  morph_test.tsv: 30.8% exact / 0.875 token-F1, differences mostly punctuation
  conventions + covert-ה normalization; real YAP error class documented
  (e.g. בהצלחה → ב ה הצלחה).

## Video (5 min) outline

~1 min RQ + motivation, ~1 min conditions/setup diagram, ~2 min results
(delta table + 1–2 striking flip examples), ~1 min conclusions + limitations.
