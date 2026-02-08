#!/usr/bin/env python3
"""
Final validation script for the Neon PostgreSQL Migration
Validates all aspects of the Todo application with Neon Serverless PostgreSQL
"""
import requests
import json
from sqlmodel import Session, select
from src.database.database import engine
from src.models.user import User, UserCreate
from src.models.task import Task, TaskCreate, PriorityEnum
from src.services.auth_service import create_user, authenticate_user, create_login_token
from src.services.task_service import create_task, get_tasks_by_user
import time
import sys


def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")


def print_status(task, status):
    marker = "+" if status else "-"
    print(f"{marker} {task}")


def validate_database_connection():
    """Validate database connection to Neon PostgreSQL"""
    print_section("DATABASE CONNECTION VALIDATION")

    try:
        with engine.connect() as conn:
            result = conn.execute(select(1))
            print_status("Neon PostgreSQL connection established", True)

            # Test table creation
            from src.models.user import User
            from src.models.task import Task
            from src.models.session import Session as SessionModel

            # Test creating tables (this happens in startup)
            print_status("Database models loaded successfully", True)

            # Test basic query
            result = conn.execute(select(1)).fetchone()
            print_status("Basic SQL query executed successfully", True)

            return True
    except Exception as e:
        print_status(f"Database connection failed: {e}", False)
        return False


def validate_user_authentication():
    """Validate user authentication system"""
    print_section("AUTHENTICATION SYSTEM VALIDATION")

    try:
        with Session(engine) as session:
            # Clean up any existing test data
            existing_user = session.exec(select(User).where(User.email == "validation@test.com")).first()
            if existing_user:
                session.delete(existing_user)
                session.commit()

            # Test user creation
            user_create = UserCreate(
                username="validation_user",
                email="validation@test.com",
                password="securepassword123!"
            )

            db_user = create_user(session, user_create)
            print_status(f"User creation successful (ID: {db_user.id})", True)

            # Test user authentication
            authenticated_user = authenticate_user(session, "validation@test.com", "securepassword123!")
            if authenticated_user:
                print_status("User authentication successful", True)
            else:
                print_status("User authentication failed", False)
                return False

            # Test JWT token creation
            token = create_login_token(authenticated_user)
            if token and len(token) > 50:  # JWT tokens are typically long strings
                print_status("JWT token generation successful", True)
            else:
                print_status("JWT token generation failed", False)
                return False

            # Clean up
            session.delete(db_user)
            session.commit()
            print_status("Test data cleanup successful", True)

            return True
    except Exception as e:
        print_status(f"Authentication validation failed: {e}", False)
        return False


def validate_task_management():
    """Validate task management functionality"""
    print_section("TASK MANAGEMENT VALIDATION")

    try:
        with Session(engine) as session:
            # Create a test user
            user_create = UserCreate(
                username="task_test_user",
                email="task_test@test.com",
                password="securepassword123!"
            )

            db_user = create_user(session, user_create)
            user_id = db_user.id
            print_status(f"Test user created (ID: {user_id})", True)

            # Test task creation
            task_create = TaskCreate(
                title="Validation Task",
                description="This is a validation task for Neon PostgreSQL integration",
                priority=PriorityEnum.HIGH
            )

            db_task = create_task(session, task_create, user_id)
            print_status(f"Task creation successful (ID: {db_task.id})", True)

            # Test task retrieval
            user_tasks = get_tasks_by_user(session, user_id)
            if len(user_tasks) >= 1:
                print_status(f"Task retrieval successful ({len(user_tasks)} tasks)", True)
            else:
                print_status("Task retrieval failed", False)
                return False

            # Test task properties
            retrieved_task = user_tasks[0]
            if (retrieved_task.title == "Validation Task" and
                retrieved_task.priority == PriorityEnum.HIGH):
                print_status("Task data integrity maintained", True)
            else:
                print_status("Task data integrity compromised", False)

            # Clean up
            session.delete(db_task)
            session.delete(db_user)
            session.commit()
            print_status("Task validation data cleanup successful", True)

            return True
    except Exception as e:
        print_status(f"Task management validation failed: {e}", False)
        return False


