# Flip categorization by morphological features (issue #13)

For each model × task × condition: mean morphological features of
examples that flipped helpfully (wrong→right), harmfully
(right→wrong), or stayed stable. `prefix_density` = clitic
prefixes split per raw token; `expansion` = seg/raw token ratio.

| model | task | condition | group | n | expansion | prefix_density | he_tokens |
|---|---|---|---|---|---|---|---|
| gpt-4 | sentiment | segmented | helpful | 19 | 1.499 | 0.413 | 3.58 |
| gpt-4 | sentiment | segmented | harmful | 21 | 1.881 | 0.364 | 6.00 |
| gpt-4 | sentiment | segmented | stable | 460 | 1.501 | 0.352 | 3.26 |
| gpt-4 | sentiment | prompt_guided | helpful | 18 | 1.455 | 0.396 | 6.22 |
| gpt-4 | sentiment | prompt_guided | harmful | 11 | 1.389 | 0.351 | 9.00 |
| gpt-4 | sentiment | prompt_guided | stable | 471 | 1.522 | 0.353 | 3.14 |
| gpt-4 | nli | segmented | helpful | 23 | 1.538 | 0.358 | 3.78 |
| gpt-4 | nli | segmented | harmful | 57 | 1.635 | 0.391 | 4.00 |
| gpt-4 | nli | segmented | stable | 804 | 1.583 | 0.368 | 3.95 |
| gpt-4 | nli | prompt_guided | helpful | 17 | 1.513 | 0.310 | 2.94 |
| gpt-4 | nli | prompt_guided | harmful | 41 | 1.590 | 0.353 | 3.59 |
| gpt-4 | nli | prompt_guided | stable | 826 | 1.586 | 0.371 | 3.99 |
| gpt-4 | qa | segmented | helpful | 23 | 1.616 | 0.438 | 23.61 |
| gpt-4 | qa | segmented | harmful | 125 | 1.642 | 0.440 | 23.61 |
| gpt-4 | qa | segmented | stable | 352 | 1.634 | 0.421 | 21.55 |
| gpt-4 | qa | prompt_guided | helpful | 29 | 1.635 | 0.441 | 22.97 |
| gpt-4 | qa | prompt_guided | harmful | 19 | 1.656 | 0.425 | 21.63 |
| gpt-4 | qa | prompt_guided | stable | 452 | 1.634 | 0.426 | 22.13 |
| claude | sentiment | segmented | helpful | 12 | 1.372 | 0.308 | 7.00 |
| claude | sentiment | segmented | harmful | 11 | 1.556 | 0.361 | 3.82 |
| claude | sentiment | segmented | stable | 477 | 1.519 | 0.356 | 3.28 |
| claude | sentiment | prompt_guided | helpful | 9 | 1.293 | 0.231 | 2.56 |
| claude | sentiment | prompt_guided | harmful | 10 | 1.419 | 0.231 | 2.20 |
| claude | sentiment | prompt_guided | stable | 481 | 1.523 | 0.359 | 3.42 |
| claude | nli | segmented | helpful | 22 | 1.573 | 0.357 | 3.09 |
| claude | nli | segmented | harmful | 42 | 1.612 | 0.364 | 3.62 |
| claude | nli | segmented | stable | 820 | 1.584 | 0.370 | 3.99 |
| claude | nli | prompt_guided | helpful | 24 | 1.632 | 0.413 | 4.62 |
| claude | nli | prompt_guided | harmful | 36 | 1.568 | 0.320 | 3.39 |
| claude | nli | prompt_guided | stable | 824 | 1.584 | 0.370 | 3.95 |
| claude | qa | segmented | helpful | 19 | 1.587 | 0.416 | 19.95 |
| claude | qa | segmented | harmful | 130 | 1.665 | 0.443 | 22.97 |
| claude | qa | segmented | stable | 351 | 1.626 | 0.421 | 21.98 |
| claude | qa | prompt_guided | helpful | 19 | 1.581 | 0.413 | 20.16 |
| claude | qa | prompt_guided | harmful | 28 | 1.601 | 0.417 | 19.96 |
| claude | qa | prompt_guided | stable | 453 | 1.639 | 0.428 | 22.38 |
| llama-3.2 | sentiment | segmented | helpful | 50 | 1.396 | 0.294 | 4.10 |
| llama-3.2 | sentiment | segmented | harmful | 43 | 1.731 | 0.362 | 2.00 |
| llama-3.2 | sentiment | segmented | stable | 407 | 1.509 | 0.361 | 3.44 |
| llama-3.2 | sentiment | prompt_guided | helpful | 52 | 1.384 | 0.299 | 2.73 |
| llama-3.2 | sentiment | prompt_guided | harmful | 41 | 1.660 | 0.328 | 3.46 |
| llama-3.2 | sentiment | prompt_guided | stable | 407 | 1.519 | 0.364 | 3.46 |
| llama-3.2 | nli | segmented | helpful | 119 | 1.567 | 0.355 | 3.71 |
| llama-3.2 | nli | segmented | harmful | 144 | 1.572 | 0.370 | 4.28 |
| llama-3.2 | nli | segmented | stable | 621 | 1.592 | 0.372 | 3.91 |
| llama-3.2 | nli | prompt_guided | helpful | 135 | 1.568 | 0.354 | 3.68 |
| llama-3.2 | nli | prompt_guided | harmful | 208 | 1.582 | 0.369 | 3.86 |
| llama-3.2 | nli | prompt_guided | stable | 541 | 1.591 | 0.373 | 4.05 |
| llama-3.2 | qa | segmented | helpful | 24 | 1.641 | 0.418 | 20.62 |
| llama-3.2 | qa | segmented | harmful | 67 | 1.629 | 0.436 | 22.48 |
| llama-3.2 | qa | segmented | stable | 409 | 1.635 | 0.425 | 22.20 |
| llama-3.2 | qa | prompt_guided | helpful | 18 | 1.665 | 0.410 | 21.50 |
| llama-3.2 | qa | prompt_guided | harmful | 75 | 1.597 | 0.418 | 20.25 |
| llama-3.2 | qa | prompt_guided | stable | 407 | 1.640 | 0.429 | 22.54 |
| mistral-7b | sentiment | segmented | helpful | 12 | 1.520 | 0.381 | 2.83 |
| mistral-7b | sentiment | segmented | harmful | 16 | 1.473 | 0.411 | 2.38 |
| mistral-7b | sentiment | segmented | stable | 472 | 1.518 | 0.352 | 3.43 |
| mistral-7b | sentiment | prompt_guided | helpful | 14 | 1.362 | 0.324 | 2.21 |
| mistral-7b | sentiment | prompt_guided | harmful | 12 | 1.419 | 0.301 | 1.67 |
| mistral-7b | sentiment | prompt_guided | stable | 474 | 1.523 | 0.357 | 3.46 |
| mistral-7b | nli | segmented | helpful | 33 | 1.627 | 0.364 | 3.48 |
| mistral-7b | nli | segmented | harmful | 77 | 1.608 | 0.377 | 3.97 |
| mistral-7b | nli | segmented | stable | 774 | 1.581 | 0.369 | 3.96 |
| mistral-7b | nli | prompt_guided | helpful | 37 | 1.571 | 0.349 | 3.59 |
| mistral-7b | nli | prompt_guided | harmful | 68 | 1.592 | 0.389 | 3.84 |
| mistral-7b | nli | prompt_guided | stable | 779 | 1.585 | 0.369 | 3.97 |
| mistral-7b | qa | segmented | helpful | 38 | 1.610 | 0.409 | 21.53 |
| mistral-7b | qa | segmented | harmful | 70 | 1.632 | 0.432 | 22.73 |
| mistral-7b | qa | segmented | stable | 392 | 1.638 | 0.427 | 22.12 |
| mistral-7b | qa | prompt_guided | helpful | 37 | 1.627 | 0.424 | 22.57 |
| mistral-7b | qa | prompt_guided | harmful | 36 | 1.622 | 0.424 | 21.78 |
| mistral-7b | qa | prompt_guided | stable | 427 | 1.637 | 0.427 | 22.16 |

## Aggregate (segmented condition, all models pooled)

| task | group | n | expansion | prefix_density |
|---|---|---|---|---|
| sentiment | helpful | 93 | 1.430 | 0.331 |
| sentiment | harmful | 91 | 1.699 | 0.371 |
| sentiment | stable | 1816 | 1.512 | 0.355 |
| nli | helpful | 197 | 1.574 | 0.357 |
| nli | harmful | 320 | 1.597 | 0.375 |
| nli | stable | 3019 | 1.585 | 0.370 |
| qa | helpful | 104 | 1.614 | 0.419 |
| qa | harmful | 392 | 1.646 | 0.439 |
| qa | stable | 1504 | 1.633 | 0.424 |
