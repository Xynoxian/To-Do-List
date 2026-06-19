"""
test_program1.py — Test core features: registration, login, task CRUD,
status management, date ordering, and error handling.

Run this script to populate the database with test data and verify
all core functionality works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import initialize_database, get_connection
from auth import register_user, login_user
from task_manager import (create_task, get_tasks, update_task, delete_task,
                          mark_task_status, get_task_by_id)
from datetime import datetime, timedelta

# Reset database for clean test
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
print("TEST PROGRAM 1: Core Features")
print("=" * 60)

# ── 1. User Registration ──────────────────────────────────
print("\n--- 1. User Registration ---")
ok, msg = register_user("alice", "alice@test.com", "pass123")
test("Register new user", ok)

ok, msg = register_user("bob", "bob@test.com", "secret456")
test("Register second user", ok)

ok, msg = register_user("alice", "alice2@test.com", "pass123")
test("Reject duplicate username", not ok and "exists" in msg.lower())

ok, msg = register_user("carol", "alice@test.com", "pass789")
test("Reject duplicate email", not ok and "email" in msg.lower())

ok, msg = register_user("", "x@x.com", "pass123")
test("Reject empty username", not ok)

ok, msg = register_user("dave", "invalid", "pass123")
test("Reject invalid email", not ok)

ok, msg = register_user("dave", "d@d.com", "12")
test("Reject short password", not ok)

# ── 2. User Login ─────────────────────────────────────────
print("\n--- 2. User Login ---")
user, msg = login_user("alice", "pass123")
test("Login with correct credentials", user is not None)
test("Login returns user dict", isinstance(user, dict) and user["username"] == "alice")

user, msg = login_user("alice", "wrong")
test("Reject wrong password", user is None and "incorrect" in msg.lower())

user, msg = login_user("nobody", "pass123")
test("Reject non-existent user", user is None and "not found" in msg.lower())

user, msg = login_user("", "")
test("Reject empty credentials", user is None)

# Get alice's user for task tests
alice, _ = login_user("alice", "pass123")
uid = alice["id"]

# ── 3. Create Tasks ───────────────────────────────────────
print("\n--- 3. Create Tasks ---")
now = datetime.now()

tid1, msg = create_task(uid, "Buy groceries", "Milk, eggs, bread",
                        "Personal", "High",
                        (now + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"))
test("Create task 1", tid1 is not None)

tid2, msg = create_task(uid, "Finish report", "Q2 financial report",
                        "Work", "Urgent",
                        (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"))
test("Create task 2 (urgent)", tid2 is not None)

tid3, msg = create_task(uid, "Go for a run", "", "Health", "Low",
                        (now + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"))
test("Create task 3 (low priority)", tid3 is not None)

tid4, msg = create_task(uid, "Study Python", "Chapter 5-7",
                        "Study", "Medium",
                        (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"))
test("Create task 4 (past due)", tid4 is not None)

tid5, msg = create_task(uid, "Call dentist", "", "Personal", "Medium",
                        (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
test("Create task 5", tid5 is not None)

bad, msg = create_task(uid, "", "no title")
test("Reject empty title", bad is None)

# ── 4. Read Tasks ─────────────────────────────────────────
print("\n--- 4. Read Tasks ---")
tasks = get_tasks(uid)
test("Get all tasks returns 5", len(tasks) == 5)

task = get_task_by_id(tid1)
test("Get task by ID", task is not None and task["title"] == "Buy groceries")

# ── 5. Update Task ────────────────────────────────────────
print("\n--- 5. Update Task ---")
ok, msg = update_task(tid1, uid, title="Buy groceries + snacks",
                      priority="Urgent")
test("Update task title and priority", ok)
task = get_task_by_id(tid1)
test("Verify updated values", task["title"] == "Buy groceries + snacks"
     and task["priority"] == "Urgent")

# ── 6. Mark Task as Done ──────────────────────────────────
print("\n--- 6. Mark Task as Done ---")
ok, msg = mark_task_status(tid3, uid, "Done")
test("Mark task as Done", ok)
task = get_task_by_id(tid3)
test("Verify Done status", task["status"] == "Done")
test("Verify completed_at is set", task["completed_at"] is not None)

# ── 7. Mark Task as Pending/Late ──────────────────────────
print("\n--- 7. Mark Task as Pending/Late ---")
ok, msg = mark_task_status(tid4, uid, "Late")
test("Mark task as Late", ok)
task = get_task_by_id(tid4)
test("Verify Late status", task["status"] == "Late")

ok, msg = mark_task_status(tid2, uid, "In Progress")
test("Mark task as In Progress", ok)

# ── 8. Sort by Date ───────────────────────────────────────
print("\n--- 8. Sort Tasks by Date ---")
sorted_tasks = get_tasks(uid, sort_by="due_date", sort_order="ASC")
test("Tasks sorted by due date", len(sorted_tasks) == 5)
# Check first non-null due date is earliest
dates = [t["due_date"] for t in sorted_tasks if t["due_date"]]
test("Dates in ascending order", dates == sorted(dates))

# ── 9. Filter Tasks ───────────────────────────────────────
print("\n--- 9. Filter Tasks ---")
done_tasks = get_tasks(uid, status="Done")
test("Filter by Done status", all(t["status"] == "Done" for t in done_tasks))

urgent = get_tasks(uid, priority="Urgent")
test("Filter by Urgent priority", all(t["priority"] == "Urgent" for t in urgent))

search = get_tasks(uid, search="groceries")
test("Search by keyword", len(search) >= 1 and "groceries" in search[0]["title"].lower())

# ── 10. Delete Task ───────────────────────────────────────
print("\n--- 10. Delete Task ---")
ok, msg = delete_task(tid5, uid)
test("Delete task", ok)
task = get_task_by_id(tid5)
test("Verify task deleted", task is None)
tasks = get_tasks(uid)
test("Total tasks after delete is 4", len(tasks) == 4)

# ── 11. Error Handling ────────────────────────────────────
print("\n--- 11. Error Handling ---")
ok, msg = delete_task(9999, uid)
test("Delete non-existent task", not ok)

ok, msg = update_task(9999, uid, title="x")
test("Update non-existent task", not ok)

ok, msg = mark_task_status(9999, uid, "Done")
test("Status change on non-existent task", not ok)

# ── Summary ───────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)