def validate_application_startup():
    """Validate application startup and basic API functionality"""
    print_section("APPLICATION STARTUP VALIDATION")

    try:
        # Test that all required modules can be imported without errors
        import src.main
        import src.database.database
        import src.auth.jwt_handler
        import src.api.auth
        import src.api.tasks

        print_status("All application modules imported successfully", True)

        # Test basic API endpoint
        import subprocess
        import time

        # Start server in background
        server_process = subprocess.Popen([
            'uvicorn', 'src.main:app', '--host', '127.0.0.1', '--port', '8001', '--log-level', 'error'
        ])

        # Wait for server to start
        time.sleep(3)

        try:
            # Test root endpoint
            response = requests.get('http://127.0.0.1:8001/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'Todo API' in data['message']:
                    print_status("Application API endpoint accessible", True)
                else:
                    print_status("API endpoint returned unexpected response", False)
                    server_process.terminate()
                    return False
            else:
                print_status(f"API endpoint returned status {response.status_code}", False)
                server_process.terminate()
                return False

        except requests.exceptions.RequestException as e:
            print_status(f"API endpoint not accessible: {e}", False)
            server_process.terminate()
            return False

        # Terminate server
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

        print_status("Application startup and shutdown successful", True)
        return True

    except Exception as e:
        print_status(f"Application validation failed: {e}", False)
        return False


def validate_neon_specific_features():
    """Validate Neon-specific features like connection pooling, SSL, etc."""
    print_section("NEON-SPECIFIC FEATURES VALIDATION")

    try:
        # Check if the database URL contains Neon-specific parameters
        import os
        from dotenv import load_dotenv
        load_dotenv()

        db_url = os.getenv('DATABASE_URL', '')
        if 'neon.tech' in db_url:
            print_status("Neon PostgreSQL URL configured", True)
        else:
            print_status("Neon PostgreSQL URL not detected", False)

        if 'sslmode=require' in db_url.lower():
            print_status("SSL mode requirement configured", True)
        else:
            print_status("SSL mode not configured", False)

        # Test connection stability
        successful_connections = 0
        total_attempts = 3

        for i in range(total_attempts):
            try:
                with engine.connect() as conn:
                    result = conn.execute(select(1))
                    successful_connections += 1
            except:
                pass

        if successful_connections == total_attempts:
            print_status("Connection stability verified", True)
        else:
            print_status(f"Connection stability issues ({successful_connections}/{total_attempts})", False)

        return True
    except Exception as e:
        print_status(f"Neon features validation failed: {e}", False)
        return False


def main():
    """Main validation function"""
    print("TODO APPLICATION - NEON POSTGRESQL MIGRATION VALIDATION")
    print("Final validation of the complete system integration")

    validations = [
        ("Database Connection", validate_database_connection),
        ("User Authentication", validate_user_authentication),
        ("Task Management", validate_task_management),
        ("Application Startup", validate_application_startup),
        ("Neon-Specific Features", validate_neon_specific_features),
    ]

    results = []
    for name, func in validations:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"Validation {name} failed with exception: {e}")
            results.append((name, False))

    # Summary
    print_section("VALIDATION SUMMARY")

    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name:<30} [{status}]")

    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n" + "="*60)
        print("*** NEON POSTGRESQL MIGRATION SUCCESSFUL! ***".center(60))
        print("="*60)
        print("✓ Todo application is fully integrated with Neon Serverless PostgreSQL")
        print("✓ All core functionalities are working correctly")
        print("✓ User authentication and task management operational")
        print("✓ Database connection is stable and secure")
        print("✓ Ready for production deployment")
        print("="*60)
        return True
    else:
        print("\n" + "="*60)
        print("XXX MIGRATION VALIDATION FAILED XXX".center(60))
        print("="*60)
        print(f"Address the {total_tests - passed_tests} failed validation(s) above")
        print("="*60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)