# Pre-correction empty-response rates (thinking-budget artifact, report §5.3)

Documentation of the empty-response counts observed BEFORE the fix
(disabling extended thinking for Claude and re-running affected examples).
The post-fix result files on main contain no empty responses; the pre-fix
files are recoverable from git history (commits prior to the
`fix-claude-empty-responses` merge). These counts were measured on those
pre-fix files.

## Claude empty-response counts by condition (unique examples)

| task | raw | segmented |
|---|---|---|
| sentiment | 0/500 (0.0%) | 7/500 (1.4%) |
| nli | 47/884 (5.3%) | 232/884 (26.2%) |
| qa | 90/500 (18.0%) | 136/500 (27.2%) |

prompt_guided pre-fix files additionally contained duplicate records from
concurrent sweeps, so per-unique-example empty rates are not cleanly
recoverable for that condition; observed record-level counts were
123/932 (sentiment), 873/2671 (nli), 244/882 (qa) — qualitatively the same
elevation as segmented.

No other model produced empty responses in any condition.

## Effect on headline numbers

With empties scored as errors, Claude's segmented NLI accuracy appeared as
0.688 (an apparent −18.8 points vs the then-computed raw 0.876). After the
fix and re-run: raw 0.914, segmented 0.891 — a real drop of −2.3 points
(McNemar p = 0.0169).

Cause: claude-sonnet-5 emits internal "thinking" tokens that count against
`max_tokens`; with tight answer budgets (8 tokens for classification), long
thinking on out-of-distribution input consumed the entire budget, yielding
an empty visible answer. Fix: `thinking: disabled` in the API call, empty
responses rejected and never cached (src/heb_morph/clients/).
