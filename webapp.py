"""
بوت صاحبك - Flask Webhook Mode
للتشغيل على PythonAnywhere (الحساب المجاني)
"""
import os
import sys
import json
import asyncio
import logging
import random
from datetime import datetime, date, timedelta
from pathlib import Path

# Fix paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Set timezone
os.environ['TZ'] = 'Africa/Cairo'
import time as _time
if hasattr(_time, 'tzset'):
    _time.tzset()

from flask import Flask, request, jsonify

from config import (
    TELEGRAM_BOT_TOKEN, DB_PATH, PRAYER_NAMES_AR, PRAYER_ORDER,
    CITY, COUNTRY, PRAYER_METHOD, DAILY_CALORIES_TARGET, DAILY_PROTEIN_TARGET
)
from database.db import Database
from modules.ai_engine import AIEngine
from modules.fitness import FitnessManager
from data.training_plan import format_plan_for_ai
from data.adhkar import get_morning_adhkar, get_evening_adhkar, get_random_dhikr

# === Logging ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Flask App ===
app = Flask(__name__)

# === Initialize Components (once at startup) ===
db = Database(DB_PATH)
ai_engine = AIEngine(db)
fitness_manager = FitnessManager(db, ai_engine)


# ============================================================
#  HELPERS
# ============================================================

def run_async(coro):
    """Run an async coroutine from sync Flask context."""
    return asyncio.run(coro)


async def _send_telegram(chat_id, text):
    """Send a message via Telegram Bot API."""
    from telegram import Bot
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    async with bot:
        await bot.send_message(chat_id=int(chat_id), text=text)


def send_message(text):
    """Send a proactive message to the saved user."""
    chat_id = db.get_chat_id()
    if not chat_id:
        logger.warning("No chat_id saved — user needs to /start first")
        return
    try:
        run_async(_send_telegram(chat_id, text))
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


# ============================================================
#  INTENT DETECTION (same logic as bot.py)
# ============================================================

def detect_intent(text: str) -> str:
    """Detect user intent from message text."""
    text_lower = text.lower().strip()

    # Check if this is a QUESTION (not a statement)
    is_question = (
        '?' in text_lower or '؟' in text_lower
        or text_lower.startswith('هل ')
        or text_lower.startswith('هو انا')
        or text_lower.startswith('هو أنا')
        or 'ولا لا' in text_lower
        or 'انا صليت' in text_lower and ('?' in text_lower or '؟' in text_lower or 'هو' in text_lower)
    )

    # Prayer responses — only if it's a STATEMENT, not a question
    prayer_kw = [
        'صليت', 'صلّيت', 'خلصت صلاة', 'الحمدلله صليت',
        'تمت الصلاة', 'صليتها', 'صليت الصبح', 'صلّيت الصبح'
    ]
    if not is_question \
       and any(kw in text_lower for kw in prayer_kw) \
       and 'هصلي' not in text_lower and 'هقوم' not in text_lower \
       and 'اصلي' not in text_lower:
        return 'prayed'

    # Food
    food_kw = ['أكلت', 'اكلت', 'فطرت', 'تغديت', 'تعشيت',
               'أكل', 'وجبة', 'كلت', 'شربت']
    if any(kw in text_lower for kw in food_kw):
        return 'food_log'

    # Today's plan
    plan_kw = [
        'تمرين النهارده', 'تمرين اليوم', 'ايه النهارده',
        'إيه النهارده', 'خطة اليوم', 'ايه اليوم',
        'تمرينت اليوم', 'تمرينتك', 'تمرينة اليوم', 'تمرينه اليوم'
    ]
    if any(kw in text_lower for kw in plan_kw):
        return 'today_plan'

    # Random workout
    random_kw = [
        'تمرين عشوائي', 'عشوائي', 'random', 'اختار تمرين',
        'اختارلي', 'عشوائيه', 'عشوائية',
        'ادينى تمرين', 'اديني تمرين', 'اديني تمرينه',
        'تمرينه عشوائيه', 'تمرينة عشوائية'
    ]
    if any(kw in text_lower for kw in random_kw):
        return 'random_workout'

    # Workout done
    done_kw = ['خلصت تمرين', 'خلصت التمرين', 'تمرنت',
               'خلصت جيم', 'خلصت تراك']
    if any(kw in text_lower for kw in done_kw):
        return 'workout_done'

    # Modify plan
    modify_kw = ['عدل', 'غير', 'بدل', 'عدلي', 'غيري',
                 'بدلي', 'عايز اغير', 'عايز أغير']
    if any(kw in text_lower for kw in modify_kw):
        return 'modify_plan'

    # Prayer status
    status_kw = ['حالة الصلاة', 'الصلوات', 'صلوات اليوم', 'كم صلاة']
    if any(kw in text_lower for kw in status_kw):
        return 'prayer_status'

    # Morning
    morning_kw = ['صباح الخير', 'صباح النور', 'صباحو']
    if any(kw in text_lower for kw in morning_kw):
        return 'morning'

    # Night
    night_kw = ['تصبح على خير', 'مساء الخير', 'هنام', 'تصبح', 'باي']
    if any(kw in text_lower for kw in night_kw):
        return 'goodnight'

    return 'general'


