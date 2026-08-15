# Sanity report — condition: raw

| model | task | n | coverage | accuracy | macro-F1 | QA EM | QA token-F1 | parse-fail % |
|---|---|---|---|---|---|---|---|---|
| gpt-4 | sentiment | 500 | 500/500 | 0.734 | 0.622 | | | 0.0 |
| gpt-4 | nli | 884 | 884/884 | 0.885 | 0.884 | | | 0.0 |
| gpt-4 | qa | 500 | 500/500 | | | 0.628 | 0.723 | 0.0 |
| claude | sentiment | 500 | 500/500 | 0.822 | 0.669 | | | 0.0 |
| claude | nli | 884 | 884/884 | 0.876 | 0.898 | | | 5.3 |
| claude | qa | 500 | 500/500 | | | 0.652 | 0.702 | 18.0 |
| llama-3.2 | sentiment | — | missing | | | | | |
| llama-3.2 | nli | — | missing | | | | | |
| llama-3.2 | qa | — | missing | | | | | |
| mistral-7b | sentiment | — | missing | | | | | |
| mistral-7b | nli | — | missing | | | | | |
| mistral-7b | qa | — | missing | | | | | |

Files found: 6/12

## ⚠ Warnings

- claude×nli: parse-failure rate 5.3% > 5% — inspect raw outputs
- claude×qa: parse-failure rate 18.0% > 5% — inspect raw outputs
