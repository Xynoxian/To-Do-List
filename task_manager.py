"""
task_manager.py — Task CRUD operations, subtask management,
status tracking, recurring tasks, and task history.
"""

from database import get_connection
from datetime import datetime, timedelta


# ── Task CRUD ──────────────────────────────────────────────

def create_task(user_id, title, description="", category="General",
                priority="Medium", due_date=None, is_recurring=0,
                recurrence_pattern=None):
    """Create a new task. Returns (task_id or None, message)."""
    if not title or not title.strip():
        return None, "Task title is required."

    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO tasks
            (user_id, title, description, category, priority, status,
             due_date, is_recurring, recurrence_pattern, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?, ?, ?, ?)
    """, (user_id, title.strip(), description, category, priority,
          due_date, is_recurring, recurrence_pattern, now, now))

    task_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO task_history (task_id, user_id, action, new_value)
        VALUES (?, ?, 'created', ?)
    """, (task_id, user_id, title.strip()))

    conn.commit()
    conn.close()
    return task_id, "Task created successfully!"


def get_tasks(user_id, status=None, priority=None, category=None,
              search=None, sort_by="due_date", sort_order="ASC"):
    """Fetch tasks with optional filters and sorting."""
    conn = get_connection()
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]

    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    allowed_sorts = {"due_date", "priority", "created_at", "title", "status"}
    if sort_by not in allowed_sorts:
        sort_by = "due_date"

    if sort_by == "priority":
        query += """ ORDER BY CASE priority
            WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2
            WHEN 'Medium' THEN 3 WHEN 'Low' THEN 4 END"""
    else:
        order = "ASC" if sort_order == "ASC" else "DESC"
        query += f" ORDER BY {sort_by} IS NULL, {sort_by} {order}"

    tasks = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(t) for t in tasks]


def get_task_by_id(task_id):
    """Fetch a single task by ID."""
    conn = get_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(task) if task else None


def update_task(task_id, user_id, **kwargs):
    """Update task fields. Returns (success, message)."""
    conn = get_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return False, "Task not found."

    allowed = {"title", "description", "category", "priority",
               "status", "due_date", "is_recurring", "recurrence_pattern"}
    updates, params = [], []

    for field, value in kwargs.items():
        if field in allowed:
            old_val = task[field]
            if str(old_val) != str(value):
                conn.execute("""
                    INSERT INTO task_history
                        (task_id, user_id, action, old_value, new_value)
                    VALUES (?, ?, ?, ?, ?)
                """, (task_id, user_id, f"{field}_changed",
                      str(old_val) if old_val else "", str(value)))
            updates.append(f"{field} = ?")
            params.append(value)

    if not updates:
        conn.close()
        return False, "No valid fields to update."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updates.append("updated_at = ?")
    params.append(now)
    params.append(task_id)

    conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    return True, "Task updated successfully!"


def delete_task(task_id, user_id):
    """Delete a task. Returns (success, message)."""
    conn = get_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return False, "Task not found."

    conn.execute("""
        INSERT INTO task_history (task_id, user_id, action, old_value)
        VALUES (?, ?, 'deleted', ?)
    """, (task_id, user_id, task["title"]))

    conn.execute("DELETE FROM subtasks WHERE task_id = ?", (task_id,))
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return True, "Task deleted successfully!"


# ── Status Management ──────────────────────────────────────

def mark_task_status(task_id, user_id, status):
    """Change task status (Pending / In Progress / Done / Late)."""
    conn = get_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return False, "Task not found."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    old_status = task["status"]

    if status == "Done":
        conn.execute(
            "UPDATE tasks SET status=?, completed_at=?, updated_at=? WHERE id=?",
            (status, now, now, task_id))
    else:
        conn.execute(
            "UPDATE tasks SET status=?, completed_at=NULL, updated_at=? WHERE id=?",
            (status, now, task_id))

    conn.execute("""
        INSERT INTO task_history (task_id, user_id, action, old_value, new_value)
        VALUES (?, ?, 'status_changed', ?, ?)
    """, (task_id, user_id, old_status, status))

    conn.commit()
    conn.close()
    return True, f"Task marked as {status}!"


# ── Subtask Operations ─────────────────────────────────────

def add_subtask(task_id, title):
    """Add a subtask to a task."""
    if not title or not title.strip():
        return None, "Subtask title is required."
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subtasks (task_id, title) VALUES (?, ?)",
        (task_id, title.strip()))
    sid = cursor.lastrowid
    conn.commit()
    conn.close()
    return sid, "Subtask added!"


