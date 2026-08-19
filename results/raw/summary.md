# Sanity report — condition: raw

| model | task | n | coverage | accuracy | macro-F1 | QA EM | QA token-F1 | parse-fail % |
|---|---|---|---|---|---|---|---|---|
| gpt-4 | sentiment | 500 | 500/500 | 0.734 | 0.622 | | | 0.0 |
| gpt-4 | nli | 884 | 884/884 | 0.885 | 0.884 | | | 0.0 |
| gpt-4 | qa | 500 | 500/500 | | | 0.628 | 0.723 | 0.0 |
| claude | sentiment | 500 | 500/500 | 0.822 | 0.669 | | | 0.0 |
| claude | nli | 884 | 884/884 | 0.914 | 0.913 | | | 0.0 |
| claude | qa | 500 | 500/500 | | | 0.700 | 0.760 | 0.0 |
| llama-3.2 | sentiment | 500 | 500/500 | 0.718 | 0.559 | | | 1.2 |
| llama-3.2 | nli | 884 | 884/884 | 0.459 | 0.362 | | | 0.0 |
| llama-3.2 | qa | 500 | 500/500 | | | 0.366 | 0.508 | 0.0 |
| mistral-7b | sentiment | 500 | 500/500 | 0.752 | 0.594 | | | 0.0 |
| mistral-7b | nli | 884 | 884/884 | 0.514 | 0.480 | | | 0.0 |
| mistral-7b | qa | 500 | 500/500 | | | 0.330 | 0.498 | 0.0 |

Files found: 12/12

All present files complete, parse-failure ≤ 5% ✔
