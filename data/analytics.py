import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def run_all_analyses(df):
    """اجرای تمام تحلیل‌های مورد نیاز - نسخه با دیباگ"""
    print(f"[analytics] شروع تحلیل روی دیتافریم با {len(df)} رکورد")

    if df.empty:
        print("[analytics] دیتافریم خالی است")
        return {"error": "داده‌ای برای تحلیل وجود ندارد"}

    results = {}

    try:
        print("[analytics] در حال محاسبه گزارش روزانه فروش...")
        results['daily_sales'] = daily_sales_report(df)
        print("[analytics] گزارش روزانه فروش انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در daily_sales: {str(e)}")
        results['daily_sales'] = None

    try:
        print("[analytics] در حال محاسبه پیش‌بینی موجودی...")
        results['inventory_forecast'] = inventory_forecast_v1(df)
        print("[analytics] پیش‌بینی موجودی انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در inventory_forecast: {str(e)}")
        results['inventory_forecast'] = None

    try:
        print("[analytics] در حال محاسبه محصولات راکد...")
        results['slow_moving'] = slow_moving_products(df)
        print("[analytics] محصولات راکد انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در slow_moving: {str(e)}")
        results['slow_moving'] = None

    try:
        print("[analytics] در حال محاسبه روند فروش...")
        results['sales_trend'] = sales_trend(df)
        print("[analytics] روند فروش انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در sales_trend: {str(e)}")
        results['sales_trend'] = None

    try:
        print("[analytics] در حال محاسبه نرخ تبدیل...")
        results['conversion_rate'] = conversion_rate(df)
        print("[analytics] نرخ تبدیل انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در conversion_rate: {str(e)}")
        results['conversion_rate'] = None

    try:
        print("[analytics] در حال محاسبه تحلیل سبد خرید...")
        results['basket_analysis'] = basket_analysis(df)
        print("[analytics] تحلیل سبد خرید انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در basket_analysis: {str(e)}")
        results['basket_analysis'] = None

    try:
        print("[analytics] در حال محاسبه نرخ ریزش...")
        results['churn_rate'] = churn_rate(df)
        print("[analytics] نرخ ریزش انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در churn_rate: {str(e)}")
        results['churn_rate'] = None

    try:
        print("[analytics] در حال محاسبه محصولات پرفروش و کم‌فروش...")
        results['top_low_products'] = top_low_products(df)
        print("[analytics] محصولات پرفروش و کم‌فروش انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در top_low_products: {str(e)}")
        results['top_low_products'] = None

    try:
        print("[analytics] در حال محاسبه وضعیت موجودی...")
        results['low_stock'] = low_stock_alert(df)
        print("[analytics] وضعیت موجودی انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در low_stock: {str(e)}")
        results['low_stock'] = None

    try:
        print("[analytics] در حال محاسبه RFM...")
        results['rfm_segments'] = rfm_analysis(df)
        print("[analytics] RFM انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در rfm_segments: {str(e)}")
        results['rfm_segments'] = None

    try:
        print("[analytics] در حال محاسبه قیف فروش...")
        results['funnel_conversion'] = funnel_conversion(df)
        print("[analytics] قیف فروش انجام شد")
    except Exception as e:
        print(f"[analytics] خطا در funnel_conversion: {str(e)}")
        results['funnel_conversion'] = None

    print("[analytics] همه تحلیل‌ها با موفقیت انجام شد")
    return results


def daily_sales_report(df):
    """گزارش روزانه فروش"""
    try:
        if 'date' not in df.columns or 'sales_amount' not in df.columns:
            return "ستون‌های date و sales_amount وجود ندارند"

        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
        df_copy = df_copy[df_copy['date'].notna()]

        if df_copy.empty:
            return "هیچ تاریخ معتبری وجود ندارد"

        daily = df_copy.groupby(df_copy['date'].dt.date).agg({
            'sales_amount': 'sum',
            'quantity_sold': 'sum' if 'quantity_sold' in df_copy.columns else 'count'
        }).rename(columns={'sales_amount': 'مبلغ کل فروش', 'quantity_sold': 'تعداد کل سفارش'})

        daily['میانگین ارزش هر سفارش'] = daily['مبلغ کل فروش'] / daily['تعداد کل سفارش']

        return daily.tail(30).to_dict()
    except Exception as e:
        return f"خطا: {str(e)}"


