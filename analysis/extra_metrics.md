# Supplementary metrics (reviewer-requested, report §5)

## QA token-F1 (SQuAD-style), all models × conditions

| model | raw | segmented | prompt_guided |
|---|---|---|---|
| gpt-4 | 0.723 | 0.617 | 0.736 |
| claude | 0.760 | 0.642 | 0.737 |
| llama-3.2 | 0.508 | 0.427 | 0.401 |
| mistral-7b | 0.498 | 0.444 | 0.471 |

## Space-insensitive QA EM: raw vs segmented, exact McNemar

| model | raw | segmented (space-insens.) | Δ | p |
|---|---|---|---|---|
| gpt-4 | 0.628 | 0.600 | −0.028 | 0.1405 |
| claude | 0.700 | 0.654 | −0.046 | 0.0128 |
| llama-3.2 | 0.366 | 0.292 | −0.074 | 0.0001 |
| mistral-7b | 0.330 | 0.332 | +0.002 | 1.0000 |

After correcting the spacing artifact, the segmented QA degradation is
statistically significant for only 2 of 4 models; GPT-4o's corrected drop is
not significant, and Mistral is flat.

## Gold label distributions (EDA)

- sentiment subset (n=500): pos 316 (63.2%), neg 154 (30.8%),
  off-topic 30 (6.0%). Majority-class baseline: 0.632 accuracy.
- nli gold test (n=884): entailment 307 (34.7%), neutral 289 (32.7%),
  contradiction 288 (32.6%). Majority-class baseline: 0.347.
- qa (n=500): answerable questions only, uniform sample.
