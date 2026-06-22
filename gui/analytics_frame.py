import customtkinter as ctk
from gui.styles import COLORS, FONTS
from analytics import get_completion_stats, get_on_time_rate, get_productivity_score, get_streak, get_avg_completion_time, get_tasks_per_day, get_tasks_by_priority, get_tasks_by_status, get_tasks_by_category, get_achievements, check_achievements
from scheduler import get_workload_summary, get_smart_task_order, detect_deadline_conflicts, predict_delayed_tasks
try:
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

class AnalyticsFrame(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS['bg_dark'])
        self.app = app
        self.user_id = app.current_user['id']
        check_achievements(self.user_id)
        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color='transparent')
        scroll.pack(fill='both', expand=True, padx=25, pady=15)
        ctk.CTkLabel(scroll, text='📈 Analytics & Insights', font=FONTS['heading'], text_color=COLORS['text_primary']).pack(anchor='w', pady=(0, 15))
        stats = get_completion_stats(self.user_id)
        score = get_productivity_score(self.user_id)
        streak = get_streak(self.user_id)
        on_time = get_on_time_rate(self.user_id)
        avg_time = get_avg_completion_time(self.user_id)
        cards_frame = ctk.CTkFrame(scroll, fg_color='transparent')
        cards_frame.pack(fill='x', pady=(0, 15))
        card_data = [('Total Tasks', str(stats['total']), COLORS['accent']), ('Completed', str(stats['done']), COLORS['success']), ('Completion Rate', f'{stats['completion_rate']}%', COLORS['accent']), ('On-Time Rate', f'{on_time}%', COLORS['success']), ('Productivity', f'{score}/100', COLORS['warning'] if score < 70 else COLORS['success']), ('Streak', f'{streak} day{('s' if streak != 1 else '')}', COLORS['accent'])]
        for i, (label, val, color) in enumerate(card_data):
            cards_frame.columnconfigure(i, weight=1)
            c = ctk.CTkFrame(cards_frame, fg_color=COLORS['bg_card'], corner_radius=10)
            c.grid(row=0, column=i, sticky='nsew', padx=4, pady=2)
            ctk.CTkLabel(c, text=val, font=('Segoe UI', 22, 'bold'), text_color=color).pack(padx=12, pady=(12, 2))
            ctk.CTkLabel(c, text=label, font=FONTS['tiny'], text_color=COLORS['text_secondary']).pack(padx=12, pady=(0, 10))
        if HAS_MPL:
            charts_frame = ctk.CTkFrame(scroll, fg_color='transparent')
            charts_frame.pack(fill='x', pady=(0, 15))
            charts_frame.columnconfigure(0, weight=2)
            charts_frame.columnconfigure(1, weight=1)
            trend_card = ctk.CTkFrame(charts_frame, fg_color=COLORS['bg_card'], corner_radius=10)
            trend_card.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
            ctk.CTkLabel(trend_card, text='14-Day Activity Trend', font=FONTS['body_bold'], text_color=COLORS['text_primary']).pack(padx=15, pady=(10, 5))
            self._draw_trend_chart(trend_card)
            pie_card = ctk.CTkFrame(charts_frame, fg_color=COLORS['bg_card'], corner_radius=10)
            pie_card.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
            ctk.CTkLabel(pie_card, text='By Priority', font=FONTS['body_bold'], text_color=COLORS['text_primary']).pack(padx=15, pady=(10, 5))
            self._draw_priority_pie(pie_card)
        ctk.CTkLabel(scroll, text='🤖 AI Insights', font=FONTS['subheading'], text_color=COLORS['text_primary']).pack(anchor='w', pady=(10, 8))
        insights_frame = ctk.CTkFrame(scroll, fg_color=COLORS['bg_card'], corner_radius=10)
        insights_frame.pack(fill='x', pady=(0, 10))
        workload = get_workload_summary(self.user_id)
        wl_inner = ctk.CTkFrame(insights_frame, fg_color='transparent')
        wl_inner.pack(fill='x', padx=15, pady=10)
        ctk.CTkLabel(wl_inner, text='Workload Overview', font=FONTS['body_bold'], text_color=COLORS['accent']).pack(anchor='w')
        wl_stats = f'Today: {workload['today']} tasks  |  Tomorrow: {workload['tomorrow']}  |  This week: {workload['this_week']}  |  Active: {workload['total_active']}'
        ctk.CTkLabel(wl_inner, text=wl_stats, font=FONTS['small'], text_color=COLORS['text_secondary']).pack(anchor='w', pady=(2, 6))
        for sug in workload['suggestions']:
            ctk.CTkLabel(wl_inner, text=sug, font=FONTS['small'], text_color=COLORS['text_primary'], anchor='w', wraplength=700).pack(fill='x', pady=1)
        conflicts = detect_deadline_conflicts(self.user_id)
        if conflicts:
            ctk.CTkLabel(wl_inner, text='', font=FONTS['tiny']).pack()
            ctk.CTkLabel(wl_inner, text='⚠️ Deadline Conflicts', font=FONTS['body_bold'], text_color=COLORS['warning']).pack(anchor='w')
            for c in conflicts[:5]:
                ctk.CTkLabel(wl_inner, text=c['message'], font=FONTS['small'], text_color=COLORS['text_secondary'], wraplength=700).pack(anchor='w', pady=1)
        at_risk = predict_delayed_tasks(self.user_id)
        if at_risk:
            ctk.CTkLabel(wl_inner, text='', font=FONTS['tiny']).pack()
            ctk.CTkLabel(wl_inner, text='🚨 At-Risk Tasks', font=FONTS['body_bold'], text_color=COLORS['danger']).pack(anchor='w')
            for r in at_risk[:5]:
                risk_color = COLORS['danger'] if r['risk'] == 'High' else COLORS['warning']
                ctk.CTkLabel(wl_inner, text=f'• [{r['risk']}] {r['title']}: {r['reason']}', font=FONTS['small'], text_color=risk_color, wraplength=700).pack(anchor='w', pady=1)
        smart = get_smart_task_order(self.user_id)
        if smart:
            ctk.CTkLabel(scroll, text='🎯 Suggested Task Order', font=FONTS['subheading'], text_color=COLORS['text_primary']).pack(anchor='w', pady=(10, 8))
            order_frame = ctk.CTkFrame(scroll, fg_color=COLORS['bg_card'], corner_radius=10)
            order_frame.pack(fill='x', pady=(0, 10))
            for i, t in enumerate(smart[:8]):
                row = ctk.CTkFrame(order_frame, fg_color='transparent')
                row.pack(fill='x', padx=15, pady=3)
                ctk.CTkLabel(row, text=f'#{i + 1}', font=FONTS['body_bold'], text_color=COLORS['accent'], width=35).pack(side='left')
                ctk.CTkLabel(row, text=t['title'], font=FONTS['body'], text_color=COLORS['text_primary']).pack(side='left', padx=5)
                ctk.CTkLabel(row, text=f'Score: {t['ai_score']}', font=FONTS['tiny'], text_color=COLORS['text_secondary']).pack(side='right')
        achievements = get_achievements(self.user_id)
        ctk.CTkLabel(scroll, text='🏆 Achievements', font=FONTS['subheading'], text_color=COLORS['text_primary']).pack(anchor='w', pady=(10, 8))
        ach_frame = ctk.CTkFrame(scroll, fg_color=COLORS['bg_card'], corner_radius=10)
        ach_frame.pack(fill='x', pady=(0, 10))
        if achievements:
            for a in achievements:
                row = ctk.CTkFrame(ach_frame, fg_color='transparent')
                row.pack(fill='x', padx=15, pady=4)
                ctk.CTkLabel(row, text='🏅', font=('Segoe UI', 18)).pack(side='left')
                ctk.CTkLabel(row, text=a['achievement_name'], font=FONTS['body_bold'], text_color=COLORS['text_primary']).pack(side='left', padx=8)
                ctk.CTkLabel(row, text=a.get('description', ''), font=FONTS['small'], text_color=COLORS['text_secondary']).pack(side='left')
        else:
            ctk.CTkLabel(ach_frame, text='  Complete tasks to earn achievements!', font=FONTS['small'], text_color=COLORS['text_secondary']).pack(padx=15, pady=12)

    def _draw_trend_chart(self, parent):
        if not HAS_MPL:
            return
        data = get_tasks_per_day(self.user_id, 14)
        fig = Figure(figsize=(5.5, 2.5), dpi=90)
        fig.patch.set_facecolor(COLORS['bg_card'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS['bg_card'])
        dates = [d['date'][5:] for d in data]
        created = [d['created'] for d in data]
        completed = [d['completed'] for d in data]
        ax.bar([i - 0.15 for i in range(len(dates))], created, 0.3, label='Created', color=COLORS['accent'], alpha=0.8)
        ax.bar([i + 0.15 for i in range(len(dates))], completed, 0.3, label='Completed', color=COLORS['success'], alpha=0.8)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, fontsize=7, color=COLORS['text_secondary'])
        ax.tick_params(colors=COLORS['text_secondary'])
        ax.legend(fontsize=8, labelcolor=COLORS['text_secondary'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLORS['border'])
        ax.spines['bottom'].set_color(COLORS['border'])
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=(0, 10))

    def _draw_priority_pie(self, parent):
        if not HAS_MPL:
            return
        data = get_tasks_by_priority(self.user_id)
        values = list(data.values())
        labels = list(data.keys())
        pie_colors = [COLORS['priority_low'], COLORS['priority_medium'], COLORS['priority_high'], COLORS['priority_urgent']]
        if sum(values) == 0:
            ctk.CTkLabel(parent, text='No tasks yet', font=FONTS['small'], text_color=COLORS['text_secondary']).pack(pady=30)
            return
        fig = Figure(figsize=(2.5, 2.5), dpi=90)
        fig.patch.set_facecolor(COLORS['bg_card'])
        ax = fig.add_subplot(111)
        ax.pie(values, labels=labels, colors=pie_colors, autopct='%1.0f%%', textprops={'fontsize': 8, 'color': COLORS['text_primary']}, startangle=90)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=(0, 10))
