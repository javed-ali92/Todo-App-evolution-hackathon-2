#!/usr/bin/env python3
"""
Script to recreate the session table with correct schema
"""

import sqlite3
import os

def recreate_session_table():
    """Recreate the session table with correct schema"""

    db_path = os.path.join(os.path.dirname(__file__), "todo_app.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Getting current session data...")

    # Get all session data
    try:
        cursor.execute("SELECT id, user_id, token, token_jti, expires_at, created_at, last_used_at FROM session")
        session_data = cursor.fetchall()
        print(f"Found {len(session_data)} existing sessions to migrate")
    except sqlite3.OperationalError as e:
        print(f"No existing session table or it has a different structure: {e}")
        session_data = []

    # Drop the current session table
    try:
        cursor.execute("DROP TABLE IF EXISTS session")
        print("Dropped existing session table")
    except sqlite3.Error as e:
        print(f"Error dropping session table: {e}")

    # Create new session table with correct schema according to the model
    cursor.execute("""
        CREATE TABLE session (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token VARCHAR(500) NOT NULL UNIQUE,
            token_jti VARCHAR(255) NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            created_at DATETIME NOT NULL,
            last_used_at DATETIME NOT NULL,
            revoked BOOLEAN NOT NULL DEFAULT 0,
            revoked_at DATETIME
        )
    """)

    # Insert the migrated data with default values for new columns
    for session_row in session_data:
        session_id, user_id, token, token_jti, expires_at, created_at, last_used_at = session_row
        cursor.execute("""
            INSERT INTO session (id, user_id, token, token_jti, expires_at, created_at, last_used_at, revoked, revoked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL)
        """, (session_id, user_id, token, token_jti, expires_at, created_at, last_used_at))

    conn.commit()
    conn.close()

    print("Session table recreated with correct schema!")


if __name__ == "__main__":
    recreate_session_table()