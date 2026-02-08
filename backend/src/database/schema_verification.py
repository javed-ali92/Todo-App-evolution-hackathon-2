from sqlmodel import SQLModel
from sqlalchemy import inspect
from .database import engine
from ..models.user import User
from ..models.task import Task
from ..models.session import Session
from typing import Dict, List, Any


def verify_table_exists(table_name: str) -> bool:
    """
    Verify if a specific table exists in the database.

    Args:
        table_name: Name of the table to check

    Returns:
        bool: True if table exists, False otherwise
    """
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def get_table_columns(table_name: str) -> List[Dict[str, Any]]:
    """
    Get column information for a specific table.

    Args:
        table_name: Name of the table to inspect

    Returns:
        List[Dict]: List of column information dictionaries
    """
    inspector = inspect(engine)
    return inspector.get_columns(table_name)


def verify_foreign_keys(table_name: str) -> List[Dict[str, Any]]:
    """
    Verify foreign key constraints for a specific table.

    Args:
        table_name: Name of the table to inspect

    Returns:
        List[Dict]: List of foreign key information
    """
    inspector = inspect(engine)
    return inspector.get_foreign_keys(table_name)


def verify_primary_keys(table_name: str) -> List[Dict[str, Any]]:
    """
    Verify primary key constraints for a specific table.

    Args:
        table_name: Name of the table to inspect

    Returns:
        List[Dict]: List of primary key information
    """
    inspector = inspect(engine)
    return inspector.get_pk_constraint(table_name)


def verify_indexes(table_name: str) -> List[Dict[str, Any]]:
    """
    Verify indexes for a specific table.

    Args:
        table_name: Name of the table to inspect

    Returns:
        List[Dict]: List of index information
    """
    inspector = inspect(engine)
    return inspector.get_indexes(table_name)


