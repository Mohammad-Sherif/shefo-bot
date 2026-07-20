"""
محرك الذكاء الاصطناعي - Groq AI
"""
import logging
from datetime import datetime, date
from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, DAILY_CALORIES_TARGET, DAILY_PROTEIN_TARGET
from data.prompts import (
    MAIN_SYSTEM_PROMPT, PRAYER_REMINDER_PROMPT, ENCOURAGEMENT_PROMPT,
    REBUKE_PROMPT, CHECKIN_PROMPT, DAILY_REPORT_PROMPT,
    MORNING_GREETING_PROMPT, FOOD_ANALYSIS_PROMPT
)
from data.training_plan import format_plan_for_ai, get_today_plan, WEEKLY_PLAN, TRAINING_RULES
from data.food_db import format_food_db_for_ai, format_meal_plan_for_ai
from config import PRAYER_NAMES_AR

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, db):
        self.db = db
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
    
    def _call_groq(self, messages: list, temperature: float = 0.8, max_tokens: int = 500) -> str:
        """Make a call to Groq API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = response.choices[0].message.content.strip()
            
            # Post-process: remove thinking tags if model outputs them
            if '<think>' in text:
                # Remove everything between <think> and </think>
                import re
                text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            
            return text
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "عذراً، حدث خطأ. حاول مرة أخرى 🙏"
    
    def _build_system_prompt(self) -> str:
        """Build the full system prompt with all context"""
        today = datetime.now()
        day_name = today.strftime('%A')  # English day name
        
        # Today's training plan
        training_context = format_plan_for_ai(day_name)
        
        # Food context
        food_context = format_food_db_for_ai()
        meal_plan = format_meal_plan_for_ai()
        food_full = f"{food_context}\n\n{meal_plan}"
        
        # Prayer context
        today_str = date.today().isoformat()
        prayers = self.db.get_today_prayers(today_str)
        prayer_lines = []
        for p in prayers:
            name_ar = PRAYER_NAMES_AR.get(p['prayer_name'], p['prayer_name'])
            
            if p['prayer_name'] == "Fajr" and datetime.now().hour >= 7:
                name_ar = "الصبح"
                
            status = "صلّى ✅" if p['prayed'] else "لم يصلِّ ❌"
            prayer_lines.append(f"{name_ar}: {status}")
        prayer_context = "حالة الصلوات اليوم:\n" + "\n".join(prayer_lines) if prayer_lines else "لم تُسجَّل صلوات بعد"
        
        # Workout modifications
        mods = self.db.get_active_modifications()
        mod_context = ""
        if mods:
            mod_context = "\nتعديلات على الخطة:\n"
            for m in mods[:3]:
                mod_context += f"• {m['reason']}: {m['modified_plan']}\n"
        
        # Today context
        macros = self.db.get_total_macros(today_str)
        meals = self.db.get_today_meals(today_str)
        today_context = f"""اليوم: {today.strftime('%A %Y-%m-%d')}
