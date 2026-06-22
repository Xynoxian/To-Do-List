import sqlite3
import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'todolist.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("\n        CREATE TABLE IF NOT EXISTS users (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            username TEXT UNIQUE NOT NULL,\n            email TEXT UNIQUE NOT NULL,\n            password_hash TEXT NOT NULL,\n            salt TEXT NOT NULL,\n            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n        );\n\n        CREATE TABLE IF NOT EXISTS tasks (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            user_id INTEGER NOT NULL,\n            title TEXT NOT NULL,\n            description TEXT DEFAULT '',\n            category TEXT DEFAULT 'General',\n            priority TEXT DEFAULT 'Medium',\n            status TEXT DEFAULT 'Pending',\n            due_date TEXT,\n            is_recurring INTEGER DEFAULT 0,\n            recurrence_pattern TEXT,\n            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n            completed_at TIMESTAMP,\n            FOREIGN KEY (user_id) REFERENCES users(id)\n        );\n\n        CREATE TABLE IF NOT EXISTS subtasks (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            task_id INTEGER NOT NULL,\n            title TEXT NOT NULL,\n            is_done INTEGER DEFAULT 0,\n            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE\n        );\n\n        CREATE TABLE IF NOT EXISTS task_history (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            task_id INTEGER NOT NULL,\n            user_id INTEGER NOT NULL,\n            action TEXT NOT NULL,\n            old_value TEXT,\n            new_value TEXT,\n            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n        );\n\n        CREATE TABLE IF NOT EXISTS achievements (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            user_id INTEGER NOT NULL,\n            achievement_name TEXT NOT NULL,\n            description TEXT,\n            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n            FOREIGN KEY (user_id) REFERENCES users(id)\n        );\n    ")
    conn.commit()
    conn.close()
