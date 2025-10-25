import sqlite3
from datetime import datetime
from contextlib import contextmanager

DB_NAME = 'bot.db'

@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        # Testlar jadvali
        c.execute('''CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            question_count INTEGER,
            answers TEXT,
            creator_id INTEGER
        )''')
        # Foydalanuvchilar natijalari
        c.execute('''CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            test_code TEXT,
            user_answers TEXT,
            correct_count INTEGER,
            total INTEGER,
            percent INTEGER,
            created_at TEXT
        )''')
        # Adminlar jadvali
        c.execute('''CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )''')
        # Sozlamalar (yopiq guruh, kanal)
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        conn.commit()

def add_admin(user_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (user_id,))
        conn.commit()

def is_admin(user_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT 1 FROM admins WHERE user_id=?', (user_id,))
        res = c.fetchone()
        return bool(res)

def get_test_by_code(code):
    """Test kodiga ko'ra test ma'lumotlarini olish"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT name, question_count, answers FROM tests WHERE code=?', (code,))
        return c.fetchone()

def save_test(code, name, question_count, answers, creator_id):
    """Yangi test saqlash"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO tests (code, name, question_count, answers, creator_id) VALUES (?, ?, ?, ?, ?)',
                  (code, name, question_count, answers, creator_id))
        conn.commit()

def save_result(user_id, full_name, test_code, user_answers, correct_count, total, percent, created_at):
    """Test natijasini saqlash"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO results (user_id, full_name, test_code, user_answers, correct_count, total, percent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                  (user_id, full_name, test_code, user_answers, correct_count, total, percent, created_at))
        conn.commit()

def get_user_tests(creator_id):
    """Foydalanuvchi yaratgan testlarni olish"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT code, name, question_count FROM tests WHERE creator_id=?', (creator_id,))
        return c.fetchall()

def get_test_results(creator_id):
    """Test natijalarini olish"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT code, name FROM tests WHERE creator_id=?', (creator_id,))
        tests = c.fetchall()
        results = []
        for code, name in tests:
            c.execute('SELECT COUNT(*), AVG(percent) FROM results WHERE test_code=?', (code,))
            count, avg_percent = c.fetchone()
            avg_percent = int(avg_percent) if avg_percent else 0
            results.append((code, name, count, avg_percent))
        return results

def get_excel_data(creator_id):
    """Excel uchun ma'lumotlarni olish"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT r.full_name, r.test_code, t.name, r.user_answers, r.correct_count, r.total, r.percent, r.created_at 
                    FROM results r JOIN tests t ON r.test_code = t.code WHERE t.creator_id=?''', (creator_id,))
        return c.fetchall()

def get_user_results(user_id):
    """Foydalanuvchi natijalarini olish"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT r.test_code, t.name, r.correct_count, r.total, r.percent, r.created_at 
                     FROM results r JOIN tests t ON r.test_code = t.code WHERE r.user_id=? ORDER BY r.created_at DESC''', (user_id,))
        return c.fetchall()

def delete_test(code):
    """Test va uning natijalarini o'chirish"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tests WHERE code=?', (code,))
        c.execute('DELETE FROM results WHERE test_code=?', (code,))
        conn.commit() 