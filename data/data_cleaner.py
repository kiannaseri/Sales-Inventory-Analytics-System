import pandas as pd
import numpy as np


def clean_data(df):
    """پاکسازی کامل داده‌ها"""
    original_count = len(df)
    cleaning_reasons = []

    # 1. حذف سطرهای کاملاً خالی
    df = df.dropna(how='all')
    removed_empty = original_count - len(df)
    if removed_empty > 0:
        cleaning_reasons.append(f"حذف {removed_empty} سطر خالی")

    # 2. حذف سطرهایی که ستون‌های ضروری خالی دارند
    mandatory_cols = ['date', 'product', 'sales_amount', 'quantity_sold', 'customer_id']
    for col in mandatory_cols:
        if col in df.columns:
            before = len(df)
            df = df[df[col].notna()]
            removed = before - len(df)
            if removed > 0:
                cleaning_reasons.append(f"حذف {removed} سطر با {col} خالی")

    # 3. تبدیل و پاکسازی ستون تاریخ
    if 'date' in df.columns:
        before = len(df)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df[df['date'].notna()]
        removed = before - len(df)
        if removed > 0:
            cleaning_reasons.append(f"حذف {removed} سطر با تاریخ نامعتبر")

    # 4. پاکسازی ستون‌های عددی
    numeric_cols = ['sales_amount', 'quantity_sold', 'product_views',
                    'add_to_cart', 'checkout_start', 'successful_purchase',
                    'current_inventory']

    for col in numeric_cols:
        if col in df.columns:
            before = len(df)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df[df[col].notna()]
            # حذف مقادیر منفی
            df = df[df[col] >= 0]
            removed = before - len(df)
            if removed > 0:
                cleaning_reasons.append(f"حذف {removed} سطر با {col} نامعتبر")

    # 5. حذف duplicate‌ها
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed > 0:
        cleaning_reasons.append(f"حذف {removed} سطر تکراری")

    # 6. پر کردن مقادیر صفر برای ستون‌های اختیاری
    optional_cols = ['category', 'alert_threshold']
    for col in optional_cols:
        if col in df.columns:
            df[col] = df[col].fillna('نامشخص')

    final_count = len(df)
    total_removed = original_count - final_count

    reason_text = " | ".join(cleaning_reasons) if cleaning_reasons else "مشکلی یافت نشد"

    return df, total_removed, reason_text


def validate_excel_columns(df):
    """بررسی ستون‌های مورد نیاز"""
    required_columns = ['date', 'product', 'sales_amount', 'quantity_sold', 'customer_id', 'current_inventory']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return False, f"ستون‌های زیر در فایل اکسل وجود ندارند: {', '.join(missing_columns)}"

    return True, "ستون‌ها معتبر هستند"