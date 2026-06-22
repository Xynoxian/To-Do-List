import customtkinter as ctk
from gui.styles import COLORS, FONTS, PRIORITY_COLORS, STATUS_COLORS, PRIORITY_EMOJI, STATUS_EMOJI
from task_manager import get_tasks, delete_task, mark_task_status, get_categories, get_subtasks
from gui.task_form import TaskFormDialog

class TaskListFrame(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS['bg_dark'])
        self.app = app
        self.user_id = app.current_user['id']
        self.current_filters = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=25, pady=(20, 10))
        ctk.CTkLabel(header, text='📋 My Tasks', font=FONTS['heading'], text_color=COLORS['text_primary']).pack(side='left')
        ctk.CTkButton(header, text='+ New Task', font=FONTS['button'], fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'], height=36, corner_radius=8, command=self._new_task).pack(side='right')
        bar = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=10)
        bar.pack(fill='x', padx=25, pady=(0, 10))
        inner_bar = ctk.CTkFrame(bar, fg_color='transparent')
        inner_bar.pack(fill='x', padx=12, pady=10)
        self.search_var = ctk.StringVar()
        search = ctk.CTkEntry(inner_bar, textvariable=self.search_var, font=FONTS['small'], height=34, width=220, fg_color=COLORS['bg_secondary'], border_color=COLORS['border'], placeholder_text='🔍 Search tasks...')
        search.pack(side='left', padx=(0, 8))
        search.bind('<Return>', lambda e: self.refresh())
        ctk.CTkButton(inner_bar, text='Search', font=FONTS['small'], width=70, height=34, fg_color=COLORS['accent'], command=self.refresh).pack(side='left', padx=(0, 15))
        ctk.CTkLabel(inner_bar, text='Status:', font=FONTS['small'], text_color=COLORS['text_secondary']).pack(side='left', padx=(0, 4))
        self.status_var = ctk.StringVar(value='All')
        ctk.CTkOptionMenu(inner_bar, values=['All', 'Pending', 'In Progress', 'Done', 'Late'], variable=self.status_var, font=FONTS['small'], height=34, width=110, fg_color=COLORS['bg_secondary'], button_color=COLORS['accent'], command=lambda _: self.refresh()).pack(side='left', padx=(0, 10))
        ctk.CTkLabel(inner_bar, text='Priority:', font=FONTS['small'], text_color=COLORS['text_secondary']).pack(side='left', padx=(0, 4))
        self.priority_var = ctk.StringVar(value='All')
        ctk.CTkOptionMenu(inner_bar, values=['All', 'Low', 'Medium', 'High', 'Urgent'], variable=self.priority_var, font=FONTS['small'], height=34, width=100, fg_color=COLORS['bg_secondary'], button_color=COLORS['accent'], command=lambda _: self.refresh()).pack(side='left', padx=(0, 10))
        ctk.CTkLabel(inner_bar, text='Sort:', font=FONTS['small'], text_color=COLORS['text_secondary']).pack(side='left', padx=(0, 4))
        self.sort_var = ctk.StringVar(value='due_date')
        ctk.CTkOptionMenu(inner_bar, values=['due_date', 'priority', 'created_at', 'title'], variable=self.sort_var, font=FONTS['small'], height=34, width=110, fg_color=COLORS['bg_secondary'], button_color=COLORS['accent'], command=lambda _: self.refresh()).pack(side='left')
        self.task_scroll = ctk.CTkScrollableFrame(self, fg_color='transparent')
        self.task_scroll.pack(fill='both', expand=True, padx=25, pady=(0, 15))

    def refresh(self):
        for w in self.task_scroll.winfo_children():
            w.destroy()
        status = self.status_var.get() if self.status_var.get() != 'All' else None
        pri = self.priority_var.get() if self.priority_var.get() != 'All' else None
        search = self.search_var.get().strip() or None
        tasks = get_tasks(self.user_id, status=status, priority=pri, search=search, sort_by=self.sort_var.get())
        if not tasks:
            ctk.CTkLabel(self.task_scroll, text='No tasks found. Create one!', font=FONTS['body'], text_color=COLORS['text_secondary']).pack(pady=40)
            return
        for t in tasks:
            self._render_task_card(t)

    def _render_task_card(self, task):
        pri_color = PRIORITY_COLORS.get(task['priority'], COLORS['accent'])
        stat_color = STATUS_COLORS.get(task['status'], COLORS['text_secondary'])
        card = ctk.CTkFrame(self.task_scroll, fg_color=COLORS['bg_card'], corner_radius=10, border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=4)
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='x', padx=15, pady=12)
        left = ctk.CTkFrame(inner, fg_color='transparent')
        left.pack(side='left', fill='x', expand=True)
        title_row = ctk.CTkFrame(left, fg_color='transparent')
        title_row.pack(fill='x')
        pri_emoji = PRIORITY_EMOJI.get(task['priority'], '')
        title_text = f'{pri_emoji} {task['title']}'
        ctk.CTkLabel(title_row, text=title_text, font=FONTS['body_bold'], text_color=COLORS['text_primary'], anchor='w').pack(side='left')
        stat_emoji = STATUS_EMOJI.get(task['status'], '')
        badge = ctk.CTkLabel(title_row, text=f' {stat_emoji} {task['status']} ', font=FONTS['tiny'], text_color=stat_color, fg_color=COLORS['bg_secondary'], corner_radius=5)
        badge.pack(side='left', padx=8)
        if task.get('category') and task['category'] != 'General':
            ctk.CTkLabel(title_row, text=f' {task['category']} ', font=FONTS['tiny'], text_color=COLORS['accent'], fg_color=COLORS['bg_secondary'], corner_radius=5).pack(side='left', padx=2)
        if task.get('is_recurring'):
            ctk.CTkLabel(title_row, text=f' 🔁 {task.get('recurrence_pattern', '')} ', font=FONTS['tiny'], text_color=COLORS['text_secondary'], fg_color=COLORS['bg_secondary'], corner_radius=5).pack(side='left', padx=2)
        desc = task.get('description', '')
        if desc:
            preview = desc[:80] + ('...' if len(desc) > 80 else '')
            ctk.CTkLabel(left, text=preview, font=FONTS['small'], text_color=COLORS['text_secondary'], anchor='w').pack(fill='x', pady=(2, 0))
        if task.get('due_date'):
            due_text = f'📅 Due: {task['due_date'][:16]}'
            ctk.CTkLabel(left, text=due_text, font=FONTS['tiny'], text_color=COLORS['text_secondary'], anchor='w').pack(fill='x', pady=(2, 0))
        subs = get_subtasks(task['id'])
        if subs:
            done_count = sum((1 for s in subs if s['is_done']))
            ctk.CTkLabel(left, text=f'  ☑ {done_count}/{len(subs)} subtasks', font=FONTS['tiny'], text_color=COLORS['text_secondary'], anchor='w').pack(fill='x')
        actions = ctk.CTkFrame(inner, fg_color='transparent')
        actions.pack(side='right')
        if task['status'] != 'Done':
            ctk.CTkButton(actions, text='✅', width=32, height=32, font=('Segoe UI', 14), fg_color=COLORS['success'], hover_color='#2ea043', command=lambda t=task: self._set_status(t['id'], 'Done')).pack(side='left', padx=2)
        if task['status'] not in ('Late', 'Done'):
            ctk.CTkButton(actions, text='⏰', width=32, height=32, font=('Segoe UI', 14), fg_color=COLORS['warning'], hover_color='#b8860b', command=lambda t=task: self._set_status(t['id'], 'Late')).pack(side='left', padx=2)
        if task['status'] == 'Pending':
            ctk.CTkButton(actions, text='▶', width=32, height=32, font=('Segoe UI', 14), fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'], command=lambda t=task: self._set_status(t['id'], 'In Progress')).pack(side='left', padx=2)
        ctk.CTkButton(actions, text='✏️', width=32, height=32, font=('Segoe UI', 14), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['bg_secondary'], command=lambda t=task: self._edit_task(t['id'])).pack(side='left', padx=2)
        ctk.CTkButton(actions, text='🗑️', width=32, height=32, font=('Segoe UI', 14), fg_color=COLORS['danger'], hover_color='#b22d2d', command=lambda t=task: self._delete_task(t['id'])).pack(side='left', padx=2)

    def _set_status(self, task_id, status):
        mark_task_status(task_id, self.user_id, status)
        self.refresh()

    def _edit_task(self, task_id):
        TaskFormDialog(self, self.user_id, task_id=task_id, on_save=self.refresh)

    def _delete_task(self, task_id):
        dialog = ctk.CTkToplevel(self)
        dialog.title('Confirm Delete')
        dialog.geometry('340x150')
        dialog.configure(fg_color=COLORS['bg_dark'])
        dialog.grab_set()
        ctk.CTkLabel(dialog, text='Delete this task?', font=FONTS['body_bold'], text_color=COLORS['text_primary']).pack(pady=(25, 15))
        bf = ctk.CTkFrame(dialog, fg_color='transparent')
        bf.pack()
        ctk.CTkButton(bf, text='Cancel', fg_color=COLORS['bg_tertiary'], command=dialog.destroy).pack(side='left', padx=10)
        ctk.CTkButton(bf, text='Delete', fg_color=COLORS['danger'], command=lambda: (delete_task(task_id, self.user_id), dialog.destroy(), self.refresh())).pack(side='right', padx=10)

    def _new_task(self):
        TaskFormDialog(self, self.user_id, on_save=self.refresh)
