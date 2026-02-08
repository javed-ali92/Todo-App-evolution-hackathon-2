#!/usr/bin/env python3
"""
Script to start the Todo API server with Neon PostgreSQL
This version includes error handling and proper startup
"""
import uvicorn
import sys
import os
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("Starting Todo API server on http://localhost:8000...")
    print("Available endpoints:")
    print("- GET  http://localhost:8000/ (Root)")
    print("- GET  http://localhost:8000/docs (API Documentation)")
    print("")
    print("Authentication endpoints:")
    print("- POST http://localhost:8000/api/auth/register (User Registration)")
    print("- POST http://localhost:8000/api/auth/login (User Login - FORM DATA)")
    print("- GET  http://localhost:8000/api/auth/me (Get Current User)")
    print("")
    print("Task endpoints:")
    print("- GET    http://localhost:8000/api/{user_id}/tasks (Get user's tasks)")
    print("- POST   http://localhost:8000/api/{user_id}/tasks (Create task)")
    print("- GET    http://localhost:8000/api/{user_id}/tasks/{id} (Get specific task)")
    print("- PUT    http://localhost:8000/api/{user_id}/tasks/{id} (Update task)")
    print("- DELETE http://localhost:8000/api/{user_id}/tasks/{id} (Delete task)")
    print("- PATCH  http://localhost:8000/api/{user_id}/tasks/{id}/complete (Toggle completion)")
    print("")
    print("Note: Most endpoints require authentication via JWT token in Authorization header")
    print("Example: Authorization: Bearer <your-jwt-token>")
    print("")
    print("Server starting...")

    try:
        from src.main import app
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()