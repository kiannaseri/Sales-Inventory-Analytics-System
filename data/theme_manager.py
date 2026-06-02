import customtkinter as ctk


class ThemeManager:
    """مدیریت تم‌های دارک و لایت"""

    THEMES = {
        'dark': {
            'bg': '#1a1a2e',
            'fg': '#16213e',
            'card': '#2d2d3f',
            'text': 'white',
            'text_secondary': 'gray',
            'sidebar': '#2c3e50',
            'success': '#2ecc71',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#3498db'
        },
        'light': {
            'bg': '#f5f5f5',
            'fg': '#ffffff',
            'card': '#e8e8e8',
            'text': '#1a1a2e',
            'text_secondary': '#666666',
            'sidebar': '#ecf0f1',
            'success': '#27ae60',
            'danger': '#c0392b',
            'warning': '#e67e22',
            'info': '#2980b9'
        }
    }

    @staticmethod
    def apply_theme(app, theme_name):
        """اعمال تم به برنامه"""
        theme = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES['dark'])

        # تنظیم CustomTkinter
        ctk.set_appearance_mode("dark" if theme_name == 'dark' else "light")

        # به‌روزرسانی رنگ‌های برنامه
        app.colors = theme.copy()

        # به‌روزرسانی سایدبار
        if hasattr(app, 'sidebar'):
            app.sidebar.configure(fg_color=theme['sidebar'])

        # به‌روزرسانی لیبل وضعیت
        if hasattr(app, 'status_label'):
            app.status_label.configure(fg_color=theme['sidebar'])

        # به‌روزرسانی جدول
        if hasattr(app, 'tree'):
            style = ttk.Style()
            style.configure("Treeview", background=theme['bg'], foreground=theme['text'],
                            fieldbackground=theme['bg'])
            style.configure("Treeview.Heading", background=theme['sidebar'],
                            foreground=theme['text'])

        return theme

    @staticmethod
    def toggle_theme(app):
        """تغییر بین دارک و لایت مود"""
        current = app.current_theme if hasattr(app, 'current_theme') else 'dark'
        new_theme = 'light' if current == 'dark' else 'dark'
        app.current_theme = new_theme
        ThemeManager.apply_theme(app, new_theme)

        # ذخیره در دیتابیس
        from database import update_user_theme
        if hasattr(app, 'user_id'):
            update_user_theme(app.user_id, new_theme)

        return new_theme