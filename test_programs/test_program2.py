"""
test_program2.py — Test bonus features: subtasks, recurring tasks,
analytics, achievements, AI scheduling, and priority scoring.

Run this AFTER test_program1.py or independently (it creates its own data).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import initialize_database, get_connection
from auth import register_user, login_user
from task_manager import (create_task, get_tasks, mark_task_status,
                          add_subtask, get_subtasks, toggle_subtask,
                          delete_subtask, get_task_history, get_categories,
                          get_upcoming_tasks, check_recurring_tasks)
from analytics import (get_completion_stats, get_on_time_rate,
                       get_productivity_score, get_streak,
                       get_tasks_by_priority, get_tasks_by_category,
                       check_achievements, get_achievements)
from scheduler import (calculate_priority_score, get_smart_task_order,
                       detect_deadline_conflicts, get_workload_summary,
                       predict_delayed_tasks)
from datetime import datetime, timedelta

# Reset database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "todolist.db")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

initialize_database()

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f"  ✅ PASS: {name}")
        passed += 1
    else:
        print(f"  ❌ FAIL: {name}")
        failed += 1

print("=" * 60)
print("TEST PROGRAM 2: Bonus Features")
print("=" * 60)

# Setup: create user and tasks
register_user("tester", "test@test.com", "test123")
user, _ = login_user("tester", "test123")
uid = user["id"]
now = datetime.now()

# Create a variety of tasks
tasks_data = [
    ("Meeting prep", "Work", "High", 2),
    ("Exercise", "Health", "Medium", 24),
    ("Read book", "Personal", "Low", 72),
    ("Submit assignment", "Study", "Urgent", 1),
    ("Clean house", "Personal", "Medium", 48),
    ("Team standup", "Work", "High", 3),
    ("Buy birthday gift", "Personal", "Medium", 5),
    ("Fix bug #42", "Work", "Urgent", 0.5),
]

task_ids = []
for title, cat, pri, hours in tasks_data:
    due = (now + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    tid, _ = create_task(uid, title, f"Description for {title}", cat, pri, due)
    task_ids.append(tid)

# ── Bonus 1: Task Management Features ─────────────────────
print("\n--- Bonus 1: Task Management ---")

# Subtasks
print("  [Subtasks]")
sid1, msg = add_subtask(task_ids[0], "Prepare slides")
test("Add subtask 1", sid1 is not None)
sid2, _ = add_subtask(task_ids[0], "Review agenda")
sid3, _ = add_subtask(task_ids[0], "Print handouts")
subs = get_subtasks(task_ids[0])
test("Get subtasks returns 3", len(subs) == 3)

ok = toggle_subtask(sid1)
test("Toggle subtask to done", ok)
subs = get_subtasks(task_ids[0])
done_sub = [s for s in subs if s["id"] == sid1][0]
test("Subtask is marked done", done_sub["is_done"] == 1)

ok = delete_subtask(sid3)
test("Delete subtask", ok)
subs = get_subtasks(task_ids[0])
test("Subtasks count after delete is 2", len(subs) == 2)

# Categories
print("  [Categories]")
cats = get_categories(uid)
test("Categories detected (4 unique)", len(cats) >= 4)

# Task History
print("  [Task History]")
history = get_task_history(task_ids[0])
test("Task history has entries", len(history) >= 1)

# Priority sorting
print("  [Priority Sorting]")
by_pri = get_tasks(uid, sort_by="priority")
test("Sort by priority works", len(by_pri) == 8)
test("Urgent tasks first", by_pri[0]["priority"] == "Urgent")

# Search
print("  [Search & Filter]")
results = get_tasks(uid, search="bug")
test("Search finds 'Fix bug #42'", len(results) >= 1)

results = get_tasks(uid, category="Work")
test("Filter by Work category", all(t["category"] == "Work" for t in results))

# Recurring tasks
print("  [Recurring Tasks]")
rec_id, _ = create_task(uid, "Daily standup", "", "Work", "Medium",
                        now.strftime("%Y-%m-%d %H:%M:%S"), is_recurring=1,
                        recurrence_pattern="daily")
test("Create recurring task", rec_id is not None)
mark_task_status(rec_id, uid, "Done")
check_recurring_tasks(uid)
all_tasks = get_tasks(uid)
recurring = [t for t in all_tasks if t["title"] == "Daily standup" and t["status"] != "Done"]
test("Recurring task recreated after completion", len(recurring) >= 1)

# ── Bonus 2: Productivity Analytics ───────────────────────
print("\n--- Bonus 2: Productivity Analytics ---")

# Mark some tasks done for analytics
mark_task_status(task_ids[1], uid, "Done")  # Exercise
mark_task_status(task_ids[2], uid, "Done")  # Read book
mark_task_status(task_ids[4], uid, "Done")  # Clean house

stats = get_completion_stats(uid)
test("Completion stats - total > 0", stats["total"] > 0)
test("Completion stats - done count", stats["done"] >= 3)
test("Completion rate calculated", stats["completion_rate"] > 0)

on_time = get_on_time_rate(uid)
test("On-time rate is a number", isinstance(on_time, float))

score = get_productivity_score(uid)
test("Productivity score between 0-100", 0 <= score <= 100)

streak = get_streak(uid)
test("Streak is non-negative", streak >= 0)

by_priority = get_tasks_by_priority(uid)
test("Tasks by priority has 4 levels", len(by_priority) == 4)

by_cat = get_tasks_by_category(uid)
test("Tasks by category has entries", len(by_cat) > 0)

# Achievements
newly = check_achievements(uid)
all_achs = get_achievements(uid)
test("Achievements checked", isinstance(all_achs, list))
test("'First Task' achievement earned", any(a["achievement_name"] == "First Task" for a in all_achs))
test("'Getting Started' achievement earned", any(a["achievement_name"] == "Getting Started" for a in all_achs))

# ── Bonus 3: AI Scheduling ───────────────────────────────
print("\n--- Bonus 3: AI-Based Scheduling ---")

# Priority scoring
task_urgent = {"priority": "Urgent", "due_date": (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "status": "Pending"}
task_low = {"priority": "Low", "due_date": (now + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"), "status": "Pending"}
score_urgent = calculate_priority_score(task_urgent)
score_low = calculate_priority_score(task_low)
test("Urgent near-deadline scores higher than low far-deadline",
     score_urgent > score_low)

# Smart task order
smart_order = get_smart_task_order(uid)
test("Smart order returns tasks", len(smart_order) > 0)
test("Tasks have AI scores", all("ai_score" in t for t in smart_order))
test("Sorted by score descending",
     all(smart_order[i]["ai_score"] >= smart_order[i+1]["ai_score"]
         for i in range(len(smart_order)-1)))

# Deadline conflicts
# Create multiple tasks on same day to trigger conflict
conflict_date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
for i in range(4):
    create_task(uid, f"Conflict task {i+1}", "", "Test", "Medium",
                f"{conflict_date} {10+i}:00:00")
conflicts = detect_deadline_conflicts(uid)
test("Deadline conflicts detected", len(conflicts) >= 1)
test("Conflict has message", all("message" in c for c in conflicts))

# Workload summary
workload = get_workload_summary(uid)
test("Workload has today count", "today" in workload)
test("Workload has suggestions", len(workload["suggestions"]) > 0)

# Delay predictions
at_risk = predict_delayed_tasks(uid)
test("Delay prediction returns list", isinstance(at_risk, list))

# ── Summary ───────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)
