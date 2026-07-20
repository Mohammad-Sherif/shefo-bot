"""
نظام اللياقة والتغذية
"""
import json
import logging
from datetime import datetime, date

from data.training_plan import (
    get_today_plan, format_plan_for_ai, is_track_day, is_gym_day, is_rest_day,
    WEEKLY_PLAN, HYBRID_TAX, TRAINING_RULES
)
from data.workouts import generate_random_workout, format_workout_ar
from data.food_db import FOOD_DB, BASE_MEAL_PLAN, FOOD_RULES, format_food_db_for_ai

logger = logging.getLogger(__name__)

class FitnessManager:
    def __init__(self, db, ai_engine):
        self.db = db
        self.ai = ai_engine
        self._today_random_workout = None  # Cache today's random workout
    
    def get_today_plan_text(self) -> str:
        """Get today's training plan as formatted text"""
        day_name = datetime.now().strftime('%A')
        return format_plan_for_ai(day_name)
    
    def get_today_type(self) -> str:
        """Get today's workout type"""
        day_name = datetime.now().strftime('%A')
        plan = get_today_plan(day_name)
        return plan.get('type', 'unknown') if plan else 'unknown'
    
    async def get_random_workout(self) -> str:
        """Generate and cache a random workout for today"""
        workout = generate_random_workout()
        self._today_random_workout = workout
        
        # Save to database
        today_str = date.today().isoformat()
        self.db.log_workout(
            today_str,
            workout.get('type', 'random'),
            json.dumps(workout, ensure_ascii=False),
            random_workout=workout.get('title', '')
        )
        
        return format_workout_ar(workout)
    
    def get_cached_random_workout(self) -> dict:
        """Get the cached random workout (if any)"""
        return self._today_random_workout
    
    async def process_food_log(self, user_text: str) -> str:
        """Process when user says what they ate"""
        # Use AI to analyze and respond
        response = await self.ai.analyze_food(user_text)
        
        # Try to log the meal (approximate)
        today_str = date.today().isoformat()
        self.db.log_meal(today_str, 'logged', user_text, 0, 0)
        
        return response
    
    async def get_workout_recommendation(self) -> str:
        """Get what to do today (plan + random if applicable)"""
        day_name = datetime.now().strftime('%A')
        plan_text = format_plan_for_ai(day_name)
        
        response = f"📋 خطة اليوم ({day_name}):\n\n{plan_text}"
        
        if self._today_random_workout:
            random_text = format_workout_ar(self._today_random_workout)
            response += f"\n\n🎲 التمرين العشوائي اللي اخترته:\n{random_text}"
        
        return response
    
    async def modify_plan(self, user_request: str) -> str:
        """Handle plan modification request"""
        today_str = date.today().isoformat()
        day_name = datetime.now().strftime('%A')
        original = format_plan_for_ai(day_name)
        
        # Use AI to process the modification
        response = await self.ai.chat(
            f"عايز أعدّل خطة اليوم: {user_request}\n\nالخطة الأصلية:\n{original}"
        )
        
        # Save modification
        self.db.save_plan_modification(
            today_str, original, user_request, user_request
        )
        
        return response
    
    def mark_workout_complete(self) -> str:
        """Mark today's workout as complete"""
        today_str = date.today().isoformat()
        workout = self.db.get_today_workout(today_str)
        if not workout:
            day_name = datetime.now().strftime('%A')
            plan = get_today_plan(day_name)
            self.db.log_workout(
                today_str,
                plan.get('type', 'general') if plan else 'general',
                plan.get('name', 'workout') if plan else 'workout'
            )
        self.db.mark_workout_done(today_str)
        return "💪 تمام! سجّلت التمرين إنه خلص. أحسنت يا بطل!"
