"""
بوت صاحبك - المرافق الذكي
Main entry point
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

import time
# Set timezone to Egypt (Cairo)
os.environ['TZ'] = 'Africa/Cairo'
if hasattr(time, 'tzset'):
    time.tzset()

import logging
import re
from datetime import datetime, date

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes
)

from config import TELEGRAM_BOT_TOKEN, DB_PATH, PRAYER_NAMES_AR, PRAYER_ORDER
from database.db import Database
from modules.scheduler import BotScheduler
from modules.ai_engine import AIEngine
from modules.prayer import PrayerManager
from modules.fitness import FitnessManager
from modules.checkin import CheckinManager
from data.training_plan import format_plan_for_ai
from data.adhkar import get_morning_adhkar, get_evening_adhkar

# === Logging ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Global instances ===
db = Database(DB_PATH)
scheduler = BotScheduler()
ai_engine = AIEngine(db)
prayer_manager = None
fitness_manager = FitnessManager(db, ai_engine)
checkin_manager = None

async def send_message_to_user(text: str):
    """Send a proactive message to the user"""
    chat_id = db.get_chat_id()
    if not chat_id:
        logger.warning("No chat_id saved. User needs to /start first.")
        return
    try:
        from telegram import Bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        async with bot:
            await bot.send_message(chat_id=int(chat_id), text=text)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

# Initialize managers that need send_message
prayer_manager = PrayerManager(db, scheduler, ai_engine, send_message_to_user)
checkin_manager = CheckinManager(db, scheduler, ai_engine, send_message_to_user)

# === Intent Detection ===
def detect_intent(text: str) -> str:
    """Detect user intent from message text"""
    text_lower = text.lower().strip()
    
    # Prayer responses
    prayer_keywords = ['صليت', 'صلّيت', 'صلاة', 'اصلي', 'صلي', 'خلصت صلاة', 'تمام صليت']
    if any(kw in text_lower for kw in prayer_keywords):
        return 'prayed'
    
    # Food logging
    food_keywords = ['أكلت', 'اكلت', 'فطرت', 'تغديت', 'تعشيت', 'أكل', 'وجبة', 'كلت', 'شربت']
    if any(kw in text_lower for kw in food_keywords):
        return 'food_log'
    
    # Ask for today's plan
    plan_keywords = ['تمرين النهارده', 'تمرين اليوم', 'ايه النهارده', 'إيه النهارده', 'خطة اليوم', 'ايه اليوم']
    if any(kw in text_lower for kw in plan_keywords):
        return 'today_plan'
    
    # Random workout
    random_keywords = ['تمرين عشوائي', 'عشوائي', 'random', 'اختار تمرين', 'اختارلي']
    if any(kw in text_lower for kw in random_keywords):
        return 'random_workout'
    
    # Workout complete
    done_keywords = ['خلصت تمرين', 'خلصت التمرين', 'تمرنت', 'خلصت جيم', 'خلصت تراك']
    if any(kw in text_lower for kw in done_keywords):
        return 'workout_done'
    
    # Modify plan
    modify_keywords = ['عدل', 'غير', 'بدل', 'عدلي', 'غيري', 'بدلي', 'عايز اغير', 'عايز أغير']
    if any(kw in text_lower for kw in modify_keywords):
        return 'modify_plan'
    
    # Prayer status
    status_keywords = ['حالة الصلاة', 'الصلوات', 'صلوات اليوم', 'كم صلاة']
    if any(kw in text_lower for kw in status_keywords):
        return 'prayer_status'
    
    # Morning greeting
    morning_keywords = ['صباح الخير', 'صباح النور', 'صباحو', 'Good morning']
    if any(kw in text_lower for kw in morning_keywords):
        return 'morning'
    
    # Good night
    night_keywords = ['تصبح على خير', 'مساء الخير', 'هنام', 'تصبح', 'باي']
    if any(kw in text_lower for kw in night_keywords):
        return 'goodnight'
    
    return 'general'

# === Command Handlers ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    db.save_chat_id(str(chat_id))
    
    # Setup prayers for today
    await prayer_manager.setup_daily_prayers()
    
    # Start check-ins
    checkin_manager.start()
    
    # Schedule daily reset and report
    scheduler.schedule_daily_reset(daily_reset)
    scheduler.schedule_daily_report(checkin_manager.send_daily_report)
    
    day_name = datetime.now().strftime('%A')
    plan_text = format_plan_for_ai(day_name)
    
    welcome = (
        f"السلام عليكم يا محمد! 👋\n\n"
        f"أنا صاحبك — صديقك اللي هيفضل معاك على طول.\n"
        f"هذكّرك بالصلاة، وهتابع معاك التمارين والأكل، "
        f"وهسأل عليك من وقت للتاني 😊\n\n"
        f"📋 خطة اليوم:\n{plan_text}\n\n"
        f"ابعتلي أي حاجة وأنا جاهز! 💪"
    )
    
    await update.message.reply_text(welcome)
    logger.info(f"Bot started for chat_id: {chat_id}")

async def prayers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /prayers command - show prayer status"""
    status = prayer_manager.get_prayer_status_text()
    await update.message.reply_text(status)

