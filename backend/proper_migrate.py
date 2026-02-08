#!/usr/bin/env python3
"""
Proper database migration to fix the schema issue
"""

import sqlite3
import tempfile
import shutil
import os

def migrate_user_table():
    """Migrate the user table to add missing username column"""
    db_path = os.path.join(os.path.dirname(__file__), "todo_app.db")

    # Connect to the original database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all user data
    cursor.execute("SELECT id, email, hashed_password, created_at, updated_at FROM user")
    users = cursor.fetchall()

    print(f"Migrating {len(users)} users...")

    # Create a temporary database to build the new structure
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()

    temp_conn = sqlite3.connect(temp_db.name)
    temp_cursor = temp_conn.cursor()

    # Create new user table with correct schema
    temp_cursor.execute("""
        CREATE TABLE user (
            id INTEGER NOT NULL PRIMARY KEY,
            username VARCHAR(30) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)

    # Insert migrated data with generated usernames
    for user in users:
        user_id, email, hashed_password, created_at, updated_at = user
        # Generate a username from email (take part before @)
        username = email.split('@')[0] if '@' in email else f"user_{user_id}"

        # Ensure uniqueness by appending numbers if needed
        original_username = username
        counter = 1
        while True:
            try:
                temp_cursor.execute("""
                    INSERT INTO user (id, username, email, hashed_password, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, username, email, hashed_password, created_at, updated_at))
                break
            except sqlite3.IntegrityError:
                # Username already exists, try with a number
                username = f"{original_username}{counter}"
                counter += 1

    # Copy other tables if they exist
    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = cursor.fetchall()

    for table_name, in all_tables:
        if table_name != 'user':
            # Copy table structure and data
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            table_sql = cursor.fetchone()
            if table_sql:
                temp_cursor.execute(table_sql[0])

                # Copy data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                if rows:
                    placeholders = ','.join(['?' for _ in rows[0]])
                    temp_cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)

    temp_conn.commit()
    temp_conn.close()
    conn.close()

    # Replace the original database with the migrated one
    shutil.move(temp_db.name, db_path)

    print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_user_table()