def verify_all_schemas() -> Dict[str, Any]:
    """
    Verify all schemas and relationships in the database.

    Returns:
        Dict: Comprehensive verification results
    """
    results = {
        'tables': {},
        'relationships': {},
        'overall_status': 'PENDING',
        'errors': []
    }

    # Define expected tables and their relationships
    expected_tables = {
        User.__tablename__: {
            'columns': ['id', 'username', 'email', 'hashed_password', 'created_at', 'updated_at'],
            'primary_key': ['id'],
            'foreign_keys': []
        },
        Task.__tablename__: {
            'columns': ['id', 'user_id', 'title', 'description', 'due_date', 'priority', 'tags', 'recursion_pattern', 'completed', 'created_at', 'updated_at'],
            'primary_key': ['id'],
            'foreign_keys': ['user_id']  # Should reference User.id
        },
        Session.__tablename__: {
            'columns': ['id', 'user_id', 'token', 'expires_at', 'created_at', 'last_used_at'],
            'primary_key': ['id'],
            'foreign_keys': ['user_id']  # Should reference User.id
        }
    }

    inspector = inspect(engine)
    db_tables = inspector.get_table_names()

    for table_name, expected_info in expected_tables.items():
        table_result = {
            'exists': table_name in db_tables,
            'columns_valid': False,
            'primary_key_valid': False,
            'foreign_keys_valid': True,  # We'll validate this separately
            'details': {}
        }

        if table_result['exists']:
            # Check columns
            db_columns = [col['name'] for col in get_table_columns(table_name)]
            expected_columns = expected_info['columns']

            missing_columns = set(expected_columns) - set(db_columns)
            extra_columns = set(db_columns) - set(expected_columns)

            table_result['columns_valid'] = len(missing_columns) == 0
            table_result['details']['db_columns'] = db_columns
            table_result['details']['expected_columns'] = expected_columns
            table_result['details']['missing_columns'] = list(missing_columns)
            table_result['details']['extra_columns'] = list(extra_columns)

            # Check primary key
            pk_info = verify_primary_keys(table_name)
            if pk_info and 'constrained_columns' in pk_info:
                db_pks = pk_info['constrained_columns']
                expected_pks = expected_info['primary_key']
                table_result['primary_key_valid'] = set(db_pks) == set(expected_pks)
                table_result['details']['db_primary_keys'] = db_pks
                table_result['details']['expected_primary_keys'] = expected_pks
            else:
                table_result['primary_key_valid'] = False
                table_result['details']['db_primary_keys'] = []
                table_result['details']['expected_primary_keys'] = expected_info['primary_key']

            # Check foreign keys
            db_fks = [fk['constrained_columns'][0] for fk in verify_foreign_keys(table_name)]
            expected_fks = expected_info['foreign_keys']

            # For our use case, we expect user_id in Task and Session to reference User.id
            table_result['foreign_keys_valid'] = set(db_fks) >= set(expected_fks)
            table_result['details']['db_foreign_keys'] = db_fks
            table_result['details']['expected_foreign_keys'] = expected_fks

        results['tables'][table_name] = table_result

    # Verify relationships
    # Task should have foreign key to User
    task_fks = verify_foreign_keys(Task.__tablename__)
    results['relationships']['task_to_user_fk'] = {
        'exists': any(fk['referred_table'] == User.__tablename__ and 'user_id' in fk['constrained_columns'] for fk in task_fks),
        'details': task_fks
    }

    # Session should have foreign key to User
    session_fks = verify_foreign_keys(Session.__tablename__)
    results['relationships']['session_to_user_fk'] = {
        'exists': any(fk['referred_table'] == User.__tablename__ and 'user_id' in fk['constrained_columns'] for fk in session_fks),
        'details': session_fks
    }

    # Overall status
    all_tables_exist = all(info['exists'] for info in results['tables'].values())
    all_columns_valid = all(info['columns_valid'] for info in results['tables'].values())
    all_pks_valid = all(info['primary_key_valid'] for info in results['tables'].values())

    all_relationships_valid = (
        results['relationships']['task_to_user_fk']['exists'] and
        results['relationships']['session_to_user_fk']['exists']
    )

    results['overall_status'] = 'PASSED' if (
        all_tables_exist and
        all_columns_valid and
        all_pks_valid and
        all_relationships_valid
    ) else 'FAILED'

    # Collect errors
    for table_name, info in results['tables'].items():
        if not info['exists']:
            results['errors'].append(f"Table '{table_name}' does not exist")
        if not info['columns_valid'] and info['details'].get('missing_columns'):
            results['errors'].extend([
                f"Table '{table_name}' missing column: {col}"
                for col in info['details']['missing_columns']
            ])
        if not info['primary_key_valid']:
            results['errors'].append(f"Table '{table_name}' primary key invalid")

    if not results['relationships']['task_to_user_fk']['exists']:
        results['errors'].append(f"Foreign key relationship between Task and User does not exist")

    if not results['relationships']['session_to_user_fk']['exists']:
        results['errors'].append(f"Foreign key relationship between Session and User does not exist")

    return results


def print_verification_report(results: Dict[str, Any]):
    """
    Print a formatted verification report.

    Args:
        results: Verification results dictionary
    """
    print("=" * 60)
    print("DATABASE SCHEMA VERIFICATION REPORT")
    print("=" * 60)

    print(f"\nOverall Status: {'✅ ' + results['overall_status'] if results['overall_status'] == 'PASSED' else '❌ ' + results['overall_status']}\n")

    print("TABLE VERIFICATION:")
    for table_name, info in results['tables'].items():
        status_icon = "✅" if info['exists'] else "❌"
        print(f"  {status_icon} {table_name}:")
        print(f"    Exists: {info['exists']}")
        print(f"    Columns: {'✅' if info['columns_valid'] else '❌'}")
        print(f"    Primary Key: {'✅' if info['primary_key_valid'] else '❌'}")
        print(f"    Foreign Keys: {'✅' if info['foreign_keys_valid'] else '❌'}")

    print("\nRELATIONSHIP VERIFICATION:")
    for rel_name, info in results['relationships'].items():
        status_icon = "✅" if info['exists'] else "❌"
        print(f"  {status_icon} {rel_name}: {info['exists']}")

    if results['errors']:
        print(f"\nERRORS ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  ❌ {error}")
    else:
        print("\n🎉 No errors found!")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("Verifying database schema and relationships...")
    verification_results = verify_all_schemas()
    print_verification_report(verification_results)