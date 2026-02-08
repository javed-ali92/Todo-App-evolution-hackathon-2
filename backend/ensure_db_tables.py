#!/usr/bin/env python3
"""
Script to ensure database tables are created
"""

from src.database.database import engine
from src.models import user, task, session
from sqlmodel import SQLModel

def create_db_and_tables():
    """Create all database tables"""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_db_and_tables()