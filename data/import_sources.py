import pandas as pd
import requests
from tkinter import filedialog, messagebox
import json
import os


class ImportManager:
    """مدیریت Import از منابع مختلف"""

    @staticmethod
    def import_from_excel():
        """Import از فایل اکسل"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            try:
                df = pd.read_excel(file_path)
                return df, f"Excel: {os.path.basename(file_path)}"
            except Exception as e:
                return None, str(e)
        return None, "Cancelled"

    @staticmethod
    def import_from_csv():
        """Import از فایل CSV"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
                return df, f"CSV: {os.path.basename(file_path)}"
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding='ansi')
                    return df, f"CSV: {os.path.basename(file_path)}"
                except:
                    return None, "Encoding error"
            except Exception as e:
                return None, str(e)
        return None, "Cancelled"

    @staticmethod
    def import_from_google_sheets(sheet_url=None):
        """Import از Google Sheets"""
        if not sheet_url:
            sheet_url = filedialog.askstring("Google Sheets", "Enter Google Sheets URL or Shareable Link:")

        if not sheet_url:
            return None, "Cancelled"

        try:
            # استخراج Sheet ID از URL
            if '/d/' in sheet_url:
                sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            else:
                sheet_id = sheet_url

            # استفاده از gspread یا pandas
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            df = pd.read_csv(csv_url)
            return df, f"Google Sheets: {sheet_id}"
        except Exception as e:
            return None, str(e)

    @staticmethod
    def import_from_dropbox():
        """Import از Dropbox"""
        # این بخش نیاز به Dropbox API دارد
        # برای سادگی، از کاربر لینک اشتراک‌گذاری می‌خواهیم
        dropbox_url = filedialog.askstring("Dropbox", "Enter Dropbox Shared Link:")

        if not dropbox_url:
            return None, "Cancelled"

        try:
            # تبدیل لینک به لینک مستقیم
            if '?dl=0' in dropbox_url:
                dropbox_url = dropbox_url.replace('?dl=0', '?dl=1')
            elif '?dl=1' not in dropbox_url and 'raw=1' not in dropbox_url:
                dropbox_url += '?dl=1'

            df = pd.read_csv(dropbox_url) if dropbox_url.endswith('.csv') else pd.read_excel(dropbox_url)
            return df, "Dropbox"
        except Exception as e:
            return None, str(e)

    @staticmethod
    def import_from_api(api_url=None, api_key=None):
        """Import از REST API"""
        if not api_url:
            api_url = filedialog.askstring("API Import", "Enter API Endpoint URL:")

        if not api_url:
            return None, "Cancelled"

        try:
            headers = {}
            if api_key:
                api_key = filedialog.askstring("API Key", "Enter API Key (optional):", show='*')
                if api_key:
                    headers['Authorization'] = f'Bearer {api_key}'

            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            elif isinstance(data, dict) and 'results' in data:
                df = pd.DataFrame(data['results'])
            else:
                df = pd.DataFrame([data])

            return df, f"API: {api_url}"
        except Exception as e:
            return None, str(e)

    @staticmethod
    def import_from_database():
        """Import از دیتابیس (SQLite, PostgreSQL)"""
        db_type = filedialog.askstring("Database Import",
                                       "Select Database Type:\n1- SQLite\n2- PostgreSQL\n3- MySQL\n\nEnter number (1-3):")

        if not db_type:
            return None, "Cancelled"

        db_type = db_type.strip()

        if db_type == '1':
            # SQLite
            file_path = filedialog.askopenfilename(title="Select SQLite Database",
                                                   filetypes=[("SQLite files", "*.db *.sqlite")])
            if file_path:
                import sqlite3
                try:
                    conn = sqlite3.connect(file_path)
                    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
                    if not tables.empty:
                        table_name = filedialog.askstring("Table Name",
                                                          f"Available tables:\n{', '.join(tables['name'].tolist())}\n\nEnter table name:")
                        if table_name:
                            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                            conn.close()
                            return df, f"SQLite: {os.path.basename(file_path)} -> {table_name}"
                    conn.close()
                except Exception as e:
                    return None, str(e)

        elif db_type == '2':
            # PostgreSQL
            host = filedialog.askstring("PostgreSQL", "Host:")
            port = filedialog.askstring("PostgreSQL", "Port (default 5432):") or "5432"
            database = filedialog.askstring("PostgreSQL", "Database:")
            username = filedialog.askstring("PostgreSQL", "Username:")
            password = filedialog.askstring("PostgreSQL", "Password:", show='*')
            table = filedialog.askstring("PostgreSQL", "Table name:")

            if all([host, database, username, password, table]):
                try:
                    import psycopg2
                    conn = psycopg2.connect(
                        host=host, port=port, database=database,
                        user=username, password=password
                    )
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    conn.close()
                    return df, f"PostgreSQL: {database}.{table}"
                except Exception as e:
                    return None, str(e)

        return None, "Not implemented or cancelled"

    @staticmethod
    def get_import_sources_list():
        """لیست منابع قابل Import"""
        return {
            "📁 Excel File (.xlsx, .xls)": ImportManager.import_from_excel,
            "📄 CSV File (.csv)": ImportManager.import_from_csv,
            "📊 Google Sheets": ImportManager.import_from_google_sheets,
            "☁️ Dropbox": ImportManager.import_from_dropbox,
            "🌐 API Endpoint": ImportManager.import_from_api,
            "🗄️ Database": ImportManager.import_from_database
        }