# Cross-condition comparison (issue #12)

Primary metric: accuracy (sentiment/NLI), exact match (QA).
Deltas are vs the raw baseline. p-values: exact two-sided
McNemar test on paired predictions; `*` p<0.05, `**` p<0.001.

## sentiment (accuracy)

| model | raw | segmented | Δseg | p(seg) | prompt_guided | Δpg | p(pg) |
|---|---|---|---|---|---|---|---|
| gpt-4 | 0.734 | 0.730 | -0.004 | 0.8746 | 0.748 | +0.014 | 0.2649 |
| claude | 0.822 | 0.814 | -0.008 | 0.5572 | 0.752 | -0.070 | **<0.0001** |
| llama-3.2 | 0.718 | 0.732 | +0.014 | 0.5341 | 0.740 | +0.022 | 0.2997 |
| mistral-7b | 0.752 | 0.744 | -0.008 | 0.5716 | 0.756 | +0.004 | 0.8450 |

## nli (accuracy)

| model | raw | segmented | Δseg | p(seg) | prompt_guided | Δpg | p(pg) |
|---|---|---|---|---|---|---|---|
| gpt-4 | 0.885 | 0.846 | -0.038 | **0.0002** | 0.860 | -0.025 | *0.0022* |
| claude | 0.876 | 0.688 | -0.188 | **<0.0001** | 0.641 | -0.235 | **<0.0001** |
| llama-3.2 | 0.459 | 0.431 | -0.028 | 0.1388 | 0.377 | -0.083 | **<0.0001** |
| mistral-7b | 0.514 | 0.464 | -0.050 | **<0.0001** | 0.479 | -0.035 | *0.0032* |

## qa (EM)

| model | raw | segmented | Δseg | p(seg) | prompt_guided | Δpg | p(pg) |
|---|---|---|---|---|---|---|---|
| gpt-4 | 0.628 | 0.424 | -0.204 | **<0.0001** | 0.653 | +0.025 | 0.1934 |
| claude | 0.652 | 0.432 | -0.220 | **<0.0001** | 0.611 | -0.041 | *0.0066* |
| llama-3.2 | 0.366 | 0.280 | -0.086 | **<0.0001** | 0.252 | -0.114 | **<0.0001** |
| mistral-7b | 0.330 | 0.266 | -0.064 | *0.0027* | 0.332 | +0.002 | 1.0000 |

## Macro-F1 (classification tasks)

| model | task | raw | segmented | prompt_guided |
|---|---|---|---|---|
| gpt-4 | sentiment | 0.622 | 0.612 | 0.620 |
| gpt-4 | nli | 0.884 | 0.846 | 0.860 |
| claude | sentiment | 0.669 | 0.667 | 0.624 |
| claude | nli | 0.898 | 0.783 | 0.756 |
| llama-3.2 | sentiment | 0.559 | 0.579 | 0.522 |
| llama-3.2 | nli | 0.362 | 0.341 | 0.278 |
| mistral-7b | sentiment | 0.594 | 0.590 | 0.581 |
| mistral-7b | nli | 0.480 | 0.413 | 0.436 |

## QA: exact match vs space-insensitive exact match

If EM(nospace) − EM is large in the segmented condition only,
part of the segmented QA drop is the spacing artifact (model
copies segmented spans), not real comprehension loss.

| model | condition | EM | EM (nospace) | gap |
|---|---|---|---|---|
| gpt-4 | raw | 0.628 | 0.628 | +0.000 |
| gpt-4 | segmented | 0.424 | 0.600 | +0.176 |
| gpt-4 | prompt_guided | 0.653 | 0.653 | +0.000 |
| claude | raw | 0.652 | 0.652 | +0.000 |
| claude | segmented | 0.432 | 0.592 | +0.160 |
| claude | prompt_guided | 0.611 | 0.611 | +0.000 |
| llama-3.2 | raw | 0.366 | 0.366 | +0.000 |
| llama-3.2 | segmented | 0.280 | 0.292 | +0.012 |
| llama-3.2 | prompt_guided | 0.252 | 0.254 | +0.002 |
| mistral-7b | raw | 0.330 | 0.330 | +0.000 |
| mistral-7b | segmented | 0.266 | 0.332 | +0.066 |
| mistral-7b | prompt_guided | 0.332 | 0.332 | +0.000 |

## Flip analysis (vs raw)

helpful = wrong→right under the condition; harmful = right→wrong.

| model | task | condition | helpful | harmful | net |
|---|---|---|---|---|---|
| gpt-4 | sentiment | segmented | 19 | 21 | -2 |
| gpt-4 | sentiment | prompt_guided | 18 | 11 | +7 |
| gpt-4 | nli | segmented | 23 | 57 | -34 |
| gpt-4 | nli | prompt_guided | 17 | 41 | -24 |
| gpt-4 | qa | segmented | 23 | 125 | -102 |
| gpt-4 | qa | prompt_guided | 29 | 19 | +10 |
| claude | sentiment | segmented | 11 | 15 | -4 |
| claude | sentiment | prompt_guided | 6 | 44 | -38 |
| claude | nli | segmented | 10 | 176 | -166 |
| claude | nli | prompt_guided | 7 | 238 | -231 |
| claude | qa | segmented | 13 | 123 | -110 |
| claude | qa | prompt_guided | 13 | 32 | -19 |
| llama-3.2 | sentiment | segmented | 50 | 43 | +7 |
| llama-3.2 | sentiment | prompt_guided | 52 | 41 | +11 |
| llama-3.2 | nli | segmented | 119 | 144 | -25 |
| llama-3.2 | nli | prompt_guided | 135 | 208 | -73 |
| llama-3.2 | qa | segmented | 24 | 67 | -43 |
| llama-3.2 | qa | prompt_guided | 18 | 75 | -57 |
| mistral-7b | sentiment | segmented | 12 | 16 | -4 |
| mistral-7b | sentiment | prompt_guided | 14 | 12 | +2 |
| mistral-7b | nli | segmented | 33 | 77 | -44 |
| mistral-7b | nli | prompt_guided | 37 | 68 | -31 |
| mistral-7b | qa | segmented | 38 | 70 | -32 |
| mistral-7b | qa | prompt_guided | 37 | 36 | +1 |
