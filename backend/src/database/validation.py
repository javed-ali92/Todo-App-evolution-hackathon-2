"""
Database validation module for Neon PostgreSQL connection and schema verification.

This module provides functions to:
1. Test database connection to Neon PostgreSQL
2. Validate database schema (tables, constraints, foreign keys)
3. Validate DATABASE_URL format and reject SQLite connections
"""

from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, DatabaseError
import logging

logger = logging.getLogger(__name__)


def validate_database_url(database_url: str) -> None:
    """
    Validate DATABASE_URL format and ensure it's not SQLite.

    Args:
        database_url: Database connection URL

    Raises:
        ValueError: If DATABASE_URL is missing, invalid, or points to SQLite
    """
    if not database_url:
        raise ValueError(
            "DATABASE_URL is not set. Please configure DATABASE_URL environment variable "
            "with your Neon PostgreSQL connection string."
        )

    # Reject SQLite connections
    if database_url.startswith("sqlite"):
        raise ValueError(
            "SQLite database detected. This application requires Neon PostgreSQL. "
            "Please set DATABASE_URL to your Neon PostgreSQL connection string."
        )

    # Validate PostgreSQL URL format
    if not database_url.startswith(("postgresql://", "postgres://")):
        raise ValueError(
            f"Invalid DATABASE_URL format. Expected PostgreSQL connection string "
            f"(postgresql:// or postgres://), got: {database_url[:20]}..."
        )

    logger.info("DATABASE_URL validation passed: PostgreSQL connection string detected")


def test_connection(engine: Engine) -> bool:
    """
    Test database connection to Neon PostgreSQL.

    Args:
        engine: SQLAlchemy engine instance

    Returns:
        True if connection successful

    Raises:
        OperationalError: If connection fails
        DatabaseError: If database operation fails
    """
    try:
        with engine.connect() as connection:
            # Execute simple query to verify connection
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

            # Get database name for logging
            db_result = connection.execute(text("SELECT current_database()"))
            db_name = db_result.fetchone()[0]

            logger.info(f"Database connection successful: {db_name}")
            return True

    except OperationalError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise OperationalError(
            "Failed to connect to Neon PostgreSQL. Please verify:\n"
            "1. DATABASE_URL is correct\n"
            "2. Neon database is running\n"
            "3. Network connectivity is available\n"
            f"Error: {str(e)}",
            params=None,
            orig=e.orig if hasattr(e, 'orig') else None
        )
    except DatabaseError as e:
        logger.error(f"Database error during connection test: {str(e)}")
        raise


def validate_schema(engine: Engine) -> bool:
    """
    Validate database schema has required tables and constraints.

    Verifies:
    1. Required tables exist (user, task, session)
    2. Foreign key constraints exist (task.user_id -> user.id, session.user_id -> user.id)

    Args:
        engine: SQLAlchemy engine instance

    Returns:
        True if schema validation passes

    Raises:
        ValueError: If required tables or constraints are missing
    """
    inspector = inspect(engine)

    # Required tables
    required_tables = ["user", "task", "session"]
    existing_tables = inspector.get_table_names()

    missing_tables = [table for table in required_tables if table not in existing_tables]
    if missing_tables:
        raise ValueError(
            f"Missing required tables: {', '.join(missing_tables)}. "
            f"Please run database initialization to create tables."
        )

    logger.info(f"Schema validation passed: All required tables exist {required_tables}")

    # Validate foreign key constraints
    required_foreign_keys = {
        "task": [("user_id", "user", "id")],
        "session": [("user_id", "user", "id")]
    }

    for table_name, expected_fks in required_foreign_keys.items():
        foreign_keys = inspector.get_foreign_keys(table_name)

        for fk_column, ref_table, ref_column in expected_fks:
            fk_exists = any(
                fk["constrained_columns"] == [fk_column] and
                fk["referred_table"] == ref_table and
                fk["referred_columns"] == [ref_column]
                for fk in foreign_keys
            )

            if not fk_exists:
                raise ValueError(
                    f"Missing foreign key constraint: {table_name}.{fk_column} -> {ref_table}.{ref_column}"
                )

    logger.info("Schema validation passed: All foreign key constraints exist")
    return True