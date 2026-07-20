"""
قاعدة بيانات الطعام - مستخرجة من Shefo Macro Pilot
"""

# السعرات والبروتين لكل 100 جرام
FOOD_DB = {
    "chicken_breast": {"name_ar": "صدور دجاج", "kcal_per_100g": 165, "protein_per_100g": 31, "category": "protein"},
    "whole_eggs": {"name_ar": "بيض كامل", "kcal_per_100g": 155, "protein_per_100g": 13, "category": "protein", "note": "1 egg ≈ 50g"},
    "white_rice_cooked": {"name_ar": "أرز أبيض مطبوخ", "kcal_per_100g": 130, "protein_per_100g": 2.7, "category": "carb"},
    "egyptian_bread": {"name_ar": "عيش بلدي", "kcal_per_100g": 260, "protein_per_100g": 8, "category": "carb", "note": "1 loaf ≈ 60g"},
    "fava_beans": {"name_ar": "فول مدمس", "kcal_per_100g": 110, "protein_per_100g": 8, "category": "carb"},
    "lentils_cooked": {"name_ar": "عدس مطبوخ", "kcal_per_100g": 116, "protein_per_100g": 9, "category": "carb"},
    "peanuts": {"name_ar": "فول سوداني", "kcal_per_100g": 567, "protein_per_100g": 26, "category": "fat"},
    "banana": {"name_ar": "موز", "kcal_per_100g": 89, "protein_per_100g": 1.1, "category": "carb", "note": "1 large ≈ 120g"},
    "white_pasta_cooked": {"name_ar": "مكرونة بيضاء مطبوخة", "kcal_per_100g": 131, "protein_per_100g": 5, "category": "carb"},
    "potatoes": {"name_ar": "بطاطس", "kcal_per_100g": 87, "protein_per_100g": 2, "category": "carb"},
    "lean_red_meat": {"name_ar": "لحم أحمر", "kcal_per_100g": 250, "protein_per_100g": 26, "category": "protein"},
    "white_fish": {"name_ar": "سمك أبيض (بلطي/باسا)", "kcal_per_100g": 110, "protein_per_100g": 21, "category": "protein"},
    "canned_tuna": {"name_ar": "تونة معلبة (مصفاة)", "kcal_per_100g": 138, "protein_per_100g": 26, "category": "protein"},
    "edam_cheese": {"name_ar": "جبنة (إيدام/رومي/شيدر)", "kcal_per_100g": 450, "protein_per_100g": 15, "category": "fat", "note": "Max 60g"},
    "peanut_butter": {"name_ar": "زبدة فول سوداني", "kcal_per_100g": 540, "protein_per_100g": 25, "category": "fat"},
    "milk": {"name_ar": "لبن", "kcal_per_100g": 60, "protein_per_100g": 3.2, "category": "protein", "note": "per 100ml"},
    "sugar": {"name_ar": "سكر", "kcal_per_100g": 400, "protein_per_100g": 0, "category": "carb"},
    "coffee": {"name_ar": "قهوة سوداء", "kcal_per_100g": 2, "protein_per_100g": 0, "category": "other"},
    "green_salad": {"name_ar": "سلطة خضراء", "kcal_per_100g": 15, "protein_per_100g": 1, "category": "other"},
}

# الخطة الغذائية الأساسية
BASE_MEAL_PLAN = {
    "breakfast": {
        "name_ar": "الفطور",
        "items": [
            {"food": "fava_beans", "grams": 150, "note_ar": "البديل: ٥٠ جرام جبنة رومي أو ٢٥٠ مل لبن أو ١٥٠ جرام عدس"},
            {"food": "whole_eggs", "grams": 200, "note_ar": "٤ بيضات كاملة (مسلوقة أو أومليت)"},
            {"food": "egyptian_bread", "grams": 90, "note_ar": "١.٥ رغيف بلدي"},
        ],
        "total_kcal": 705,
        "total_protein": 45
    },
    "pre_workout": {
        "name_ar": "ما قبل التمرين",
        "items": [
            {"food": "banana", "grams": 120, "note_ar": "موزة كبيرة"},
            {"food": "peanuts", "grams": 60, "note_ar": "فول سوداني"},
            {"food": "coffee", "grams": 200, "note_ar": "كوب قهوة سوداء + ٣ ملاعق سكر"},
        ],
        "total_kcal": 505,
        "total_protein": 17
    },
    "lunch": {
        "name_ar": "الغداء",
        "items": [
            {"food": "white_rice_cooked", "grams": 300, "note_ar": "أرز أبيض مطبوخ"},
            {"food": "chicken_breast", "grams": 150, "note_ar": "صدور دجاج مطبوخة"},
            {"food": "green_salad", "grams": 100, "note_ar": "سلطة خضراء"},
        ],
        "total_kcal": 640,
        "total_protein": 55
    },
    "dinner": {
        "name_ar": "العشاء",
        "items": [
            {"food": "fava_beans", "grams": 200, "note_ar": "البديل: ٦٠ جرام جبنة رومي أو ٣٥٠ مل لبن أو ٢٠٠ جرام عدس"},
            {"food": "whole_eggs", "grams": 150, "note_ar": "٣ بيضات مسلوقة"},
            {"food": "egyptian_bread", "grams": 60, "note_ar": "رغيف بلدي"},
        ],
        "total_kcal": 600,
        "total_protein": 38
    }
}

