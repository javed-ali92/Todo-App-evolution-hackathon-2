"""
Authentication module initialization for the Todo application.
Exports key authentication functions and classes.
"""
from .jwt_handler import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user,
    validate_user_token_for_access,
    security
)

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "verify_token",
    "get_current_user",
    "validate_user_token_for_access",
    "security"
]