# ============================================================
#  PRAYER HELPERS
# ============================================================

async def fetch_prayer_times() -> dict:
    """Fetch today's prayer times from AlAdhan API."""
    import aiohttp
    url = "https://api.aladhan.com/v1/timingsByCity"
    params = {"city": CITY, "country": COUNTRY, "method": PRAYER_METHOD}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                timings = data['data']['timings']
                return {p: timings[p] for p in PRAYER_ORDER}
    except Exception as e:
        logger.error(f"Failed to fetch prayer times: {e}")
        # Fallback approximate times for Tanta
        return {
            "Fajr": "03:30", "Dhuhr": "12:00", "Asr": "15:40",
            "Maghrib": "19:00", "Isha": "20:30"
        }


def ensure_today_prayers():
    """Make sure today's prayers exist in the database."""
    today_str = date.today().isoformat()
    prayers = db.get_today_prayers(today_str)
    if not prayers:
        times = run_async(fetch_prayer_times())
        for prayer_name, time_str in times.items():
            db.log_prayer(today_str, prayer_name, time_str)
        prayers = db.get_today_prayers(today_str)
    return prayers


def get_prayer_name_ar(prayer_name: str) -> str:
    """Get Arabic name, using 'الصبح' after 7 AM for Fajr."""
    name_ar = PRAYER_NAMES_AR.get(prayer_name, prayer_name)
    if prayer_name == "Fajr" and datetime.now().hour >= 7:
        name_ar = "الصبح"
    return name_ar


def get_prayer_status_text() -> str:
    """Get today's prayer status as readable text."""
    today_str = date.today().isoformat()
    prayers = db.get_today_prayers(today_str)
    if not prayers:
        return "لم يتم تسجيل صلوات اليوم بعد"

    lines = ["🕌 حالة صلوات اليوم:\n"]
    for p in prayers:
        name_ar = get_prayer_name_ar(p['prayer_name'])
        status = "✅" if p['prayed'] else "❌"
        time_str = p.get('adhan_time', '')
        prayed_at = f" (صلّيت الساعة {p['prayed_at']})" if p.get('prayed_at') else ""
        lines.append(f"{status} {name_ar} — {time_str}{prayed_at}")

    done = sum(1 for p in prayers if p['prayed'])
    lines.append(f"\n📊 {done}/5 صلوات")
    return "\n".join(lines)


def get_most_recent_prayer() -> str:
    """Get the most recent prayer based on current time."""
    today_str = date.today().isoformat()
    prayers = db.get_today_prayers(today_str)
    if not prayers:
        return PRAYER_ORDER[0]

    now = datetime.now()
    for p in reversed(prayers):
        time_str = p.get('adhan_time', '')
        if time_str:
            h, m = map(int, time_str.split(':'))
            prayer_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if prayer_time <= now:
                return p['prayer_name']
    return PRAYER_ORDER[0]


async def handle_prayed() -> str:
    """Handle when user says they prayed."""
    today_str = date.today().isoformat()
    prayer_name = get_most_recent_prayer()

    if not prayer_name:
        return "ما شاء الله عليك! ربنا يتقبل 🤲"

    # Mark as prayed
    db.mark_prayed(today_str, prayer_name)

    # Generate encouragement + dhikr
    used_ids = db.get_used_adhkar_today(today_str)
    dhikr = get_random_dhikr(used_ids)
    if dhikr:
        db.log_dhikr(today_str, prayer_name, dhikr['id'], dhikr['text'])

    encouragement = await ai_engine.generate_encouragement(prayer_name)
    response = encouragement
    if dhikr:
        response += f"\n\n💎 {dhikr['text']}\n📖 {dhikr['source']}"
    return response


