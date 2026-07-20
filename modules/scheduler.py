"""
مدير الجدولة - APScheduler wrapper
"""
import random
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class BotScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone='Africa/Cairo')
        self._reminder_jobs = {}  # prayer_name -> list of job_ids

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def schedule_at_time(self, job_id: str, run_time: datetime, callback, **kwargs):
        """Schedule a one-time job at specific datetime"""
        try:
            self.scheduler.add_job(
                callback,
                trigger=DateTrigger(run_date=run_time),
                id=job_id,
                replace_existing=True,
                kwargs=kwargs
            )
            logger.info(f"Scheduled job {job_id} at {run_time}")
        except Exception as e:
            logger.error(f"Error scheduling job {job_id}: {e}")

    def schedule_prayer_reminder(self, prayer_name: str, adhan_time: datetime, callback):
        """Schedule the initial prayer adhan notification"""
        job_id = f"adhan_{prayer_name}"
        self.schedule_at_time(job_id, adhan_time, callback, prayer_name=prayer_name)

    def schedule_followup_reminders(self, prayer_name: str, callback, interval_minutes: int = 2, max_duration_minutes: int = 30):
        """Schedule recurring follow-up reminders for a prayer"""
        job_id = f"followup_{prayer_name}"

        # Cancel existing followups first
        self.cancel_followup_reminders(prayer_name)

        # Schedule interval job
        self.scheduler.add_job(
            callback,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            replace_existing=True,
            kwargs={'prayer_name': prayer_name}
        )

        # Schedule auto-cancel after max_duration
        cancel_time = datetime.now() + timedelta(minutes=max_duration_minutes)
        self.scheduler.add_job(
            self.cancel_followup_reminders,
            trigger=DateTrigger(run_date=cancel_time),
            id=f"cancel_followup_{prayer_name}",
            replace_existing=True,
            args=[prayer_name]
        )

        logger.info(f"Followup reminders for {prayer_name} every {interval_minutes}min for {max_duration_minutes}min")

    def cancel_followup_reminders(self, prayer_name: str):
        """Cancel follow-up reminders for a prayer"""
        for prefix in ['followup_', 'cancel_followup_']:
            job_id = f"{prefix}{prayer_name}"
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"Cancelled job {job_id}")
            except Exception:
                pass

    def schedule_checkin(self, callback, min_minutes: int = 60, max_minutes: int = 180):
        """Schedule next random check-in"""
        delay = random.randint(min_minutes, max_minutes)
        # Add jitter of ±15 minutes
        jitter = random.randint(-15, 15)
        delay = max(30, delay + jitter)  # minimum 30 minutes

        run_time = datetime.now() + timedelta(minutes=delay)
        job_id = f"checkin_{run_time.strftime('%H%M')}"

        self.schedule_at_time(job_id, run_time, callback)
        logger.info(f"Next check-in in {delay} minutes at {run_time.strftime('%H:%M')}")

    def schedule_daily_reset(self, callback):
        """Schedule daily reset at midnight"""
        self.scheduler.add_job(
            callback,
            trigger=CronTrigger(hour=0, minute=5),  # 00:05 every day
            id='daily_reset',
            replace_existing=True
        )
        logger.info("Daily reset scheduled at 00:05")

    def schedule_daily_report(self, callback):
        """Schedule daily report before sleep"""
        self.scheduler.add_job(
            callback,
            trigger=CronTrigger(hour=1, minute=45),  # 1:45 AM
            id='daily_report',
            replace_existing=True
        )
        logger.info("Daily report scheduled at 01:45")

    def schedule_fajr_buzzer(self, fajr_time: datetime, callback, interval_minutes: int = 1, duration_minutes: int = 30):
        """Schedule Fajr wake-up buzzer every minute"""
        job_id = "fajr_buzzer"

        self.scheduler.add_job(
            callback,
            trigger=IntervalTrigger(minutes=interval_minutes, start_date=fajr_time),
            id=job_id,
            replace_existing=True
        )

        # Auto cancel after duration
        cancel_time = fajr_time + timedelta(minutes=duration_minutes)
        self.scheduler.add_job(
            self._cancel_fajr_buzzer,
            trigger=DateTrigger(run_date=cancel_time),
            id='cancel_fajr_buzzer',
            replace_existing=True
        )
        logger.info(f"Fajr buzzer from {fajr_time.strftime('%H:%M')} every {interval_minutes}min for {duration_minutes}min")

    def _cancel_fajr_buzzer(self):
        try:
            self.scheduler.remove_job('fajr_buzzer')
            self.scheduler.remove_job('cancel_fajr_buzzer')
        except Exception:
            pass

    def cancel_fajr_buzzer(self):
        self._cancel_fajr_buzzer()

    def cancel_all_prayer_jobs(self):
        """Cancel all prayer-related jobs"""
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            if any(prefix in job.id for prefix in ['adhan_', 'followup_', 'cancel_followup_', 'fajr_buzzer', 'cancel_fajr']):
                try:
                    self.scheduler.remove_job(job.id)
                except Exception:
                    pass
