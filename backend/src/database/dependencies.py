from sqlmodel import Session
from fastapi import Depends
from .database import engine


def get_session():
    """
    Dependency function to get database session.

    Yields:
        Session: Database session that will be automatically closed
    """
    with Session(engine) as session:
        yield session


# Alias for cleaner imports
DatabaseSessionDep = Depends(get_session)