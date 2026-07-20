"""
إعدادات بوت صاحبك
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# === API Keys ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# === Location (لمواقيت الصلاة) ===
CITY = os.getenv("CITY", "Tanta")
COUNTRY = os.getenv("COUNTRY", "Egypt")
PRAYER_METHOD = int(os.getenv("PRAYER_METHOD", "5"))  # هيئة المساحة المصرية

# === AI Model ===
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")

# === Database ===
DB_PATH = str(BASE_DIR / "database" / "shefo.db")

# === أسماء الصلوات ===
PRAYER_NAMES_AR = {
    "Fajr": "الفجر",
    "Dhuhr": "الظهر",
    "Asr": "العصر",
    "Maghrib": "المغرب",
    "Isha": "العشاء",
}

PRAYER_ORDER = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

# === توقيتات التذكير ===
PRAYER_FOLLOWUP_INTERVAL = 2     # دقائق بين كل تذكير
FAJR_FOLLOWUP_INTERVAL = 1       # دقيقة واحدة للفجر
MAX_FOLLOWUP_DURATION = 30       # أقصى مدة للتذكيرات بالدقائق

# === توقيتات السؤال على الحال ===
CHECKIN_MIN_INTERVAL = 60        # أقل فاصل بين كل سؤال (بالدقائق)
CHECKIN_MAX_INTERVAL = 180       # أكبر فاصل
CHECKIN_JITTER_MINUTES = 15      # تذبذب عشوائي (± دقائق)

# === ساعات النوم ===
SLEEP_HOUR = 2                   # الساعة 2 الفجر → ينام البوت
# يصحى عند أذان الفجر تلقائياً

# === أهداف التغذية اليومية ===
DAILY_CALORIES_TARGET = 2450
DAILY_PROTEIN_TARGET = 155
CALORIES_WARNING_THRESHOLD = 2720  # لو تعدى ده يحذّر
