"""
Execution watchdog for timeout protection.
Prevents requests from hanging indefinitely.
"""
import asyncio
import logging
from typing import Callable, Any, TypeVar, Coroutine
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TimeoutError(Exception):
    """Raised when execution exceeds timeout."""
    pass


async def with_timeout(
    coro: Coroutine[Any, Any, T],
    timeout_seconds: float,
    operation_name: str = "operation"
) -> T:
    """
    Execute coroutine with timeout protection.

    Args:
        coro: Coroutine to execute
        timeout_seconds: Maximum execution time
        operation_name: Name for logging

    Returns:
        Result from coroutine

    Raises:
        TimeoutError: If execution exceeds timeout
    """
    try:
        logger.debug(f"[WATCHDOG] Starting {operation_name} with {timeout_seconds}s timeout")
        result = await asyncio.wait_for(coro, timeout=timeout_seconds)
        logger.debug(f"[WATCHDOG] {operation_name} completed within timeout")
        return result

    except asyncio.TimeoutError:
        logger.error(
            f"[WATCHDOG] {operation_name} exceeded timeout of {timeout_seconds}s"
        )
        raise TimeoutError(
            f"{operation_name} exceeded timeout of {timeout_seconds}s"
        )


def timeout_protection(timeout_seconds: float = 30.0):
    """
    Decorator for async functions to add timeout protection.

    Usage:
        @timeout_protection(timeout_seconds=10.0)
        async def call_llm(prompt):
            return await llm.generate(prompt)
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            operation_name = func.__name__
            coro = func(*args, **kwargs)
            return await with_timeout(coro, timeout_seconds, operation_name)
        return wrapper
    return decorator


class ExecutionWatchdog:
    """
    Watchdog for monitoring and terminating long-running operations.

    Usage:
        watchdog = ExecutionWatchdog(timeout_seconds=30)

        async with watchdog.monitor("llm_call"):
            result = await call_llm()
    """

    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self.active_operations: dict[str, float] = {}

    class Monitor:
        """Context manager for monitoring an operation."""

        def __init__(self, watchdog: 'ExecutionWatchdog', operation_name: str):
            self.watchdog = watchdog
            self.operation_name = operation_name
            self.task = None

        async def __aenter__(self):
            logger.debug(
                f"[WATCHDOG] Monitoring {self.operation_name} "
                f"with {self.watchdog.timeout_seconds}s timeout"
            )
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_type is asyncio.TimeoutError:
                logger.error(
                    f"[WATCHDOG] {self.operation_name} timed out after "
                    f"{self.watchdog.timeout_seconds}s"
                )
                return False  # Re-raise timeout
            return False

    def monitor(self, operation_name: str) -> Monitor:
        """Create a monitor context for an operation."""
        return self.Monitor(self, operation_name)
