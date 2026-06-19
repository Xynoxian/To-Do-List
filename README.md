# Advanced To-Do List Organizer

A comprehensive, GUI-based task management and productivity application built with Python. This application goes beyond standard checklists by integrating user authentication, a visual Kanban board, smart scheduling, and built-in productivity analytics.

---

## ✨ Features

* **Secure Authentication:** User registration and secure login interfaces to keep individual task lists private (`auth.py`, `login_frame.py`).
* **Interactive Dashboard:** A centralized interface to overview pending, ongoing, and completed tasks (`dashboard_frame.py`).
* **Kanban Board:** Visually track and manage workflow stages with an intuitive card-based system (`kanban_frame.py`).
* **Intelligent Scheduling:** Smart deadline tracking and proactive reminder alerts to stay ahead of upcoming tasks (`scheduler.py`).
* **Productivity Analytics:** Graphical performance tracking and statistics to monitor task completion rates and analyze efficiency trends over time (`analytics.py`, `analytics_frame.py`).
* **Persistent Storage:** Built on a robust SQLite backend to ensure data remains safely stored between sessions (`database.py`, `todolist.db`).

---

## 📂 Project Structure

The project codebase is organized as follows:

```text
├── main.py                 # Application entry point
├── auth.py                 # Authentication and user logic
├── database.py             # Database initialization and queries
├── task_manager.py         # Core task manipulation logic
├── scheduler.py            # Notification and scheduling handlers
├── analytics.py            # Productivity and trend analytics calculations
├── requirements.txt        # Third-party dependencies
├── todolist.db             # SQLite local database
│
├── gui/                    # Graphical User Interface modules
│   ├── __init__.py
│   ├── app.py              # Main application window router
│   ├── styles.py           # Centralized UI themes and configurations
│   ├── login_frame.py      # Sign-in and registration views
│   ├── dashboard_frame.py  # Overview interface
│   ├── kanban_frame.py     # Agile-style task management view
│   ├── task_list.py        # List-view and status toggle panels
│   ├── task_form.py        # Dialog forms for creating/editing tasks
│   └── analytics_frame.py  # Productivity dashboards and performance charts
│
└── test_programs/          # Simulation and testing suites
    ├── test_program1.py
    └── test_program2.py
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.x installed on your machine.

### Installation
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   ```
2. Navigate into the project root directory:
   ```bash
   cd YOUR_REPOSITORY
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
Launch the main application script to start the GUI application:
```bash
python main.py
```
