# Sanity report — condition: segmented

| model | task | n | coverage | accuracy | macro-F1 | QA EM | QA token-F1 | parse-fail % |
|---|---|---|---|---|---|---|---|---|
| gpt-4 | sentiment | — | missing | | | | | |
| gpt-4 | nli | — | missing | | | | | |
| gpt-4 | qa | — | missing | | | | | |
| claude | sentiment | — | missing | | | | | |
| claude | nli | — | missing | | | | | |
| claude | qa | — | missing | | | | | |
| llama-3.2 | sentiment | 500 | 500/500 | 0.732 | 0.579 | | | 0.0 |
| llama-3.2 | nli | 884 | 884/884 | 0.431 | 0.341 | | | 0.0 |
| llama-3.2 | qa | 500 | 500/500 | | | 0.280 | 0.427 | 0.0 |
| mistral-7b | sentiment | 500 | 500/500 | 0.744 | 0.590 | | | 0.0 |
| mistral-7b | nli | 884 | 884/884 | 0.464 | 0.413 | | | 0.0 |
| mistral-7b | qa | 500 | 500/500 | | | 0.266 | 0.444 | 0.0 |

Files found: 6/12

All present files complete, parse-failure ≤ 5% ✔
