"""Async base HTTP client for Jules API."""

from typing import Optional, Dict, Any
import aiohttp
from jules_agent_sdk.exceptions import (
    JulesAPIError,
    JulesAuthenticationError,
    JulesNotFoundError,
    JulesValidationError,
    JulesRateLimitError,
    JulesServerError,
)


class AsyncBaseClient:
    """Async HTTP client for making requests to Jules API."""

    BASE_URL = "https://jules.googleapis.com/v1alpha"

    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        """Initialize the async base client.

        Args:
            api_key: Jules API key for authentication
            base_url: Optional custom base URL (defaults to official API endpoint)
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"X-Goog-Api-Key": self.api_key}
            )
        return self._session

    async def _handle_error(self, response: aiohttp.ClientResponse) -> None:
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
        try:
            error_data = await response.json()
        except Exception:
            error_data = {"error": await response.text()}

        error_msg = error_data.get("error", {}).get("message", str(error_data))

        if response.status == 401:
            raise JulesAuthenticationError(error_msg, response.status, error_data)
        elif response.status == 404:
            raise JulesNotFoundError(error_msg, response.status, error_data)
        elif response.status == 400:
            raise JulesValidationError(error_msg, response.status, error_data)
        elif response.status == 429:
            raise JulesRateLimitError(error_msg, response.status, error_data)
        elif response.status >= 500:
            raise JulesServerError(error_msg, response.status, error_data)
        else:
            raise JulesAPIError(error_msg, response.status, error_data)

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an async HTTP request to the Jules API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json: JSON request body

        Returns:
            API response as dictionary

        Raises:
            JulesAPIError: On API error
        """
        session = await self._get_session()
        url = f"{self.base_url}/{path.lstrip('/')}"

        async with session.request(
            method=method, url=url, params=params, json=json
        ) as response:
            if not response.ok:
                await self._handle_error(response)

            if response.status == 204 or not response.content_length:
                return {}

            return await response.json()

    async def get(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an async GET request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            API response as dictionary
        """
        return await self._request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an async POST request.

        Args:
            path: API endpoint path
            json: JSON request body
            params: Query parameters

        Returns:
            API response as dictionary
        """
        return await self._request("POST", path, params=params, json=json)

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "AsyncBaseClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