def inventory_forecast_v1(df):
    """پیش‌بینی موجودی نسخه 1 - میانگین 7 روز گذشته - ساده شده برای سرعت"""
    try:
        required_cols = ['date', 'product', 'quantity_sold', 'current_inventory']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return f"ستون‌های مورد نیاز وجود ندارند: {missing}"

        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
        df_copy = df_copy[df_copy['date'].notna()]

        if df_copy.empty:
            return "هیچ تاریخ معتبری برای پیش‌بینی وجود ندارد"

        today = datetime.now()
        last_7_days = df_copy[df_copy['date'] >= today - timedelta(days=7)]

        if last_7_days.empty:
            return "داده کافی برای پیش‌بینی وجود ندارد (حداقل 7 روز داده نیاز است)"

        # فقط 20 محصول اول برای سرعت
        top_products = df_copy['product'].value_counts().head(20).index

        forecast = {}
        for product in top_products:
            product_data = df_copy[df_copy['product'] == product]
            if len(product_data) > 0:
                current_stock = product_data['current_inventory'].iloc[-1]
                last_7_sales = last_7_days[last_7_days['product'] == product]['quantity_sold'].sum()
                avg_sales = last_7_sales / 7

                if avg_sales > 0:
                    days_until_out = current_stock / avg_sales
                    if days_until_out <= 3:
                        status = "کritikal"
                    elif days_until_out <= 7:
                        status = "هشدار"
                    else:
                        status = "عادی"
                else:
                    days_until_out = 999
                    status = "بدون فروش"

                forecast[product] = {
                    'موجودی فعلی': int(current_stock),
                    'میانگین فروش روزانه': round(avg_sales, 2),
                    'روز تا اتمام موجودی': int(days_until_out),
                    'وضعیت': status
                }

        return forecast if forecast else "هیچ محصولی برای پیش‌بینی یافت نشد"
    except Exception as e:
        return f"خطا در پیش‌بینی: {str(e)}"


def slow_moving_products(df):
    """محصولات راکد (بدون فروش در 30 روز گذشته)"""
    try:
        if 'date' not in df.columns or 'product' not in df.columns or 'quantity_sold' not in df.columns:
            return "ستون‌های مورد نیاز وجود ندارند"

        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
        df_copy = df_copy[df_copy['date'].notna()]

        last_30_days = df_copy[df_copy['date'] >= datetime.now() - timedelta(days=30)]
        sold_products = set(last_30_days[last_30_days['quantity_sold'] > 0]['product'].unique())
        all_products = set(df_copy['product'].unique())
        slow = all_products - sold_products

        return list(slow) if slow else ["✅ همه محصولات در 30 روز اخیر فروش داشته‌اند"]
    except Exception as e:
        return f"خطا: {str(e)}"


def sales_trend(df):
    """روند فروش ماهانه"""
    try:
        if 'date' not in df.columns or 'sales_amount' not in df.columns:
            return "ستون‌های مورد نیاز وجود ندارند"

        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
        df_copy = df_copy[df_copy['date'].notna()]

        if df_copy.empty:
            return "هیچ تاریخ معتبری وجود ندارد"

        df_copy['month'] = df_copy['date'].dt.strftime('%Y-%m')
        monthly = df_copy.groupby('month')['sales_amount'].sum().sort_index()

        return monthly.tail(12).to_dict()
    except Exception as e:
        return f"خطا: {str(e)}"


def conversion_rate(df):
    """نرخ تبدیل کلی"""
    try:
        if 'product_views' not in df.columns or 'successful_purchase' not in df.columns:
            return None

        total_views = pd.to_numeric(df['product_views'], errors='coerce').sum()
        total_purchases = pd.to_numeric(df['successful_purchase'], errors='coerce').sum()

        if total_views > 0:
            return round((total_purchases / total_views) * 100, 2)
        return None
    except:
        return None


def basket_analysis(df):
    """تحلیل سبد خرید ساده"""
    try:
        if 'customer_id' not in df.columns or 'product' not in df.columns:
            return "ستون‌های customer_id و product وجود ندارند"

        baskets = df.groupby('customer_id')['product'].apply(list)
        avg_items = round(baskets.str.len().mean(), 2)
        return f"تعداد {len(baskets)} سبد خرید | میانگین {avg_items} محصول در هر سبد"
    except Exception as e:
        return f"خطا: {str(e)}"


