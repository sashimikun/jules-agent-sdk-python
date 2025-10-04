"""Main Jules API client."""

from typing import Optional
from jules_agent_sdk.base import BaseClient
from jules_agent_sdk.sessions import SessionsAPI
from jules_agent_sdk.activities import ActivitiesAPI
from jules_agent_sdk.sources import SourcesAPI


class JulesClient:
    """Main client for interacting with the Jules API.

    This is the primary entry point for using the Jules Agent SDK.
    It provides access to all API resources through convenient properties.

    Example:
        >>> from jules_agent_sdk import JulesClient
        >>>
        >>> # Initialize the client
        >>> client = JulesClient(api_key="your-api-key")
        >>>
        >>> # Create a new session
        >>> session = client.sessions.create(
        ...     prompt="Fix the login bug in the authentication module",
        ...     source="sources/my-repo-id",
        ...     starting_branch="main"
        ... )
        >>>
        >>> # Wait for completion
        >>> completed_session = client.sessions.wait_for_completion(session.id)
        >>>
        >>> # List activities
        >>> activities = client.activities.list_all(session.id)
        >>> for activity in activities:
        ...     print(activity.description)
        >>>
        >>> # List sources
        >>> sources = client.sources.list_all()
        >>> for source in sources:
        ...     print(source.id)

    Attributes:
        sessions: API client for session operations
        activities: API client for activity operations
        sources: API client for source operations
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 1.0,
    ) -> None:
        """Initialize the Jules API client.

        Args:
            api_key: Your Jules API key for authentication
            base_url: Optional custom base URL (defaults to https://jules.googleapis.com/v1alpha)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_backoff_factor: Backoff factor for retries (default: 1.0)

        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("API key is required")

        self._base_client = BaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff_factor=retry_backoff_factor,
        )
        self.sessions = SessionsAPI(self._base_client)
        self.activities = ActivitiesAPI(self._base_client)
        self.sources = SourcesAPI(self._base_client)

    def close(self) -> None:
        """Close the HTTP session.

        Example:
            >>> client = JulesClient(api_key="your-api-key")
            >>> try:
            ...     session = client.sessions.create(...)
            ... finally:
            ...     client.close()
        """
        self._base_client.close()

    def __enter__(self) -> "JulesClient":
        """Context manager entry.

        Example:
            >>> with JulesClient(api_key="your-api-key") as client:
            ...     session = client.sessions.create(...)
            ...     # Client automatically closes when exiting the context
        """
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit."""
        self.close()
