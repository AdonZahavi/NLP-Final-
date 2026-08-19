# Qualitative flip examples (issue #13)

Claude × NLI × segmented — the largest harmful effect
(−166 net flips). First 10 harmful flips:

### nli-108
- raw premise+hypothesis: נשמע ממש כמו אגדה. אבל סר ג'יימס היה זהיר מדי מכדי להיסחף. זה נשמע כמו סיפור מהנה.
- segmented: נשמע ממש כמו אגדה . אבל סר ג'יימס היה זהיר מדי מ כדי להיסחף . זה נשמע כמו סיפור מהנה .
- gold: entailment
- raw answer: entailment ✓
- segmented answer: neutral ✗

### nli-119
- raw premise+hypothesis: בהחלט. לגמרי.
- segmented: בהחלט . לגמרי .
- gold: entailment
- raw answer: entailment ✓
- segmented answer: neutral ✗

### nli-138
- raw premise+hypothesis: רק פוארו נראה רגוע לחלוטין, וניגב פינה נשכחת של ארון הספרים. פוארו נראה רגוע ונינוח, וניגב את הרהיטים.
- segmented: רק פוארו נראה רגוע לחלוטין , ו ניגב פינה נשכחת של ארון ה ספרים . פוארו נראה רגוע ו נינוח , ו ניגב את ה רהיטים .
- gold: entailment
- raw answer: entailment ✓
- segmented answer: neutral ✗

### nli-153
- raw premise+hypothesis: העובדה האובייקטיבית היא שמה שלא תחשוב על מהת׳יר, מלזיה הצליחה להתחמק מהכפירה הכלכלית שלה. למלזיה היתה כפירה כלכלית במשך עשרות שנים.
- segmented: ה עובדה ה אובייקטיבית היא ש מה ש לא תחשוב על מהת׳יר , מלזיה הצליחה להתחמק מ ה כפירה ה כלכלית של היא . ל מלזיה היתה כפירה כלכלית במשך עשרות שנים .
- gold: neutral
- raw answer: neutral ✓
- segmented answer: contradiction ✗

### nli-163
- raw premise+hypothesis: הכרה במציאות אינה לא אתית, אבל התעלמות ממנה יכולה להיות. התעלמות מהמציאות יכולה להיות לא אתית מכיוון שאסור להתעלם מהמציאות לעולם.
- segmented: הכרה ב ה מציאות אינה לא אתית , אבל התעלמות מן היא יכולה ל היות . התעלמות מ ה מציאות יכולה להיות לא אתית מכיוון ש אסור להתעלם מ ה מציאות ל ה עולם .
- gold: neutral
- raw answer: neutral ✓
- segmented answer: entailment ✗

### nli-170
- raw premise+hypothesis: אבל בטווח הארוך, זה בלתי נמנע. זה יכול להתעכב.
- segmented: אבל ב ה טווח ה ארוך , זה בלתי נמנע . זה יכול להתעכב .
- gold: neutral
- raw answer: neutral ✓
- segmented answer: contradiction ✗

### nli-178
- raw premise+hypothesis: תחשבו על ענבים חסרי גרעינים או תפוזים טבוריים - אם אין גרעינים, מאיפה הם הגיעו?  האם ענבים ללא זרעים ותפוזים טבוריים מקורם בהתערבות אנושית?
- segmented: תחשבו על ענבים חסרי גרעינים או תפוזים טבוריים - אם אין גרעינים , מ איפה הם הגיעו ? האם ענבים ללא זרעים ו תפוזים טבוריים מ קורם ב התערבות אנושית ?
- gold: neutral
- raw answer: neutral ✓
- segmented answer: entailment ✗

### nli-229
- raw premise+hypothesis: ווייקבורדינג, השחקן וינס ווהן, מדינת ניו מקסיקו (רוזוול, ג'ורג'יה אוקיף), רכבות הרים. אלמנטים אלה משולבים בסרט.
- segmented: ווייקבורדינג , ה שחקן ו ינס ווהן , מדינת ניו מקסיקו ( רוזוול , ג'ורג'יה אוקיף ) , רכבות הרים . אלמנטים אלה משולבים ב ה סרט .
- gold: neutral
- raw answer: neutral ✓
- segmented answer: entailment ✗

### nli-237
- raw premise+hypothesis: הדיאלוג החופף והמוזיקה הקובנית-אפריקאית הצורמת שנשמעת מתוך מקלטי רדיו בעלי צליל מתכתי, נשמעים כאילו נועדו לגרום למיגרנה שתלווה את מחלת הים. להקת הג'אז ניגנה מוזיקת ג׳מייקנית שגורמת למיגרנות.
- segmented: ה דיאלוג ה חופף ו ה מוזיקה ה קובנית - אפריקאית ה צורמת ש נשמעת מתוך מקלטי רדיו ב עלי צליל מתכתי , נשמעים כאילו נועדו לגרום ל ה מיגרנה ש תלווה את מחלת ה ים . להקת ה ג'אז ניגנה מוזיקת ג׳מייקנית ש גורמת ל ה מיגרנות .
- gold: contradiction
- raw answer: contradiction ✓
- segmented answer: neutral ✗

### nli-256
- raw premise+hypothesis: אני חושד שאני יודע את התשובות לשאלות האלה, ואני חושד שגם מר שוגר יודע. אני לא ממש יודע איך לענות לך על זה.
- segmented: אני חושד ש אני יודע את ה תשובות ל שאלות ה אלה , ו אני חושד ש גם מר שוגר יודע . אני לא ממש יודע איך לענות ל אתה על זה .
- gold: contradiction
- raw answer: contradiction ✓
- segmented answer: neutral ✗
