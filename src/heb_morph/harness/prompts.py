"""Prompt templates per task × condition.

Design decisions (document in the report):
- Instructions are in ENGLISH with the Hebrew text embedded — all four models
  follow English instructions reliably, and it keeps output parsing uniform.
- Answers are requested as a SINGLE English label token (classification) or a
  copied Hebrew span (QA), enabling strict parsing.
- The `segmented` condition adds one sentence explaining that the text is
  split into morphemes, so models don't treat the spacing as noise.
- The `prompt_guided` condition injects a morphology instruction. The default
  below is v1; issue #8 pilots multiple variants and the winner is passed in
  via `morph_instruction`.
"""

from __future__ import annotations

DEFAULT_MORPH_INSTRUCTION = (
    "Note: Hebrew words often contain attached prefixes (ו- 'and', ש- 'that', "
    "ה- 'the', ל- 'to', ב- 'in', מ- 'from', כש- 'when') and pronominal "
    "suffixes packed into a single written word. Before reasoning, mentally "
    "decompose each word into its morphemes."
)

SEGMENTED_NOTE = (
    "Note: the Hebrew text below has been morphologically segmented — each "
    "word is split into its component morphemes, separated by spaces."
)

_SENTIMENT = (
    "{prefix}You are given a comment written in Hebrew, posted on the Facebook "
    "page of Israel's president.\n"
    "Classify its sentiment toward the president/post as exactly one of: "
    "positive, negative, off-topic.\n"
    "(off-topic means the comment does not relate to the post at all.)\n\n"
    "Comment: {text}\n\n"
    "Answer with one word only: positive, negative, or off-topic."
)

_NLI = (
    "{prefix}You are given a premise and a hypothesis in Hebrew.\n"
    "Decide the relationship between them: entailment (the premise implies "
    "the hypothesis), contradiction (they cannot both be true), or neutral "
    "(neither).\n\n"
    "Premise: {premise}\n"
    "Hypothesis: {hypothesis}\n\n"
    "Answer with one word only: entailment, contradiction, or neutral."
)

_QA = (
    "{prefix}Read the Hebrew paragraph and answer the question.\n"
    "Answer ONLY with the shortest exact span copied from the paragraph, in "
    "Hebrew. Do not add explanations.\n\n"
    "Paragraph: {context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)

CONDITIONS = ("raw", "segmented", "prompt_guided")


def build_prompt(task: str, record: dict, condition: str,
                 morph_instruction: str | None = None) -> str:
    """Build the exact prompt for one example under one condition."""
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition: {condition}")

    if condition == "segmented":
        prefix = SEGMENTED_NOTE + "\n\n"
        suffix = "_seg"
    elif condition == "prompt_guided":
        prefix = (morph_instruction or DEFAULT_MORPH_INSTRUCTION) + "\n\n"
        suffix = ""
    else:
        prefix, suffix = "", ""

    if task == "sentiment":
        return _SENTIMENT.format(prefix=prefix, text=record["text" + suffix])
    if task == "nli":
        return _NLI.format(prefix=prefix,
                           premise=record["premise" + suffix],
                           hypothesis=record["hypothesis" + suffix])
    if task == "qa":
        return _QA.format(prefix=prefix,
                          context=record["context" + suffix],
                          question=record["question" + suffix])
    raise ValueError(f"unknown task: {task}")
