"""Custom exceptions for the Jules Agent SDK."""

from typing import Optional, Dict, Any


class JulesAPIError(Exception):
    """Base exception for all Jules API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code
            response: API response data
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class JulesAuthenticationError(JulesAPIError):
    """Raised when authentication fails (401)."""

    pass


class JulesNotFoundError(JulesAPIError):
    """Raised when a resource is not found (404)."""

    pass


class JulesValidationError(JulesAPIError):
    """Raised when request validation fails (400)."""

    pass


class JulesRateLimitError(JulesAPIError):
    """Raised when rate limit is exceeded (429)."""

    pass


class JulesServerError(JulesAPIError):
    """Raised when server returns 5xx error."""

    pass
