from sqlmodel import Session
from contextlib import contextmanager
from typing import Generator
from .database import engine
from ..utils.logging import log_error


@contextmanager
def get_db_transaction() -> Generator[Session, None, None]:
    """
    Context manager for database transactions with automatic commit/rollback.

    Yields:
        Session: Database session with transaction handling
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        log_error(e, "Database transaction")
        raise
    finally:
        session.close()


def execute_in_transaction(func, *args, **kwargs):
    """
    Execute a function within a database transaction.

    Args:
        func: Function to execute within the transaction
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of the function execution

    Raises:
        Exception: If the function or transaction fails
    """
    with get_db_transaction() as session:
        try:
            return func(session, *args, **kwargs)
        except Exception as e:
            log_error(e, f"Transaction execution: {func.__name__}")
            raise


class TransactionManager:
    """
    Class to manage database transactions with context management.
    """
    def __init__(self):
        self.session = None

    def __enter__(self):
        self.session = Session(engine)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
        except Exception as e:
            log_error(e, "Transaction cleanup")
            # Still raise the original exception
            raise
        finally:
            self.session.close()


def atomic_transaction(func):
    """
    Decorator to wrap a function in a database transaction.

    Args:
        func: Function to wrap with transaction handling

    Returns:
        Wrapped function that executes within a transaction
    """
    def wrapper(*args, **kwargs):
        with get_db_transaction() as session:
            # Inject session as first argument if the function expects it
            if args and isinstance(args[0], Session):
                return func(session, *args[1:], **kwargs)
            else:
                return func(session, *args, **kwargs)
    return wrapper


# Async version for async operations
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_async_db_transaction() -> Generator[AsyncSession, None, None]:
    """
    Async context manager for database transactions with automatic commit/rollback.

    Yields:
        AsyncSession: Async database session with transaction handling
    """
    # Create async engine based on sync engine URL
    async_engine = create_async_engine(engine.url)
    async_session = AsyncSession(async_engine)

    try:
        yield async_session
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        log_error(e, "Async database transaction")
        raise
    finally:
        await async_session.close()


__all__ = [
    'get_db_transaction',
    'execute_in_transaction',
    'TransactionManager',
    'atomic_transaction',
    'get_async_db_transaction'
]