def toggle_subtask(subtask_id):
    """Toggle a subtask's done state."""
    conn = get_connection()
    sub = conn.execute(
        "SELECT * FROM subtasks WHERE id = ?", (subtask_id,)).fetchone()
    if not sub:
        conn.close()
        return False
    conn.execute(
        "UPDATE subtasks SET is_done = ? WHERE id = ?",
        (0 if sub["is_done"] else 1, subtask_id))
    conn.commit()
    conn.close()
    return True


def delete_subtask(subtask_id):
    """Delete a subtask."""
    conn = get_connection()
    conn.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()
    conn.close()
    return True


def get_subtasks(task_id):
    """Get all subtasks for a task."""
    conn = get_connection()
    subs = conn.execute(
        "SELECT * FROM subtasks WHERE task_id = ? ORDER BY id",
        (task_id,)).fetchall()
    conn.close()
    return [dict(s) for s in subs]


# ── Queries & Helpers ──────────────────────────────────────

def get_categories(user_id):
    """Get distinct categories for a user."""
    conn = get_connection()
    cats = conn.execute(
        "SELECT DISTINCT category FROM tasks WHERE user_id = ?",
        (user_id,)).fetchall()
    conn.close()
    return [c["category"] for c in cats]


def get_upcoming_tasks(user_id, hours=24):
    """Get tasks due within the next N hours."""
    conn = get_connection()
    now = datetime.now()
    future = now + timedelta(hours=hours)
    tasks = conn.execute("""
        SELECT * FROM tasks
        WHERE user_id = ? AND status NOT IN ('Done')
          AND due_date IS NOT NULL
          AND due_date BETWEEN ? AND ?
        ORDER BY due_date ASC
    """, (user_id, now.strftime("%Y-%m-%d %H:%M:%S"),
          future.strftime("%Y-%m-%d %H:%M:%S"))).fetchall()
    conn.close()
    return [dict(t) for t in tasks]


def get_overdue_tasks(user_id):
    """Get overdue tasks and auto-mark them as Late."""
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tasks = conn.execute("""
        SELECT * FROM tasks
        WHERE user_id = ? AND status NOT IN ('Done', 'Late')
          AND due_date IS NOT NULL AND due_date < ?
        ORDER BY due_date ASC
    """, (user_id, now)).fetchall()

    for task in tasks:
        conn.execute("UPDATE tasks SET status = 'Late' WHERE id = ?",
                     (task["id"],))
    conn.commit()
    conn.close()
    return [dict(t) for t in tasks]


def check_recurring_tasks(user_id):
    """Recreate completed recurring tasks for their next occurrence."""
    conn = get_connection()
    recurring = conn.execute("""
        SELECT * FROM tasks
        WHERE user_id = ? AND is_recurring = 1 AND status = 'Done'
    """, (user_id,)).fetchall()

    now = datetime.now()
    for task in recurring:
        pattern = task["recurrence_pattern"]
        completed_str = task["completed_at"]
        if not completed_str:
            continue
        try:
            completed = datetime.strptime(completed_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        if pattern == "daily":
            next_due = completed + timedelta(days=1)
        elif pattern == "weekly":
            next_due = completed + timedelta(weeks=1)
        elif pattern == "monthly":
            next_due = completed + timedelta(days=30)
        else:
            continue

        existing = conn.execute("""
            SELECT id FROM tasks
            WHERE user_id = ? AND title = ? AND status != 'Done'
              AND is_recurring = 1
        """, (user_id, task["title"])).fetchone()

        if not existing:
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO tasks
                    (user_id, title, description, category, priority,
                     status, due_date, is_recurring, recurrence_pattern,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'Pending', ?, 1, ?, ?, ?)
            """, (user_id, task["title"], task["description"],
                  task["category"], task["priority"],
                  next_due.strftime("%Y-%m-%d %H:%M:%S"),
                  pattern, now_str, now_str))

    conn.commit()
    conn.close()


def get_task_history(task_id):
    """Get audit log for a task."""
    conn = get_connection()
    history = conn.execute("""
        SELECT * FROM task_history WHERE task_id = ?
        ORDER BY timestamp DESC
    """, (task_id,)).fetchall()
    conn.close()
    return [dict(h) for h in history]
