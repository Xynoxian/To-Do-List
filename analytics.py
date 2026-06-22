from database import get_connection
from datetime import datetime, timedelta

def get_completion_stats(user_id):
    conn = get_connection()
    total = conn.execute('SELECT COUNT(*) as c FROM tasks WHERE user_id=?', (user_id,)).fetchone()['c']
    done = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND status='Done'", (user_id,)).fetchone()['c']
    pending = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND status='Pending'", (user_id,)).fetchone()['c']
    in_progress = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND status='In Progress'", (user_id,)).fetchone()['c']
    late = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND status='Late'", (user_id,)).fetchone()['c']
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    overdue = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND status NOT IN ('Done') AND due_date IS NOT NULL AND due_date < ?", (user_id, now_str)).fetchone()['c']
    conn.close()
    rate = done / total * 100 if total > 0 else 0
    return {'total': total, 'done': done, 'pending': pending, 'in_progress': in_progress, 'late': late, 'overdue': overdue, 'completion_rate': round(rate, 1)}

def get_on_time_rate(user_id):
    conn = get_connection()
    done_due = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND status='Done' AND due_date IS NOT NULL AND completed_at IS NOT NULL", (user_id,)).fetchone()['c']
    on_time = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND status='Done' AND due_date IS NOT NULL AND completed_at IS NOT NULL AND completed_at <= due_date", (user_id,)).fetchone()['c']
    conn.close()
    return round(on_time / done_due * 100 if done_due > 0 else 100, 1)

def get_tasks_per_day(user_id, days=14):
    conn = get_connection()
    results = []
    for i in range(days - 1, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        created = conn.execute('SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND DATE(created_at)=?', (user_id, day)).fetchone()['c']
        completed = conn.execute('SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND DATE(completed_at)=?', (user_id, day)).fetchone()['c']
        results.append({'date': day, 'created': created, 'completed': completed})
    conn.close()
    return results

def get_tasks_by_priority(user_id):
    conn = get_connection()
    result = {}
    for p in ['Low', 'Medium', 'High', 'Urgent']:
        result[p] = conn.execute('SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND priority=?', (user_id, p)).fetchone()['c']
    conn.close()
    return result

def get_tasks_by_category(user_id):
    conn = get_connection()
    rows = conn.execute('SELECT category, COUNT(*) as c FROM tasks WHERE user_id=? GROUP BY category ORDER BY c DESC', (user_id,)).fetchall()
    conn.close()
    return {r['category']: r['c'] for r in rows}

def get_tasks_by_status(user_id):
    conn = get_connection()
    rows = conn.execute('SELECT status, COUNT(*) as c FROM tasks WHERE user_id=? GROUP BY status', (user_id,)).fetchall()
    conn.close()
    return {r['status']: r['c'] for r in rows}

def get_streak(user_id):
    conn = get_connection()
    streak = 0
    day = datetime.now().date()
    while True:
        c = conn.execute('SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND DATE(completed_at)=?', (user_id, day.strftime('%Y-%m-%d'))).fetchone()['c']
        if c > 0:
            streak += 1
            day -= timedelta(days=1)
        else:
            break
    conn.close()
    return streak

def get_avg_completion_time(user_id):
    conn = get_connection()
    tasks = conn.execute("SELECT created_at, completed_at FROM tasks WHERE user_id=? AND status='Done' AND completed_at IS NOT NULL", (user_id,)).fetchall()
    conn.close()
    if not tasks:
        return 0
    total, count = (0, 0)
    for t in tasks:
        try:
            c = datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S')
            d = datetime.strptime(t['completed_at'], '%Y-%m-%d %H:%M:%S')
            total += (d - c).total_seconds() / 3600
            count += 1
        except (ValueError, TypeError):
            continue
    return round(total / count, 1) if count > 0 else 0

def get_productivity_score(user_id):
    stats = get_completion_stats(user_id)
    if stats['total'] == 0:
        return 0
    on_time = get_on_time_rate(user_id)
    comp = stats['completion_rate'] * 0.4
    ot = on_time * 0.3
    health = max(0, 100 - (stats['overdue'] + stats['late']) / stats['total'] * 100) * 0.3
    return round(comp + ot + health, 1)

def _count_categories(user_id):
    conn = get_connection()
    c = conn.execute('SELECT COUNT(DISTINCT category) as c FROM tasks WHERE user_id=?', (user_id,)).fetchone()['c']
    conn.close()
    return c
ACHIEVEMENT_DEFS = [('First Task', 'Create your first task', lambda s, u: s['total'] >= 1), ('Getting Started', 'Complete your first task', lambda s, u: s['done'] >= 1), ('Task Master', 'Complete 10 tasks', lambda s, u: s['done'] >= 10), ('Prolific', 'Complete 25 tasks', lambda s, u: s['done'] >= 25), ('On Fire', '3-day completion streak', lambda s, u: get_streak(u) >= 3), ('Week Warrior', '7-day completion streak', lambda s, u: get_streak(u) >= 7), ('Organized', 'Use 3+ categories', lambda s, u: _count_categories(u) >= 3), ('Productivity Pro', 'Score 80+ productivity', lambda s, u: get_productivity_score(u) >= 80)]

def check_achievements(user_id):
    stats = get_completion_stats(user_id)
    conn = get_connection()
    existing = {a['achievement_name'] for a in conn.execute('SELECT achievement_name FROM achievements WHERE user_id=?', (user_id,)).fetchall()}
    conn.close()
    newly = []
    for name, desc, fn in ACHIEVEMENT_DEFS:
        if name not in existing:
            try:
                if fn(stats, user_id):
                    conn = get_connection()
                    conn.execute('INSERT INTO achievements (user_id, achievement_name, description) VALUES (?,?,?)', (user_id, name, desc))
                    conn.commit()
                    conn.close()
                    newly.append({'name': name, 'description': desc})
            except Exception:
                continue
    return newly

def get_achievements(user_id):
    conn = get_connection()
    achs = conn.execute('SELECT * FROM achievements WHERE user_id=? ORDER BY earned_at DESC', (user_id,)).fetchall()
    conn.close()
    return [dict(a) for a in achs]
