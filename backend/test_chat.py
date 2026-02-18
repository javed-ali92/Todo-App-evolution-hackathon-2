#!/usr/bin/env python3
"""Test script to generate JWT token and test chatbot."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth.jwt_handler import create_user_token

# Generate token for existing user (user_id=77 exists in database based on logs)
token = create_user_token(user_id=77, email="test@example.com", username="testuser")
print(f"JWT Token: {token}")
print(f"\nTest with curl:")
print(f'curl -X POST http://localhost:8001/api/77/chat \\')
print(f'  -H "Content-Type: application/json" \\')
print(f'  -H "Authorization: Bearer {token}" \\')
print(f'  -d \'{{"message": "Add task buy milk", "conversation_id": null}}\'')
