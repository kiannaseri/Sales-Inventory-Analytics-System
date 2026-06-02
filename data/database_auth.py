import sqlite3
import hashlib
from datetime import datetime

DB_NAME = 'users.db'


def hash_password(password):
    """هش کردن رمز عبور"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_user_database():
    """ایجاد دیتابیس کاربران"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            language TEXT DEFAULT 'persian'
        )
    ''')

    conn.commit()
    conn.close()


def register_user(first_name, last_name, username, password, language='persian'):
    """ثبت نام کاربر جدید"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (first_name, last_name, username, password, created_at, language)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, username, hash_password(password), datetime.now().isoformat(), language))

        conn.commit()
        return True, "ثبت نام با موفقیت انجام شد"
    except sqlite3.IntegrityError:
        return False, "این نام کاربری قبلاً ثبت شده است"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def login_user(username, password):
    """ورود کاربر"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                   (username, hash_password(password)))
    user = cursor.fetchone()

    conn.close()

    if user:
        return True, {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "username": user[3],
            "language": user[6]
        }
    return False, "نام کاربری یا رمز عبور اشتباه است"