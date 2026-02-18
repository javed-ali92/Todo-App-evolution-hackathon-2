"""
Circuit breaker pattern for LLM provider fault tolerance.
Prevents cascading failures by temporarily disabling failing providers.
"""
import time
import logging
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout_seconds: int = 60   # Time before trying half-open


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.

    Usage:
        breaker = CircuitBreaker("gemini_llm")

        if breaker.can_execute():
            try:
                result = call_llm()
                breaker.record_success()
            except Exception as e:
                breaker.record_failure()
                raise
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = Lock()

        logger.info(
            f"[CIRCUIT_BREAKER] Initialized {name} "
            f"failure_threshold={self.config.failure_threshold} "
            f"timeout={self.config.timeout_seconds}s"
        )

    def can_execute(self) -> bool:
        """Check if execution is allowed based on circuit state."""
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                # Check if timeout has elapsed
                if self._should_attempt_reset():
                    logger.info(f"[CIRCUIT_BREAKER] {self.name} transitioning to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    return True

                logger.warning(f"[CIRCUIT_BREAKER] {self.name} is OPEN, rejecting request")
                return False

            if self.state == CircuitState.HALF_OPEN:
                # Allow limited requests to test recovery
                return True

            return False

    def record_success(self):
        """Record successful execution."""
        with self.lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.info(
                    f"[CIRCUIT_BREAKER] {self.name} success in HALF_OPEN "
                    f"({self.success_count}/{self.config.success_threshold})"
                )

                if self.success_count >= self.config.success_threshold:
                    logger.info(f"[CIRCUIT_BREAKER] {self.name} transitioning to CLOSED (recovered)")
                    self.state = CircuitState.CLOSED
                    self.success_count = 0

    def record_failure(self, error: Optional[Exception] = None):
        """Record failed execution."""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            error_msg = f"{type(error).__name__}: {str(error)[:100]}" if error else "unknown"

            if self.state == CircuitState.HALF_OPEN:
                logger.warning(
                    f"[CIRCUIT_BREAKER] {self.name} failed in HALF_OPEN, "
                    f"reopening circuit. Error: {error_msg}"
                )
                self.state = CircuitState.OPEN
                self.success_count = 0
                return

            if self.state == CircuitState.CLOSED:
                logger.warning(
                    f"[CIRCUIT_BREAKER] {self.name} failure "
                    f"({self.failure_count}/{self.config.failure_threshold}). "
                    f"Error: {error_msg}"
                )

                if self.failure_count >= self.config.failure_threshold:
                    logger.error(
                        f"[CIRCUIT_BREAKER] {self.name} threshold exceeded, "
                        f"opening circuit for {self.config.timeout_seconds}s"
                    )
                    self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.timeout_seconds

    def get_state(self) -> dict:
        """Get current circuit breaker state for monitoring."""
        with self.lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time
            }

    def reset(self):
        """Manually reset circuit breaker to closed state."""
        with self.lock:
            logger.info(f"[CIRCUIT_BREAKER] {self.name} manually reset to CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None


class CircuitBreakerRegistry:
    """Global registry for managing multiple circuit breakers."""

    _breakers: dict[str, CircuitBreaker] = {}
    _lock = Lock()

    @classmethod
    def get_or_create(
        cls,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get existing breaker or create new one."""
        with cls._lock:
            if name not in cls._breakers:
                cls._breakers[name] = CircuitBreaker(name, config)
            return cls._breakers[name]

    @classmethod
    def get_all_states(cls) -> dict[str, dict]:
        """Get states of all registered circuit breakers."""
        with cls._lock:
            return {
                name: breaker.get_state()
                for name, breaker in cls._breakers.items()
            }
