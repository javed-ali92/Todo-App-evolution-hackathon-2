#!/usr/bin/env python3
"""
Database migration script to update schema
"""

import sqlite3
import os
from sqlmodel import SQLModel
from src.database.database import engine

def migrate_database():
    """Add missing columns to existing tables"""
    print("Connecting to database...")

    # Connect to the SQLite database directly
    import os
    db_path = os.path.join(os.path.dirname(__file__), "todo_app.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking current user table schema...")

    # Get current columns
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    print(f"Current columns: {column_names}")

    # Check if username column exists
    if 'username' not in column_names:
        print("Adding missing 'username' column to user table...")
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN username VARCHAR(30) UNIQUE")
            print("Added 'username' column successfully")
        except sqlite3.Error as e:
            print(f"Error adding username column: {e}")

    # Check if unique constraint exists properly
    # We need to update existing records that don't have usernames
    # For now, let's add a default username for any records that might exist
    cursor.execute("UPDATE user SET username = email WHERE username IS NULL OR username = ''")

    conn.commit()
    conn.close()

    print("Database migration completed!")

    # Now recreate tables to ensure all indexes/constraints are correct
    print("Recreating tables to ensure proper schema...")
    SQLModel.metadata.create_all(engine)
    print("Tables recreated successfully!")


if __name__ == "__main__":
    migrate_database()