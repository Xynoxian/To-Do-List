from database import get_connection
from datetime import datetime, timedelta
from analytics import get_avg_completion_time

def calculate_priority_score(task):
    importance = {'Low': 2, 'Medium': 5, 'High': 8, 'Urgent': 10}.get(task['priority'], 5)
    urgency = 5
    if task['due_date']:
        try:
            due = datetime.strptime(task['due_date'], '%Y-%m-%d %H:%M:%S')
            hours_left = (due - datetime.now()).total_seconds() / 3600
            if hours_left < 0:
                urgency = 10
            elif hours_left < 6:
                urgency = 9
            elif hours_left < 24:
                urgency = 8
            elif hours_left < 48:
                urgency = 6
            elif hours_left < 168:
                urgency = 4
            else:
                urgency = 2
        except (ValueError, TypeError):
            urgency = 5
    status_mult = {'Late': 1.2, 'In Progress': 1.1, 'Pending': 1.0, 'Done': 0.0}
    mult = status_mult.get(task['status'], 1.0)
    score = (urgency * 5 + importance * 5) * mult
    return min(round(score, 1), 100)

def get_smart_task_order(user_id):
    conn = get_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id=? AND status NOT IN ('Done')", (user_id,)).fetchall()
    conn.close()
    scored = []
    for t in tasks:
        td = dict(t)
        td['ai_score'] = calculate_priority_score(td)
        scored.append(td)
    scored.sort(key=lambda x: x['ai_score'], reverse=True)
    return scored

def detect_deadline_conflicts(user_id):
    conn = get_connection()
    tasks = conn.execute("\n        SELECT due_date, COUNT(*) as c FROM tasks\n        WHERE user_id=? AND status NOT IN ('Done') AND due_date IS NOT NULL\n        GROUP BY DATE(due_date) HAVING c >= 3\n        ORDER BY due_date\n    ", (user_id,)).fetchall()
    conn.close()
    conflicts = []
    for row in tasks:
        conflicts.append({'date': row['due_date'][:10] if row['due_date'] else 'Unknown', 'count': row['c'], 'message': f'You have {row['c']} tasks due on {row['due_date'][:10]}. Consider rescheduling some.'})
    return conflicts

def predict_delayed_tasks(user_id):
    avg_hours = get_avg_completion_time(user_id)
    if avg_hours <= 0:
        avg_hours = 24
    conn = get_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id=? AND status NOT IN ('Done', 'Late') AND due_date IS NOT NULL", (user_id,)).fetchall()
    conn.close()
    at_risk = []
    for t in tasks:
        td = dict(t)
        try:
            created = datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S')
            due = datetime.strptime(t['due_date'], '%Y-%m-%d %H:%M:%S')
            remaining = (due - datetime.now()).total_seconds() / 3600
            if remaining < avg_hours * 0.5 and remaining > 0:
                td['risk'] = 'High'
                td['reason'] = f'Only {remaining:.0f}h left, avg completion takes {avg_hours:.0f}h'
                at_risk.append(td)
            elif remaining < avg_hours and remaining > 0:
                td['risk'] = 'Medium'
                td['reason'] = f'{remaining:.0f}h left, cutting it close'
                at_risk.append(td)
        except (ValueError, TypeError):
            continue
    return at_risk

def get_workload_summary(user_id):
    conn = get_connection()
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
    week_end = (now + timedelta(days=7)).strftime('%Y-%m-%d')
    today_count = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND DATE(due_date)=? AND status!='Done'", (user_id, today)).fetchone()['c']
    tomorrow_count = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND DATE(due_date)=? AND status!='Done'", (user_id, tomorrow)).fetchone()['c']
    week_count = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND DATE(due_date) BETWEEN ? AND ? AND status!='Done'", (user_id, today, week_end)).fetchone()['c']
    total_active = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND status NOT IN ('Done')", (user_id,)).fetchone()['c']
    conn.close()
    suggestions = []
    if today_count > 3:
        suggestions.append(f'⚠️ Heavy day: {today_count} tasks due today. Prioritize the most urgent ones.')
    if tomorrow_count > 3:
        suggestions.append(f'📋 Tomorrow has {tomorrow_count} tasks. Start some today if possible.')
    if week_count > 10:
        suggestions.append(f'📊 Busy week ahead: {week_count} tasks. Consider breaking large tasks into subtasks.')
    if total_active > 15:
        suggestions.append(f'🔄 You have {total_active} active tasks. Review and close any that are no longer needed.')
    if not suggestions:
        suggestions.append('✅ Workload looks manageable. Keep it up!')
    return {'today': today_count, 'tomorrow': tomorrow_count, 'this_week': week_count, 'total_active': total_active, 'suggestions': suggestions}
