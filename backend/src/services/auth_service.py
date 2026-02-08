from sqlmodel import Session, select
from passlib.context import CryptContext
from typing import Optional
from ..models.user import User, UserCreate
from ..auth.jwt_handler import create_access_token, get_password_hash, get_token_jti
from datetime import timedelta, datetime
from ..models.session import Session as SessionModel
from .session_service import create_session
import secrets
import hashlib

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password

    Args:
        session: Database session
        email: User's email address
        password: User's plain text password

    Returns:
        Optional[User]: Authenticated user if credentials are valid, None otherwise
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user or not verify_password(password, user.hashed_password):
        return None

    return user


def create_user(session: Session, user_create: UserCreate) -> User:
    """
    Create a new user with hashed password

    Args:
        session: Database session
        user_create: User creation data

    Returns:
        User: The created user object
    """
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def create_login_token(user: User) -> tuple[str, str, str, datetime]:
    """
    Create an access token for the authenticated user

    Args:
        user: Authenticated user object

    Returns:
        tuple: (token, jti, token_hash, expires_at)
    """
    data = {
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
        "iat": datetime.utcnow()  # issued at time
    }

    # Generate a random JTI
    jti = secrets.token_urlsafe(32)
    data["jti"] = jti

    token = create_access_token(
        data=data,
        expires_delta=timedelta(minutes=30)
    )

    # Hash the token for storage
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    return token, jti, token_hash, expires_at


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Get a user by their email address

    Args:
        session: Database session
        email: User's email address

    Returns:
        Optional[User]: User if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """
    Get a user by their ID

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        Optional[User]: User if found, None otherwise
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user