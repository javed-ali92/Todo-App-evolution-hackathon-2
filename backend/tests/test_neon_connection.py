"""
Test suite for User Story 1: Database Connection Establishment

Validates that:
1. Application connects exclusively to Neon PostgreSQL
2. No SQLite fallback exists
3. DATABASE_URL validation works correctly
4. Connection errors are handled properly
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError


class TestDatabaseURLValidation:
    """Test DATABASE_URL validation (Tasks T024, T026, T027)"""

    def test_database_url_is_read_correctly(self):
        """Task T024: Test DATABASE_URL is read correctly from environment"""
        # Verify DATABASE_URL is set in environment
        database_url = os.getenv("DATABASE_URL")
        assert database_url is not None, "DATABASE_URL must be set in environment"
        assert database_url.startswith(("postgresql://", "postgres://")), \
            "DATABASE_URL must be a PostgreSQL connection string"

    def test_missing_database_url_raises_error(self):
        """Task T026: Test missing DATABASE_URL raises error"""
        from src.database.validation import validate_database_url

        with pytest.raises(ValueError) as exc_info:
            validate_database_url(None)

        assert "DATABASE_URL is not set" in str(exc_info.value)

    def test_empty_database_url_raises_error(self):
        """Task T026: Test empty DATABASE_URL raises error"""
        from src.database.validation import validate_database_url

        with pytest.raises(ValueError) as exc_info:
            validate_database_url("")

        assert "DATABASE_URL is not set" in str(exc_info.value)

    def test_sqlite_database_url_raises_error(self):
        """Task T027: Test SQLite DATABASE_URL raises error"""
        from src.database.validation import validate_database_url

        sqlite_urls = [
            "sqlite:///./todo_app.db",
            "sqlite:///database.db",
            "sqlite:///:memory:"
        ]

        for sqlite_url in sqlite_urls:
            with pytest.raises(ValueError) as exc_info:
                validate_database_url(sqlite_url)

            assert "SQLite database detected" in str(exc_info.value)
            assert "Neon PostgreSQL" in str(exc_info.value)

    def test_invalid_database_url_format_raises_error(self):
        """Task T027: Test invalid DATABASE_URL format raises error"""
        from src.database.validation import validate_database_url

        invalid_urls = [
            "mysql://localhost/db",
            "mongodb://localhost/db",
            "http://example.com",
            "invalid_connection_string"
        ]

        for invalid_url in invalid_urls:
            with pytest.raises(ValueError) as exc_info:
                validate_database_url(invalid_url)

            assert "Invalid DATABASE_URL format" in str(exc_info.value)

    def test_valid_postgresql_url_passes(self):
        """Task T024: Test valid PostgreSQL URL passes validation"""
        from src.database.validation import validate_database_url

        valid_urls = [
            "postgresql://user:pass@host/db",
            "postgres://user:pass@host/db",
            "postgresql://user:pass@neon.tech/db?sslmode=require"
        ]

        for valid_url in valid_urls:
            # Should not raise any exception
            validate_database_url(valid_url)


class TestNeonConnection:
    """Test connection to Neon PostgreSQL (Task T025)"""

    def test_connection_to_neon_succeeds(self):
        """Task T025: Test connection to Neon succeeds"""
        from src.database.database import engine
        from src.database.validation import test_connection

        # This will raise an exception if connection fails
        result = test_connection(engine)
        assert result is True, "Connection to Neon PostgreSQL should succeed"

    def test_connection_returns_postgresql_dialect(self):
        """Task T025: Verify engine uses PostgreSQL dialect"""
        from src.database.database import engine

        assert engine.dialect.name == "postgresql", \
            f"Expected PostgreSQL dialect, got {engine.dialect.name}"

    def test_database_url_points_to_neon(self):
        """Task T025: Verify DATABASE_URL points to Neon (not local)"""
        from src.database.database import DATABASE_URL

        assert DATABASE_URL is not None
        assert DATABASE_URL.startswith(("postgresql://", "postgres://"))
        assert "sqlite" not in DATABASE_URL.lower()


class TestSQLiteRemoval:
    """Test SQLite is completely removed (Tasks T028, T029)"""

    def test_no_local_db_files_exist(self):
        """Task T028: Verify no local .db files exist after startup"""
        backend_dir = Path(__file__).parent.parent

        # Check for common SQLite database file patterns
        db_patterns = ["*.db", "*.sqlite", "*.sqlite3"]
        found_db_files = []

        for pattern in db_patterns:
            found_db_files.extend(backend_dir.glob(pattern))

        # Filter out test databases if any
        production_db_files = [
            f for f in found_db_files
            if "test" not in f.name.lower() and "todo_app.db" in f.name
        ]

        assert len(production_db_files) == 0, \
            f"Found local database files that should not exist: {production_db_files}"

    def test_sqlite_not_imported_in_database_module(self):
        """Task T029: Verify SQLite is not imported in database module"""
        # Read the database.py file and check for SQLite imports
        database_file = Path(__file__).parent.parent / "src" / "database" / "database.py"

        with open(database_file, "r") as f:
            content = f.read()

        # Check for SQLite-related imports or references
        sqlite_indicators = [
            "import sqlite3",
            "from sqlite3",
            "sqlite://",
        ]

        found_indicators = []
        for indicator in sqlite_indicators:
            if indicator in content:
                found_indicators.append(indicator)

        assert len(found_indicators) == 0, \
            f"Found SQLite references in database.py: {found_indicators}"

    def test_no_sqlite_fallback_in_database_url(self):
        """Task T028: Verify no SQLite fallback exists in DATABASE_URL assignment"""
        database_file = Path(__file__).parent.parent / "src" / "database" / "database.py"

        with open(database_file, "r") as f:
            content = f.read()

        # Check that there's no fallback to SQLite in DATABASE_URL assignment
        assert 'os.getenv("DATABASE_URL", "sqlite:' not in content, \
            "Found SQLite fallback in DATABASE_URL assignment"

        # Verify the correct pattern exists (no default value)
        assert 'os.getenv("DATABASE_URL")' in content, \
            "DATABASE_URL should be read without fallback"


class TestConnectionErrorHandling:
    """Test connection error handling (Task T022)"""

    @patch('src.database.validation.test_connection')
    def test_startup_fails_with_invalid_connection(self, mock_test_connection):
        """Test that startup fails gracefully with invalid connection"""
        from src.main import create_db_and_tables

        # Simulate connection failure
        mock_test_connection.side_effect = OperationalError(
            "Connection failed",
            params=None,
            orig=None
        )

        with pytest.raises(RuntimeError) as exc_info:
            create_db_and_tables()

        assert "Database initialization failed" in str(exc_info.value)


class TestSchemaValidation:
    """Test schema validation on startup (Task T019)"""

    def test_required_tables_exist(self):
        """Verify required tables exist in Neon database"""
        from src.database.database import engine
        from sqlalchemy import inspect

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        required_tables = ["user", "task", "session"]
        for table in required_tables:
            assert table in existing_tables, \
                f"Required table '{table}' does not exist in database"

    def test_schema_validation_function_works(self):
        """Test schema validation function executes successfully"""
        from src.database.database import engine
        from src.database.validation import validate_schema

        # This will raise an exception if validation fails
        result = validate_schema(engine)
        assert result is True, "Schema validation should pass"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
