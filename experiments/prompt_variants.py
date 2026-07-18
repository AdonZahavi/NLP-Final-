"""Issue #8: morphology-instruction variants for the prompt_guided condition.

Each variant replaces the instruction PREFIX only — the task template, answer
format, and parser stay identical, so pilot differences are attributable to
the instruction itself. V5 additionally needs a larger token budget because it
asks for a (discarded) decomposition before the final answer.
"""

VARIANTS = {
    "v1_brief": {
        "max_tokens": None,  # task default
        "instruction": (
            "Note: Hebrew words often contain attached prefixes (ו- 'and', "
            "ש- 'that', ה- 'the', ל- 'to', ב- 'in', מ- 'from', כש- 'when') "
            "and pronominal suffixes packed into a single written word. "
            "Before reasoning, mentally decompose each word into its morphemes."
        ),
    },
    "v2_linguistic": {
        "max_tokens": None,
        "instruction": (
            "Hebrew is a morphologically rich language: a single written word "
            "may bundle a conjunction, a preposition, the definite article, a "
            "content stem, and a pronominal suffix. For example, וכשהלכתי is "
            "ו (and) + כש (when) + הלכ (walked) + תי (I) — a whole clause in "
            "one word. Common prefixes: ו (and), ש (that/which), ה (the), "
            "ל (to), ב (in), מ (from), כ (as/like), כש (when). Suffixes mark "
            "possession or object pronouns (ביתו = בית + שלו). While reading "
            "the text below, mentally decompose every word into its morphemes "
            "before deciding your answer."
        ),
    },
    "v3_worked_example": {
        "max_tokens": None,
        "instruction": (
            "Hebrew packs several grammatical units into single words. "
            "Example of mental decomposition:\n"
            "  וכשהלכתי הביתה  →  ו + כש + הלכתי | ה + ביתה "
            "('and + when + I-walked | the + homeward')\n"
            "Apply this kind of decomposition mentally to every word in the "
            "text below before answering."
        ),
    },
    "v4_hebrew": {
        "max_tokens": None,
        "instruction": (
            "שים לב: מילים בעברית מכילות לעיתים קרובות אותיות שימוש מוצמדות "
            "(ו', ש', ה', ל', ב', מ', כש') וכינויי שייכות או מושא בסוף המילה. "
            "לפני שאתה עונה, פרק בראש כל מילה למורפמות המרכיבות אותה."
        ),
    },
    "v5_decompose_first": {
        "max_tokens": 250,  # the decomposition costs output tokens
        "instruction": (
            "Hebrew words often bundle prefixes (ו, ש, ה, ל, ב, מ, כש) and "
            "suffixes with the content stem. Step 1: silently rewrite the "
            "Hebrew text with every word split into its morphemes. Step 2: "
            "using that decomposition, decide your answer. Your reply must "
            "END with the final answer alone on its last line, in the exact "
            "format requested below."
        ),
    },
}
