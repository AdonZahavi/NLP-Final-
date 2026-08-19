# Sanity report — condition: prompt_guided

| model | task | n | coverage | accuracy | macro-F1 | QA EM | QA token-F1 | parse-fail % |
|---|---|---|---|---|---|---|---|---|
| gpt-4 | sentiment | 500 | 500/500 | 0.748 | 0.620 | | | 0.0 |
| gpt-4 | nli | 884 | 884/884 | 0.857 | 0.858 | | | 0.0 |
| gpt-4 | qa | 500 | 500/500 | | | 0.648 | 0.736 | 0.0 |
| claude | sentiment | 500 | 500/500 | 0.820 | 0.667 | | | 0.0 |
| claude | nli | 884 | 884/884 | 0.900 | 0.904 | | | 0.6 |
| claude | qa | 500 | 500/500 | | | 0.682 | 0.737 | 0.0 |
| llama-3.2 | sentiment | 500 | 500/500 | 0.740 | 0.522 | | | 0.4 |
| llama-3.2 | nli | 884 | 884/884 | 0.377 | 0.278 | | | 0.0 |
| llama-3.2 | qa | 500 | 500/500 | | | 0.252 | 0.401 | 0.0 |
| mistral-7b | sentiment | 500 | 500/500 | 0.756 | 0.581 | | | 0.0 |
| mistral-7b | nli | 884 | 884/884 | 0.479 | 0.436 | | | 0.0 |
| mistral-7b | qa | 500 | 500/500 | | | 0.332 | 0.471 | 0.0 |

Files found: 12/12

All present files complete, parse-failure ≤ 5% ✔
