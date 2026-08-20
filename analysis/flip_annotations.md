# Annotated flip examples for report Section 6.3 — VERIFIED

Source: Claude × NLI, raw → segmented harmful flips (analysis/flip_examples.md).
Annotations drafted by the assistant and verified by Or Zahavi (native
speaker). Verification outcomes: Ex.1 confirmed for ל ה עולם only (the
מן היא claim was dropped — the rest of that segmentation is acceptable);
Ex.2 confirmed (קורם is not a word; the stem of מקורם is מקור);
Ex.3 confirmed (name corrupted); Ex.4 confirmed (error-free segmentation).

---

## Example 1 — nli-163: segmentation changed the meaning (covert-ה normalization)

- raw hypothesis: התעלמות מהמציאות יכולה להיות לא אתית מכיוון שאסור להתעלם מהמציאות לעולם.
- segmented:      התעלמות מ ה מציאות יכולה להיות לא אתית מכיוון ש אסור להתעלם מ ה מציאות ל ה עולם.
- gold: neutral | raw answer: neutral ✓ | segmented answer: entailment ✗

**Verified annotation:** YAP normalized לעולם ("ever", idiomatic with
negation: "one must never ignore reality") into ל ה עולם — literally "to the
world" — a false segmentation that removes the temporal idiom. The rest of
the example's segmentation is acceptable. The segmented hypothesis no longer
says what the author wrote; the flip reflects altered meaning, not model
failure.

## Example 2 — nli-178: segmenter error destroyed the key content word

- raw hypothesis: האם ענבים ללא זרעים ותפוזים טבוריים מקורם בהתערבות אנושית?
- segmented:      האם ענבים ללא זרעים ו תפוזים טבוריים מ קורם ב התערבות אנושית ?
- gold: neutral | raw answer: neutral ✓ | segmented answer: entailment ✗

**Verified annotation:** מקורם ("their origin" = מקור + possessive ם) was
mis-split as מ קורם, treating the initial מ as the preposition "from" and
leaving the non-word קורם. The content word carrying the entire question —
*origin* — disappeared. This is a true YAP error (the class documented in
Section 4.2), and the model flipped on a hypothesis that no longer contains
its own key concept.


## Example 3 — nli-229: named-entity mangling

- raw premise (excerpt): ווייקבורדינג, השחקן וינס ווהן, מדינת ניו מקסיקו...
- segmented:             ווייקבורדינג , ה שחקן ו ינס ווהן , מדינת ניו מקסיקו...
- gold: neutral | raw answer: neutral ✓ | segmented answer: entailment ✗

**Verified annotation:** The actor's name וינס ווהן (Vince Vaughn) begins with ו,
which YAP treated as the conjunction "and", producing ו ינס ווהן ("and Ince
Vaughn"). Morphological segmenters cannot distinguish a name-initial vav from
a clitic; segmentation corrupted a named entity and the model lost the
premise's list structure.


## Example 4 — nli-138: flawless segmentation, still flipped (the control case)

- raw: רק פוארו נראה רגוע לחלוטין, וניגב פינה נשכחת של ארון הספרים. פוארו נראה רגוע ונינוח, וניגב את הרהיטים.
- segmented: רק פוארו נראה רגוע לחלוטין , ו ניגב פינה נשכחת של ארון ה ספרים . פוארו נראה רגוע ו נינוח , ו ניגב את ה רהיטים .
- gold: entailment | raw answer: entailment ✓ | segmented answer: neutral ✗

**Verified annotation:** Here YAP's output is linguistically correct — every
split (ו ניגב, ה ספרים, ה רהיטים) is a genuine clitic boundary and no meaning
changed. The model still flipped. This is direct evidence for the
distribution-shift interpretation (Section 6.2): even *error-free*
segmentation degrades comprehension, because the spacing pattern itself is
foreign to the model's training distribution.


---

Taxonomy these four establish: (1) meaning-changing normalization,
(2) segmenter error, (3) named-entity damage, (4) harm without any error.
After verification, condensed versions go into report Section 6.3.
