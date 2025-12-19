import sqlite3
import json
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_name="task_manager.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Emotional entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotional_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                mood TEXT NOT NULL,
                day_rating INTEGER,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Task methods
    def add_task(self, title, description, due_date):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)",
            (title, description, due_date)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def get_all_tasks(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY due_date DESC")
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def get_tasks_by_date(self, date):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE due_date = ? ORDER BY created_at", (date,))
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def update_task(self, task_id, title, description, due_date, completed):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET title=?, description=?, due_date=?, completed=? WHERE id=?",
            (title, description, due_date, completed, task_id)
        )
        conn.commit()
        conn.close()
    
    def delete_task(self, task_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
    
    def get_task(self, task_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        task = cursor.fetchone()
        conn.close()
        return task
    
    # Emotional tracker methods
    def add_emotional_entry(self, mood, day_rating, notes):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO emotional_entries (date, mood, day_rating, notes) VALUES (?, ?, ?, ?)",
            (today, mood, day_rating, notes)
        )
        conn.commit()
        conn.close()
    
    def get_emotional_entries(self, start_date, end_date):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM emotional_entries WHERE date BETWEEN ? AND ? ORDER BY date",
            (start_date, end_date)
        )
        entries = cursor.fetchall()
        conn.close()
        return entries
    
    def get_recent_emotional_entries(self, days=7):
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return self.get_emotional_entries(start_date, end_date)