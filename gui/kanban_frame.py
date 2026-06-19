"""
kanban_frame.py — Kanban board view with columns for each task status.
"""

import customtkinter as ctk
from gui.styles import COLORS, FONTS, PRIORITY_EMOJI, STATUS_COLORS
from task_manager import get_tasks, mark_task_status
from gui.task_form import TaskFormDialog


KANBAN_COLUMNS = [
    ("Pending", "⏳"),
    ("In Progress", "🔄"),
    ("Done", "✅"),
    ("Late", "⏰"),
]


class KanbanFrame(ctk.CTkFrame):
    """Kanban board with drag-like columns for task status management."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self.user_id = app.current_user["id"]
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        ctk.CTkLabel(header, text="📊 Kanban Board", font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkButton(header, text="+ New Task", font=FONTS["button"],
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      height=36, corner_radius=8,
                      command=self._new_task).pack(side="right")

        # Columns container
        self.columns_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.columns_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def refresh(self):
        for w in self.columns_frame.winfo_children():
            w.destroy()

        tasks = get_tasks(self.user_id, sort_by="due_date")
        grouped = {s: [] for s, _ in KANBAN_COLUMNS}
        for t in tasks:
            if t["status"] in grouped:
                grouped[t["status"]].append(t)

        for i, (status, emoji) in enumerate(KANBAN_COLUMNS):
            self.columns_frame.columnconfigure(i, weight=1)
            col = self._build_column(status, emoji, grouped.get(status, []))
            col.grid(row=0, column=i, sticky="nsew", padx=5, pady=0)
        self.columns_frame.rowconfigure(0, weight=1)

    def _build_column(self, status, emoji, tasks):
        col_color = STATUS_COLORS.get(status, COLORS["accent"])
        col = ctk.CTkFrame(self.columns_frame, fg_color=COLORS["bg_card"],
                           corner_radius=12)

        # Column header
        header = ctk.CTkFrame(col, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 6))
        ctk.CTkLabel(header, text=f"{emoji} {status}", font=FONTS["body_bold"],
                     text_color=col_color).pack(side="left")
        ctk.CTkLabel(header, text=str(len(tasks)), font=FONTS["small"],
                     text_color=COLORS["text_secondary"],
                     fg_color=COLORS["bg_secondary"], corner_radius=10,
                     width=28, height=22).pack(side="right")

        # Divider
        ctk.CTkFrame(col, fg_color=col_color, height=2).pack(fill="x", padx=10, pady=(0, 6))

        # Scrollable task area
        scroll = ctk.CTkScrollableFrame(col, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        for t in tasks:
            self._render_kanban_card(scroll, t, status)

        return col

    def _render_kanban_card(self, parent, task, current_status):
        pri_emoji = PRIORITY_EMOJI.get(task["priority"], "")
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=8)
        card.pack(fill="x", pady=3)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)

        # Title
        ctk.CTkLabel(inner, text=f"{pri_emoji} {task['title']}", font=FONTS["small"],
                     text_color=COLORS["text_primary"],
                     anchor="w", wraplength=180).pack(fill="x")

        # Due date
        if task.get("due_date"):
            ctk.CTkLabel(inner, text=f"📅 {task['due_date'][:10]}",
                         font=FONTS["tiny"],
                         text_color=COLORS["text_secondary"]).pack(anchor="w")

        # Move buttons
        move_frame = ctk.CTkFrame(inner, fg_color="transparent")
        move_frame.pack(fill="x", pady=(4, 0))

        moves = {
            "Pending": [("▶", "In Progress"), ("✅", "Done")],
            "In Progress": [("◀", "Pending"), ("✅", "Done")],
            "Done": [("◀", "Pending")],
            "Late": [("▶", "In Progress"), ("✅", "Done")],
        }

        for btn_text, target in moves.get(current_status, []):
            ctk.CTkButton(
                move_frame, text=btn_text, width=30, height=24,
                font=FONTS["tiny"], fg_color=COLORS["bg_tertiary"],
                hover_color=COLORS["accent"],
                command=lambda tid=task["id"], s=target: self._move(tid, s)
            ).pack(side="left", padx=1)

        # Edit button
        ctk.CTkButton(
            move_frame, text="✏️", width=30, height=24,
            font=FONTS["tiny"], fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["accent"],
            command=lambda tid=task["id"]: self._edit(tid)
        ).pack(side="right")

    def _move(self, task_id, status):
        mark_task_status(task_id, self.user_id, status)
        self.refresh()

    def _edit(self, task_id):
        TaskFormDialog(self, self.user_id, task_id=task_id, on_save=self.refresh)

    def _new_task(self):
        TaskFormDialog(self, self.user_id, on_save=self.refresh)