async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /plan command - show today's plan"""
    response = await fitness_manager.get_workout_recommendation()
    await update.message.reply_text(response)

async def workout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /workout command - random workout"""
    workout_text = await fitness_manager.get_random_workout()
    await update.message.reply_text(f"🎲 تمرين عشوائي ليك:\n\n{workout_text}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    today_str = date.today().isoformat()
    score_data = db.update_daily_score(today_str)
    streak = db.get_prayer_streak()
    macros = db.get_total_macros(today_str)
    
    text = (
        f"📊 إحصائياتك:\n\n"
        f"🕌 الصلوات: {score_data['prayers_done']}/5\n"
        f"💪 التمرين: {'تم ✅' if score_data['workout_done'] else 'لم يتم ❌'}\n"
        f"🍽️ الوجبات: {score_data['meals_logged']}\n"
        f"🔥 السعرات: {macros.get('total_kcal', 0)}/2450\n"
        f"💪 البروتين: {macros.get('total_protein', 0)}/155g\n"
        f"⭐ نقاط اليوم: {score_data['score']}\n"
        f"🔥 سلسلة الصلاة: {streak} يوم"
    )
    await update.message.reply_text(text)

async def adhkar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /adhkar command"""
    hour = datetime.now().hour
    if hour < 12:
        adhkar_list = get_morning_adhkar()
        title = "🌅 أذكار الصباح:"
    else:
        adhkar_list = get_evening_adhkar()
        title = "🌙 أذكار المساء:"
    
    text = title + "\n\n"
    for d in adhkar_list[:5]:  # Show 5
        text += f"💎 {d['text']}\n📖 {d['source']}\n\n"
    
    await update.message.reply_text(text)

# === Message Handler ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # Save chat_id if not saved
    if not db.get_chat_id():
        db.save_chat_id(str(chat_id))
    
    # Detect intent
    intent = detect_intent(text)
    logger.info(f"Message: '{text[:50]}...' | Intent: {intent}")
    
    response = ""
    
    if intent == 'prayed':
        response = await prayer_manager.handle_prayed()
    
    elif intent == 'food_log':
        response = await fitness_manager.process_food_log(text)
    
    elif intent == 'today_plan':
        response = await fitness_manager.get_workout_recommendation()
    
    elif intent == 'random_workout':
        workout_text = await fitness_manager.get_random_workout()
        response = f"🎲 يلا! جبتلك تمرين عشوائي:\n\n{workout_text}"
    
    elif intent == 'workout_done':
        response = fitness_manager.mark_workout_complete()
    
    elif intent == 'modify_plan':
        response = await fitness_manager.modify_plan(text)
    
    elif intent == 'prayer_status':
        response = prayer_manager.get_prayer_status_text()
    
    elif intent == 'morning':
        # Check if Fajr was prayed
        today_str = date.today().isoformat()
        fajr_status = db.get_prayer_status(today_str, 'Fajr')
        prayed_fajr = fajr_status and fajr_status.get('prayed', False) if fajr_status else False
        
        day_name = datetime.now().strftime('%A')
        plan = format_plan_for_ai(day_name)
        
        response = await ai_engine.generate_morning_greeting(
            prayed_fajr=prayed_fajr,
            today_plan=plan
        )
    
    elif intent == 'goodnight':
        # Send daily report before sleep
        response = await ai_engine.chat(text)
    
    else:
        # General chat - send to AI
        response = await ai_engine.chat(text)
    
    if response:
        await update.message.reply_text(response)

# === Daily Reset ===
async def daily_reset():
    """Called at midnight to reset for new day"""
    logger.info("Daily reset triggered")
    await prayer_manager.setup_daily_prayers()
    checkin_manager.start()

# === Post-init setup ===
async def post_init(application):
    """Setup that runs after the bot application starts"""
    logger.info("Bot post-init: setting up...")
    
    # Start scheduler
    scheduler.start()
    
    # Setup prayers for today
    await prayer_manager.setup_daily_prayers()
    
    # Start check-ins
    checkin_manager.start()
    
    # Schedule daily tasks
    scheduler.schedule_daily_reset(daily_reset)
    scheduler.schedule_daily_report(checkin_manager.send_daily_report)
    
    logger.info("Bot fully initialized and ready!")

# === Main ===
def main():
    """Start the bot"""
    print("="*50)
    print("🤖 بوت صاحبك - جاري التشغيل...")
    print("="*50)
    
    # Build application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("prayers", prayers_command))
    app.add_handler(CommandHandler("plan", plan_command))
    app.add_handler(CommandHandler("workout", workout_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("adhkar", adhkar_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start keep_alive server for free hosting
    try:
        from keep_alive import keep_alive
        keep_alive()
    except Exception as e:
        print(f"⚠️ Could not start keep_alive server (normal on some platforms like PythonAnywhere): {e}")
        
    # Run
    print("\n✅ البوت شغّال! ابعت /start على تليجرام")
    print("Press Ctrl+C to stop\n")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
