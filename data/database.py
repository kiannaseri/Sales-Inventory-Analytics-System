import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import secrets
import os

DB_NAME = 'users.db'
DATA_DB_NAME = 'data.db'


def hash_password(password):
    """هش کردن رمز عبور"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_reset_token():
    """تولید توکن یکبار مصرف"""
    return secrets.token_urlsafe(32)


def init_user_database():
    """ایجاد دیتابیس کامل کاربران"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # جدول users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login TEXT,
            language TEXT DEFAULT 'persian',
            theme TEXT DEFAULT 'dark'
        )
    ''')

    # جدول سوالات امنیتی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT NOT NULL,
            answer_hash TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # جدول توکن‌های بازیابی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # جدول لاگ فعالیت
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            ip_address TEXT,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # اضافه کردن کاربر ادمین پیش‌فرض
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (first_name, last_name, username, password, email, role, created_at, language, theme)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Admin', 'User', 'admin', hash_password('admin123'), 'admin@example.com', 'admin',
              datetime.now().isoformat(), 'persian', 'dark'))

        admin_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO security_questions (user_id, question, answer_hash)
            VALUES (?, ?, ?)
        ''', (admin_id, 'What is your favorite color?', hash_password('admin')))

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


def register_user(first_name, last_name, username, password, email='', language='persian', role='user'):
    """ثبت نام کاربر جدید"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (first_name, last_name, username, password, email, role, created_at, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
        first_name, last_name, username, hash_password(password), email, role, datetime.now().isoformat(), language))

        user_id = cursor.lastrowid
        conn.commit()

        # اضافه کردن سوال امنیتی پیش‌فرض
        cursor.execute('''
            INSERT INTO security_questions (user_id, question, answer_hash)
            VALUES (?, ?, ?)
        ''', (user_id, 'What is your favorite color?', hash_password('blue')))
        conn.commit()

        conn.close()
        return True, user_id, "User registered successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, None, "Username already exists"
    except Exception as e:
        conn.close()
        return False, None, str(e)


def login_user(username, password, ip_address='127.0.0.1'):
    """ورود کاربر"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ? AND is_active = 1',
                   (username, hash_password(password)))
    user = cursor.fetchone()

    if user:
        # به‌روزرسانی last_login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                       (datetime.now().isoformat(), user[0]))

        # ثبت لاگ ورود
        cursor.execute('''
            INSERT INTO user_activity_log (user_id, action, ip_address, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user[0], 'login', ip_address, datetime.now().isoformat()))

        conn.commit()

        # ساخت دیکشنری اطلاعات کاربر با نام ستون‌ها
        user_info = {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "username": user[3],
            "email": user[5] if len(user) > 5 else '',
            "role": user[6] if len(user) > 6 else 'user',
            "language": user[9] if len(user) > 9 else 'persian',
            "theme": user[10] if len(user) > 10 else 'dark'
        }
        conn.close()
        return True, user_info

    conn.close()
    return False, None


def get_security_question(username):
    """دریافت سوال امنیتی کاربر"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT sq.question FROM users u
        JOIN security_questions sq ON u.id = sq.user_id
        WHERE u.username = ?
    ''', (username,))

    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def verify_security_answer(username, answer):
    """بررسی پاسخ سوال امنیتی"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.id FROM users u
        JOIN security_questions sq ON u.id = sq.user_id
        WHERE u.username = ? AND sq.answer_hash = ?
    ''', (username, hash_password(answer)))

    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def reset_password_direct(user_id, new_password):
    """بازیابی مستقیم رمز عبور"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET password = ? WHERE id = ?',
                   (hash_password(new_password), user_id))
    conn.commit()
    conn.close()
    return True


def get_users_list():
    """دریافت لیست کاربران"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, username, first_name, last_name, email, role, is_active, last_login FROM users",
                           conn)
    conn.close()
    return df


def update_user_role(user_id, new_role):
    """به‌روزرسانی نقش کاربر"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()
    return True


def delete_user(user_id):
    """حذف کاربر (غیرفعال کردن)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True


def update_user_theme(user_id, theme):
    """به‌روزرسانی تم کاربر"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET theme = ? WHERE id = ?', (theme, user_id))
    conn.commit()
    conn.close()


def get_user_theme(user_id):
    """دریافت تم کاربر"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT theme FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'dark'


def update_user_language(user_id, language):
    """به‌روزرسانی زبان کاربر"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE id = ?', (language, user_id))
    conn.commit()
    conn.close()


def get_user_language(user_id):
    """دریافت زبان کاربر"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'persian'


# ========== دیتابیس داده ==========
def init_data_database():
    """ایجاد دیتابیس داده‌ها"""
    conn = sqlite3.connect(DATA_DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            product TEXT,
            quantity_sold INTEGER,
            sales_amount REAL,
            customer_id TEXT,
            current_inventory INTEGER,
            product_views INTEGER,
            add_to_cart INTEGER,
            checkout_start INTEGER,
            successful_purchase INTEGER,
            source TEXT,
            uploaded_at TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_user_data(user_id, df, source='excel'):
    """ذخیره داده کاربر"""
    conn = sqlite3.connect(DATA_DB_NAME)

    conn.execute("DELETE FROM sales_data WHERE user_id = ?", (user_id,))

    for _, row in df.iterrows():
        conn.execute('''
            INSERT INTO sales_data (user_id, date, product, quantity_sold, sales_amount, 
                                   customer_id, current_inventory, product_views, 
                                   add_to_cart, checkout_start, successful_purchase, source, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, str(row.get('date', '')), row.get('product', ''),
              row.get('quantity_sold', 0), row.get('sales_amount', 0),
              row.get('customer_id', ''), row.get('current_inventory', 0),
              row.get('product_views', 0), row.get('add_to_cart', 0),
              row.get('checkout_start', 0), row.get('successful_purchase', 0),
              source, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def load_user_data(user_id):
    """بارگذاری داده کاربر"""
    conn = sqlite3.connect(DATA_DB_NAME)
    df = pd.read_sql_query("SELECT * FROM sales_data WHERE user_id = ?", conn, params=(user_id,))
    conn.close()

    for col in ['id', 'user_id', 'source', 'uploaded_at']:
        if col in df.columns:
            df = df.drop(col, axis=1)

    return df