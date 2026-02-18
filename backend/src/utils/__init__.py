"""
Production-grade utilities for self-healing agent system.

Modules:
- request_tracer: Request correlation and stage tracing
- circuit_breaker: Fault tolerance for LLM providers
- execution_watchdog: Timeout protection
- config_factory: Immutable configuration factory
- token_protection: Token overflow prevention
"""
from .request_tracer import RequestTracer, trace_stage
from .circuit_breaker import CircuitBreaker, CircuitBreakerRegistry, CircuitBreakerConfig
from .execution_watchdog import ExecutionWatchdog, timeout_protection, with_timeout, TimeoutError
from .config_factory import ImmutableConfigFactory
from .token_protection import TokenOverflowProtection, get_token_protector

__all__ = [
    'RequestTracer',
    'trace_stage',
    'CircuitBreaker',
    'CircuitBreakerRegistry',
    'CircuitBreakerConfig',
    'ExecutionWatchdog',
    'timeout_protection',
    'with_timeout',
    'TimeoutError',
    'ImmutableConfigFactory',
    'TokenOverflowProtection',
    'get_token_protector',
]
