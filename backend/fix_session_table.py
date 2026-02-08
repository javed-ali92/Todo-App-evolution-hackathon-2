#!/usr/bin/env python3
"""
Script to fix the session table schema by adding missing columns
"""

import sqlite3
import os

def fix_session_table():
    """Add missing columns to the session table"""

    db_path = os.path.join(os.path.dirname(__file__), "todo_app.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking session table schema...")

    # Get current columns
    cursor.execute("PRAGMA table_info(session)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    print(f"Current session columns: {column_names}")

    # Check if token_jti column exists
    if 'token_jti' not in column_names:
        print("Adding missing 'token_jti' column to session table...")
        try:
            # First, add the token_jti column (with a default value to avoid NOT NULL constraint issues)
            cursor.execute("ALTER TABLE session ADD COLUMN token_jti VARCHAR(255)")
            print("Added 'token_jti' column successfully")

            # Update existing records to have a token_jti value (generate from existing data)
            cursor.execute("SELECT id, token FROM session WHERE token_jti IS NULL OR token_jti = ''")
            sessions = cursor.fetchall()

            for session_id, token in sessions:
                # Generate a simple token_jti from the token hash
                import hashlib
                token_jti = hashlib.md5(token.encode()).hexdigest()[:32]
                cursor.execute("UPDATE session SET token_jti = ? WHERE id = ?", (token_jti, session_id))

            # Now set the NOT NULL constraint by recreating the table properly
            # Get all session data
            cursor.execute("SELECT id, user_id, token, token_jti, expires_at, created_at, last_used_at, revoked, revoked_at FROM session")
            session_data = cursor.fetchall()

            # Drop the current session table
            cursor.execute("DROP TABLE session")

            # Create new session table with correct schema
            cursor.execute("""
                CREATE TABLE session (
                    id INTEGER NOT NULL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    token VARCHAR(500) NOT NULL UNIQUE,
                    token_jti VARCHAR(255) NOT NULL UNIQUE,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_used_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    revoked BOOLEAN NOT NULL DEFAULT 0,
                    revoked_at DATETIME
                )
            """)

            # Insert the migrated data
            for session_row in session_data:
                cursor.execute("""
                    INSERT INTO session (id, user_id, token, token_jti, expires_at, created_at, last_used_at, revoked, revoked_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, session_row)

            print("Session table recreated with correct schema!")
        except sqlite3.Error as e:
            print(f"Error adding token_jti column: {e}")

    conn.commit()
    conn.close()

    print("Session table schema fixed successfully!")


if __name__ == "__main__":
    fix_session_table()