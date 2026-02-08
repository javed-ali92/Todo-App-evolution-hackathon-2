#!/usr/bin/env python3
"""
Script to fix the database schema by recreating the user table with correct structure
"""

import sqlite3
import os

def fix_user_table_schema():
    """Fix the user table schema by recreating it properly"""

    db_path = os.path.join(os.path.dirname(__file__), "todo_app.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Fixing user table schema...")

    # Get current user data
    cursor.execute("SELECT id, email, hashed_password, created_at, updated_at FROM user")
    user_data = cursor.fetchall()

    print(f"Found {len(user_data)} existing users to migrate")

    # Drop the current user table
    cursor.execute("DROP TABLE user")

    # Create new user table with correct schema
    cursor.execute("""
        CREATE TABLE user (
            username VARCHAR(30) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            id INTEGER NOT NULL PRIMARY KEY,
            hashed_password VARCHAR NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)

    # Insert the migrated data
    for user_row in user_data:
        user_id, email, hashed_password, created_at, updated_at = user_row
        # Use email as username for existing users if no username exists
        username = email.split('@')[0]  # Take part before @ as username
        cursor.execute("""
            INSERT INTO user (username, email, id, hashed_password, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, user_id, hashed_password, created_at, updated_at))

    conn.commit()
    conn.close()

    print("User table schema fixed successfully!")


if __name__ == "__main__":
    fix_user_table_schema()