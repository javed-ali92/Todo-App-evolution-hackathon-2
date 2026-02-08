from sqlmodel import SQLModel
from sqlalchemy import create_engine, inspect
from .database import engine
from ..models.user import User
from ..models.task import Task
from ..models.session import Session
from typing import Dict, List


def check_table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        table_name: Name of the table to check

    Returns:
        bool: True if table exists, False otherwise
    """
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def get_database_schema_info() -> Dict:
    """
    Get information about the current database schema.

    Returns:
        Dict: Information about tables, columns, etc.
    """
    inspector = inspect(engine)
    tables = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        tables[table_name] = [col['name'] for col in columns]

    return {
        'tables': tables,
        'table_count': len(tables)
    }


def validate_models_against_database() -> Dict[str, List[str]]:
    """
    Validate that all model-defined tables exist in the database.

    Returns:
        Dict: Mapping of model names to missing columns/tables
    """
    inspector = inspect(engine)
    db_tables = set(inspector.get_table_names())

    # Expected tables based on models
    expected_tables = {
        User.__tablename__,
        Task.__tablename__,
        Session.__tablename__
    }

    missing_tables = expected_tables - db_tables
    existing_tables = expected_tables & db_tables

    result = {
        'missing_tables': list(missing_tables),
        'existing_tables': list(existing_tables),
        'validation_passed': len(missing_tables) == 0
    }

    return result


def run_migrations():
    """
    Run database migrations to create/update tables.
    """
    print("Starting database migration...")

    # Create all tables defined in SQLModel models
    SQLModel.metadata.create_all(engine)

    # Validate the schema after migration
    validation_result = validate_models_against_database()

    if validation_result['validation_passed']:
        print("✓ Migration completed successfully!")
        print(f"Tables created: {validation_result['existing_tables']}")
    else:
        print("⚠ Migration completed with warnings:")
        print(f"Missing tables: {validation_result['missing_tables']}")

    return validation_result


def rollback_migrations():
    """
    Rollback database migrations (drops all tables defined in models).
    WARNING: This will delete all data!
    """
    print("WARNING: Rolling back all migrations. This will delete ALL data.")
    confirm = input("Are you sure? Type 'YES' to continue: ")

    if confirm != 'YES':
        print("Rollback cancelled.")
        return

    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    print("✓ All tables dropped successfully!")


if __name__ == "__main__":
    # If run as main script, execute migration
    run_migrations()