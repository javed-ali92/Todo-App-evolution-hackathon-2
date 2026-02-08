import logging
from fastapi import HTTPException
from typing import Any, Dict, Optional
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.

    Args:
        name: Name of the logger
        level: Logging level (default: INFO)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding multiple handlers to the same logger
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_api_call(endpoint: str, method: str, user_id: str = None, status_code: int = None):
    """
    Log API call information.

    Args:
        endpoint: API endpoint that was called
        method: HTTP method used
        user_id: ID of the user making the call (if authenticated)
        status_code: HTTP status code of the response
    """
    user_info = f"User: {user_id}" if user_id else "User: anonymous"
    status_info = f"Status: {status_code}" if status_code else ""

    logger.info(f"API Call - {method} {endpoint} | {user_info} | {status_info}")


def log_error(error: Exception, context: str = ""):
    """
    Log error information.

    Args:
        error: Exception that occurred
        context: Additional context about where the error occurred
    """
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)


def create_error_response(
    error: str,
    message: str,
    code: Optional[str] = None,
    details: Optional[Dict] = None,
    status_code: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        error: Error type/identifier
        message: Human-readable error message
        code: Optional error code
        details: Optional additional error details
        status_code: HTTP status code associated with the error

    Returns:
        Dictionary with standardized error response format
    """
    response = {
        "error": error,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

    if code:
        response["code"] = code

    if status_code:
        response["status_code"] = status_code

    if details:
        response["details"] = details

    return response


class AppException(HTTPException):
    """
    Custom application exception that extends FastAPI's HTTPException.
    """
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.timestamp = datetime.utcnow()

    def get_error_response(self) -> Dict[str, Any]:
        """
        Get standardized error response for this exception.

        Returns:
            Standardized error response dictionary
        """
        return create_error_response(
            error=self.__class__.__name__,
            message=self.detail,
            code=self.error_code,
            status_code=self.status_code
        )


class ValidationError(AppException):
    """
    Exception for validation errors.
    """
    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR", field_errors: Dict[str, str] = None):
        super().__init__(status_code=400, detail=detail, error_code=error_code)
        self.field_errors = field_errors

    def get_error_response(self) -> Dict[str, Any]:
        """
        Get standardized error response for validation errors.

        Returns:
            Standardized error response dictionary with field errors if available
        """
        response = super().get_error_response()
        if self.field_errors:
            response["details"] = {"field_errors": self.field_errors}
        return response


class AuthenticationError(AppException):
    """
    Exception for authentication errors.
    """
    def __init__(self, detail: str = "Authentication failed", error_code: str = "AUTH_ERROR"):
        super().__init__(status_code=401, detail=detail, error_code=error_code)


class AuthorizationError(AppException):
    """
    Exception for authorization errors.
    """
    def __init__(self, detail: str = "Access denied", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(status_code=403, detail=detail, error_code=error_code)


class NotFoundError(AppException):
    """
    Exception for not found errors.
    """
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND_ERROR"):
        super().__init__(status_code=404, detail=detail, error_code=error_code)


class ConflictError(AppException):
    """
    Exception for conflict errors.
    """
    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT_ERROR"):
        super().__init__(status_code=409, detail=detail, error_code=error_code)


class DatabaseError(AppException):
    """
    Exception for database errors.
    """
    def __init__(self, detail: str = "Database error occurred", error_code: str = "DATABASE_ERROR"):
        super().__init__(status_code=500, detail=detail, error_code=error_code)


class ServiceUnavailableError(AppException):
    """
    Exception for service unavailable errors.
    """
    def __init__(self, detail: str = "Service temporarily unavailable", error_code: str = "SERVICE_UNAVAILABLE_ERROR"):
        super().__init__(status_code=503, detail=detail, error_code=error_code)


def handle_exception(exc: Exception, context: str = "") -> AppException:
    """
    Handle an exception and convert it to an appropriate AppException.

    Args:
        exc: Exception to handle
        context: Context where the exception occurred

    Returns:
        AppException instance
    """
    log_error(exc, context)

    if isinstance(exc, AppException):
        return exc

    # Convert common exceptions to appropriate AppExceptions
    if isinstance(exc, ValueError):
        return ValidationError(str(exc))
    elif isinstance(exc, PermissionError):
        return AuthorizationError(str(exc))
    elif isinstance(exc, KeyError):
        return NotFoundError(f"Key not found: {str(exc)}")
    else:
        return AppException(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")