الوقت الحالي: {today.strftime('%H:%M')}
السعرات المستهلكة: {macros.get('total_kcal', 0)} / {DAILY_CALORIES_TARGET}
البروتين المستهلك: {macros.get('total_protein', 0)} / {DAILY_PROTEIN_TARGET}
عدد الوجبات: {len(meals)}
{mod_context}"""
        
        # Recent conversation for context
        recent = self.db.get_recent_messages(limit=5)
        conv_context = ""
        if recent:
            conv_context = "آخر المحادثات:\n"
            for msg in recent:
                role_label = "محمد" if msg['role'] == 'user' else "صاحبك"
                conv_context += f"{role_label}: {msg['content'][:100]}\n"
        
        prompt = MAIN_SYSTEM_PROMPT.format(
            today_context=today_context,
            training_plan_context=training_context,
            food_context=food_full,
            prayer_context=prayer_context,
            conversation_context=conv_context
        )
        
        return prompt
    
    async def chat(self, user_message: str, context: dict = None) -> str:
        """Main chat function - handles any user message"""
        # Save user message
        self.db.save_message('user', user_message)
        
        # Build messages
        system_prompt = self._build_system_prompt()
        
        # Get conversation history
        recent = self.db.get_recent_messages(limit=20)
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in recent:
            role = "user" if msg['role'] == 'user' else "assistant"
            messages.append({"role": role, "content": msg['content']})
        
        # Make sure last message is the current one
        if not messages or messages[-1].get('content') != user_message:
            messages.append({"role": "user", "content": user_message})
        
        response = self._call_groq(messages, temperature=0.8, max_tokens=800)
        
        # Save assistant response
        self.db.save_message('assistant', response)
        
        return response
    
    async def generate_prayer_reminder(self, prayer_name: str, reminder_number: int) -> str:
        """Generate a prayer reminder message"""
        prayer_ar = PRAYER_NAMES_AR.get(prayer_name, prayer_name)
        if prayer_name == "Fajr" and datetime.now().hour >= 7:
            prayer_ar = "الصبح"
            
        context = ""
        if reminder_number > 5:
            context = "تذكير متأخر جداً - عاتب بحنية أكثر"
        elif reminder_number > 3:
            context = "تذكير متأخر - كن أكثر إلحاحاً"
        
        prompt = PRAYER_REMINDER_PROMPT.format(
            prayer_name=prayer_ar,
            reminder_number=reminder_number,
            context=context
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"اكتب تذكير رقم {reminder_number} لصلاة {prayer_ar}"}
        ]
        
        return self._call_groq(messages, temperature=0.95, max_tokens=150)
    
    async def generate_encouragement(self, prayer_name: str) -> str:
        """Generate a short encouragement after praying"""
        prayer_ar = PRAYER_NAMES_AR.get(prayer_name, prayer_name)
        if prayer_name == "Fajr" and datetime.now().hour >= 7:
            prayer_ar = "الصبح"
            
        prompt = ENCOURAGEMENT_PROMPT.format(prayer_name=prayer_ar)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"محمد صلّى {prayer_ar}"}
        ]
        
        return self._call_groq(messages, temperature=0.9, max_tokens=150)
    
    async def generate_rebuke(self, prayer_name: str) -> str:
        """Generate a rebuke for missing a prayer"""
        prayer_ar = PRAYER_NAMES_AR.get(prayer_name, prayer_name)
        if prayer_name == "Fajr" and datetime.now().hour >= 7:
            prayer_ar = "الصبح"
            
        context = ""
        prompt = REBUKE_PROMPT.format(prayer_name=prayer_ar, context=context)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"محمد لم يصلِّ {prayer_ar}"}
        ]
        
        return self._call_groq(messages, temperature=0.9, max_tokens=200)
    
    async def generate_checkin_message(self, current_time: str = "", last_interaction: str = "", day_summary: str = "") -> str:
        """Generate a random check-in message"""
        prompt = CHECKIN_PROMPT.format(
            current_time=current_time or datetime.now().strftime('%H:%M'),
            last_interaction=last_interaction or "غير معروف",
            day_summary=day_summary or "لا توجد بيانات"
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "اكتب رسالة سؤال على الحال"}
        ]
        
        return self._call_groq(messages, temperature=0.95, max_tokens=100)
    
    async def generate_daily_report(self, prayers_summary: str = "", food_summary: str = "", workout_summary: str = "", score: int = 0) -> str:
        """Generate daily report"""
        prompt = DAILY_REPORT_PROMPT.format(
            prayers_summary=prayers_summary,
            food_summary=food_summary,
            workout_summary=workout_summary,
            score=score
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "اكتب التقرير اليومي"}
        ]
        
        return self._call_groq(messages, temperature=0.8, max_tokens=400)
    
    async def generate_morning_greeting(self, prayed_fajr: bool = False, today_plan: str = "") -> str:
        """Generate morning greeting"""
        prompt = MORNING_GREETING_PROMPT.format(
            prayed_fajr="نعم" if prayed_fajr else "لا",
            today_plan=today_plan or "لا توجد خطة"
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "اكتب رسالة صباحية"}
        ]
        
        return self._call_groq(messages, temperature=0.9, max_tokens=200)
    
    async def analyze_food(self, user_input: str) -> str:
        """Analyze food input and calculate macros"""
        today_str = date.today().isoformat()
        meals = self.db.get_today_meals(today_str)
        macros = self.db.get_total_macros(today_str)
        
        prev_meals_text = "لا يوجد" if not meals else "\n".join(
            f"• {m['description']} ({m['calories']} سعر, {m['protein']}g بروتين)" for m in meals
        )
        
        prompt = FOOD_ANALYSIS_PROMPT.format(
            user_input=user_input,
            food_db=format_food_db_for_ai(),
            previous_meals=prev_meals_text,
            daily_target_kcal=DAILY_CALORIES_TARGET,
            daily_target_protein=DAILY_PROTEIN_TARGET
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ]
        
        return self._call_groq(messages, temperature=0.3, max_tokens=500)
