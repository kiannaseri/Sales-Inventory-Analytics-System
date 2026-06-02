import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys

# تنظیمات matplotlib
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.facecolor'] = '#1a1a2e'
plt.rcParams['axes.facecolor'] = '#1a1a2e'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# متون دو زبانه
TEXTS = {
    'persian': {
        'control_panel': 'کنترل پنل', 'welcome': 'خوش آمدید',
        'upload_excel': '📂 بارگذاری فایل اکسل', 'clean_data': '🧹 پاکسازی اطلاعات',
        'run_analysis': '📈 اجرای ۱۲ تحلیل اصلی', 'save_data': '💾 ذخیره داده تمیز',
        'theme_toggle': '🌓 دارک/لایت مود', 'quick_stats': 'آمار لحظه‌ای',
        'records': 'رکوردها', 'total_sales': 'کل فروش', 'avg_order': 'میانگین ارزش سفارش',
        'total_customers': 'تعداد مشتریان', 'total_products': 'تعداد محصولات',
        'data_preview': '📋 پیش‌نمایش داده', 'analysis_report': '📊 گزارش ۱۲ گانه',
        'charts': '📈 نمودارهای تحلیلی', 'no_data': 'هیچ داده‌ای بارگذاری نشده است',
        'ready': '✅ آماده', 'loading': '⏳ در حال پردازش...', 'error': '❌ خطا', 'success': '✅ موفق',
        'select_chart': 'انتخاب نوع نمودار:', 'show_chart': 'نمایش نمودار',
    },
    'english': {
        'control_panel': 'Control Panel', 'welcome': 'Welcome',
        'upload_excel': '📂 Upload Excel File', 'clean_data': '🧹 Clean Data',
        'run_analysis': '📈 Run 12 Key Analyses', 'save_data': '💾 Save Clean Data',
        'theme_toggle': '🌓 Dark/Light Mode', 'quick_stats': 'Quick Stats',
        'records': 'Records', 'total_sales': 'Total Sales', 'avg_order': 'Avg Order Value',
        'total_customers': 'Total Customers', 'total_products': 'Total Products',
        'data_preview': '📋 Data Preview', 'analysis_report': '📊 Analysis Report',
        'charts': '📈 Charts', 'no_data': 'No data loaded',
        'ready': '✅ Ready', 'loading': '⏳ Loading...', 'error': '❌ Error', 'success': '✅ Success',
        'select_chart': 'Select Chart Type:', 'show_chart': 'Show Chart',
    }
}


class SalesAnalyticsApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Sales Analytics Dashboard")
        self.window.geometry("1600x950")
        self.window.minsize(1400, 800)

        self.load_user_info()

        self.original_data = None
        self.cleaned_data = None
        self.analysis_results = {}
        self.current_theme = 'dark'

        self.colors = {
            'primary': '#1f538d', 'secondary': '#2a6fb5', 'success': '#2ecc71',
            'danger': '#e74c3c', 'warning': '#f39c12', 'info': '#3498db',
            'dark': '#2c3e50', 'card_bg': '#2d2d3f', 'purple': '#9b59b6'
        }

        self.setup_ui()
        self.update_all_texts()
        self.status_label.configure(text=f"{self.get_text('ready')} | {self.get_text('welcome')} {self.user_name}")
        self.load_previous_data()

    def get_text(self, key):
        return TEXTS.get(self.language, TEXTS['persian']).get(key, key)

    def update_all_texts(self):
        if hasattr(self, 'title_label'):
            self.title_label.configure(text=self.get_text('control_panel'))
            self.subtitle_label.configure(text=f"{self.get_text('welcome')} {self.user_name}")
            self.upload_btn.configure(text=self.get_text('upload_excel'))
            self.clean_btn.configure(text=self.get_text('clean_data'))
            self.analyze_btn.configure(text=self.get_text('run_analysis'))
            self.save_btn.configure(text=self.get_text('save_data'))
            self.theme_btn.configure(text=self.get_text('theme_toggle'))
            self.stats_title.configure(text=self.get_text('quick_stats'))
            self.update_stats_display()

        if hasattr(self, 'main_content'):
            try:
                self.main_content.tab("Data").configure(text=self.get_text('data_preview'))
                self.main_content.tab("Analysis").configure(text=self.get_text('analysis_report'))
                self.main_content.tab("Charts").configure(text=self.get_text('charts'))
            except:
                pass

        if hasattr(self, 'chart_label'):
            self.chart_label.configure(text=self.get_text('select_chart'))
            self.show_chart_btn.configure(text=self.get_text('show_chart'))

        self.window.title("Sales Analytics Dashboard" if self.language == 'english' else "داشبورد تحلیل فروش")

    def update_stats_display(self):
        if not hasattr(self, 'total_records_label'):
            return
        if self.original_data is not None and not self.original_data.empty:
            data = self.cleaned_data if self.cleaned_data is not None else self.original_data
            self.total_records_label.configure(text=f"{self.get_text('records')}: {len(data)}")
            if 'sales_amount' in data.columns:
                total = data['sales_amount'].sum()
                self.total_sales_label.configure(text=f"{self.get_text('total_sales')}: {total:,.0f} Toman")
            if 'customer_id' in data.columns:
                self.total_customers_label.configure(
                    text=f"{self.get_text('total_customers')}: {data['customer_id'].nunique()}")
            if 'product' in data.columns:
                self.total_products_label.configure(
                    text=f"{self.get_text('total_products')}: {data['product'].nunique()}")
        else:
            self.total_records_label.configure(text=f"{self.get_text('records')}: 0")
            self.total_sales_label.configure(text=f"{self.get_text('total_sales')}: 0 Toman")
            self.total_customers_label.configure(text=f"{self.get_text('total_customers')}: 0")
            self.total_products_label.configure(text=f"{self.get_text('total_products')}: 0")

    def load_user_info(self):
        try:
            with open('current_user.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.user_id = int(lines[0].strip())
                self.username = lines[1].strip()
                self.user_name = lines[2].strip()
                self.user_lastname = lines[3].strip()
                self.language = lines[4].strip() if len(lines) > 4 else 'persian'
                self.user_role = lines[5].strip() if len(lines) > 5 else 'user'
        except:
            self.user_id = 1
            self.username = "guest"
            self.user_name = "Guest"
            self.language = 'persian'
            self.user_role = 'user'

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.main_frame, width=320, corner_radius=15, fg_color=self.colors['dark'])
        self.sidebar.pack(side=ctk.RIGHT, fill=ctk.Y, padx=(10, 0), pady=0)
        self.sidebar.pack_propagate(False)

        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(fill=ctk.X, padx=20, pady=20)
        self.title_label = ctk.CTkLabel(title_frame, text="", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack()
        self.subtitle_label = ctk.CTkLabel(title_frame, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.subtitle_label.pack()

        self.upload_btn = ctk.CTkButton(self.sidebar, text="", command=self.upload_excel, height=45, corner_radius=10,
                                        fg_color=self.colors['info'])
        self.upload_btn.pack(fill=ctk.X, padx=20, pady=8)
        self.clean_btn = ctk.CTkButton(self.sidebar, text="", command=self.clean_data, height=45, corner_radius=10,
                                       fg_color=self.colors['warning'])
        self.clean_btn.pack(fill=ctk.X, padx=20, pady=8)
        self.analyze_btn = ctk.CTkButton(self.sidebar, text="", command=self.run_all_analyses, height=45,
                                         corner_radius=10, fg_color=self.colors['success'])
        self.analyze_btn.pack(fill=ctk.X, padx=20, pady=8)
        self.save_btn = ctk.CTkButton(self.sidebar, text="", command=self.save_to_database, height=40, corner_radius=10,
                                      fg_color=self.colors['secondary'])
        self.save_btn.pack(fill=ctk.X, padx=20, pady=8)
        self.theme_btn = ctk.CTkButton(self.sidebar, text="", command=self.toggle_theme, height=40, corner_radius=10,
                                       fg_color=self.colors['purple'])
        self.theme_btn.pack(fill=ctk.X, padx=20, pady=8)

        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray").pack(fill=ctk.X, padx=20, pady=15)

        stats_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        stats_frame.pack(fill=ctk.X, padx=20, pady=10)
        self.stats_title = ctk.CTkLabel(stats_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.stats_title.pack(anchor="w")
        self.total_records_label = ctk.CTkLabel(stats_frame, text="", text_color="gray", anchor="w")
        self.total_records_label.pack(anchor="w", pady=(5, 0))
        self.total_sales_label = ctk.CTkLabel(stats_frame, text="", text_color="gray", anchor="w")
        self.total_sales_label.pack(anchor="w")
        self.total_customers_label = ctk.CTkLabel(stats_frame, text="", text_color="gray", anchor="w")
        self.total_customers_label.pack(anchor="w")
        self.total_products_label = ctk.CTkLabel(stats_frame, text="", text_color="gray", anchor="w")
        self.total_products_label.pack(anchor="w")

        self.status_label = ctk.CTkLabel(self.window, text="", font=ctk.CTkFont(size=12), height=30,
                                         fg_color=self.colors['dark'], corner_radius=0)
        self.status_label.pack(side=ctk.BOTTOM, fill=ctk.X)

        # Main Tabs
        self.main_content = ctk.CTkTabview(self.main_frame, corner_radius=15)
        self.main_content.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        self.data_tab = self.main_content.add("Data")
        self.analytics_tab = self.main_content.add("Analysis")
        self.charts_tab = self.main_content.add("Charts")

        # Data Tab
        info_frame = ctk.CTkFrame(self.data_tab)
        info_frame.pack(fill=ctk.X, padx=15, pady=15)
        self.data_info_label = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.data_info_label.pack(pady=10)

        table_frame = ctk.CTkFrame(self.data_tab)
        table_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=(0, 15))
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_y.pack(side=ctk.RIGHT, fill=ctk.Y)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_x.pack(side=ctk.BOTTOM, fill=ctk.X)
        self.tree = ttk.Treeview(table_frame, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set, height=25)
        self.tree.pack(fill=ctk.BOTH, expand=True)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a1a2e", foreground="white", fieldbackground="#1a1a2e")
        style.configure("Treeview.Heading", background="#2c3e50", foreground="white")

        # Analytics Tab
        self.analytics_scroll = ctk.CTkScrollableFrame(self.analytics_tab)
        self.analytics_scroll.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        self.analytics_container = ctk.CTkFrame(self.analytics_scroll, fg_color="transparent")
        self.analytics_container.pack(fill=ctk.BOTH, expand=True)

        # Charts Tab
        charts_frame = ctk.CTkFrame(self.charts_tab)
        charts_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        select_frame = ctk.CTkFrame(charts_frame)
        select_frame.pack(fill=ctk.X, pady=(0, 15))
        self.chart_label = ctk.CTkLabel(select_frame, text="", font=ctk.CTkFont(size=14))
        self.chart_label.pack(side=ctk.LEFT, padx=10)
        self.chart_type = ctk.CTkComboBox(select_frame, values=[
            "1- Daily Sales (Line Chart)", "2- Inventory Forecast (Bar Chart)",
            "3- Slow Moving Products (Bar Chart)", "4- Monthly Sales Trend (Line Chart)",
            "5- Conversion Rate (Pie Chart)", "6- Basket Analysis (Bar Chart)",
            "7- Customer Churn Rate (Pie Chart)", "8- Top 10 Products (Bar Chart)",
            "9- Bottom 10 Products (Bar Chart)", "10- Low Stock Alert (Bar Chart)",
            "11- Customer RFM Segments (Pie Chart)", "12- Sales Funnel (Bar Chart)"
        ], width=400)
        self.chart_type.pack(side=ctk.LEFT, padx=10)
        self.show_chart_btn = ctk.CTkButton(select_frame, text="", command=self.show_chart, width=120,
                                            fg_color=self.colors['success'])
        self.show_chart_btn.pack(side=ctk.LEFT, padx=10)
        self.chart_frame = ctk.CTkFrame(charts_frame)
        self.chart_frame.pack(fill=ctk.BOTH, expand=True)
        self.no_chart_label = ctk.CTkLabel(self.chart_frame, text="Select a chart", font=ctk.CTkFont(size=16),
                                           text_color="gray")
        self.no_chart_label.pack(expand=True)

    def display_dataframe_in_tree(self, df, title_key):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if df is None or df.empty:
            self.data_info_label.configure(text=self.get_text('no_data'), text_color="red")
            return
        columns = list(df.columns)
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=120, minwidth=80, anchor='center')
        for _, row in df.head(500).iterrows():
            values = []
            for col in columns:
                val = row[col]
                if col == 'sales_amount' and pd.notna(val):
                    values.append(f"{val:,.0f}")
                elif pd.isna(val):
                    values.append("-")
                else:
                    values.append(str(val)[:30])
            self.tree.insert('', 'end', values=values)
        title = self.get_text(title_key)
        self.data_info_label.configure(text=f"📊 {title} | {len(df)} {self.get_text('records')}", text_color="green")

    def upload_excel(self):
        file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return
        try:
            self.status_label.configure(text=self.get_text('loading'))
            self.window.update()
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

            # استانداردسازی ستون‌ها
            mapping = {'تاریخ': 'date', 'محصول': 'product', 'تعداد': 'quantity_sold',
                       'مبلغ': 'sales_amount', 'مشتری': 'customer_id', 'موجودی': 'current_inventory',
                       'بازدید': 'product_views', 'افزودن به سبد': 'add_to_cart',
                       'شروع تسویه': 'checkout_start', 'خرید موفق': 'successful_purchase'}
            for old, new in mapping.items():
                if old in df.columns:
                    df = df.rename(columns={old: new})

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
                df = df[df['date'].notna()]

            # پر کردن مقادیر缺失
            for col in ['quantity_sold', 'sales_amount', 'current_inventory', 'product_views', 'add_to_cart',
                        'checkout_start', 'successful_purchase']:
                if col in df.columns:
                    df[col] = df[col].fillna(0)

            if df.empty:
                messagebox.showerror(self.get_text('error'), "Invalid file")
                return

            self.original_data = df
            self.cleaned_data = None
            self.display_dataframe_in_tree(df, 'original_data')
            self.update_stats_display()
            self.status_label.configure(text=f"✅ {len(df)} {self.get_text('records')} loaded")
            messagebox.showinfo(self.get_text('success'),
                                f"{self.get_text('file_loaded')}! {len(df)} {self.get_text('records')}")
        except Exception as e:
            messagebox.showerror(self.get_text('error'), str(e))

    def clean_data(self):
        if self.original_data is None:
            messagebox.showwarning(self.get_text('error'), self.get_text('upload_first'))
            return
        self.status_label.configure(text=self.get_text('loading'))
        self.window.update()
        try:
            cleaned = self.original_data.copy()
            if 'date' in cleaned.columns:
                cleaned = cleaned[cleaned['date'].notna()]
            if 'product' in cleaned.columns:
                cleaned = cleaned[cleaned['product'].notna()]
            if 'sales_amount' in cleaned.columns:
                cleaned = cleaned[cleaned['sales_amount'] > 0]
            if 'customer_id' in cleaned.columns:
                cleaned = cleaned[cleaned['customer_id'].notna()]
            cleaned = cleaned.drop_duplicates()
            self.cleaned_data = cleaned
            self.display_dataframe_in_tree(cleaned, 'clean_data_title')
            self.update_stats_display()
            self.status_label.configure(
                text=f"✅ Cleaned: {len(self.original_data) - len(cleaned)} removed, {len(cleaned)} remaining")
            messagebox.showinfo(self.get_text('success'), f"{self.get_text('cleaning_complete')}!")
        except Exception as e:
            messagebox.showerror(self.get_text('error'), str(e))

    def load_previous_data(self):
        try:
            from database import load_user_data
            df = load_user_data(self.user_id)
            if not df.empty:
                self.original_data = df
                self.display_dataframe_in_tree(df, 'previous_data')
                self.update_stats_display()
        except:
            pass

    def save_to_database(self):
        data = self.cleaned_data if self.cleaned_data is not None else self.original_data
        if data is None or data.empty:
            messagebox.showwarning(self.get_text('error'), self.get_text('upload_first'))
            return
        try:
            from database import save_user_data
            save_user_data(self.user_id, data)
            self.status_label.configure(text="✅ Data saved")
            messagebox.showinfo(self.get_text('success'), "Data saved successfully!")
        except Exception as e:
            messagebox.showerror(self.get_text('error'), str(e))

    def toggle_theme(self):
        if self.current_theme == 'dark':
            self.current_theme = 'light'
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙 Dark Mode" if self.language == 'english' else "🌙 حالت شب")
        else:
            self.current_theme = 'dark'
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="🌓 Light Mode" if self.language == 'english' else "🌓 حالت روز")

    def run_all_analyses(self):
        data = self.cleaned_data if self.cleaned_data is not None else self.original_data
        if data is None or data.empty:
            messagebox.showwarning(self.get_text('error'), self.get_text('no_data_analysis'))
            return

        self.status_label.configure(text=self.get_text('loading'))
        self.window.update()

        for widget in self.analytics_container.winfo_children():
            widget.destroy()

        # Header
        header = ctk.CTkFrame(self.analytics_container, corner_radius=10, fg_color=self.colors['primary'])
        header.pack(fill=ctk.X, pady=(0, 15))
        ctk.CTkLabel(header, text="12-KEY SALES ANALYTICS REPORT", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=15)
        ctk.CTkLabel(header, text=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Records: {len(data)}",
                     font=ctk.CTkFont(size=12)).pack(pady=(0, 15))

        self.analysis_results = {}

        # 1. Daily Sales Report
        if 'date' in data.columns and 'sales_amount' in data.columns:
            daily = data.groupby('date')['sales_amount'].sum().sort_index(ascending=False).head(10)
            self.analysis_results['daily_sales'] = daily
            self.create_analytics_card("1️⃣ Daily Sales Report (Last 10 Days)", daily.to_dict())

        # 2. Inventory Forecast
        if all(col in data.columns for col in ['date', 'product', 'quantity_sold', 'current_inventory']):
            data_copy = data.copy()
            data_copy['date'] = pd.to_datetime(data_copy['date'])
            last_7 = data_copy[data_copy['date'] >= datetime.now() - timedelta(days=7)]
            if not last_7.empty:
                avg_sales = last_7.groupby('product')['quantity_sold'].mean()
                forecast = {}
                for product in avg_sales.head(10).index:
                    current = data_copy[data_copy['product'] == product]['current_inventory'].iloc[-1] if len(
                        data_copy[data_copy['product'] == product]) > 0 else 0
                    avg = avg_sales[product]
                    if avg > 0:
                        days = int(current / avg)
                        status = "🔴 Critical" if days <= 3 else "🟠 Warning" if days <= 7 else "🟢 OK"
                        forecast[product] = f"Stock: {current}, Days left: {days} {status}"
                self.analysis_results['inventory_forecast'] = forecast
                self.create_analytics_card("2️⃣ Inventory Forecast (7-Day Avg)", forecast)

        # 3. Slow Moving Products
        if all(col in data.columns for col in ['date', 'product', 'quantity_sold']):
            data_copy = data.copy()
            data_copy['date'] = pd.to_datetime(data_copy['date'])
            last_30 = data_copy[data_copy['date'] >= datetime.now() - timedelta(days=30)]
            sold = set(last_30[last_30['quantity_sold'] > 0]['product'].unique())
            all_products = set(data_copy['product'].unique())
            slow = all_products - sold
            self.analysis_results['slow_products'] = list(slow)[:20]
            self.create_analytics_card(f"3️⃣ Slow Moving Products ({len(slow)} items)",
                                       {p: "No sales in 30 days" for p in list(slow)[:15]})

        # 4. Monthly Sales Trend
        if 'date' in data.columns and 'sales_amount' in data.columns:
            data_copy = data.copy()
            data_copy['date'] = pd.to_datetime(data_copy['date'])
            data_copy['month'] = data_copy['date'].dt.strftime('%Y-%m')
            monthly = data_copy.groupby('month')['sales_amount'].sum().sort_index().tail(6)
            self.analysis_results['monthly_trend'] = monthly
            self.create_analytics_card("4️⃣ Monthly Sales Trend (Last 6 Months)", monthly.to_dict())

        # 5. Conversion Rate
        if 'product_views' in data.columns and 'successful_purchase' in data.columns:
            views = data['product_views'].sum()
            purchases = data['successful_purchase'].sum()
            cr = (purchases / views * 100) if views > 0 else 0
            self.analysis_results['conversion_rate'] = cr
            self.create_analytics_card("5️⃣ Conversion Rate",
                                       {"Rate": f"{cr:.2f}%", "Views": int(views), "Purchases": int(purchases)})

        # 6. Basket Analysis
        if 'customer_id' in data.columns and 'product' in data.columns:
            baskets = data.groupby('customer_id')['product'].apply(list)
            avg_items = baskets.str.len().mean()
            self.analysis_results['basket_analysis'] = {"Total Baskets": len(baskets), "Avg Items": f"{avg_items:.2f}"}
            self.create_analytics_card("6️⃣ Basket Analysis", self.analysis_results['basket_analysis'])

        # 7. Customer Churn Rate
        if 'date' in data.columns and 'customer_id' in data.columns:
            data_copy = data.copy()
            data_copy['date'] = pd.to_datetime(data_copy['date'])
            last_30 = set(data_copy[data_copy['date'] >= datetime.now() - timedelta(days=30)]['customer_id'].unique())
            last_60 = set(data_copy[data_copy['date'] >= datetime.now() - timedelta(days=60)]['customer_id'].unique())
            churned = last_60 - last_30
            churn = (len(churned) / len(last_60) * 100) if len(last_60) > 0 else 0
            self.analysis_results['churn_rate'] = churn
            self.create_analytics_card("7️⃣ Customer Churn Rate",
                                       {"Rate": f"{churn:.1f}%", "Churned": len(churned), "Total 60d": len(last_60)})

        # 8. Top 10 Products
        if 'product' in data.columns and 'quantity_sold' in data.columns:
            product_sales = data.groupby('product')['quantity_sold'].sum().sort_values(ascending=False)
            self.analysis_results['top_products'] = product_sales.head(10).to_dict()
            self.create_analytics_card("8️⃣ Top 10 Products", self.analysis_results['top_products'])

        # 9. Bottom 10 Products
        if 'product' in data.columns and 'quantity_sold' in data.columns:
            product_sales = data.groupby('product')['quantity_sold'].sum().sort_values(ascending=True)
            self.analysis_results['bottom_products'] = product_sales.head(10).to_dict()
            self.create_analytics_card("9️⃣ Bottom 10 Products", self.analysis_results['bottom_products'])

        # 10. Low Stock Alert
        if 'product' in data.columns and 'current_inventory' in data.columns:
            latest = data.groupby('product')['current_inventory'].last()
            low = latest[latest < 10].to_dict()
            self.analysis_results['low_stock'] = low
            self.create_analytics_card(f"🔟 Low Stock Alert ({len(low)} items)",
                                       low if low else {"Status": "No low stock items"})

        # 11. RFM Segmentation
        if all(col in data.columns for col in ['date', 'customer_id', 'sales_amount']):
            data_copy = data.copy()
            data_copy['date'] = pd.to_datetime(data_copy['date'])
            today = datetime.now()
            rfm = data_copy.groupby('customer_id').agg({
                'date': lambda x: (today - x.max()).days,
                'customer_id': 'count',
                'sales_amount': 'sum'
            })
            loyal = len(rfm[rfm['date'] <= 30])
            regular = len(rfm[(rfm['date'] > 30) & (rfm['date'] <= 60)])
            at_risk = len(rfm[rfm['date'] > 60])
            self.analysis_results['rfm'] = {"👑 Loyal": loyal, "📊 Regular": regular, "⚠️ At Risk": at_risk}
            self.create_analytics_card("1️⃣1️⃣ Customer RFM Segmentation", self.analysis_results['rfm'])

        # 12. Sales Funnel
        funnel_cols = ['product_views', 'add_to_cart', 'checkout_start', 'successful_purchase']
        if all(col in data.columns for col in funnel_cols):
            funnel = {col.replace('_', ' ').title(): int(data[col].sum()) for col in funnel_cols}
            self.analysis_results['funnel'] = funnel
            if funnel.get('Product Views', 0) > 0:
                funnel['View to Cart'] = f"{(funnel.get('Add To Cart', 0) / funnel['Product Views'] * 100):.1f}%"
                funnel[
                    'Cart to Checkout'] = f"{(funnel.get('Checkout Start', 0) / funnel.get('Add To Cart', 1) * 100):.1f}%" if funnel.get(
                    'Add To Cart', 0) > 0 else "0%"
                funnel[
                    'Checkout to Purchase'] = f"{(funnel.get('Successful Purchase', 0) / funnel.get('Checkout Start', 1) * 100):.1f}%" if funnel.get(
                    'Checkout Start', 0) > 0 else "0%"
            self.create_analytics_card("1️⃣2️⃣ Sales Funnel", funnel)

        footer = ctk.CTkFrame(self.analytics_container, corner_radius=10, fg_color=self.colors['success'])
        footer.pack(fill=ctk.X, pady=(15, 0))
        ctk.CTkLabel(footer, text=f"✅ Analysis Complete | Go to Charts tab for visualizations",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(pady=12)

        self.status_label.configure(text=f"✅ Analysis completed - 12 analyses done")
        messagebox.showinfo(self.get_text('success'), f"12 analyses completed!\nGo to Charts tab for visualizations.")

    def create_analytics_card(self, title, content):
        card = ctk.CTkFrame(self.analytics_container, corner_radius=10, fg_color=self.colors['card_bg'])
        card.pack(fill=ctk.X, pady=5, padx=5)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkFrame(card, height=1, fg_color="gray").pack(fill=ctk.X, padx=15)
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill=ctk.X, padx=15, pady=10)
        if isinstance(content, dict):
            for k, v in list(content.items())[:15]:
                ctk.CTkLabel(content_frame, text=f"• {k}: {v}", font=ctk.CTkFont(size=12), wraplength=500,
                             justify="left").pack(anchor="w", pady=2)
        elif isinstance(content, str):
            ctk.CTkLabel(content_frame, text=content, font=ctk.CTkFont(size=12)).pack(anchor="w")

    def show_chart(self):
        if not self.analysis_results:
            messagebox.showwarning(self.get_text('error'), self.get_text('run_analysis_first'))
            return

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        chart_name = self.chart_type.get()
        fig = plt.figure(figsize=(13, 7), facecolor='#1a1a2e', dpi=100)

        try:
            # 1. Daily Sales
            if "Daily Sales" in chart_name and 'daily_sales' in self.analysis_results:
                data = self.analysis_results['daily_sales']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                dates = [str(d) for d in data.index]
                values = list(data.values)
                ax.plot(range(len(dates)), values, marker='o', linewidth=2, color='#3498db', markersize=8)
                ax.fill_between(range(len(dates)), values, alpha=0.3, color='#3498db')
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=8)
                ax.set_ylabel('Sales Amount', fontsize=11, color='white')
                ax.set_title('Daily Sales Report', fontsize=13, color='white', pad=15)
                ax.tick_params(colors='white')
                ax.grid(True, alpha=0.2)

            # 2. Inventory Forecast
            elif "Inventory Forecast" in chart_name and 'inventory_forecast' in self.analysis_results:
                inv = self.analysis_results['inventory_forecast']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                products = list(inv.keys())[:10]
                days = []
                for p in products:
                    try:
                        days.append(int(inv[p].split('Days left: ')[1].split()[0]))
                    except:
                        days.append(0)
                colors = ['#e74c3c' if d <= 3 else '#f39c12' if d <= 7 else '#2ecc71' for d in days]
                ax.barh(range(len(products)), days, color=colors)
                ax.set_yticks(range(len(products)))
                ax.set_yticklabels(products, fontsize=8)
                ax.set_xlabel('Days Until Out of Stock', fontsize=11, color='white')
                ax.set_title('Inventory Forecast', fontsize=13, color='white', pad=15)
                ax.tick_params(colors='white')

            # 3. Slow Moving Products
            elif "Slow Moving" in chart_name and 'slow_products' in self.analysis_results:
                slow = self.analysis_results['slow_products']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                if slow:
                    ax.barh(range(min(10, len(slow))), [1] * min(10, len(slow)), color='#e74c3c')
                    ax.set_yticks(range(min(10, len(slow))))
                    ax.set_yticklabels(slow[:10], fontsize=8)
                    ax.set_title(f'Slow Moving Products (Total: {len(slow)})', fontsize=13, color='white', pad=15)
                else:
                    ax.text(0.5, 0.5, 'No slow moving products', transform=ax.transAxes, ha='center', va='center',
                            fontsize=14, color='white')
                ax.tick_params(colors='white')

            # 4. Monthly Trend
            elif "Monthly Sales Trend" in chart_name and 'monthly_trend' in self.analysis_results:
                trend = self.analysis_results['monthly_trend']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                months = [str(m) for m in trend.index]
                values = list(trend.values)
                ax.plot(range(len(months)), values, marker='s', linewidth=2, color='#9b59b6', markersize=7)
                ax.fill_between(range(len(months)), values, alpha=0.3, color='#9b59b6')
                ax.set_xticks(range(len(months)))
                ax.set_xticklabels(months, rotation=45, ha='right', fontsize=8)
                ax.set_ylabel('Sales Amount', fontsize=11, color='white')
                ax.set_title('Monthly Sales Trend', fontsize=13, color='white', pad=15)
                ax.tick_params(colors='white')
                ax.grid(True, alpha=0.2)

            # 5. Conversion Rate Pie
            elif "Conversion Rate" in chart_name and 'conversion_rate' in self.analysis_results:
                cr = self.analysis_results['conversion_rate']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                sizes = [cr, 100 - cr]
                labels = [f'Converted ({cr:.1f}%)', f'Not Converted ({100 - cr:.1f}%)']
                colors_pie = ['#2ecc71', '#e74c3c']
                ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90,
                       textprops={'color': 'white', 'fontsize': 10})
                ax.set_title('Conversion Rate', fontsize=13, color='white', pad=15)

            # 6. Basket Analysis
            elif "Basket Analysis" in chart_name and 'basket_analysis' in self.analysis_results:
                ba = self.analysis_results['basket_analysis']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                ax.bar(['Total Baskets', 'Avg Items'], [ba.get('Total Baskets', 0), float(ba.get('Avg Items', 0))],
                       color=['#3498db', '#2ecc71'])
                ax.set_ylabel('Value', fontsize=11, color='white')
                ax.set_title('Basket Analysis', fontsize=13, color='white', pad=15)
                ax.tick_params(colors='white')

            # 7. Churn Rate Pie
            elif "Customer Churn Rate" in chart_name and 'churn_rate' in self.analysis_results:
                churn = self.analysis_results['churn_rate']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                sizes = [churn, 100 - churn]
                labels = [f'Churned ({churn:.1f}%)', f'Retained ({100 - churn:.1f}%)']
                colors_pie = ['#e74c3c', '#2ecc71']
                ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90,
                       textprops={'color': 'white', 'fontsize': 10})
                ax.set_title('Customer Churn Rate', fontsize=13, color='white', pad=15)

            # 8. Top 10 Products
            elif "Top 10 Products" in chart_name and 'top_products' in self.analysis_results:
                top = self.analysis_results['top_products']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                products = list(top.keys())[:10]
                sales = list(top.values())[:10]
                colors_bar = plt.cm.Greens(np.linspace(0.3, 0.9, len(products)))
                ax.barh(range(len(products)), sales, color=colors_bar)
                ax.set_yticks(range(len(products)))
                ax.set_yticklabels(products, fontsize=8)
                ax.set_xlabel('Units Sold', fontsize=11, color='white')
                ax.set_title('Top 10 Products', fontsize=13, color='white', pad=15)
                ax.tick_params(colors='white')

            # 9. Bottom 10 Products
            elif "Bottom 10 Products" in chart_name and 'bottom_products' in self.analysis_results:
                low = self.analysis_results['bottom_products']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                products = list(low.keys())[:10]
                sales = list(low.values())[:10]
                colors_bar = plt.cm.Reds(np.linspace(0.3, 0.9, len(products)))
                ax.barh(range(len(products)), sales, color=colors_bar)
                ax.set_yticks(range(len(products)))
                ax.set_yticklabels(products, fontsize=8)
                ax.set_xlabel('Units Sold', fontsize=11, color='white')
                ax.set_title('Bottom 10 Products', fontsize=13, color='white', pad=15)
                ax.tick_params(colors='white')

            # 10. Low Stock Alert
            elif "Low Stock Alert" in chart_name and 'low_stock' in self.analysis_results:
                low = self.analysis_results['low_stock']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                if low:
                    products = list(low.keys())[:10]
                    stocks = list(low.values())[:10]
                    colors_bar = ['#e74c3c' if s < 5 else '#f39c12' for s in stocks]
                    ax.bar(range(len(products)), stocks, color=colors_bar)
                    ax.set_xticks(range(len(products)))
                    ax.set_xticklabels(products, rotation=45, ha='right', fontsize=7)
                    ax.set_ylabel('Remaining Stock', fontsize=11, color='white')
                    ax.set_title('Low Stock Alert (Stock < 10)', fontsize=13, color='white', pad=15)
                    ax.tick_params(colors='white')
                    for i, (bar, s) in enumerate(zip(ax.patches, stocks)):
                        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, str(int(s)), ha='center',
                                va='bottom', fontsize=8, color='white')
                else:
                    ax.text(0.5, 0.5, 'No low stock items', transform=ax.transAxes, ha='center', va='center',
                            fontsize=14, color='white')

            # 11. RFM Segmentation Pie
            elif "RFM" in chart_name and 'rfm' in self.analysis_results:
                rfm = self.analysis_results['rfm']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                sizes = [rfm.get('👑 Loyal', 0), rfm.get('📊 Regular', 0), rfm.get('⚠️ At Risk', 0)]
                labels = [f'Loyal ({sizes[0]})', f'Regular ({sizes[1]})', f'At Risk ({sizes[2]})']
                colors_pie = ['#2ecc71', '#f39c12', '#e74c3c']
                ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90,
                       textprops={'color': 'white', 'fontsize': 10})
                ax.set_title('Customer RFM Segmentation', fontsize=13, color='white', pad=15)

            # 12. Sales Funnel
            elif "Sales Funnel" in chart_name and 'funnel' in self.analysis_results:
                funnel = self.analysis_results['funnel']
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                stages = ['Views', 'Cart', 'Checkout', 'Purchase']
                values = [funnel.get('Product Views', 0), funnel.get('Add To Cart', 0),
                          funnel.get('Checkout Start', 0), funnel.get('Successful Purchase', 0)]
                colors_bar = ['#3498db', '#f39c12', '#e67e22', '#2ecc71']
                bars = ax.bar(stages, values, color=colors_bar)
                ax.set_ylabel('Count', fontsize=11, color='white')
                ax.set_title('Sales Funnel', fontsize=13, color='white', pad=15)
                ax.tick_params(colors='white')
                if funnel.get('Product Views', 0) > 0:
                    for i, bar in enumerate(bars):
                        pct = (values[i] / funnel['Product Views']) * 100
                        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.02,
                                f'{pct:.1f}%', ha='center', va='bottom', fontsize=9, color='white', fontweight='bold')

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

        except Exception as e:
            error_label = ctk.CTkLabel(self.chart_frame, text=f"Error: {str(e)}", text_color="red")
            error_label.pack(expand=True)
            print(f"Chart error: {e}")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = SalesAnalyticsApp()
    app.run()