# Sanity report — condition: prompt_guided

| model | task | n | coverage | accuracy | macro-F1 | QA EM | QA token-F1 | parse-fail % |
|---|---|---|---|---|---|---|---|---|
| gpt-4 | sentiment | 500 | 500/500 | 0.748 | 0.620 | | | 0.0 |
| gpt-4 | nli | 1739 | 1739/884 | 0.860 | 0.860 | | | 0.0 |
| gpt-4 | qa | 980 | 980/500 | | | 0.653 | 0.740 | 0.0 |
| claude | sentiment | 932 | 932/500 | 0.752 | 0.624 | | | 13.2 |
| claude | nli | 2671 | 2671/884 | 0.641 | 0.756 | | | 32.7 |
| claude | qa | 882 | 882/500 | | | 0.611 | 0.643 | 27.7 |
| llama-3.2 | sentiment | — | missing | | | | | |
| llama-3.2 | nli | — | missing | | | | | |
| llama-3.2 | qa | — | missing | | | | | |
| mistral-7b | sentiment | — | missing | | | | | |
| mistral-7b | nli | — | missing | | | | | |
| mistral-7b | qa | — | missing | | | | | |

Files found: 6/12

## ⚠ Warnings

- claude×sentiment: parse-failure rate 13.2% > 5% — inspect raw outputs
- claude×nli: parse-failure rate 32.7% > 5% — inspect raw outputs
- claude×qa: parse-failure rate 27.7% > 5% — inspect raw outputs
