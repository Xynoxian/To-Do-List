"""
app.py — Main application window with sidebar navigation and reminder system.
"""

import customtkinter as ctk
from gui.styles import COLORS, FONTS
from gui.login_frame import LoginFrame
from gui.dashboard_frame import DashboardFrame
from gui.task_list import TaskListFrame
from gui.kanban_frame import KanbanFrame
from gui.analytics_frame import AnalyticsFrame
from task_manager import get_upcoming_tasks, get_overdue_tasks


class App(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("TaskFlow — Smart To-Do Manager")
        self.geometry("1250x780")
        self.minsize(1000, 600)
        self.current_user = None
        self._current_page = None
        self._reminder_shown = set()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.show_login()

    # ── Navigation ─────────────────────────────────────────

    def show_login(self):
        self.current_user = None
        for w in self.winfo_children():
            w.destroy()
        login = LoginFrame(self, self._on_login)
        login.pack(fill="both", expand=True)

    def _on_login(self, user):
        self.current_user = user
        self._show_main_layout()
        self._start_reminders()

    def _show_main_layout(self):
        for w in self.winfo_children():
            w.destroy()

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], width=200,
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App brand
        ctk.CTkLabel(self.sidebar, text="✅ TaskFlow",
                     font=("Segoe UI", 20, "bold"),
                     text_color=COLORS["accent"]).pack(padx=20, pady=(25, 5))
        ctk.CTkLabel(self.sidebar, text=f"@{self.current_user['username']}",
                     font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(padx=20, pady=(0, 20))

        ctk.CTkFrame(self.sidebar, fg_color=COLORS["border"],
                     height=1).pack(fill="x", padx=15, pady=(0, 10))

        # Nav buttons
        nav_items = [
            ("🏠  Dashboard", "dashboard"),
            ("📋  Tasks", "tasks"),
            ("📊  Kanban", "kanban"),
            ("📈  Analytics", "analytics"),
        ]
        self.nav_buttons = {}
        for text, page in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=text, font=FONTS["body"],
                fg_color="transparent", text_color=COLORS["text_primary"],
                hover_color=COLORS["bg_secondary"], anchor="w",
                height=40, corner_radius=8,
                command=lambda p=page: self.navigate(p))
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[page] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Logout button
        ctk.CTkFrame(self.sidebar, fg_color=COLORS["border"],
                     height=1).pack(fill="x", padx=15, pady=(0, 5))
        ctk.CTkButton(self.sidebar, text="🚪  Logout", font=FONTS["body"],
                      fg_color="transparent", text_color=COLORS["text_secondary"],
                      hover_color=COLORS["bg_secondary"], anchor="w",
                      height=40, corner_radius=8,
                      command=self.show_login).pack(fill="x", padx=10, pady=(2, 15))

        # Content area
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

        self.navigate("dashboard")

    def navigate(self, page):
        """Switch the content area to a different page."""
        self._current_page = page

        # Update nav button highlights
        for p, btn in self.nav_buttons.items():
            if p == page:
                btn.configure(fg_color=COLORS["bg_secondary"],
                              text_color=COLORS["accent"])
            else:
                btn.configure(fg_color="transparent",
                              text_color=COLORS["text_primary"])

        for w in self.content.winfo_children():
            w.destroy()

        frames = {
            "dashboard": DashboardFrame,
            "tasks": TaskListFrame,
            "kanban": KanbanFrame,
            "analytics": AnalyticsFrame,
        }

        frame_class = frames.get(page, DashboardFrame)
        frame = frame_class(self.content, self)
        frame.pack(fill="both", expand=True)

    # ── Reminder System ────────────────────────────────────

    def _start_reminders(self):
        """Periodically check for upcoming/overdue tasks."""
        self._check_reminders()

    def _check_reminders(self):
        if not self.current_user:
            return
        try:
            upcoming = get_upcoming_tasks(self.current_user["id"], hours=24)
            overdue = get_overdue_tasks(self.current_user["id"])

            for t in upcoming + overdue:
                task_key = f"{t['id']}_{t.get('due_date', '')}"
                if task_key not in self._reminder_shown:
                    self._reminder_shown.add(task_key)
                    self._show_reminder(t, is_overdue=(t in overdue))
        except Exception:
            pass

        # Check again in 5 minutes
        self.after(300000, self._check_reminders)

    def _show_reminder(self, task, is_overdue=False):
        """Show a popup reminder for a task."""
        popup = ctk.CTkToplevel(self)
        popup.title("⏰ Task Reminder")
        popup.geometry("380x180")
        popup.configure(fg_color=COLORS["bg_dark"])
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        color = COLORS["danger"] if is_overdue else COLORS["warning"]
        label = "OVERDUE" if is_overdue else "UPCOMING"

        ctk.CTkLabel(popup, text=f"⏰ {label}", font=FONTS["subheading"],
                     text_color=color).pack(pady=(15, 5))
        ctk.CTkLabel(popup, text=task["title"], font=FONTS["body_bold"],
                     text_color=COLORS["text_primary"]).pack(pady=(0, 3))

        if task.get("due_date"):
            ctk.CTkLabel(popup, text=f"Due: {task['due_date'][:16]}",
                         font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack()

        ctk.CTkButton(popup, text="Dismiss", font=FONTS["button"],
                      fg_color=COLORS["bg_tertiary"],
                      hover_color=COLORS["bg_secondary"],
                      command=popup.destroy).pack(pady=15)

        # Auto-dismiss after 15 seconds
        popup.after(15000, lambda: popup.destroy() if popup.winfo_exists() else None)
