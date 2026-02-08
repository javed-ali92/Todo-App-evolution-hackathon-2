#!/usr/bin/env python3
"""
Script to start the Todo API server with Neon PostgreSQL
"""
import uvicorn
from src.main import app

if __name__ == "__main__":
    print("Starting Todo API server...")
    print("Available endpoints:")
    print("- GET  http://localhost:8000/ (Root)")
    print("- GET  http://localhost:8000/docs (API Documentation)")
    print("- GET  http://localhost:8000/redoc (Alternative API Documentation)")
    print("")
    print("Authentication endpoints (with /api prefix):")
    print("- POST http://localhost:8000/api/auth/register (User Registration)")
    print("- POST http://localhost:8000/api/auth/login (User Login)")
    print("- GET  http://localhost:8000/api/auth/me (Get Current User)")
    print("- POST http://localhost:8000/api/auth/logout (Logout)")
    print("")
    print("Task endpoints (with /api prefix):")
    print("- GET    http://localhost:8000/api/{user_id}/tasks (Get user's tasks)")
    print("- POST   http://localhost:8000/api/{user_id}/tasks (Create task)")
    print("- GET    http://localhost:8000/api/{user_id}/tasks/{id} (Get specific task)")
    print("- PUT    http://localhost:8000/api/{user_id}/tasks/{id} (Update task)")
    print("- DELETE http://localhost:8000/api/{user_id}/tasks/{id} (Delete task)")
    print("- PATCH  http://localhost:8000/api/{user_id}/tasks/{id}/complete (Toggle completion)")
    print("")
    print("Note: Most endpoints require authentication via JWT token in Authorization header")
    print("Example: Authorization: Bearer <your-jwt-token>")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)