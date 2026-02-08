from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize security scheme
security = HTTPBearer()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hash for a plain password.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new access token with the provided data.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify the JWT token and return the payload if valid.

    Args:
        token: JWT token to verify

    Returns:
        Optional[Dict]: Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def decode_token_payload(token: str) -> Optional[Dict]:
    """
    Decode JWT token without verification (for debugging purposes).

    Args:
        token: JWT token to decode

    Returns:
        Optional[Dict]: Token payload if decodable, None otherwise
    """
    try:
        # This does not verify the signature, just decodes the payload
        payload = jwt.get_unverified_claims(token)
        return payload
    except JWTError:
        return None


def get_token_jti(token: str) -> Optional[str]:
    """
    Extract the JTI (JWT ID) from a token without verification.

    Args:
        token: JWT token to extract JTI from

    Returns:
        Optional[str]: JTI if found, None otherwise
    """
    try:
        payload = jwt.get_unverified_claims(token)
        return payload.get("jti")
    except Exception:
        return None


def get_current_user_from_token(token: str) -> Optional[Dict]:
    """
    Get user information from token without raising exceptions.

    Args:
        token: JWT token to extract user info from

    Returns:
        Optional[Dict]: User information if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "username": payload.get("username")
    }


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
    token = credentials.credentials

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "username": payload.get("username")
    }


def create_user_token(user_id: int, email: str, username: str) -> str:
    """
    Create a JWT token for a specific user.

    Args:
        user_id: User's unique identifier
        email: User's email address
        username: User's username

    Returns:
        str: JWT token for the user
    """
    data = {
        "sub": str(user_id),
        "email": email,
        "username": username,
        "iat": datetime.utcnow(),  # issued at time
        "type": "access"  # token type
    }

    return create_access_token(data)


def validate_user_token_for_access(token: str, requested_user_id: int) -> bool:
    """
    Validate that the user in the token has permission to access the requested user's data.

    Args:
        token: JWT token to validate
        requested_user_id: User ID that is being accessed

    Returns:
        bool: True if user has permission, False otherwise
    """
    user_info = get_current_user_from_token(token)
    if user_info is None:
        return False

    token_user_id = user_info.get("user_id")
    if token_user_id is None:
        return False

    # Compare token user ID with requested user ID
    return str(token_user_id) == str(requested_user_id)


__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "verify_token",
    "decode_token_payload",
    "get_current_user_from_token",
    "get_current_user",
    "create_user_token",
    "validate_user_token_for_access",
    "security"
]