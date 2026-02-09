from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from typing import Dict
from ..database.database import engine
from ..models.user import User, UserCreate, UserRead, UserLogin
from ..services.auth_service import authenticate_user, create_user, create_login_token, get_user_by_email
from ..auth.jwt_handler import get_current_user
from datetime import timedelta
from ..services.session_service import create_session


def get_session():
    with Session(engine) as session:
        yield session

router = APIRouter()


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, request: Request, session: Session = Depends(get_session)) -> Dict[str, str]:
    """
    Register a new user and return access token for immediate login

    Args:
        user: User registration data
        request: HTTP request object
        session: Database session dependency

    Returns:
        Dict: Access token, token type, and user info

    Raises:
        HTTPException: If user already exists
    """
    # Check if user already exists by email
    existing_user = get_user_by_email(session, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Check if user already exists by username
    existing_username = session.exec(select(User).where(User.username == user.username)).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )

    # Create new user
    db_user = create_user(session, user)

    # Create access token for immediate login
    access_token, jti, token_hash, expires_at = create_login_token(db_user)

    # Create session record
    create_session(
        session=session,
        user_id=db_user.id,
        token_jti=jti,
        token=token_hash,  # Store the hash of the token
        expires_at=expires_at
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(db_user.id),
        "username": db_user.username,
        "email": db_user.email
    }


@router.post("/auth/login", response_model=Dict[str, str])
def login(form_data: UserLogin, request: Request, session: Session = Depends(get_session)) -> Dict[str, str]:
    """
    Login with email and password

    Args:
        form_data: User login data (email and password)
        request: HTTP request object
        session: Database session dependency

    Returns:
        Dict: Access token and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(session, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token, jti, token_hash, expires_at = create_login_token(user)

    # Create session record
    create_session(
        session=session,
        user_id=user.id,
        token_jti=jti,
        token=token_hash,  # Store the hash of the token
        expires_at=expires_at
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }


@router.post("/auth/token", response_model=Dict[str, str])  # Alternative login endpoint for JSON requests
def login_json(login_data: UserLogin, session: Session = Depends(get_session)) -> Dict[str, str]:
    """
    Login with email and password via JSON request

    Args:
        login_data: User login data (email and password) as JSON
        session: Database session dependency

    Returns:
        Dict: Access token and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(session, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token, jti, token_hash, expires_at = create_login_token(user)

    # Create session record
    create_session(
        session=session,
        user_id=user.id,
        token_jti=jti,
        token=token_hash,  # Store the hash of the token
        expires_at=expires_at
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }


@router.get("/auth/me", response_model=UserRead)
def read_users_me(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)) -> UserRead:
    """
    Get current user info

    Args:
        current_user: Currently authenticated user (from JWT token)
        session: Database session dependency

    Returns:
        UserRead: Current user's information

    Raises:
        HTTPException: If user is not found
    """
    user_id = int(current_user.get("user_id"))
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserRead.model_validate(user) if hasattr(UserRead, 'model_validate') else UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/auth/logout")
def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Logout user by revoking the current session

    Args:
        request: HTTP request object to extract the token
        current_user: Current authenticated user
        session: Database session dependency

    Returns:
        Dict: Success message
    """
    # Extract the token from the Authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[len("Bearer "):]

    # Get the JTI from the token
    from ..auth.jwt_handler import get_token_jti
    jti = get_token_jti(token)

    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Revoke only the session associated with this specific JTI
    from ..services.session_service import revoke_session_by_jti
    success = revoke_session_by_jti(session, jti)

    if not success:
        # Even if session wasn't found, we still return success
        # as the token is effectively invalidated
        pass

    return {"message": "Logout successful"}