"""
COACH CLAUDE PRO V6.1 - بيانات خطة التمارين الأسبوعية
"""

WEEKLY_PLAN = {
    "Sunday": {
        "type": "gym",
        "name": "Upper 1",
        "name_ar": "جزء علوي ١",
        "exercises": [
            {"name": "Incline DB Press", "name_ar": "ضغط مائل بالدمبل", "sets": 2, "reps": "8-10", "rir": 1, "rest": "2 min"},
            {"name": "Lat Pulldown (Width)", "name_ar": "سحب علوي عريض", "sets": 2, "reps": "8-10", "rir": 1, "rest": "2 min"},
            {"name": "Lateral Raises (Scapular Plane)", "name_ar": "رفع جانبي", "sets": 2, "reps": "12-15", "rir": 1, "rest": "90 sec"},
            {"name": "Seated Cable Row", "name_ar": "تجديف كابل جالس", "sets": 2, "reps": "10-12", "rir": 1, "rest": "2 min"},
            {"name": "Cable Curls", "name_ar": "كيرل كابل", "sets": 2, "reps": "10-12", "rir": 1, "rest": "90 sec"},
            {"name": "Tricep Pushdown", "name_ar": "ضغط تراي كابل", "sets": 2, "reps": "10-12", "rir": 1, "rest": "90 sec"},
        ]
    },
    "Monday": {
        "type": "track",
        "name": "Endurance",
        "name_ar": "تحمّل",
        "drills": "10 Mins: A-Skips, B-Skips, High Knees",
        "drills_ar": "١٠ دقائق: A-Skips, B-Skips, ركب عالية",
        "main": "45 Mins Continuous Run in Zone 2 (Heart Rate < 140bpm)",
        "main_ar": "٤٥ دقيقة جري متواصل في Zone 2 (نبض أقل من ١٤٠)",
        "alternative": "45 Mins Bike (Trinx M136 Pro) if joints are stiff",
        "alternative_ar": "٤٥ دقيقة دراجة لو المفاصل متيبسة"
    },
    "Tuesday": {
        "type": "gym",
        "name": "Lower",
        "name_ar": "جزء سفلي",
        "exercises": [
            {"name": "Smith Machine or Hack Squats", "name_ar": "سكوات سميث أو هاك", "sets": 2, "reps": "6-8", "rir": 1, "rest": "2 min"},
            {"name": "B-Stance RDL (Right Leg Focus)", "name_ar": "رفعة ميتة رومانية بساق واحدة", "sets": 1, "reps": "warmup", "rir": 0, "rest": "90 sec", "note": "Warmup set, slow eccentric"},
            {"name": "Romanian Deadlift (RDL)", "name_ar": "رفعة ميتة رومانية", "sets": 2, "reps": "8-10", "rir": 1, "rest": "2 min", "note": "3s negative, brace core"},
            {"name": "Hatfield Bulgarian Split Squats", "name_ar": "سبليت سكوات بلغاري", "sets": 2, "reps": "8-10/leg", "rir": 1, "rest": "2 min"},
            {"name": "Leg Curls", "name_ar": "ثني رجل (هامسترينج)", "sets": 2, "reps": "10-12", "rir": 1, "rest": "90 sec"},
            {"name": "Calf Raises", "name_ar": "رفع سمانة", "sets": 2, "reps": "15-20", "rir": 1, "rest": "90 sec", "note": "Adjust foot angle"},
            {"name": "CORE: Farmer's Walks & Suitcase Holds", "name_ar": "كور: مشي بالأوزان", "sets": 3, "reps": "hold", "rir": 0, "rest": "90 sec"},
        ]
    },
    "Wednesday": {
        "type": "track",
        "name": "Tempo",
        "name_ar": "تيمبو",
        "drills": "10 Mins: Form Running, Arm Mechanics",
        "drills_ar": "١٠ دقائق: تمارين الفورم والذراعين",
        "main": "6 x 400m at 75%-80% Speed (Tempo)",
        "main_ar": "٦ × ٤٠٠ متر بسرعة ٧٥-٨٠٪",
        "rest": "90 seconds walk between reps",
        "rest_ar": "٩٠ ثانية مشي بين العدّات"
    },
    "Thursday": {
        "type": "gym",
        "name": "Upper 2",
        "name_ar": "جزء علوي ٢",
        "exercises": [
            {"name": "Overhead DB Press", "name_ar": "ضغط كتف بالدمبل", "sets": 2, "reps": "8-10", "rir": 1, "rest": "2 min"},
            {"name": "Close-Grip Lat Pulldown", "name_ar": "سحب علوي ضيق", "sets": 2, "reps": "10-12", "rir": 1, "rest": "2 min"},
            {"name": "Pec Deck (Chest Fly)", "name_ar": "فلاي صدر", "sets": 2, "reps": "10-12", "rir": 1, "rest": "90 sec"},
            {"name": "Single-Leg Extensions", "name_ar": "إكستنشن رجل واحدة", "sets": 2, "reps": "12-15", "rir": 1, "rest": "90 sec", "note": "Start Right, pause 1s at top"},
            {"name": "Reverse Pec Deck", "name_ar": "فلاي خلفي", "sets": 2, "reps": "12-15", "rir": 1, "rest": "90 sec"},
            {"name": "Hammer Curls", "name_ar": "هامر كيرل", "sets": 2, "reps": "10-12", "rir": 1, "rest": "90 sec"},
            {"name": "Overhead Tricep Extension", "name_ar": "تراي فوق الرأس", "sets": 2, "reps": "10-12", "rir": 1, "rest": "90 sec"},
            {"name": "CORE: Farmer's Walks & Suitcase Holds", "name_ar": "كور: مشي بالأوزان", "sets": 3, "reps": "hold", "rir": 0, "rest": "90 sec"},
        ]
    },
    "Friday": {
        "type": "rest",
        "name": "Recovery",
        "name_ar": "راحة",
        "details": "Total Rest. Deep sleep for CNS repair.",
        "details_ar": "راحة تامة. نوم عميق لتعافي الجهاز العصبي المركزي."
    },
    "Saturday": {
        "type": "track",
        "name": "Sprints",
        "name_ar": "سرعة قصوى",
        "drills": "15 Mins: Max Velocity Mechanics, Bounds, Plyometrics",
        "drills_ar": "١٥ دقيقة: ميكانيكا السرعة القصوى والقفز",
        "main": "6 x 100m Sprints at 100% Speed (Max Velocity)",
        "main_ar": "٦ × ١٠٠ متر سبرنت بأقصى سرعة",
        "rest": "5 to 8 minutes complete passive rest",
        "rest_ar": "٥-٨ دقائق راحة سلبية كاملة"
    }
}

