from sqlmodel import Session, select
from typing import Optional
from datetime import datetime, timedelta
from ..models.session import Session as SessionModel, SessionCreate, SessionUpdate
import secrets
import hashlib


def create_session(session: Session, user_id: int, token_jti: str, token: str, expires_at: datetime) -> SessionModel:
    """
    Create a new session for a user

    Args:
        session: Database session
        user_id: User ID for whom to create the session
        token_jti: JWT ID for the token
        token: Session token
        expires_at: Expiration time for the session

    Returns:
        SessionModel: The created session
    """
    # Create session object
    session_obj = SessionModel(
        user_id=user_id,
        token_jti=token_jti,
        token=token,
        expires_at=expires_at
    )

    session.add(session_obj)
    session.commit()
    session.refresh(session_obj)

    return session_obj


def get_session_by_token(session: Session, token: str) -> Optional[SessionModel]:
    """
    Get a session by its token

    Args:
        session: Database session
        token: Session token to look up

    Returns:
        Optional[SessionModel]: Session if found and not expired, None otherwise
    """
    session_obj = session.exec(
        select(SessionModel).where(
            SessionModel.token == token
        )
    ).first()

    # Check if session exists, hasn't expired, and isn't revoked
    if session_obj and session_obj.expires_at > datetime.utcnow() and not session_obj.revoked:
        # Update last_used_at
        session_obj.last_used_at = datetime.utcnow()
        session.add(session_obj)
        session.commit()
        return session_obj

    return None


def get_session_by_jti(session: Session, jti: str) -> Optional[SessionModel]:
    """
    Get a session by its JTI (JWT ID)

    Args:
        session: Database session
        jti: JWT ID to look up

    Returns:
        Optional[SessionModel]: Session if found and not expired, None otherwise
    """
    session_obj = session.exec(
        select(SessionModel).where(
            SessionModel.token_jti == jti
        )
    ).first()

    # Check if session exists, hasn't expired, and isn't revoked
    if session_obj and session_obj.expires_at > datetime.utcnow() and not session_obj.revoked:
        # Update last_used_at
        session_obj.last_used_at = datetime.utcnow()
        session.add(session_obj)
        session.commit()
        return session_obj

    return None


def get_sessions_by_user(session: Session, user_id: int) -> list[SessionModel]:
    """
    Get all sessions for a specific user

    Args:
        session: Database session
        user_id: User ID to get sessions for

    Returns:
        list[SessionModel]: List of active sessions for the user
    """
    sessions = session.exec(
        select(SessionModel).where(
            SessionModel.user_id == user_id
        )
    ).all()

    # Filter out expired sessions
    active_sessions = []
    current_time = datetime.utcnow()
    for s in sessions:
        if s.expires_at > current_time:
            active_sessions.append(s)

    return active_sessions


def delete_session(session: Session, token: str) -> bool:
    """
    Delete a session by its token

    Args:
        session: Database session
        token: Session token to delete

    Returns:
        bool: True if session was deleted, False if not found
    """
    session_obj = session.exec(
        select(SessionModel).where(
            SessionModel.token == token
        )
    ).first()

    if session_obj:
        session.delete(session_obj)
        session.commit()
        return True

    return False


def revoke_session_by_token(session: Session, token: str) -> bool:
    """
    Revoke a session by its token by marking it as revoked

    Args:
        session: Database session
        token: Session token to revoke

    Returns:
        bool: True if session was revoked, False if not found
    """
    session_obj = session.exec(
        select(SessionModel).where(
            SessionModel.token == token
        )
    ).first()

    if session_obj:
        session_obj.revoked = True
        session_obj.revoked_at = datetime.utcnow()
        session.add(session_obj)
        session.commit()
        return True

    return False


def revoke_session_by_jti(session: Session, jti: str) -> bool:
    """
    Revoke a session by its JTI (JWT ID) by marking it as revoked

    Args:
        session: Database session
        jti: JWT ID to revoke

    Returns:
        bool: True if session was revoked, False if not found
    """
    session_obj = session.exec(
        select(SessionModel).where(
            SessionModel.token_jti == jti
        )
    ).first()

    if session_obj:
        session_obj.revoked = True
        session_obj.revoked_at = datetime.utcnow()
        session.add(session_obj)
        session.commit()
        return True

    return False


def delete_sessions_by_user(session: Session, user_id: int) -> int:
    """
    Delete all sessions for a specific user

    Args:
        session: Database session
        user_id: User ID whose sessions to delete

    Returns:
        int: Number of sessions deleted
    """
    sessions = session.exec(
        select(SessionModel).where(
            SessionModel.user_id == user_id
        )
    ).all()

    deleted_count = 0
    current_time = datetime.utcnow()
    for s in sessions:
        if s.expires_at > current_time:  # Only delete active sessions
            session.delete(s)
            deleted_count += 1

    session.commit()
    return deleted_count


def cleanup_expired_sessions(session: Session) -> int:
    """
    Remove all expired sessions from the database

    Args:
        session: Database session

    Returns:
        int: Number of expired sessions removed
    """
    expired_sessions = session.exec(
        select(SessionModel).where(
            SessionModel.expires_at < datetime.utcnow()
        )
    ).all()

    deleted_count = 0
    for expired_session in expired_sessions:
        session.delete(expired_session)
        deleted_count += 1

    session.commit()
    return deleted_count


def invalidate_user_sessions(session: Session, user_id: int) -> int:
    """
    Invalidate all sessions for a specific user (used for security purposes)

    Args:
        session: Database session
        user_id: User ID whose sessions to invalidate

    Returns:
        int: Number of sessions invalidated
    """
    return delete_sessions_by_user(session, user_id)


def extend_session_expiration(session: Session, token: str, additional_minutes: int = 30) -> bool:
    """
    Extend a session's expiration time

    Args:
        session: Database session
        token: Session token to extend
        additional_minutes: Number of minutes to add to current expiration

    Returns:
        bool: True if session was extended, False if not found
    """
    session_obj = get_session_by_token(session, token)
    if session_obj:
        session_obj.expires_at = session_obj.expires_at + timedelta(minutes=additional_minutes)
        session.add(session_obj)
        session.commit()
        return True

    return False