"""
نظام الصلاة - جلب المواقيت والتذكيرات والمتابعة
"""
import aiohttp
import logging
from datetime import datetime, date, timedelta

from config import (
    CITY, COUNTRY, PRAYER_METHOD, PRAYER_NAMES_AR, PRAYER_ORDER,
    PRAYER_FOLLOWUP_INTERVAL, FAJR_FOLLOWUP_INTERVAL, MAX_FOLLOWUP_DURATION
)

logger = logging.getLogger(__name__)


class PrayerManager:
    def __init__(self, db, scheduler, ai_engine, send_message_func):
        """
        Args:
            db: Database instance
            scheduler: BotScheduler instance
            ai_engine: AIEngine instance
            send_message_func: async function(text) to send message to user
        """
        self.db = db
        self.scheduler = scheduler
        self.ai = ai_engine
        self.send_message = send_message_func
        self.today_times = {}  # {"Fajr": "04:15", ...}
        self._fajr_responded = False

    async def fetch_prayer_times(self) -> dict:
        """Fetch today's prayer times from AlAdhan API"""
        url = f"https://api.aladhan.com/v1/timingsByCity"
        params = {
            "city": CITY,
            "country": COUNTRY,
            "method": PRAYER_METHOD
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    timings = data['data']['timings']
                    self.today_times = {
                        prayer: timings[prayer]
                        for prayer in PRAYER_ORDER
                    }
                    logger.info(f"Prayer times fetched: {self.today_times}")
                    return self.today_times
        except Exception as e:
            logger.error(f"Failed to fetch prayer times: {e}")
            # Fallback approximate times for Tanta
            self.today_times = {
                "Fajr": "03:30", "Dhuhr": "12:00", "Asr": "15:40",
                "Maghrib": "19:00", "Isha": "20:30"
            }
            return self.today_times

    async def setup_daily_prayers(self):
        """Called at midnight (or startup) to setup all prayer reminders for the day"""
        self.scheduler.cancel_all_prayer_jobs()
        self._fajr_responded = False

        times = await self.fetch_prayer_times()
        today_str = date.today().isoformat()

        now = datetime.now()

        for prayer_name, time_str in times.items():
            # Log prayer in database
            self.db.log_prayer(today_str, prayer_name, time_str)

            # Parse time
            hour, minute = map(int, time_str.split(':'))
            prayer_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Only schedule future prayers
            if prayer_dt > now:
                self.scheduler.schedule_prayer_reminder(
                    prayer_name, prayer_dt, self.on_adhan
                )
                logger.info(f"Scheduled {prayer_name} at {time_str}")
            else:
                logger.info(f"Skipped {prayer_name} at {time_str} (already passed)")

    async def on_adhan(self, prayer_name: str):
        """Called when prayer time arrives"""
        today_str = date.today().isoformat()
        prayer_ar = PRAYER_NAMES_AR.get(prayer_name, prayer_name)

        # Check if previous prayer was missed
        idx = PRAYER_ORDER.index(prayer_name)
        if idx > 0:
            prev_prayer = PRAYER_ORDER[idx - 1]
            prev_status = self.db.get_prayer_status(today_str, prev_prayer)
            if prev_status and not prev_status['prayed']:
                # Previous prayer missed - send rebuke
                rebuke = await self.ai.generate_rebuke(prev_prayer)
                await self.send_message(rebuke)

        # Send adhan notification
        reminder = await self.ai.generate_prayer_reminder(prayer_name, 1)
        await self.send_message(reminder)

        # Schedule follow-up reminders
        interval = FAJR_FOLLOWUP_INTERVAL if prayer_name == "Fajr" else PRAYER_FOLLOWUP_INTERVAL
        self.scheduler.schedule_followup_reminders(
            prayer_name, self.on_followup_reminder,
            interval_minutes=interval,
            max_duration_minutes=MAX_FOLLOWUP_DURATION
        )

        # For Fajr, also schedule the special buzzer
        if prayer_name == "Fajr":
            self._fajr_responded = False

    async def on_followup_reminder(self, prayer_name: str):
        """Called for follow-up reminders"""
        today_str = date.today().isoformat()
        status = self.db.get_prayer_status(today_str, prayer_name)

        if status and status['prayed']:
            # Already prayed, cancel reminders
            self.scheduler.cancel_followup_reminders(prayer_name)
            return

        # Increment reminder count
        self.db.increment_reminders(today_str, prayer_name)
        count = (status['reminders_sent'] + 1) if status else 1

        # Generate varied reminder
        reminder = await self.ai.generate_prayer_reminder(prayer_name, count + 1)
        await self.send_message(reminder)

    async def handle_prayed(self, prayer_name: str = None) -> str:
        """Handle when user says they prayed. Returns response text."""
        today_str = date.today().isoformat()

        # Find which prayer they're responding to
        if not prayer_name:
            # Get the most recent unprayed prayer
            pending = self.db.get_current_pending_prayer(today_str)
            if pending:
                prayer_name = pending['prayer_name']
            else:
                # Default to most recent prayer
                prayer_name = self._get_most_recent_prayer()

        if not prayer_name:
            return "ما شاء الله عليك! ربنا يتقبل 🤲"

        # Mark as prayed
        self.db.mark_prayed(today_str, prayer_name)

        # Cancel follow-up reminders
        self.scheduler.cancel_followup_reminders(prayer_name)

        # Cancel Fajr buzzer if it was Fajr
        if prayer_name == "Fajr":
            self.scheduler.cancel_fajr_buzzer()
            self._fajr_responded = True

        # Generate encouragement + dhikr
        from data.adhkar import get_random_dhikr
        used_ids = self.db.get_used_adhkar_today(today_str)
        dhikr = get_random_dhikr(used_ids)

        if dhikr:
            self.db.log_dhikr(today_str, prayer_name, dhikr['id'], dhikr['text'])

        encouragement = await self.ai.generate_encouragement(prayer_name)

        response = encouragement
        if dhikr:
            response += f"\n\n💎 {dhikr['text']}\n📖 {dhikr['source']}"

        return response

    def _get_most_recent_prayer(self) -> str:
        """Get the most recent prayer based on current time"""
        now = datetime.now()
        for prayer_name in reversed(PRAYER_ORDER):
            time_str = self.today_times.get(prayer_name)
            if time_str:
                h, m = map(int, time_str.split(':'))
                prayer_time = now.replace(hour=h, minute=m)
                if prayer_time <= now:
                    return prayer_name
        return PRAYER_ORDER[0]

    def get_prayer_status_text(self) -> str:
        """Get today's prayer status as readable text"""
        today_str = date.today().isoformat()
        prayers = self.db.get_today_prayers(today_str)

        if not prayers:
            return "لم يتم تسجيل صلوات اليوم بعد"

        lines = ["🕌 حالة صلوات اليوم:\n"]
        for p in prayers:
            name_ar = PRAYER_NAMES_AR.get(p['prayer_name'], p['prayer_name'])
            status = "✅" if p['prayed'] else "❌"
            time_str = p.get('adhan_time', '')
            prayed_at = f" (صلّيت الساعة {p['prayed_at']})" if p.get('prayed_at') else ""
            lines.append(f"{status} {name_ar} — {time_str}{prayed_at}")

        done = sum(1 for p in prayers if p['prayed'])
        lines.append(f"\n📊 {done}/5 صلوات")

        return "\n".join(lines)

    def is_fajr_responded(self) -> bool:
        return self._fajr_responded