# Hybrid Tax: extra carbs on track days
HYBRID_TAX = {
    "rule": "On track days (Monday, Wednesday & Saturday), add extra 100g Egyptian Bread OR 100g Cooked Rice",
    "rule_ar": "في أيام التراك (الاثنين والأربعاء والسبت) أضف ١٠٠ جرام عيش بلدي أو ١٠٠ جرام أرز مطبوخ إضافي",
    "days": ["Monday", "Wednesday", "Saturday"]
}

# General training rules
TRAINING_RULES = {
    "volume": "2 Working Sets per exercise",
    "intensity": "Train to 1 RIR (leave 1 rep in the tank)",
    "negatives": "Lower weight slowly (2-second negative)",
    "rest_compound": "2 minutes",
    "rest_isolation": "90 seconds",
    "cns_alert": "Academic stress = physical stress. If sleep-deprived, reduce to 1 set per exercise."
}


def get_today_plan(day_name: str) -> dict:
    """Get today's training plan by English day name (e.g. 'Sunday')"""
    return WEEKLY_PLAN.get(day_name, {})


def is_track_day(day_name: str) -> bool:
    plan = WEEKLY_PLAN.get(day_name, {})
    return plan.get("type") == "track"


def is_gym_day(day_name: str) -> bool:
    plan = WEEKLY_PLAN.get(day_name, {})
    return plan.get("type") == "gym"


def is_rest_day(day_name: str) -> bool:
    plan = WEEKLY_PLAN.get(day_name, {})
    return plan.get("type") == "rest"


def format_plan_for_ai(day_name: str) -> str:
    """Format today's plan as readable text for the AI context"""
    plan = get_today_plan(day_name)
    if not plan:
        return "لا توجد خطة لهذا اليوم"

    lines = [f"📋 خطة اليوم ({plan.get('name_ar', plan.get('name', ''))}):\n"]

    if plan["type"] == "gym":
        for i, ex in enumerate(plan.get("exercises", []), 1):
            note = f" ({ex['note']})" if ex.get('note') else ''
            lines.append(f"{i}. {ex['name_ar']} — {ex['sets']} مجموعات × {ex['reps']}{note}")
    elif plan["type"] == "track":
        lines.append(f"التمهيد: {plan.get('drills_ar', '')}")
        lines.append(f"التمرين الرئيسي: {plan.get('main_ar', '')}")
        if plan.get('rest_ar'):
            lines.append(f"الراحة: {plan['rest_ar']}")
        if plan.get('alternative_ar'):
            lines.append(f"البديل: {plan['alternative_ar']}")
    elif plan["type"] == "rest":
        lines.append(plan.get('details_ar', 'راحة تامة'))

    if day_name in HYBRID_TAX.get("days", []):
        lines.append(f"\n⚠️ ضريبة الهايبرد: {HYBRID_TAX['rule_ar']}")

    return "\n".join(lines)
