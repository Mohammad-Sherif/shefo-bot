"""
تمارين عشوائية - مستخرجة من Protocol Generator
"""
import random

TRACK_WORKOUTS = [
    {
        "title": "The Lactic Acid Burner",
        "title_ar": "حارق حمض اللاكتيك",
        "type": "Track Protocol",
        "type_ar": "بروتوكول تراك",
        "details": [
            "Warmup: 10 min jog + dynamic stretches",
            "Main Set: 8 × 200m at 85% effort",
            "Rest: 90 seconds between reps",
            "Focus: Lactic acid tolerance & speed endurance"
        ],
        "details_ar": [
            "إحماء: ١٠ دقائق جري خفيف + إطالات ديناميكية",
            "التمرين الرئيسي: ٨ × ٢٠٠ متر بجهد ٨٥٪",
            "الراحة: ٩٠ ثانية بين العدّات",
            "التركيز: تحمّل حمض اللاكتيك وتحمّل السرعة"
        ]
    },
    {
        "title": "Max Velo Shocker",
        "title_ar": "صدمة السرعة القصوى",
        "type": "Track Protocol",
        "type_ar": "بروتوكول تراك",
        "details": [
            "Warmup: 15 min progressive drills",
            "Main Set: 6 × 60m at 100% MAX speed",
            "Rest: 4-5 minutes full recovery",
            "Focus: Pure max velocity & neural activation"
        ],
        "details_ar": [
            "إحماء: ١٥ دقيقة تمارين تدريجية",
            "التمرين الرئيسي: ٦ × ٦٠ متر بأقصى سرعة",
            "الراحة: ٤-٥ دقائق استشفاء كامل",
            "التركيز: سرعة قصوى وتنشيط عصبي"
        ]
    },
    {
        "title": "The Curve Assassin",
        "title_ar": "قاتل المنحنيات",
        "type": "Track Protocol",
        "type_ar": "بروتوكول تراك",
        "details": [
            "Warmup: 10 min drills + curve technique",
            "Main Set: 4 × 200m on the curve at 90%",
            "Rest: 3 minutes between reps",
            "Focus: Curve mechanics & lean technique"
        ],
        "details_ar": [
            "إحماء: ١٠ دقائق تمارين + تقنية المنحنى",
            "التمرين الرئيسي: ٤ × ٢٠٠ متر على المنحنى بجهد ٩٠٪",
            "الراحة: ٣ دقائق بين العدّات",
            "التركيز: ميكانيكا المنحنى وتقنية الميل"
        ]
    },
    {
        "title": "The Death Pyramid",
        "title_ar": "هرم الموت",
        "type": "Track Protocol",
        "type_ar": "بروتوكول تراك",
        "details": [
            "Warmup: 15 min progressive build-up",
            "Main Set: 100m → 200m → 300m → 400m → 300m → 200m → 100m",
            "Rest: Equal to run time",
            "Focus: Complete speed endurance pyramid"
        ],
        "details_ar": [
            "إحماء: ١٥ دقيقة بناء تدريجي",
            "التمرين الرئيسي: ١٠٠م ← ٢٠٠م ← ٣٠٠م ← ٤٠٠م ← ٣٠٠م ← ٢٠٠م ← ١٠٠م",
            "الراحة: مساوية لوقت الجري",
            "التركيز: هرم تحمّل سرعة كامل"
        ]
    }
]

GYM_WORKOUTS = [
    {
        "title": "The 100-Rep Chest Obliterator",
        "title_ar": "مُدمّر الصدر ١٠٠ عدة",
        "type": "Gym Protocol",
        "type_ar": "بروتوكول جيم",
        "details": [
            "Exercise: Bench Press (rest-pause method)",
            "Target: 100 total reps with your 15RM weight",
            "Method: Max reps → 15sec rest → repeat until 100",
            "Focus: Chest hypertrophy & mental toughness"
        ],
        "details_ar": [
            "التمرين: بنش بريس (طريقة الراحة-الاستمرار)",
            "الهدف: ١٠٠ عدة إجمالي بوزن ١٥ عدة قصوى",
            "الطريقة: أقصى عدات ← ١٥ ثانية راحة ← كرر حتى ١٠٠",
            "التركيز: تضخيم الصدر وقوة العقل"
        ]
    },
    {
        "title": "The Widowmaker Leg Day",
        "title_ar": "يوم الرجل القاتل",
        "type": "Gym Protocol",
        "type_ar": "بروتوكول جيم",
        "details": [
            "Exercise: Barbell Squats",
            "The Set: 1 × 20 reps with your 10RM weight",
            "Method: DO NOT rack the bar. Breathe and continue.",
            "Focus: Leg hypertrophy & extreme willpower"
        ],
        "details_ar": [
            "التمرين: سكوات بالبار",
            "المجموعة: ١ × ٢٠ عدة بوزن ١٠ عدات قصوى",
            "الطريقة: لا تنزّل البار. تنفّس واستمر.",
            "التركيز: تضخيم الرجل وقوة إرادة خارقة"
        ]
    },
    {
        "title": "The Armageddon Pump",
        "title_ar": "ضخ يوم القيامة",
        "type": "Gym Protocol",
        "type_ar": "بروتوكول جيم",
        "details": [
            "Method: Giant Sets (no rest between exercises)",
            "Biceps: Barbell Curl → Hammer Curl → Concentration Curl",
            "Triceps: Skull Crusher → Close Grip Press → Overhead Extension",
            "3 rounds. Focus: Maximum arm pump & blood flow"
        ],
        "details_ar": [
            "الطريقة: مجموعات عملاقة (بدون راحة بين التمارين)",
            "باي: بار كيرل ← هامر كيرل ← كونسنتريشن كيرل",
            "تراي: سكل كراشر ← ضغط ضيق ← إكستنشن فوق الرأس",
            "٣ جولات. التركيز: أقصى ضخ للذراعين"
        ]
    }
]


def generate_random_workout() -> dict:
    """Generate a random workout with 70% track / 30% gym probability"""
    if random.random() < 0.7:
        return random.choice(TRACK_WORKOUTS)
    else:
        return random.choice(GYM_WORKOUTS)


def format_workout_ar(workout: dict) -> str:
    """Format a workout for display in Arabic"""
    lines = [
        f"🔥 {workout['type_ar']}",
        f"💀 {workout['title_ar']}",
        ""
    ]
    for detail in workout['details_ar']:
        lines.append(f"• {detail}")
    return "\n".join(lines)
