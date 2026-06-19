"""
dashboard_frame.py — Main dashboard with summary cards, upcoming tasks,
reminders, and quick-add functionality.
"""

import customtkinter as ctk
from datetime import datetime
from gui.styles import COLORS, FONTS, PRIORITY_EMOJI, STATUS_EMOJI
from task_manager import (get_tasks, get_upcoming_tasks, get_overdue_tasks,
                          mark_task_status, create_task, check_recurring_tasks)
from analytics import get_completion_stats, get_productivity_score, get_streak, check_achievements
from scheduler import get_workload_summary
from gui.task_form import TaskFormDialog


class DashboardFrame(ctk.CTkFrame):
    """Main dashboard shown after login."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self.user_id = app.current_user["id"]

        # Check recurring tasks and achievements on load
        check_recurring_tasks(self.user_id)
        check_achievements(self.user_id)

        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=15)

        # Welcome header
        name = self.app.current_user["username"]
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        ctk.CTkLabel(scroll, text=f"{greeting}, {name}! 👋",
                     font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 5))

        # Quick add task bar
        quick = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=10)
        quick.pack(fill="x", pady=(0, 15))
        q_inner = ctk.CTkFrame(quick, fg_color="transparent")
        q_inner.pack(fill="x", padx=15, pady=12)
        self.quick_entry = ctk.CTkEntry(q_inner, font=FONTS["body"], height=38,
                                        fg_color=COLORS["bg_secondary"],
                                        border_color=COLORS["border"],
                                        placeholder_text="⚡ Quick add a task...")
        self.quick_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.quick_entry.bind("<Return>", lambda e: self._quick_add())
        ctk.CTkButton(q_inner, text="Add", font=FONTS["button"], width=70,
                      height=38, fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      command=self._quick_add).pack(side="right")

        # Stats cards
        stats = get_completion_stats(self.user_id)
        score = get_productivity_score(self.user_id)
        streak = get_streak(self.user_id)

        cards = ctk.CTkFrame(scroll, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 15))
        card_data = [
            ("📋 Total", str(stats["total"]), COLORS["accent"]),
            ("✅ Done", str(stats["done"]), COLORS["success"]),
            ("⏳ Pending", str(stats["pending"]), COLORS["warning"]),
            ("⏰ Overdue", str(stats["overdue"]), COLORS["danger"]),
            ("📊 Score", f"{score}", COLORS["accent"]),
            ("🔥 Streak", f"{streak}d", COLORS["success"]),
        ]
        for i, (label, val, color) in enumerate(card_data):
            cards.columnconfigure(i, weight=1)
            c = ctk.CTkFrame(cards, fg_color=COLORS["bg_card"], corner_radius=10)
            c.grid(row=0, column=i, sticky="nsew", padx=4, pady=2)
            ctk.CTkLabel(c, text=val, font=("Segoe UI", 24, "bold"),
                         text_color=color).pack(padx=15, pady=(12, 0))
            ctk.CTkLabel(c, text=label, font=FONTS["tiny"],
                         text_color=COLORS["text_secondary"]).pack(padx=15, pady=(0, 10))

        # Workload suggestions
        workload = get_workload_summary(self.user_id)
        if workload["suggestions"]:
            sug_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=10)
            sug_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(sug_frame, text="💡 Smart Suggestions", font=FONTS["body_bold"],
                         text_color=COLORS["accent"]).pack(anchor="w", padx=15, pady=(10, 5))
            for s in workload["suggestions"]:
                ctk.CTkLabel(sug_frame, text=s, font=FONTS["small"],
                             text_color=COLORS["text_primary"],
                             wraplength=700).pack(anchor="w", padx=15, pady=2)
            ctk.CTkLabel(sug_frame, text="", font=FONTS["tiny"]).pack()

        # Two-column layout: Upcoming + Overdue
        two_col = ctk.CTkFrame(scroll, fg_color="transparent")
        two_col.pack(fill="x", pady=(0, 15))
        two_col.columnconfigure(0, weight=1)
        two_col.columnconfigure(1, weight=1)

        # Upcoming tasks (next 48h)
        upcoming = get_upcoming_tasks(self.user_id, hours=48)
        up_card = ctk.CTkFrame(two_col, fg_color=COLORS["bg_card"], corner_radius=10)
        up_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        ctk.CTkLabel(up_card, text="📅 Upcoming (48h)", font=FONTS["body_bold"],
                     text_color=COLORS["accent"]).pack(anchor="w", padx=15, pady=(10, 5))

        if upcoming:
            for t in upcoming[:6]:
                self._render_mini_task(up_card, t)
        else:
            ctk.CTkLabel(up_card, text="  No upcoming tasks", font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack(padx=15, pady=8)
        ctk.CTkLabel(up_card, text="", font=FONTS["tiny"]).pack()

        # Overdue tasks
        overdue = get_overdue_tasks(self.user_id)
        ov_card = ctk.CTkFrame(two_col, fg_color=COLORS["bg_card"], corner_radius=10)
        ov_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        ctk.CTkLabel(ov_card, text="🚨 Overdue", font=FONTS["body_bold"],
                     text_color=COLORS["danger"]).pack(anchor="w", padx=15, pady=(10, 5))

        if overdue:
            for t in overdue[:6]:
                self._render_mini_task(ov_card, t, is_overdue=True)
        else:
            ctk.CTkLabel(ov_card, text="  All caught up! 🎉", font=FONTS["small"],
                         text_color=COLORS["success"]).pack(padx=15, pady=8)
        ctk.CTkLabel(ov_card, text="", font=FONTS["tiny"]).pack()

        # Recent tasks
        recent = get_tasks(self.user_id, sort_by="created_at", sort_order="DESC")
        if recent:
            ctk.CTkLabel(scroll, text="🕐 Recent Tasks", font=FONTS["body_bold"],
                         text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 5))
            for t in recent[:5]:
                self._render_mini_task(scroll, t, show_status=True)

    def _render_mini_task(self, parent, task, is_overdue=False, show_status=False):
        row = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=8)
        row.pack(fill="x", padx=12, pady=2)
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=6)

        pri_emoji = PRIORITY_EMOJI.get(task["priority"], "")
        title_text = f"{pri_emoji} {task['title']}"
        ctk.CTkLabel(inner, text=title_text, font=FONTS["small"],
                     text_color=COLORS["text_primary"],
                     anchor="w").pack(side="left", fill="x", expand=True)

        if show_status:
            stat_emoji = STATUS_EMOJI.get(task["status"], "")
            ctk.CTkLabel(inner, text=f"{stat_emoji} {task['status']}",
                         font=FONTS["tiny"],
                         text_color=COLORS["text_secondary"]).pack(side="right", padx=(5, 0))

        if task.get("due_date"):
            due_display = task["due_date"][:16]
            color = COLORS["danger"] if is_overdue else COLORS["text_secondary"]
            ctk.CTkLabel(inner, text=due_display, font=FONTS["tiny"],
                         text_color=color).pack(side="right")

        if task["status"] != "Done":
            ctk.CTkButton(inner, text="✅", width=26, height=26,
                          font=("Segoe UI", 11), fg_color=COLORS["success"],
                          hover_color="#2ea043",
                          command=lambda t=task: self._quick_done(t["id"])
                          ).pack(side="right", padx=(5, 0))

    def _quick_done(self, task_id):
        mark_task_status(task_id, self.user_id, "Done")
        self.app.navigate("dashboard")

    def _quick_add(self):
        title = self.quick_entry.get().strip()
        if title:
            create_task(self.user_id, title)
            self.quick_entry.delete(0, "end")
            self.app.navigate("dashboard")
