"""
Request tracing and instrumentation for debugging and monitoring.
Provides correlation ID tracking and stage-level performance metrics.
"""
import time
import uuid
import logging
from typing import Any, Dict, Optional
from contextvars import ContextVar
from functools import wraps

logger = logging.getLogger(__name__)

# Thread-safe request context storage
_request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
_request_traces: ContextVar[list] = ContextVar('request_traces', default=[])


class RequestTracer:
    """
    Request tracing utility for tracking execution through pipeline stages.

    Usage:
        tracer = RequestTracer.start()
        tracer.stage("auth", input={"user_id": 1}, output={"success": True})
        tracer.stage("llm", input={"prompt": "..."}, output={"response": "..."})
        report = tracer.report()
    """

    def __init__(self, request_id: str):
        self.request_id = request_id
        self.traces = []
        self.start_time = time.time()

    @classmethod
    def start(cls, request_id: Optional[str] = None) -> 'RequestTracer':
        """Start a new request trace with optional custom ID."""
        if not request_id:
            request_id = str(uuid.uuid4())[:8]

        tracer = cls(request_id)
        _request_id.set(request_id)
        _request_traces.set([])

        logger.info(f"[TRACE_START] request_id={request_id}")
        return tracer

    @classmethod
    def get_current_id(cls) -> Optional[str]:
        """Get current request ID from context."""
        return _request_id.get()

    def stage(
        self,
        stage_name: str,
        input_data: Any = None,
        output_data: Any = None,
        success: bool = True,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None
    ):
        """
        Record a pipeline stage execution.

        Args:
            stage_name: Name of the stage (e.g., "auth", "llm", "db")
            input_data: Input to this stage (will be truncated if large)
            output_data: Output from this stage (will be truncated if large)
            success: Whether stage succeeded
            error: Error message if failed
            latency_ms: Optional manual latency override
        """
        trace_entry = {
            "request_id": self.request_id,
            "stage": stage_name,
            "input": self._truncate(input_data),
            "output": self._truncate(output_data),
            "success": success,
            "error": error,
            "latency_ms": latency_ms if latency_ms else 0,
            "timestamp": time.time()
        }

        self.traces.append(trace_entry)

        status = "SUCCESS" if success else "FAILED"
        logger.info(
            f"[TRACE_STAGE] request_id={self.request_id} "
            f"stage={stage_name} status={status} "
            f"latency={latency_ms:.2f}ms" if latency_ms else ""
        )

        if error:
            logger.error(f"[TRACE_ERROR] request_id={self.request_id} stage={stage_name} error={error}")

    def report(self) -> Dict[str, Any]:
        """Generate execution report with all stages."""
        total_latency = (time.time() - self.start_time) * 1000

        report = {
            "request_id": self.request_id,
            "total_latency_ms": total_latency,
            "stages": self.traces,
            "success": all(t["success"] for t in self.traces),
            "failed_stage": next((t["stage"] for t in self.traces if not t["success"]), None)
        }

        logger.info(
            f"[TRACE_COMPLETE] request_id={self.request_id} "
            f"total_latency={total_latency:.2f}ms "
            f"stages={len(self.traces)} "
            f"success={report['success']}"
        )

        return report

    def _truncate(self, data: Any, max_len: int = 200) -> Any:
        """Truncate large data for logging."""
        if data is None:
            return None

        if isinstance(data, str):
            return data[:max_len] + "..." if len(data) > max_len else data

        if isinstance(data, dict):
            return {k: self._truncate(v, max_len=100) for k, v in list(data.items())[:5]}

        if isinstance(data, list):
            return [self._truncate(item, max_len=100) for item in data[:3]]

        return str(data)[:max_len]


def trace_stage(stage_name: str):
    """
    Decorator to automatically trace a function as a pipeline stage.

    Usage:
        @trace_stage("auth")
        def authenticate(user_id):
            return {"valid": True}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = RequestTracer.get_current_id()
            if not request_id:
                # No active trace, execute normally
                return func(*args, **kwargs)

            start = time.time()
            try:
                result = func(*args, **kwargs)
                latency = (time.time() - start) * 1000

                # Try to get tracer from context and log stage
                logger.info(
                    f"[TRACE_STAGE] request_id={request_id} "
                    f"stage={stage_name} status=SUCCESS latency={latency:.2f}ms"
                )

                return result

            except Exception as e:
                latency = (time.time() - start) * 1000
                logger.error(
                    f"[TRACE_STAGE] request_id={request_id} "
                    f"stage={stage_name} status=FAILED latency={latency:.2f}ms "
                    f"error={type(e).__name__}: {str(e)[:200]}"
                )
                raise

        return wrapper
    return decorator