# القواعد الغذائية
FOOD_RULES = {
    "daily_target_kcal": 2450,
    "daily_target_protein": 155,
    "warning_threshold_kcal": 2720,
    "banned_foods": ["واي بروتين", "جبنة قريش", "بياض بيض فقط (كل البيضة كاملة دائماً)"],
    "banned_foods_en": ["Whey Protein", "Cottage Cheese", "Egg Whites alone"],
    "max_eggs_dinner": 3,
    "max_cheese_grams": 60,
    "hybrid_tax": "في أيام التراك أضف ١٠٠ جرام عيش بلدي أو ١٠٠ جرام أرز مطبوخ"
}

# Exchange Matrix
EXCHANGE_MATRIX = {
    "carb": {
        "description_ar": "بدائل الكربوهيدرات (~١٣٠ سعر و ٢٨ جرام كارب)",
        "items": [
            {"name_ar": "أرز أبيض مطبوخ", "grams": 100},
            {"name_ar": "مكرونة بيضاء مطبوخة", "grams": 100},
            {"name_ar": "عيش بلدي", "grams": 50, "note": "تقريباً رغيف"},
            {"name_ar": "بطاطس مسلوقة/إير فراير", "grams": 150},
            {"name_ar": "فول مدمس مطبوخ", "grams": 150},
            {"name_ar": "عدس مطبوخ", "grams": 110},
        ]
    },
    "protein": {
        "description_ar": "بدائل البروتين (~١٦٥ سعر و ٣١ جرام بروتين)",
        "items": [
            {"name_ar": "صدور دجاج", "grams": 100},
            {"name_ar": "لحم أحمر", "grams": 100},
            {"name_ar": "سمك أبيض (بلطي/باسا)", "grams": 150},
            {"name_ar": "تونة معلبة مصفاة", "grams": 120},
            {"name_ar": "٣ بيضات كاملة", "grams": 150},
        ]
    },
    "fat": {
        "description_ar": "بدائل الدهون (~١٣٥ سعر و ١٥ جرام دهون)",
        "items": [
            {"name_ar": "فول سوداني", "grams": 30},
            {"name_ar": "جبنة إيدام/رومي/شيدر", "grams": 30, "note": "ممنوع جبنة قريش"},
            {"name_ar": "زبدة فول سوداني بدون سكر", "grams": 25},
        ]
    }
}


def calculate_macros(food_key: str, grams: float) -> dict:
    """Calculate kcal and protein for given food and grams"""
    food = FOOD_DB.get(food_key)
    if not food:
        return {"kcal": 0, "protein": 0, "error": f"Food '{food_key}' not found"}
    kcal = round(food["kcal_per_100g"] * grams / 100)
    protein = round(food["protein_per_100g"] * grams / 100, 1)
    return {"kcal": kcal, "protein": protein, "food_ar": food["name_ar"]}


def format_food_db_for_ai() -> str:
    """Format the food database as a readable string for AI context"""
    lines = ["📊 قاعدة بيانات الطعام (لكل ١٠٠ جرام):"]
    for key, food in FOOD_DB.items():
        note = f" ({food['note']})" if food.get('note') else ""
        lines.append(f"• {food['name_ar']}: {food['kcal_per_100g']} سعر، {food['protein_per_100g']}g بروتين{note}")

    lines.append("\n🚫 ممنوعات:")
    for ban in FOOD_RULES['banned_foods']:
        lines.append(f"• {ban}")

    lines.append(f"\n🎯 الأهداف اليومية: {FOOD_RULES['daily_target_kcal']} سعر | {FOOD_RULES['daily_target_protein']}g بروتين")
    return "\n".join(lines)


def format_meal_plan_for_ai() -> str:
    """Format the base meal plan for AI context"""
    lines = ["🍽️ الخطة الغذائية الأساسية:"]
    for meal_key, meal in BASE_MEAL_PLAN.items():
        lines.append(f"\n{meal['name_ar']} (~{meal['total_kcal']} سعر | ~{meal['total_protein']}g بروتين):")
        for item in meal['items']:
            food = FOOD_DB.get(item['food'], {})
            lines.append(f"  • {item.get('note_ar', food.get('name_ar', ''))} — {item['grams']}g")
    return "\n".join(lines)
