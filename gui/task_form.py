"""
task_form.py — Add / Edit task dialog with subtask management.
"""

import customtkinter as ctk
from datetime import datetime
from gui.styles import COLORS, FONTS
from task_manager import (create_task, update_task, get_task_by_id,
                          add_subtask, get_subtasks, delete_subtask, toggle_subtask)


class TaskFormDialog(ctk.CTkToplevel):
    """Modal dialog for creating or editing a task."""

    def __init__(self, parent, user_id, task_id=None, on_save=None):
        super().__init__(parent)
        self.user_id = user_id
        self.task_id = task_id
        self.on_save = on_save
        self.task_data = get_task_by_id(task_id) if task_id else None

        self.title("Edit Task" if task_id else "New Task")
        self.geometry("500x620")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=15)

        header = "Edit Task" if self.task_id else "Create New Task"
        ctk.CTkLabel(scroll, text=header, font=FONTS["subheading"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 15))

        # Title
        ctk.CTkLabel(scroll, text="Title *", font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(scroll, font=FONTS["body"], height=38,
                                        fg_color=COLORS["bg_secondary"],
                                        border_color=COLORS["border"])
        self.title_entry.pack(fill="x", pady=(2, 8))

        # Description
        ctk.CTkLabel(scroll, text="Description", font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.desc_entry = ctk.CTkTextbox(scroll, font=FONTS["small"], height=70,
                                         fg_color=COLORS["bg_secondary"],
                                         border_color=COLORS["border"])
        self.desc_entry.pack(fill="x", pady=(2, 8))

        # Row: Category + Priority
        row = ctk.CTkFrame(scroll, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(left, text="Category", font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.category_entry = ctk.CTkEntry(left, font=FONTS["small"], height=34,
                                           fg_color=COLORS["bg_secondary"],
                                           border_color=COLORS["border"])
        self.category_entry.pack(fill="x", pady=(2, 0))
        self.category_entry.insert(0, "General")

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(right, text="Priority", font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.priority_var = ctk.StringVar(value="Medium")
        self.priority_menu = ctk.CTkOptionMenu(
            right, values=["Low", "Medium", "High", "Urgent"],
            variable=self.priority_var, font=FONTS["small"], height=34,
            fg_color=COLORS["bg_secondary"], button_color=COLORS["accent"])
        self.priority_menu.pack(fill="x", pady=(2, 0))

        # Due date
        ctk.CTkLabel(scroll, text="Due Date (YYYY-MM-DD HH:MM)", font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.due_entry = ctk.CTkEntry(scroll, font=FONTS["small"], height=34,
                                      fg_color=COLORS["bg_secondary"],
                                      border_color=COLORS["border"],
                                      placeholder_text="2026-06-15 14:00")
        self.due_entry.pack(fill="x", pady=(2, 8))

        # Recurring
        rec_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        rec_frame.pack(fill="x", pady=(0, 8))
        self.recurring_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(rec_frame, text="Recurring", variable=self.recurring_var,
                        font=FONTS["small"], fg_color=COLORS["accent"],
                        text_color=COLORS["text_primary"]).pack(side="left")
        self.recurrence_menu = ctk.CTkOptionMenu(
            rec_frame, values=["daily", "weekly", "monthly"],
            font=FONTS["small"], height=30, width=120,
            fg_color=COLORS["bg_secondary"], button_color=COLORS["accent"])
        self.recurrence_menu.pack(side="right")

        # Subtasks section (only for editing existing tasks)
        if self.task_id:
            ctk.CTkLabel(scroll, text="Subtasks", font=FONTS["body_bold"],
                         text_color=COLORS["text_primary"]).pack(anchor="w", pady=(8, 4))
            self.subtask_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_secondary"],
                                              corner_radius=8)
            self.subtask_frame.pack(fill="x", pady=(0, 4))
            self._refresh_subtasks()

            add_sub_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            add_sub_frame.pack(fill="x", pady=(0, 8))
            self.sub_entry = ctk.CTkEntry(add_sub_frame, font=FONTS["small"],
                                          height=32, fg_color=COLORS["bg_secondary"],
                                          border_color=COLORS["border"],
                                          placeholder_text="Add subtask...")
            self.sub_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            ctk.CTkButton(add_sub_frame, text="+", width=32, height=32,
                          font=FONTS["button"], fg_color=COLORS["accent"],
                          command=self._add_subtask).pack(side="right")

        # Error message
        self.msg_label = ctk.CTkLabel(scroll, text="", font=FONTS["small"],
                                      text_color=COLORS["danger"])
        self.msg_label.pack(pady=(0, 5))

        # Buttons
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))
        ctk.CTkButton(btn_frame, text="Cancel", font=FONTS["button"],
                      fg_color=COLORS["bg_tertiary"],
                      hover_color=COLORS["bg_secondary"],
                      command=self.destroy).pack(side="left", expand=True,
                                                 fill="x", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Save", font=FONTS["button"],
                      fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      command=self._save).pack(side="right", expand=True,
                                               fill="x", padx=(5, 0))

        # Pre-fill if editing
        if self.task_data:
            self.title_entry.insert(0, self.task_data.get("title", ""))
            self.desc_entry.insert("1.0", self.task_data.get("description", ""))
            self.category_entry.delete(0, "end")
            self.category_entry.insert(0, self.task_data.get("category", "General"))
            self.priority_var.set(self.task_data.get("priority", "Medium"))
            if self.task_data.get("due_date"):
                due_str = self.task_data["due_date"][:16]
                self.due_entry.insert(0, due_str)
            if self.task_data.get("is_recurring"):
                self.recurring_var.set(True)
                if self.task_data.get("recurrence_pattern"):
                    self.recurrence_menu.set(self.task_data["recurrence_pattern"])

    def _refresh_subtasks(self):
        for w in self.subtask_frame.winfo_children():
            w.destroy()
        subs = get_subtasks(self.task_id)
        if not subs:
            ctk.CTkLabel(self.subtask_frame, text="  No subtasks yet",
                         font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack(padx=10, pady=8)
            return
        for s in subs:
            row = ctk.CTkFrame(self.subtask_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)
            cb = ctk.CTkCheckBox(row, text=s["title"], font=FONTS["small"],
                                 fg_color=COLORS["success"],
                                 text_color=COLORS["text_primary"],
                                 command=lambda sid=s["id"]: self._toggle_sub(sid))
            if s["is_done"]:
                cb.select()
            cb.pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="✕", width=28, height=28,
                          fg_color=COLORS["danger"], font=FONTS["tiny"],
                          command=lambda sid=s["id"]: self._del_sub(sid)).pack(side="right")

    def _toggle_sub(self, sid):
        toggle_subtask(sid)
        self._refresh_subtasks()

    def _del_sub(self, sid):
        delete_subtask(sid)
        self._refresh_subtasks()

    def _add_subtask(self):
        title = self.sub_entry.get().strip()
        if title and self.task_id:
            add_subtask(self.task_id, title)
            self.sub_entry.delete(0, "end")
            self._refresh_subtasks()

    def _save(self):
        title = self.title_entry.get().strip()
        if not title:
            self.msg_label.configure(text="Title is required.")
            return

        desc = self.desc_entry.get("1.0", "end").strip()
        cat = self.category_entry.get().strip() or "General"
        pri = self.priority_var.get()
        due_raw = self.due_entry.get().strip()

        due_date = None
        if due_raw:
            try:
                # Accept multiple formats
                for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        dt = datetime.strptime(due_raw, fmt)
                        due_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                        break
                    except ValueError:
                        continue
                if due_date is None:
                    raise ValueError()
            except ValueError:
                self.msg_label.configure(text="Invalid date format. Use YYYY-MM-DD HH:MM")
                return

        is_rec = 1 if self.recurring_var.get() else 0
        rec_pat = self.recurrence_menu.get() if is_rec else None

        if self.task_id:
            ok, msg = update_task(self.task_id, self.user_id, title=title,
                                  description=desc, category=cat, priority=pri,
                                  due_date=due_date, is_recurring=is_rec,
                                  recurrence_pattern=rec_pat)
        else:
            ok, msg = create_task(self.user_id, title, desc, cat, pri,
                                  due_date, is_rec, rec_pat)
            ok = ok is not None

        if ok:
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            self.msg_label.configure(text=msg)