# ============================================================
#  ROUTES — Webhook
# ============================================================

@app.route('/')
def home():
    """Health-check endpoint."""
    return "🤖 بوت صاحبك شغّال! ✅"


@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive updates from Telegram."""
    try:
        data = request.get_json(force=True)

        if 'message' not in data:
            return jsonify({"ok": True})

        message = data['message']
        if 'text' not in message:
            return jsonify({"ok": True})

        text = message['text'].strip()
        chat_id = message['chat']['id']

        # Save chat_id on first contact
        if not db.get_chat_id():
            db.save_chat_id(str(chat_id))

        # Make sure prayers are set up for today
        ensure_today_prayers()

        # Route to handler
        if text.startswith('/'):
            response = _handle_command(text, chat_id)
        else:
            response = _handle_text(text)

        if response:
            run_async(_send_telegram(chat_id, response))

        return jsonify({"ok": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({"ok": True})


# ============================================================
#  COMMAND + TEXT HANDLERS
# ============================================================

def _handle_command(text: str, chat_id: int) -> str:
    """Handle slash commands — all responses come from the AI."""
    cmd = text.split()[0].lower().split('@')[0]

    if cmd == '/start':
        db.save_chat_id(str(chat_id))
        ensure_today_prayers()
        # Let the AI welcome the user naturally
        response = run_async(ai_engine.chat(
            "[نظام: محمد بدأ المحادثة لأول مرة. رحّب به، قوله خطة اليوم، وشجعه.]"
        ))
        return _execute_actions(response, '/start')

    elif cmd == '/prayers':
        response = run_async(ai_engine.chat("اعرض لي حالة صلواتي النهاردة"))
        return _execute_actions(response, '/prayers')

    elif cmd == '/plan':
        response = run_async(ai_engine.chat("إيه خطة تمريني النهاردة؟"))
        return _execute_actions(response, '/plan')

    elif cmd == '/workout':
        response = run_async(ai_engine.chat("اديني تمرينة عشوائية"))
        return _execute_actions(response, '/workout')

    elif cmd == '/stats':
        today_str = date.today().isoformat()
        score = db.update_daily_score(today_str)
        streak = db.get_prayer_streak()
        macros = db.get_total_macros(today_str)
        stats_msg = (
            f"اعرض لي إحصائياتي بشكل حلو: "
            f"الصلوات {score['prayers_done']}/5، "
            f"التمرين {'اتعمل' if score['workout_done'] else 'لسه'}، "
            f"الوجبات {score['meals_logged']}، "
            f"السعرات {macros.get('total_kcal', 0)}/2450، "
            f"البروتين {macros.get('total_protein', 0)}/155g، "
            f"النقاط {score['score']}، "
            f"سلسلة الصلاة {streak} يوم"
        )
        return run_async(ai_engine.chat(stats_msg))

    elif cmd == '/adhkar':
        hour = datetime.now().hour
        if hour < 12:
            adhkar_list = get_morning_adhkar()
            title = "🌅 أذكار الصباح:"
        else:
            adhkar_list = get_evening_adhkar()
            title = "🌙 أذكار المساء:"
        out = title + "\n\n"
        for d in adhkar_list[:5]:
            out += f"💎 {d['text']}\n📖 {d['source']}\n\n"
        return out

    return None


def _handle_text(text: str) -> str:
    """Handle ALL text messages — the AI decides everything."""
    logger.info(f"Message: '{text[:50]}'")

    # Send everything to the AI — it has full context and will decide
    response = run_async(ai_engine.chat(text))

    # Parse and execute any [ACTION:XXX] tags the AI included
    response = _execute_actions(response, text)

    return response


def _execute_actions(response: str, original_text: str) -> str:
    """Parse [ACTION:XXX] tags from AI response, execute DB actions, return clean text."""
    clean = response

    if '[ACTION:PRAYED]' in clean:
        clean = clean.replace('[ACTION:PRAYED]', '').strip()
        today_str = date.today().isoformat()
        prayer_name = get_most_recent_prayer()
        if prayer_name:
            db.mark_prayed(today_str, prayer_name)
            # Add a dhikr after the AI's response
            used_ids = db.get_used_adhkar_today(today_str)
            dhikr = get_random_dhikr(used_ids)
            if dhikr:
                db.log_dhikr(today_str, prayer_name, dhikr['id'], dhikr['text'])
                clean += f"\n\n💎 {dhikr['text']}\n📖 {dhikr['source']}"

    if '[ACTION:WORKOUT_DONE]' in clean:
        clean = clean.replace('[ACTION:WORKOUT_DONE]', '').strip()
        fitness_manager.mark_workout_complete()

    if '[ACTION:RANDOM_WORKOUT]' in clean:
        clean = clean.replace('[ACTION:RANDOM_WORKOUT]', '').strip()
        wk = run_async(fitness_manager.get_random_workout())
        clean += f"\n\n{wk}"

    if '[ACTION:FOOD]' in clean:
        clean = clean.replace('[ACTION:FOOD]', '').strip()
        today_str = date.today().isoformat()
        db.log_meal(today_str, 'logged', original_text, 0, 0)

    return clean


# ============================================================
#  CRON ENDPOINTS (called by cron-job.org)
# ============================================================

@app.route('/check_prayers')
def check_prayers():
    """Called every 5 minutes by cron-job.org to send prayer reminders."""
    try:
        chat_id = db.get_chat_id()
        if not chat_id:
            return jsonify({"status": "no_user"})

        today_str = date.today().isoformat()
        prayers = ensure_today_prayers()
        now = datetime.now()
        sent = 0

        for p in prayers:
            name = p['prayer_name']
            adhan_str = p.get('adhan_time', '')
            if not adhan_str or p['prayed']:
                continue

            h, m = map(int, adhan_str.split(':'))
            adhan_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)

            # Within the 30-minute reminder window
            diff = (now - adhan_dt).total_seconds()
            if 0 <= diff <= 1800:
                reminders = p.get('reminders_sent', 0)
                expected = int(diff / 300) + 1  # one every 5 min
                if reminders < expected and reminders < 7:
                    reminder = run_async(ai_engine.generate_prayer_reminder(
                        name, reminders + 1
                    ))
                    send_message(reminder)
                    db.increment_reminders(today_str, name)
                    sent += 1

        return jsonify({"status": "ok", "sent": sent, "time": now.strftime('%H:%M')})
    except Exception as e:
        logger.error(f"Prayer check error: {e}", exc_info=True)
        return jsonify({"status": "error", "msg": str(e)})


@app.route('/check_in')
def check_in():
    """Called every 1-2 hours by cron-job.org for casual check-ins."""
    try:
        chat_id = db.get_chat_id()
        if not chat_id:
            return jsonify({"status": "no_user"})

        now = datetime.now()

        # Don't check in during sleep hours
        if 2 <= now.hour <= 6:
            return jsonify({"status": "sleep_hours"})

        # 40% chance — makes it feel natural, not robotic
        if random.random() > 0.4:
            return jsonify({"status": "skipped"})

        # Build context
        today_str = date.today().isoformat()
        macros = db.get_total_macros(today_str)
        meals = db.get_today_meals(today_str)
        recent = db.get_recent_messages(limit=3)
        last_msg = recent[-1]['content'][:50] if recent else "لا يوجد"
        summary = f"وجبات: {len(meals)}, سعرات: {macros.get('total_kcal', 0)}"

        msg = run_async(ai_engine.generate_checkin_message(
            current_time=now.strftime('%H:%M'),
            last_interaction=last_msg,
            day_summary=summary
        ))
        send_message(msg)
        return jsonify({"status": "sent"})
    except Exception as e:
        logger.error(f"Check-in error: {e}", exc_info=True)
        return jsonify({"status": "error"})


@app.route('/daily_reset')
def daily_reset():
    """Called once at midnight by cron-job.org."""
    try:
        times = run_async(fetch_prayer_times())
        today_str = date.today().isoformat()
        for prayer_name, time_str in times.items():
            db.log_prayer(today_str, prayer_name, time_str)
        return jsonify({"status": "ok", "prayers": times})
    except Exception as e:
        logger.error(f"Daily reset error: {e}")
        return jsonify({"status": "error"})


@app.route('/setup')
def setup():
    """One-time setup: register the Telegram webhook."""
    try:
        host = request.host
        webhook_url = f"https://{host}/webhook"

        async def _set():
            from telegram import Bot
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            async with bot:
                await bot.set_webhook(url=webhook_url)
                info = await bot.get_webhook_info()
                return info.url

        result = run_async(_set())
        ensure_today_prayers()

        return jsonify({
            "status": "✅ تم تفعيل الـ Webhook!",
            "webhook_url": result,
            "message": "البوت شغّال دلوقتي! ابعت /start على تليجرام 🚀"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ============================================================
#  LOCAL DEVELOPMENT
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
