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
    # Use PORT environment variable with fallback to 7860 for Hugging Face Spaces
    port = int(os.getenv("PORT", 7860))

    print(f"Starting Todo API server on http://localhost:{port}...")
    print("Available endpoints:")
    print(f"- GET  http://localhost:{port}/ (Root)")
    print(f"- GET  http://localhost:{port}/docs (API Documentation)")
    print("")
    print("Authentication endpoints:")
    print(f"- POST http://localhost:{port}/api/auth/register (User Registration)")
    print(f"- POST http://localhost:{port}/api/auth/login (User Login - FORM DATA)")
    print(f"- GET  http://localhost:{port}/api/auth/me (Get Current User)")
    print("")
    print("Task endpoints:")
    print(f"- GET    http://localhost:{port}/api/{{user_id}}/tasks (Get user's tasks)")
    print(f"- POST   http://localhost:{port}/api/{{user_id}}/tasks (Create task)")
    print(f"- GET    http://localhost:{port}/api/{{user_id}}/tasks/{{id}} (Get specific task)")
    print(f"- PUT    http://localhost:{port}/api/{{user_id}}/tasks/{{id}} (Update task)")
    print(f"- DELETE http://localhost:{port}/api/{{user_id}}/tasks/{{id}} (Delete task)")
    print(f"- PATCH  http://localhost:{port}/api/{{user_id}}/tasks/{{id}}/complete (Toggle completion)")
    print("")
    print("Note: Most endpoints require authentication via JWT token in Authorization header")
    print("Example: Authorization: Bearer <your-jwt-token>")
    print("")
    print("Server starting...")

    try:
        from src.main import app
        # Use PORT environment variable with fallback to 7860 for Hugging Face Spaces
        port = int(os.getenv("PORT", 7860))
        print(f"Starting server on port {port}...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()