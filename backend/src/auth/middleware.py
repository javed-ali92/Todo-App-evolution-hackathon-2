from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from .jwt_handler import verify_token, get_current_user_from_token
from ..utils.logging import AuthorizationError
from functools import wraps

# Initialize security scheme
security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Get the current user from the JWT token in the Authorization header.

    Args:
        credentials: HTTP authorization credentials from request

    Returns:
        Dict: User information extracted from token

    Raises:
        HTTPException: If token is invalid or user information is missing
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    user_info = get_current_user_from_token(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_info


def require_same_user_or_admin(current_user: Dict = Depends(get_current_user)):
    """
    Dependency to check if the current user is accessing their own data or is an admin.

    Args:
        current_user: The currently authenticated user

    Returns:
        Dict: The current user information

    Raises:
        HTTPException: If the user is not authorized to access the resource
    """
    # For basic authorization, we just return the user
    # Additional checks can be added here if needed
    return current_user


def authorize_user_access(requested_user_id: int, current_user: Dict = Depends(get_current_user)) -> bool:
    """
    Authorize a user to access resources belonging to a specific user ID.
    This ensures users can only access their own data.

    Args:
        requested_user_id: The user ID that is being accessed
        current_user: The currently authenticated user

    Returns:
        bool: True if the user is authorized to access the requested resource

    Raises:
        HTTPException: If the user is not authorized
    """
    token_user_id = int(current_user.get("user_id"))

    # Check if the token user ID matches the requested user ID
    if token_user_id != requested_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - you can only access your own data"
        )

    return True