def churn_rate(df):
    """نرخ ریزش مشتری"""
    try:
        if 'date' not in df.columns or 'customer_id' not in df.columns:
            return None

        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
        df_copy = df_copy[df_copy['date'].notna()]

        if df_copy.empty:
            return None

        today = datetime.now()
        last_30_days = set(df_copy[df_copy['date'] >= today - timedelta(days=30)]['customer_id'].unique())
        last_60_days = set(df_copy[df_copy['date'] >= today - timedelta(days=60)]['customer_id'].unique())

        churned = last_60_days - last_30_days
        if len(last_60_days) > 0:
            return round((len(churned) / len(last_60_days)) * 100, 2)
        return None
    except:
        return None


def top_low_products(df):
    """10 محصول پرفروش و کم‌فروش"""
    try:
        if 'product' not in df.columns or 'quantity_sold' not in df.columns:
            return "ستون‌های مورد نیاز وجود ندارند"

        product_sales = df.groupby('product')['quantity_sold'].sum().sort_values(ascending=False)

        if product_sales.empty:
            return "داده‌ای برای تحلیل وجود ندارد"

        top10 = product_sales.head(10).to_dict()
        low10 = product_sales.tail(10).to_dict()

        return {'top_10': top10, 'low_10': low10}
    except Exception as e:
        return f"خطا: {str(e)}"


def low_stock_alert(df):
    """کالاهای رو به اتمام"""
    try:
        if 'product' not in df.columns or 'current_inventory' not in df.columns:
            return "ستون‌های مورد نیاز وجود ندارند"

        latest_stock = df.groupby('product')['current_inventory'].last()
        threshold = 10
        low_stock = latest_stock[latest_stock < threshold]

        if low_stock.empty:
            return {"وضعیت": "هیچ کالایی رو به اتمام نیست"}

        return low_stock.to_dict()
    except Exception as e:
        return f"خطا: {str(e)}"


def rfm_analysis(df):
    """دسته‌بندی RFM"""
    try:
        required = ['date', 'customer_id', 'sales_amount']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return f"ستون‌های مورد نیاز وجود ندارند: {missing}"

        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
        df_copy = df_copy[df_copy['date'].notna()]

        if df_copy.empty:
            return "هیچ تاریخ معتبری وجود ندارد"

        today = datetime.now()

        rfm = df_copy.groupby('customer_id').agg({
            'date': lambda x: (today - x.max()).days,
            'customer_id': 'count',
            'sales_amount': 'sum'
        }).rename(columns={
            'date': 'Recency',
            'customer_id': 'Frequency',
            'sales_amount': 'Monetary'
        })

        rfm['Segment'] = 'معمولی'
        rfm.loc[rfm['Recency'] <= 30, 'Segment'] = 'وفادار'
        rfm.loc[rfm['Recency'] >= 60, 'Segment'] = 'در معرض ریزش'

        return rfm['Segment'].value_counts().to_dict()
    except Exception as e:
        return f"خطا: {str(e)}"


def funnel_conversion(df):
    """نرخ تبدیل قیف فروش"""
    try:
        required = ['product_views', 'add_to_cart', 'checkout_start', 'successful_purchase']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return f"ستون‌های مورد نیاز وجود ندارند: {missing}"

        total_views = pd.to_numeric(df['product_views'], errors='coerce').sum()
        to_cart = pd.to_numeric(df['add_to_cart'], errors='coerce').sum()
        to_checkout = pd.to_numeric(df['checkout_start'], errors='coerce').sum()
        purchased = pd.to_numeric(df['successful_purchase'], errors='coerce').sum()

        if total_views == 0:
            return "داده کافی برای محاسبه قیف فروش وجود ندارد"

        return {
            'بازدید → سبد خرید': round((to_cart / total_views * 100), 2) if total_views > 0 else 0,
            'سبد خرید → تسویه': round((to_checkout / to_cart * 100), 2) if to_cart > 0 else 0,
            'تسویه → خرید': round((purchased / to_checkout * 100), 2) if to_checkout > 0 else 0,
            'نرخ نهایی تبدیل': round((purchased / total_views * 100), 2) if total_views > 0 else 0
        }
    except Exception as e:
        return f"خطا: {str(e)}"