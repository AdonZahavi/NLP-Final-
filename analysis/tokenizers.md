# Tokenizer analysis (issue #14)

Fertility = subword tokens per whitespace word, measured on 300 sentiment examples (user-generated Hebrew).
`seg cost` = tokens of the SEGMENTED text per RAW word — the
total sequence-length cost of feeding YAP output to the model.
English baseline: simple news-register English text.

| tokenizer | Hebrew raw | Hebrew segmented (per seg word) | seg cost (per raw word) | English |
|---|---|---|---|---|
| gpt-4o (o200k) | 1.79 | 1.44 | 2.12 | 1.06 |
| llama-3.2 | 4.37 | 3.17 | 4.65 | 1.06 |
| mistral-7b | 4.59 | 3.51 | 5.15 | 1.09 |
| claude (API, sample) | 3.58 | 2.94 | 4.09 | 1.76 |

## Reading the table

- Hebrew raw fertility >> English fertility: every tokenizer
  already fragments Hebrew words into multiple pieces — the
  models never see whole Hebrew words, with or without YAP.
- If segmented fertility (per seg word) is close to 1-1.5, the
  tokenizers largely recognize the split morphemes as units,
  yet performance still DROPPED — evidence the harm is a
  distribution shift (unfamiliar spacing), not a tokenization
  failure.
- `seg cost` shows segmentation also lengthens sequences,
  raising compute/API cost for zero accuracy benefit.