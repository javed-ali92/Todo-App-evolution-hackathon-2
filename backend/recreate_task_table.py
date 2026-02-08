#!/usr/bin/env python3
"""
Script to recreate the task table with correct schema
"""

import sqlite3
import os

def recreate_task_table():
    """Recreate the task table with correct schema"""

    db_path = os.path.join(os.path.dirname(__file__), "todo_app.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Getting current task data...")

    # Get all task data
    try:
        cursor.execute("SELECT id, title, description, completed, owner_id, created_at, updated_at FROM task")
        task_data = cursor.fetchall()
        print(f"Found {len(task_data)} existing tasks to migrate")
    except sqlite3.OperationalError as e:
        print(f"No existing task table or it has a different structure: {e}")
        task_data = []

    # Drop the current task table
    try:
        cursor.execute("DROP TABLE IF EXISTS task")
        print("Dropped existing task table")
    except sqlite3.Error as e:
        print(f"Error dropping task table: {e}")

    # Create new task table with correct schema according to the model
    cursor.execute("""
        CREATE TABLE task (
            id INTEGER NOT NULL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description VARCHAR,
            due_date VARCHAR,
            priority VARCHAR(20) DEFAULT 'Medium',
            tags VARCHAR,
            recursion_pattern VARCHAR(100),
            completed BOOLEAN NOT NULL DEFAULT 0,
            user_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)

    # Insert the migrated data with default values for new columns
    for task_row in task_data:
        task_id, title, description, completed, owner_id, created_at, updated_at = task_row
        # Map old owner_id to new user_id
        cursor.execute("""
            INSERT INTO task (id, title, description, due_date, priority, tags, recursion_pattern, completed, user_id, created_at, updated_at)
            VALUES (?, ?, ?, NULL, 'Medium', NULL, NULL, ?, ?, ?, ?)
        """, (task_id, title, description, completed, owner_id, created_at, updated_at))

    conn.commit()
    conn.close()

    print("Task table recreated with correct schema!")


if __name__ == "__main__":
    recreate_task_table()