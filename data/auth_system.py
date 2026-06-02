import customtkinter as ctk
from tkinter import messagebox
from database_auth import init_user_database, register_user, login_user
import subprocess
import sys
import os

# تنظیمات ظاهری
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AuthWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("ورود به سیستم")
        self.window.geometry("600x700")
        self.window.resizable(False, False)

        # متغیرهای نمایش رمز
        self.show_password_login = False

        # زبان فعلی
        self.current_language = 'persian'

        # متون زبان‌ها
        self.texts = {
            'persian': {
                'app_title': '📊 سیستم تحلیل هوشمند فروش و انبار',
                'login_title': 'ورود به سیستم',
                'username': 'نام کاربری',
                'password': 'رمز عبور',
                'login_btn': 'ورود',
                'register_btn': 'ثبت نام',
                'language': 'زبان:',
                'login_success': 'ورود با موفقیت انجام شد!',
                'login_failed': 'نام کاربری یا رمز عبور اشتباه است!',
                'register_title': 'ثبت نام کاربر جدید',
                'first_name': 'نام',
                'last_name': 'نام خانوادگی',
                'confirm_password': 'تکرار رمز عبور',
                'register_new_btn': 'ثبت نام',
                'back_btn': 'بازگشت به صفحه ورود',
                'go_to_login': 'رفتن به صفحه ورود',
                'register_success': 'ثبت نام با موفقیت انجام شد!',
                'empty_fields': 'لطفا تمام فیلدها را پر کنید!',
                'password_mismatch': 'رمز عبور و تکرار آن مطابقت ندارند!',
                'welcome': 'خوش آمدید',
                'show_password': '👁 نمایش رمز',
                'hide_password': '🙈 مخفی کردن رمز'
            },
            'english': {
                'app_title': '📊 Sales & Inventory Analytics System',
                'login_title': 'Login',
                'username': 'Username',
                'password': 'Password',
                'login_btn': 'Login',
                'register_btn': 'Register',
                'language': 'Language:',
                'login_success': 'Login successful!',
                'login_failed': 'Invalid username or password!',
                'register_title': 'Register New User',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'confirm_password': 'Confirm Password',
                'register_new_btn': 'Register',
                'back_btn': 'Back to Login',
                'go_to_login': 'Go to Login Page',
                'register_success': 'Registration successful!',
                'empty_fields': 'Please fill all fields!',
                'password_mismatch': 'Passwords do not match!',
                'welcome': 'Welcome',
                'show_password': '👁 Show',
                'hide_password': '🙈 Hide'
            }
        }

        # راه‌اندازی دیتابیس
        init_user_database()

        # ساخت رابط کاربری
        self.setup_ui()

    def get_text(self, key):
        """دریافت متن بر اساس زبان"""
        return self.texts[self.current_language].get(key, key)

    def toggle_password_visibility_login(self):
        """نمایش/مخفی کردن رمز عبور در صفحه ورود"""
        self.show_password_login = not self.show_password_login
        if self.show_password_login:
            self.password_entry.configure(show="")
            self.show_password_btn.configure(text=self.get_text('hide_password'))
        else:
            self.password_entry.configure(show="*")
            self.show_password_btn.configure(text=self.get_text('show_password'))

    def setup_ui(self):
        """ساخت رابط کاربری ورود"""

        # فریم اصلی
        self.main_frame = ctk.CTkFrame(self.window, corner_radius=20)
        self.main_frame.pack(expand=True, fill=ctk.BOTH, padx=30, pady=30)

        # عنوان
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=self.get_text('app_title'),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=25)

        # انتخاب زبان
        lang_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        lang_frame.pack(pady=10)

        self.lang_label = ctk.CTkLabel(lang_frame, text=self.get_text('language'), font=ctk.CTkFont(size=12))
        self.lang_label.pack(side=ctk.LEFT, padx=5)

        self.lang_combo = ctk.CTkComboBox(
            lang_frame,
            values=["فارسی", "English"],
            command=self.change_language,
            width=120
        )
        self.lang_combo.pack(side=ctk.LEFT, padx=5)

        # فریم ورود
        login_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        login_frame.pack(pady=25)

        # نام کاربری
        self.username_label = ctk.CTkLabel(login_frame, text=self.get_text('username'), font=ctk.CTkFont(size=14))
        self.username_label.pack(anchor="w", pady=(0, 5))

        self.username_entry = ctk.CTkEntry(login_frame, width=400, height=45, font=ctk.CTkFont(size=14))
        self.username_entry.pack(pady=(0, 15))

        # رمز عبور با دکمه نمایش
        self.password_label = ctk.CTkLabel(login_frame, text=self.get_text('password'), font=ctk.CTkFont(size=14))
        self.password_label.pack(anchor="w", pady=(0, 5))

        # فریم برای قرار دادن entry و دکمه در کنار هم
        password_container = ctk.CTkFrame(login_frame, fg_color="transparent")
        password_container.pack(fill=ctk.X, pady=(0, 20))

        self.password_entry = ctk.CTkEntry(password_container, width=310, height=45, font=ctk.CTkFont(size=14),
                                           show="*")
        self.password_entry.pack(side=ctk.LEFT, padx=(0, 10))

        self.show_password_btn = ctk.CTkButton(
            password_container,
            text=self.get_text('show_password'),
            command=self.toggle_password_visibility_login,
            width=90, height=45,
            font=ctk.CTkFont(size=12),
            fg_color="#34495e",
            hover_color="#2c3e50"
        )
        self.show_password_btn.pack(side=ctk.LEFT)

        # دکمه ورود
        self.login_btn = ctk.CTkButton(
            login_frame,
            text=self.get_text('login_btn'),
            command=self.login,
            width=400, height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.login_btn.pack(pady=15)

        # دکمه ثبت نام
        self.register_btn = ctk.CTkButton(
            login_frame,
            text=self.get_text('register_btn'),
            command=self.open_register_window,
            width=400, height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.register_btn.pack(pady=5)

        # رویداد Enter
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())

    def change_language(self, choice):
        """تغییر زبان"""
        if choice == "فارسی":
            self.current_language = 'persian'
        else:
            self.current_language = 'english'

        # به‌روزرسانی متون
        self.title_label.configure(text=self.get_text('app_title'))
        self.lang_label.configure(text=self.get_text('language'))
        self.username_label.configure(text=self.get_text('username'))
        self.password_label.configure(text=self.get_text('password'))
        self.login_btn.configure(text=self.get_text('login_btn'))
        self.register_btn.configure(text=self.get_text('register_btn'))

        # به‌روزرسانی دکمه نمایش رمز
        if self.show_password_login:
            self.show_password_btn.configure(text=self.get_text('hide_password'))
        else:
            self.show_password_btn.configure(text=self.get_text('show_password'))

    def login(self):
        """ورود کاربر"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("خطا", self.get_text('empty_fields'))
            return

        success, result = login_user(username, password)

        if success:
            # ذخیره اطلاعات کاربر برای برنامه اصلی
            with open('current_user.txt', 'w', encoding='utf-8') as f:
                f.write(f"{result['id']}\n")
                f.write(f"{result['username']}\n")
                f.write(f"{result['first_name']}\n")
                f.write(f"{result['last_name']}\n")
                f.write(f"{self.current_language}\n")

            messagebox.showinfo("موفق", self.get_text('login_success'))
            self.window.destroy()

            # اجرای برنامه اصلی (app.py)
            subprocess.Popen([sys.executable, 'app.py'])
            sys.exit()
        else:
            messagebox.showerror("خطا", self.get_text('login_failed'))

    def open_register_window(self):
        """باز کردن پنجره ثبت نام"""
        # مخفی کردن پنجره اصلی
        self.window.withdraw()
        RegisterWindow(self.current_language, self)


class RegisterWindow:
    def __init__(self, language='persian', parent_window=None):
        self.language = language
        self.parent_window = parent_window
        self.window = ctk.CTkToplevel()
        self.window.title("ثبت نام")
        self.window.geometry("650x800")
        self.window.resizable(False, False)

        # متغیرهای نمایش رمز
        self.show_password = False
        self.show_confirm_password = False

        # تنظیم بستن پنجره
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.texts = {
            'persian': {
                'title': '📝 ثبت نام کاربر جدید',
                'first_name': 'نام',
                'last_name': 'نام خانوادگی',
                'username': 'نام کاربری',
                'password': 'رمز عبور',
                'confirm_password': 'تکرار رمز عبور',
                'register_btn': '✅ ثبت نام',
                'back_btn': '🔙 برگشت به صفحه ورود',
                'success': 'ثبت نام با موفقیت انجام شد!',
                'empty': 'لطفا تمام فیلدها را پر کنید!',
                'mismatch': 'رمز عبور و تکرار آن مطابقت ندارند!',
                'show_password': '👁 نمایش',
                'hide_password': '🙈 مخفی'
            },
            'english': {
                'title': '📝 Register New User',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'username': 'Username',
                'password': 'Password',
                'confirm_password': 'Confirm Password',
                'register_btn': '✅ Register',
                'back_btn': '🔙 Back to Login',
                'success': 'Registration successful!',
                'empty': 'Please fill all fields!',
                'mismatch': 'Passwords do not match!',
                'show_password': '👁 Show',
                'hide_password': '🙈 Hide'
            }
        }

        self.setup_ui()

    def get_text(self, key):
        return self.texts[self.language].get(key, key)

    def on_close(self):
        """وقتی پنجره بسته می‌شود"""
        if self.parent_window:
            self.parent_window.window.deiconify()  # نمایش پنجره اصلی
        self.window.destroy()

    def toggle_password_visibility(self):
        """نمایش/مخفی کردن رمز عبور"""
        self.show_password = not self.show_password
        if self.show_password:
            self.password_entry.configure(show="")
            self.show_password_btn.configure(text=self.get_text('hide_password'))
        else:
            self.password_entry.configure(show="*")
            self.show_password_btn.configure(text=self.get_text('show_password'))

    def toggle_confirm_password_visibility(self):
        """نمایش/مخفی کردن تکرار رمز عبور"""
        self.show_confirm_password = not self.show_confirm_password
        if self.show_confirm_password:
            self.confirm_entry.configure(show="")
            self.show_confirm_btn.configure(text=self.get_text('hide_password'))
        else:
            self.confirm_entry.configure(show="*")
            self.show_confirm_btn.configure(text=self.get_text('show_password'))

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.window, corner_radius=20)
        self.main_frame.pack(expand=True, fill=ctk.BOTH, padx=30, pady=30)

        title = ctk.CTkLabel(
            self.main_frame,
            text=self.get_text('title'),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=25)

        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(pady=20)

        # نام
        ctk.CTkLabel(form_frame, text=self.get_text('first_name'), font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, 5))
        self.first_name_entry = ctk.CTkEntry(form_frame, width=450, height=45, font=ctk.CTkFont(size=14),
                                             placeholder_text="مثال: علی")
        self.first_name_entry.pack(pady=(0, 15))

        # نام خانوادگی
        ctk.CTkLabel(form_frame, text=self.get_text('last_name'), font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, 5))
        self.last_name_entry = ctk.CTkEntry(form_frame, width=450, height=45, font=ctk.CTkFont(size=14),
                                            placeholder_text="مثال: محمدی")
        self.last_name_entry.pack(pady=(0, 15))

        # نام کاربری
        ctk.CTkLabel(form_frame, text=self.get_text('username'), font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, 5))
        self.username_entry = ctk.CTkEntry(form_frame, width=450, height=45, font=ctk.CTkFont(size=14),
                                           placeholder_text="مثال: alim22")
        self.username_entry.pack(pady=(0, 15))

        # رمز عبور با دکمه نمایش
        ctk.CTkLabel(form_frame, text=self.get_text('password'), font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, 5))

        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(fill=ctk.X, pady=(0, 15))

        self.password_entry = ctk.CTkEntry(password_frame, width=360, height=45, font=ctk.CTkFont(size=14), show="*",
                                           placeholder_text="••••••••")
        self.password_entry.pack(side=ctk.LEFT, padx=(0, 10))

        self.show_password_btn = ctk.CTkButton(
            password_frame,
            text=self.get_text('show_password'),
            command=self.toggle_password_visibility,
            width=90, height=45,
            font=ctk.CTkFont(size=12),
            fg_color="#34495e",
            hover_color="#2c3e50"
        )
        self.show_password_btn.pack(side=ctk.LEFT)

        # تکرار رمز عبور با دکمه نمایش
        ctk.CTkLabel(form_frame, text=self.get_text('confirm_password'), font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, 5))

        confirm_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        confirm_frame.pack(fill=ctk.X, pady=(0, 25))

        self.confirm_entry = ctk.CTkEntry(confirm_frame, width=360, height=45, font=ctk.CTkFont(size=14), show="*",
                                          placeholder_text="••••••••")
        self.confirm_entry.pack(side=ctk.LEFT, padx=(0, 10))

        self.show_confirm_btn = ctk.CTkButton(
            confirm_frame,
            text=self.get_text('show_password'),
            command=self.toggle_confirm_password_visibility,
            width=90, height=45,
            font=ctk.CTkFont(size=12),
            fg_color="#34495e",
            hover_color="#2c3e50"
        )
        self.show_confirm_btn.pack(side=ctk.LEFT)

        # دکمه ثبت نام (بزرگ - 55px)
        self.register_btn = ctk.CTkButton(
            form_frame,
            text=self.get_text('register_btn'),
            command=self.register,
            width=450, height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.register_btn.pack(pady=15)

        # دکمه بازگشت به صفحه ورود
        self.back_btn = ctk.CTkButton(
            form_frame,
            text=self.get_text('back_btn'),
            command=self.back_to_login,
            width=450, height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.back_btn.pack(pady=5)

    def register(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not all([first_name, last_name, username, password, confirm]):
            messagebox.showwarning("⚠️ خطا", self.get_text('empty'))
            return

        if password != confirm:
            messagebox.showwarning("⚠️ خطا", self.get_text('mismatch'))
            return

        success, message = register_user(first_name, last_name, username, password, self.language)

        if success:
            messagebox.showinfo("✅ موفق", self.get_text('success'))
            # بستن پنجره ثبت نام و نمایش پنجره ورود
            self.window.destroy()
            if self.parent_window:
                self.parent_window.window.deiconify()  # نمایش پنجره اصلی
        else:
            messagebox.showerror("❌ خطا", message)

    def back_to_login(self):
        """بازگشت به صفحه ورود - بدون بسته شدن برنامه"""
        self.window.destroy()
        if self.parent_window:
            self.parent_window.window.deiconify()  # نمایش پنجره اصلی


def main():
    app = AuthWindow()
    app.window.mainloop()


if __name__ == "__main__":
    main()