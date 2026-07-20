"""
نظام السؤال على الحال - check-ins عشوائية
"""
import logging
import random
from datetime import datetime, date

from config import (
    CHECKIN_MIN_INTERVAL, CHECKIN_MAX_INTERVAL, SLEEP_HOUR,
    PRAYER_NAMES_AR
)

logger = logging.getLogger(__name__)


class CheckinManager:
    def __init__(self, db, scheduler, ai_engine, send_message_func):
        self.db = db
        self.scheduler = scheduler
        self.ai = ai_engine
        self.send_message = send_message_func
        self._active = True

    def start(self):
        """Start the check-in cycle"""
        self._active = True
        self._schedule_next()

    def stop(self):
        self._active = False

    def _schedule_next(self):
        """Schedule the next random check-in"""
        if not self._active:
            return

        if self.is_sleep_time():
            logger.info("Sleep time - no more check-ins until Fajr")
            return

        self.scheduler.schedule_checkin(
            self._on_checkin,
            min_minutes=CHECKIN_MIN_INTERVAL,
            max_minutes=CHECKIN_MAX_INTERVAL
        )

    async def _on_checkin(self):
        """Called when it's time for a check-in"""
        if not self._active or self.is_sleep_time():
            return

        try:
            # Build context for AI
            today_str = date.today().isoformat()
            prayers = self.db.get_today_prayers(today_str)
            meals = self.db.get_today_meals(today_str)
            workout = self.db.get_today_workout(today_str)

            day_summary = self._build_day_summary(prayers, meals, workout)

            now = datetime.now()
            current_time = now.strftime('%H:%M')

            # Get last interaction time
            recent = self.db.get_recent_messages(limit=1)
            last_interaction = recent[-1]['content'][:50] if recent else "لا يوجد تفاعل سابق"

            message = await self.ai.generate_checkin_message(
                current_time=current_time,
                last_interaction=last_interaction,
                day_summary=day_summary
            )

            await self.send_message(message)

        except Exception as e:
            logger.error(f"Check-in error: {e}")
        finally:
            # Schedule next check-in
            self._schedule_next()

    def is_sleep_time(self) -> bool:
        """Check if it's sleep time (2 AM to Fajr)"""
        now = datetime.now()
        hour = now.hour
        # Sleep from 2 AM until Fajr (which the prayer system handles)
        return SLEEP_HOUR <= hour < 3  # 2 AM to ~3:30 AM (Fajr will wake up)

    def _build_day_summary(self, prayers, meals, workout) -> str:
        lines = []

        if prayers:
            done = sum(1 for p in prayers if p['prayed'])
            lines.append(f"الصلوات: {done}/{len(prayers)}")

        if meals:
            total_kcal = sum(m.get('calories', 0) for m in meals)
            lines.append(f"الأكل: {len(meals)} وجبات ({total_kcal} سعر)")
        else:
            lines.append("الأكل: لم يسجل شيء")

        if workout:
            status = "تم" if workout.get('completed') else "لم يتم"
            lines.append(f"التمرين: {status}")
        else:
            lines.append("التمرين: لم يسجل")

        return " | ".join(lines)

    async def send_morning_greeting(self, prayed_fajr: bool, today_plan: str):
        """Send morning greeting after Fajr"""
        message = await self.ai.generate_morning_greeting(
            prayed_fajr=prayed_fajr,
            today_plan=today_plan
        )
        await self.send_message(message)

    async def send_daily_report(self):
        """Send end-of-day report (before sleep at ~1:45 AM)"""
        today_str = date.today().isoformat()

        # Get all stats
        prayers = self.db.get_today_prayers(today_str)
        meals = self.db.get_today_meals(today_str)
        workout = self.db.get_today_workout(today_str)
        macros = self.db.get_total_macros(today_str)
        score_data = self.db.update_daily_score(today_str)

        prayers_done = sum(1 for p in prayers if p['prayed'])
        prayers_summary = f"{prayers_done}/5"
        if prayers:
            for p in prayers:
                name_ar = PRAYER_NAMES_AR.get(p['prayer_name'], p['prayer_name'])
                status = "✅" if p['prayed'] else "❌"
                prayers_summary += f"\n  {status} {name_ar}"

        food_summary = f"{macros['total_kcal']} سعر | {macros['total_protein']}g بروتين"
        if meals:
            food_summary += f" ({len(meals)} وجبات)"

        workout_summary = "لم يتمرن"
        if workout:
            workout_summary = f"{workout.get('workout_type', '')} — {'تم ✅' if workout.get('completed') else 'لم يكتمل'}"

        message = await self.ai.generate_daily_report(
            prayers_summary=prayers_summary,
            food_summary=food_summary,
            workout_summary=workout_summary,
            score=score_data['score']
        )
        await self.send_message(message)

    async def send_water_reminder(self):
        """Send water reminder"""
        reminders = [
            "💧 شربت مية كفاية النهارده؟ جسمك محتاج ترطيب!",
            "💧 فكّرتك بالماء! اشرب كوباية دلوقتي",
            "💧 الماء مهم للعضلات والتركيز — اشرب!",
            "💧 هل شربت ٨ أكواب مية النهارده؟",
            "💧 قم اشرب ماء يا بطل!"
        ]
        await self.send_message(random.choice(reminders))
