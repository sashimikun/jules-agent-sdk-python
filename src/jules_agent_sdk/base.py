"""Base HTTP client for Jules API with retries, timeouts, and logging."""

import time
import logging
import json
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from jules_agent_sdk.exceptions import (
    JulesAPIError,
    JulesAuthenticationError,
    JulesNotFoundError,
    JulesValidationError,
    JulesRateLimitError,
    JulesServerError,
)

logger = logging.getLogger(__name__)


# Default configuration constants
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_FACTOR = 1.0
DEFAULT_MAX_BACKOFF = 10.0


class BaseClient:
    """Base HTTP client for making requests to Jules API.

    Features:
    - Automatic retries with exponential backoff
    - Configurable timeouts
    - Comprehensive logging
    - Rate limit handling
    - Connection pooling
    """

    BASE_URL = "https://jules.googleapis.com/v1alpha"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
    ) -> None:
        """Initialize the base client.

        Args:
            api_key: Jules API key for authentication
            base_url: Optional custom base URL (defaults to official API endpoint)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff_factor: Backoff factor for retries (exponential)
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor

        # Statistics
        self.request_count = 0
        self.error_count = 0

        # Create session with connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "X-Goog-Api-Key": self.api_key,
            "User-Agent": "jules-agent-sdk/0.1.0 (Python)",
        })

        # Configure connection pool
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0,  # We handle retries manually
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(f"Initialized Jules API client (base_url={self.base_url})")

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if request should be retried.

        Args:
            exception: The exception that occurred
            attempt: Current attempt number (1-indexed)

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False

        # Retry on network errors
        if isinstance(exception, (ConnectionError, Timeout)):
            logger.warning(f"Network error on attempt {attempt}, will retry: {exception}")
            return True

        # Retry on 5xx errors
        if isinstance(exception, JulesServerError):
            logger.warning(f"Server error on attempt {attempt}, will retry: {exception}")
            return True

        # Don't retry on client errors (4xx)
        return False

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time for retry.

        Args:
            attempt: Current attempt number (1-indexed)

        Returns:
            Backoff time in seconds
        """
        backoff = min(
            self.retry_backoff_factor * (2 ** (attempt - 1)),
            DEFAULT_MAX_BACKOFF,
        )
        logger.debug(f"Backoff for attempt {attempt}: {backoff}s")
        return backoff

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Handle rate limit response.

        Args:
            response: HTTP response with 429 status

        Raises:
            JulesRateLimitError: With retry information
        """
        retry_after = response.headers.get("Retry-After")
        retry_info = {}

        if retry_after:
            try:
                retry_info["retry_after_seconds"] = int(retry_after)
                logger.warning(f"Rate limited. Retry after {retry_after} seconds")
            except ValueError:
                logger.warning(f"Rate limited. Invalid Retry-After header: {retry_after}")

        error_msg = "Rate limit exceeded"
        if retry_info.get("retry_after_seconds"):
            error_msg += f". Retry after {retry_info['retry_after_seconds']} seconds"

        raise JulesRateLimitError(error_msg, 429, retry_info)

    def _handle_error(self, response: requests.Response) -> None:
        """Handle HTTP error responses.

        Args:
            response: HTTP response object

        Raises:
            JulesAuthenticationError: For 401 errors
            JulesNotFoundError: For 404 errors
            JulesValidationError: For 400 errors
            JulesRateLimitError: For 429 errors
            JulesServerError: For 5xx errors
            JulesAPIError: For other errors
        """
        # Special handling for rate limits
        if response.status_code == 429:
            self._handle_rate_limit(response)
            return

        # Parse error response
        try:
            error_data = response.json()
        except (ValueError, json.JSONDecodeError) as e:
            logger.debug(f"Failed to parse error response as JSON: {e}")
            error_data = {"error": {"message": response.text}}

        error_msg = error_data.get("error", {}).get("message", response.text)

        # Log error
        logger.error(
            f"API error: {response.status_code} - {error_msg}",
            extra={
                "status_code": response.status_code,
                "url": response.url,
                "response": error_data,
            },
        )

        # Raise appropriate exception
        if response.status_code == 401:
            raise JulesAuthenticationError(error_msg, response.status_code, error_data)
        elif response.status_code == 404:
            raise JulesNotFoundError(error_msg, response.status_code, error_data)
        elif response.status_code == 400:
            raise JulesValidationError(error_msg, response.status_code, error_data)
        elif response.status_code >= 500:
            raise JulesServerError(error_msg, response.status_code, error_data)
        else:
            raise JulesAPIError(error_msg, response.status_code, error_data)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Jules API with retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json: JSON request body

        Returns:
            API response as dictionary

        Raises:
            JulesAPIError: On API error
            Timeout: On timeout
            ConnectionError: On connection error
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.request_count += 1

        logger.debug(f"Request: {method} {path}", extra={"params": params, "json": json})

        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                # Make request with timeout
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                )

                logger.debug(
                    f"Response: {response.status_code}",
                    extra={"attempt": attempt, "status": response.status_code},
                )

                # Handle errors
                if not response.ok:
                    try:
                        self._handle_error(response)
                    except JulesAPIError as e:
                        self.error_count += 1
                        if self._should_retry(e, attempt):
                            last_exception = e
                            time.sleep(self._calculate_backoff(attempt))
                            continue
                        raise

                # Handle empty responses
                if response.status_code == 204 or not response.content:
                    return {}

                # Parse and return JSON
                try:
                    return response.json()
                except (ValueError, json.JSONDecodeError) as e:
                    logger.error(f"Failed to parse response as JSON: {e}")
                    raise JulesAPIError(f"Invalid JSON response: {e}")

            except (ConnectionError, Timeout) as e:
                self.error_count += 1
                logger.warning(f"Request failed (attempt {attempt}/{self.max_retries}): {e}")

                if self._should_retry(e, attempt):
                    last_exception = e
                    time.sleep(self._calculate_backoff(attempt))
                    continue

                raise JulesAPIError(f"Request failed after {attempt} attempts: {e}") from e

        # If we got here, all retries were exhausted
        if last_exception:
            raise JulesAPIError(
                f"Request failed after {self.max_retries} retries: {last_exception}"
            ) from last_exception

        # Shouldn't reach here, but just in case
        raise JulesAPIError("Request failed for unknown reason")

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            API response as dictionary
        """
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request.

        Args:
            path: API endpoint path
            json: JSON request body
            params: Query parameters

        Returns:
            API response as dictionary
        """
        return self._request("POST", path, params=params, json=json)

    def get_stats(self) -> Dict[str, int]:
        """Get client usage statistics.

        Returns:
            Dictionary with request and error counts
        """
        return {
            "requests": self.request_count,
            "errors": self.error_count,
        }

    def close(self) -> None:
        """Close the HTTP session."""
        logger.info(
            f"Closing client. Stats: {self.request_count} requests, {self.error_count} errors"
        )
        self.session.close()

    def __enter__(self) -> "BaseClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
