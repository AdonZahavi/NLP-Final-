# Qualitative flip examples (issue #13)

Claude × NLI × segmented — the largest harmful effect
(−166 net flips). First 10 harmful flips:

### nli-108
- raw premise+hypothesis: נשמע ממש כמו אגדה. אבל סר ג'יימס היה זהיר מדי מכדי להיסחף. זה נשמע כמו סיפור מהנה.
- segmented: נשמע ממש כמו אגדה . אבל סר ג'יימס היה זהיר מדי מ כדי להיסחף . זה נשמע כמו סיפור מהנה .
- gold: entailment
- raw answer: entailment ✓
- segmented answer: None ✗

### nli-11
- raw premise+hypothesis: אבל דרו לא העז לשאול שאלות. דרו לא שאל שום שאלות.
- segmented: אבל דרו לא העז לשאול שאלות . דרו לא שאל שום שאלות .
- gold: entailment
- raw answer: entailment ✓
- segmented answer: None ✗

### nli-113
- raw premise+hypothesis: ג'ון דאג לחברו עד שראה את הפגיון הימני של סנדורו חותך פצעים עמוקים ופתוחים בגופו של האיש. ג'ון ראה שהסכין של סנדורו דקרה את האיש.
- segmented: ג'ון דאג לחברו עד ש ראה את ה פגיון ה ימני של סנדורו חותך פצעים עמוקים ו פתוחים ב גופו של ה איש . ג'ון ראה ש ה סכין של סנדורו דקרה את ה איש .
- gold: entailment
- raw answer: entailment ✓
- segmented answer: None ✗

### nli-117
- raw premise+hypothesis: כבר שלחתי את גרייפיתר בחזרה לספר לזקן שהילד נפצע ועכשיו הוא כאן. לא הצלחתי למצוא את גרייפיתר, אז שלחתי לזקן מייל.
- segmented: כבר שלחתי את גרייפיתר ב חזרה ל ה ספר ל זקן ש ה ילד נפצע ו עכשיו הוא כאן . לא הצלחתי למצוא את גרייפיתר , אז ש ל חתי ל זקן מייל .
- gold: contradiction
- raw answer: contradiction ✓
- segmented answer: None ✗

### nli-119
- raw premise+hypothesis: בהחלט. לגמרי.
- segmented: בהחלט . לגמרי .
- gold: entailment
- raw answer: entailment ✓
- segmented answer: neutral ✗

### nli-12
- raw premise+hypothesis: הוא התכוון שהוא לא ידע על כך, דייב הבין. דייב הניח שהוא התכוון שהוא לא ידע על כך.
- segmented: הוא התכוון ש הוא לא ידע על כך , דייב הבין . דייב הניח ש הוא התכוון ש הוא לא ידע על כך .
- gold: entailment
- raw answer: entailment ✓
- segmented answer: None ✗

### nli-120
- raw premise+hypothesis: אם המסקנות שלי נכונות, הילדה ההיא במנצ'סטר הייתה רק שתולה. הגעתי למסקנה שהילדה במנצ'סטר לא הייתה בכלל שתולה.
- segmented: אם ה מסקנות של אני נכונות , ה ילדה ה היא ב מנצ'סטר הייתה רק שתולה . הגעתי ל ה מסקנה ש ה ילדה ב ה מנצ'סטר לא הייתה בכלל שתולה .
- gold: contradiction
- raw answer: contradiction ✓
- segmented answer: None ✗

### nli-126
- raw premise+hypothesis: גבר הציץ מהחלון, בדיוק כשהם התחילו. אדם ראה אותם דרך החלון מיד
- segmented: גבר ה ציץ מ ה חלון , בדיוק כש הם התחילו . אדם ראה את הם דרך ה חלון מיד
- gold: entailment
- raw answer: entailment ✓
- segmented answer: None ✗

### nli-128
- raw premise+hypothesis: אבל, גם בזמן שעשה זאת, הוא הרגיש את עצמו נתפס מאחור באחיזת ברזל. מי שאחז אותו בחוזקה היה מלפניו.
- segmented: אבל , גם ב ה זמן ש עשה זאת , הוא הרגיש את עצמו נתפס מאחור ב אחיזת ברזל . מי ש אחז את הוא בחוזקה היה מלפני הוא .
- gold: contradiction
- raw answer: contradiction ✓
- segmented answer: None ✗

### nli-142
- raw premise+hypothesis: דווקא כן הייתה נערה צרפתייה שגרה בבית. האישה הזקנה מרוסיה הייתה מחוץ לבית במרפסת.
- segmented: דווקא כן הייתה נערה צרפתייה ש גרה ב ה בית . ה אישה ה זקנה מ רוסיה הייתה מ חוץ ל ה בית ב מרפסת .
- gold: neutral
- raw answer: neutral ✓
- segmented answer: None ✗
