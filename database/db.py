"""
قاعدة بيانات بوت صاحبك - SQLite
"""
import sqlite3
import os
from datetime import datetime, date


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        """Create all tables if not exist"""
        cursor = self.conn.cursor()

        # Prayers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prayers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                prayer_name TEXT NOT NULL,
                adhan_time TEXT,
                prayed INTEGER DEFAULT 0,
                prayed_at TEXT,
                reminders_sent INTEGER DEFAULT 0,
                UNIQUE(date, prayer_name)
            )
        ''')

        # Meals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal_type TEXT,
                description TEXT,
                calories INTEGER DEFAULT 0,
                protein REAL DEFAULT 0,
                logged_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Workouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                workout_type TEXT,
                details TEXT,
                completed INTEGER DEFAULT 0,
                random_workout TEXT,
                logged_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Conversations (for AI memory)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')

        # Plan modifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plan_modifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                original_plan TEXT,
                modified_plan TEXT,
                reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Daily adhkar tracking (to avoid repeats)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_adhkar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                prayer_name TEXT,
                dhikr_id INTEGER,
                dhikr_text TEXT
            )
        ''')

        # Settings (chat_id, etc)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Daily scores / streaks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_scores (
                date TEXT PRIMARY KEY,
                prayers_done INTEGER DEFAULT 0,
                prayers_total INTEGER DEFAULT 5,
                workout_done INTEGER DEFAULT 0,
                meals_logged INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0
            )
        ''')

        self.conn.commit()

    # === Settings ===
    def save_setting(self, key: str, value: str):
        self.conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()

    def get_setting(self, key: str, default: str = None) -> str:
        row = self.conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        return row['value'] if row else default

    def save_chat_id(self, chat_id: str):
        self.save_setting('chat_id', str(chat_id))

    def get_chat_id(self) -> str:
        return self.get_setting('chat_id')

    # === Prayers ===
    def log_prayer(self, prayer_date: str, prayer_name: str, adhan_time: str = None):
        try:
            self.conn.execute(
                'INSERT OR IGNORE INTO prayers (date, prayer_name, adhan_time) VALUES (?, ?, ?)',
                (prayer_date, prayer_name, adhan_time)
            )
            self.conn.commit()
        except Exception:
            pass

    def mark_prayed(self, prayer_date: str, prayer_name: str):
        now = datetime.now().strftime('%H:%M:%S')
        self.conn.execute(
            'UPDATE prayers SET prayed = 1, prayed_at = ? WHERE date = ? AND prayer_name = ?',
            (now, prayer_date, prayer_name)
        )
        self.conn.commit()

    def get_prayer_status(self, prayer_date: str, prayer_name: str) -> dict:
        row = self.conn.execute(
            'SELECT * FROM prayers WHERE date = ? AND prayer_name = ?',
            (prayer_date, prayer_name)
        ).fetchone()
        return dict(row) if row else None

    def get_today_prayers(self, prayer_date: str) -> list:
        rows = self.conn.execute(
            'SELECT * FROM prayers WHERE date = ? ORDER BY id',
            (prayer_date,)
        ).fetchall()
        return [dict(r) for r in rows]

    def increment_reminders(self, prayer_date: str, prayer_name: str):
        self.conn.execute(
            'UPDATE prayers SET reminders_sent = reminders_sent + 1 WHERE date = ? AND prayer_name = ?',
            (prayer_date, prayer_name)
        )
        self.conn.commit()

    def get_unprayed(self, prayer_date: str) -> list:
        rows = self.conn.execute(
            'SELECT * FROM prayers WHERE date = ? AND prayed = 0',
            (prayer_date,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_current_pending_prayer(self, prayer_date: str) -> dict:
        """Get the most recent unprayed prayer"""
        row = self.conn.execute(
            'SELECT * FROM prayers WHERE date = ? AND prayed = 0 ORDER BY id ASC LIMIT 1',
            (prayer_date,)
        ).fetchone()
        return dict(row) if row else None

    # === Meals ===
    def log_meal(self, meal_date: str, meal_type: str, description: str, calories: int = 0, protein: float = 0):
        self.conn.execute(
            'INSERT INTO meals (date, meal_type, description, calories, protein) VALUES (?, ?, ?, ?, ?)',
            (meal_date, meal_type, description, calories, protein)
        )
        self.conn.commit()

    def get_today_meals(self, meal_date: str) -> list:
        rows = self.conn.execute(
            'SELECT * FROM meals WHERE date = ? ORDER BY id', (meal_date,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_total_macros(self, meal_date: str) -> dict:
        row = self.conn.execute(
            'SELECT COALESCE(SUM(calories), 0) as total_kcal, COALESCE(SUM(protein), 0) as total_protein FROM meals WHERE date = ?',
            (meal_date,)
        ).fetchone()
        return dict(row)

    # === Workouts ===
    def log_workout(self, workout_date: str, workout_type: str, details: str, random_workout: str = None):
        self.conn.execute(
            'INSERT INTO workouts (date, workout_type, details, random_workout) VALUES (?, ?, ?, ?)',
            (workout_date, workout_type, details, random_workout)
        )
        self.conn.commit()

    def mark_workout_done(self, workout_date: str):
        self.conn.execute('UPDATE workouts SET completed = 1 WHERE date = ?', (workout_date,))
        self.conn.commit()

    def get_today_workout(self, workout_date: str) -> dict:
        row = self.conn.execute(
            'SELECT * FROM workouts WHERE date = ? ORDER BY id DESC LIMIT 1', (workout_date,)
        ).fetchone()
        return dict(row) if row else None

    # === Conversations ===
    def save_message(self, role: str, content: str):
        self.conn.execute(
            'INSERT INTO conversations (role, content) VALUES (?, ?)',
            (role, content)
        )
        self.conn.commit()

    def get_recent_messages(self, limit: int = 20) -> list:
        rows = self.conn.execute(
            'SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?', (limit,)
        ).fetchall()
        return [dict(r) for r in reversed(rows)]

    # === Plan Modifications ===
    def save_plan_modification(self, mod_date: str, original: str, modified: str, reason: str):
        self.conn.execute(
            'INSERT INTO plan_modifications (date, original_plan, modified_plan, reason) VALUES (?, ?, ?, ?)',
            (mod_date, original, modified, reason)
        )
        self.conn.commit()

    def get_active_modifications(self) -> list:
        rows = self.conn.execute(
            'SELECT * FROM plan_modifications ORDER BY id DESC LIMIT 10'
        ).fetchall()
        return [dict(r) for r in rows]

    # === Adhkar ===
    def log_dhikr(self, dhikr_date: str, prayer_name: str, dhikr_id: int, dhikr_text: str):
        self.conn.execute(
            'INSERT INTO daily_adhkar (date, prayer_name, dhikr_id, dhikr_text) VALUES (?, ?, ?, ?)',
            (dhikr_date, prayer_name, dhikr_id, dhikr_text)
        )
        self.conn.commit()

    def get_used_adhkar_today(self, dhikr_date: str) -> list:
        rows = self.conn.execute(
            'SELECT dhikr_id FROM daily_adhkar WHERE date = ?', (dhikr_date,)
        ).fetchall()
        return [r['dhikr_id'] for r in rows]

    # === Scores ===
    def update_daily_score(self, score_date: str):
        prayers = self.get_today_prayers(score_date)
        prayers_done = sum(1 for p in prayers if p['prayed'])
        meals = self.get_today_meals(score_date)
        workout = self.get_today_workout(score_date)
        workout_done = 1 if workout and workout.get('completed') else 0
        score = prayers_done * 10 + workout_done * 15 + len(meals) * 5

        self.conn.execute(
            'INSERT OR REPLACE INTO daily_scores (date, prayers_done, prayers_total, workout_done, meals_logged, score) VALUES (?, ?, 5, ?, ?, ?)',
            (score_date, prayers_done, workout_done, len(meals), score)
        )
        self.conn.commit()
        return {"prayers_done": prayers_done, "workout_done": workout_done, "meals_logged": len(meals), "score": score}

    def get_prayer_streak(self) -> int:
        """Get consecutive days with all 5 prayers completed"""
        rows = self.conn.execute(
            'SELECT date, prayers_done FROM daily_scores ORDER BY date DESC LIMIT 30'
        ).fetchall()
        streak = 0
        for r in rows:
            if r['prayers_done'] >= 5:
                streak += 1
            else:
                break
        return streak

    def close(self):
        self.conn.close()
