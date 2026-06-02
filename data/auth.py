import customtkinter as ctk
from tkinter import messagebox
from database import init_user_database, register_user, login_user, get_security_question, verify_security_answer, \
    reset_password_direct
import subprocess
import sys
import os

# تنظیمات ظاهری
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AuthWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Login - Sales Analytics System")
        self.window.geometry("500x600")
        self.window.resizable(False, False)

        self.current_language = 'persian'

        # راه‌اندازی دیتابیس
        init_user_database()

        self.setup_ui()

    def setup_ui(self):
        """ساخت رابط کاربری ورود"""

        self.main_frame = ctk.CTkFrame(self.window, corner_radius=20)
        self.main_frame.pack(expand=True, fill=ctk.BOTH, padx=30, pady=30)

        # عنوان
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="📊 سیستم تحلیل هوشمند فروش و انبار",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=30)

        # انتخاب زبان
        lang_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        lang_frame.pack(pady=10)

        ctk.CTkLabel(lang_frame, text="زبان:", font=ctk.CTkFont(size=12)).pack(side=ctk.LEFT, padx=5)

        self.lang_combo = ctk.CTkComboBox(
            lang_frame,
            values=["فارسی", "English"],
            command=self.change_language,
            width=120
        )
        self.lang_combo.pack(side=ctk.LEFT, padx=5)
        self.lang_combo.set("فارسی")

        # فرم ورود
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(pady=30)

        # نام کاربری
        ctk.CTkLabel(form_frame, text="نام کاربری:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.username_entry = ctk.CTkEntry(form_frame, width=300, height=40, font=ctk.CTkFont(size=14))
        self.username_entry.pack(pady=(0, 15))

        # رمز عبور
        ctk.CTkLabel(form_frame, text="رمز عبور:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.password_entry = ctk.CTkEntry(form_frame, width=300, height=40, font=ctk.CTkFont(size=14), show="*")
        self.password_entry.pack(pady=(0, 20))

        # دکمه ورود
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="ورود",
            command=self.login,
            width=300, height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71"
        )
        self.login_btn.pack(pady=10)

        # دکمه ثبت نام
        self.register_btn = ctk.CTkButton(
            form_frame,
            text="ثبت نام",
            command=self.open_register_window,
            width=300, height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#3498db"
        )
        self.register_btn.pack(pady=5)

        # دکمه فراموشی رمز
        self.forgot_btn = ctk.CTkButton(
            form_frame,
            text="فراموشی رمز عبور؟",
            command=self.open_forgot_password_window,
            width=300, height=35,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="#34495e"
        )
        self.forgot_btn.pack(pady=5)

        # رویداد Enter
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())

    def change_language(self, choice):
        """تغییر زبان"""
        if choice == "فارسی":
            self.current_language = 'persian'
            self.title_label.configure(text="📊 سیستم تحلیل هوشمند فروش و انبار")
            self.login_btn.configure(text="ورود")
            self.register_btn.configure(text="ثبت نام")
            self.forgot_btn.configure(text="فراموشی رمز عبور؟")
        else:
            self.current_language = 'english'
            self.title_label.configure(text="📊 Sales & Inventory Analytics System")
            self.login_btn.configure(text="Login")
            self.register_btn.configure(text="Register")
            self.forgot_btn.configure(text="Forgot Password?")

    def login(self):
        """ورود کاربر"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("خطا", "لطفا نام کاربری و رمز عبور را وارد کنید")
            return

        success, result = login_user(username, password)

        if success:
            messagebox.showinfo("موفقیت", f"خوش آمدید {result['first_name']} {result['last_name']}")

            # ذخیره اطلاعات کاربر
            with open('current_user.txt', 'w', encoding='utf-8') as f:
                f.write(f"{result['id']}\n")
                f.write(f"{result['username']}\n")
                f.write(f"{result['first_name']}\n")
                f.write(f"{result['last_name']}\n")
                f.write(f"{self.current_language}\n")
                f.write(f"{result['role']}\n")

            self.window.destroy()

            # اجرای برنامه اصلی
            try:
                subprocess.Popen([sys.executable, 'app.py'])
            except Exception as e:
                print(f"Error launching app: {e}")
                # اگر اجرا نشد، مستقیم import کن
                from app import SalesAnalyticsApp
                root = ctk.CTk()
                root.withdraw()
                app = SalesAnalyticsApp()
                app.run()

            sys.exit(0)
        else:
            messagebox.showerror("خطا", "نام کاربری یا رمز عبور اشتباه است!")
    def open_register_window(self):
        """باز کردن پنجره ثبت نام"""
        self.window.withdraw()
        RegisterWindow(self.current_language, self)

    def open_forgot_password_window(self):
        """باز کردن پنجره بازیابی رمز"""
        self.window.withdraw()
        ForgotPasswordWindow(self.current_language, self)

    def show(self):
        """نمایش پنجره"""
        self.window.deiconify()


class RegisterWindow:
    def __init__(self, language='persian', parent_window=None):
        self.language = language
        self.parent_window = parent_window
        self.window = ctk.CTkToplevel()
        self.window.title("ثبت نام کاربر جدید")
        self.window.geometry("500x650")
        self.window.resizable(False, False)

        # در صورت بستن پنجره، پنجره اصلی را نشان بده
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.setup_ui()

    def on_close(self):
        """بستن پنجره و نمایش پنجره اصلی"""
        self.window.destroy()
        if self.parent_window:
            self.parent_window.show()

    def setup_ui(self):
        """ساخت رابط کاربری ثبت نام"""

        self.main_frame = ctk.CTkFrame(self.window, corner_radius=20)
        self.main_frame.pack(expand=True, fill=ctk.BOTH, padx=30, pady=30)

        # عنوان
        title = ctk.CTkLabel(
            self.main_frame,
            text="📝 ثبت نام کاربر جدید",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)

        # فرم
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(pady=20)

        # نام
        ctk.CTkLabel(form_frame, text="نام:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.first_name_entry = ctk.CTkEntry(form_frame, width=300, height=40, font=ctk.CTkFont(size=14))
        self.first_name_entry.pack(pady=(0, 15))

        # نام خانوادگی
        ctk.CTkLabel(form_frame, text="نام خانوادگی:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.last_name_entry = ctk.CTkEntry(form_frame, width=300, height=40, font=ctk.CTkFont(size=14))
        self.last_name_entry.pack(pady=(0, 15))

        # نام کاربری
        ctk.CTkLabel(form_frame, text="نام کاربری:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.username_entry = ctk.CTkEntry(form_frame, width=300, height=40, font=ctk.CTkFont(size=14))
        self.username_entry.pack(pady=(0, 15))

        # رمز عبور
        ctk.CTkLabel(form_frame, text="رمز عبور:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.password_entry = ctk.CTkEntry(form_frame, width=300, height=40, font=ctk.CTkFont(size=14), show="*")
        self.password_entry.pack(pady=(0, 15))

        # تکرار رمز
        ctk.CTkLabel(form_frame, text="تکرار رمز عبور:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.confirm_password_entry = ctk.CTkEntry(form_frame, width=300, height=40, font=ctk.CTkFont(size=14),
                                                   show="*")
        self.confirm_password_entry.pack(pady=(0, 20))

        # دکمه ثبت نام
        register_btn = ctk.CTkButton(
            form_frame,
            text="ثبت نام",
            command=self.register,
            width=300, height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71"
        )
        register_btn.pack(pady=10)

        # دکمه بازگشت
        back_btn = ctk.CTkButton(
            form_frame,
            text="بازگشت به صفحه ورود",
            command=self.back_to_login,
            width=300, height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#e74c3c"
        )
        back_btn.pack(pady=5)

    def register(self):
        """ثبت نام کاربر"""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()

        if not all([first_name, last_name, username, password, confirm]):
            messagebox.showwarning("خطا", "لطفا تمام فیلدها را پر کنید!")
            return

        if password != confirm:
            messagebox.showwarning("خطا", "رمز عبور و تکرار آن مطابقت ندارند!")
            return

        if len(password) < 4:
            messagebox.showwarning("خطا", "رمز عبور باید حداقل ۴ کاراکتر باشد!")
            return

        success, _, message = register_user(first_name, last_name, username, password, '', self.language)

        if success:
            messagebox.showinfo("موفقیت", "ثبت نام با موفقیت انجام شد!\nاکنون می‌توانید وارد شوید.")
            self.back_to_login()
        else:
            messagebox.showerror("خطا", message)

    def back_to_login(self):
        """بازگشت به صفحه ورود"""
        self.window.destroy()
        if self.parent_window:
            self.parent_window.show()
        else:
            # اگر parent_window وجود نداشت، یک پنجره جدید باز کن
            AuthWindow()


class ForgotPasswordWindow:
    def __init__(self, language='persian', parent_window=None):
        self.language = language
        self.parent_window = parent_window
        self.user_id = None
        self.username = None
        self.window = ctk.CTkToplevel()
        self.window.title("بازیابی رمز عبور")
        self.window.geometry("500x550")
        self.window.resizable(False, False)

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.setup_ui()

    def on_close(self):
        """بستن پنجره و نمایش پنجره اصلی"""
        self.window.destroy()
        if self.parent_window:
            self.parent_window.show()

    def setup_ui(self):
        """ساخت رابط کاربری بازیابی رمز"""

        self.main_frame = ctk.CTkFrame(self.window, corner_radius=20)
        self.main_frame.pack(expand=True, fill=ctk.BOTH, padx=30, pady=30)

        ctk.CTkLabel(
            self.main_frame,
            text="🔐 بازیابی رمز عبور",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(pady=20)

        # نام کاربری
        ctk.CTkLabel(form_frame, text="نام کاربری:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.username_entry = ctk.CTkEntry(form_frame, width=300, height=40)
        self.username_entry.pack(pady=(0, 15))

        # دکمه بررسی
        self.check_btn = ctk.CTkButton(
            form_frame, text="بررسی کاربر",
            command=self.check_user, width=300, height=40,
            fg_color="#3498db"
        )
        self.check_btn.pack(pady=5)

        # سوال امنیتی (در ابتدا مخفی)
        self.question_frame = ctk.CTkFrame(form_frame, fg_color="transparent")

        ctk.CTkLabel(self.question_frame, text="سوال امنیتی:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.question_label = ctk.CTkLabel(self.question_frame, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.question_label.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(self.question_frame, text="پاسخ:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.answer_entry = ctk.CTkEntry(self.question_frame, width=300, height=40)
        self.answer_entry.pack(pady=(0, 15))

        ctk.CTkLabel(self.question_frame, text="رمز عبور جدید:", font=ctk.CTkFont(size=14)).pack(anchor="w",
                                                                                                 pady=(0, 5))
        self.new_password_entry = ctk.CTkEntry(self.question_frame, width=300, height=40, show="*")
        self.new_password_entry.pack(pady=(0, 15))

        self.reset_btn = ctk.CTkButton(
            self.question_frame, text="بازیابی رمز عبور",
            command=self.reset_password, width=300, height=40,
            fg_color="#2ecc71"
        )
        self.reset_btn.pack(pady=5)

        # دکمه بازگشت
        back_btn = ctk.CTkButton(
            form_frame, text="بازگشت به صفحه ورود",
            command=self.back_to_login, width=300, height=35,
            fg_color="transparent", hover_color="#34495e"
        )
        back_btn.pack(pady=10)

    def check_user(self):
        """بررسی کاربر و دریافت سوال امنیتی"""
        username = self.username_entry.get().strip()

        if not username:
            messagebox.showwarning("خطا", "لطفا نام کاربری را وارد کنید")
            return

        question = get_security_question(username)

        if question:
            self.username = username
            self.question_label.configure(text=question, text_color="white")
            self.question_frame.pack(fill=ctk.X, pady=10)
            self.check_btn.configure(text="✓ کاربر یافت شد", fg_color="#2ecc71", state="disabled")
        else:
            messagebox.showerror("خطا", "کاربر یافت نشد یا سوال امنیتی تنظیم نشده است")

    def reset_password(self):
        """بازیابی رمز عبور"""
        if not self.username:
            messagebox.showwarning("خطا", "لطفا ابتدا نام کاربری را بررسی کنید")
            return

        answer = self.answer_entry.get().strip()
        new_password = self.new_password_entry.get().strip()

        if not all([answer, new_password]):
            messagebox.showwarning("خطا", "لطفا تمام فیلدها را پر کنید")
            return

        if len(new_password) < 4:
            messagebox.showwarning("خطا", "رمز عبور جدید باید حداقل ۴ کاراکتر باشد")
            return

        user_id = verify_security_answer(self.username, answer)

        if user_id:
            if reset_password_direct(user_id, new_password):
                messagebox.showinfo("موفقیت", "رمز عبور با موفقیت تغییر کرد!\nاکنون می‌توانید با رمز جدید وارد شوید.")
                self.back_to_login()
            else:
                messagebox.showerror("خطا", "خطا در تغییر رمز عبور")
        else:
            messagebox.showerror("خطا", "پاسخ سوال امنیتی اشتباه است!")

    def back_to_login(self):
        """بازگشت به صفحه ورود"""
        self.window.destroy()
        if self.parent_window:
            self.parent_window.show()
        else:
            AuthWindow()


def main():
    app = AuthWindow()
    app.window.mainloop()


if __name__ == "__main__":
    main()