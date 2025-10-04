"""Async Jules API client."""

from typing import Optional, List, Dict, Any
import asyncio
from jules_agent_sdk.async_base import AsyncBaseClient
from jules_agent_sdk.models import Session, Activity, Source, SessionState
from jules_agent_sdk.exceptions import JulesAPIError


class AsyncSessionsAPI:
    """Async API client for managing Jules sessions."""

    def __init__(self, client: AsyncBaseClient) -> None:
        """Initialize the async Sessions API."""
        self.client = client

    async def create(
        self,
        prompt: str,
        source: str,
        starting_branch: Optional[str] = None,
        title: Optional[str] = None,
        require_plan_approval: bool = False,
    ) -> Session:
        """Create a new session asynchronously."""
        data: Dict[str, Any] = {
            "prompt": prompt,
            "sourceContext": {"source": source},
        }

        if starting_branch:
            data["sourceContext"]["githubRepoContext"] = {"startingBranch": starting_branch}

        if title:
            data["title"] = title

        if require_plan_approval:
            data["requirePlanApproval"] = require_plan_approval

        response = await self.client.post("sessions", json=data)
        return Session.from_dict(response)

    async def get(self, session_id: str) -> Session:
        """Get a single session by ID asynchronously."""
        if not session_id.startswith("sessions/"):
            session_id = f"sessions/{session_id}"

        response = await self.client.get(session_id)
        return Session.from_dict(response)

    async def list(
        self, page_size: Optional[int] = None, page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all sessions asynchronously."""
        params: Dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token

        response = await self.client.get("sessions", params=params)

        sessions = []
        if response.get("sessions"):
            sessions = [Session.from_dict(s) for s in response["sessions"]]

        return {
            "sessions": sessions,
            "nextPageToken": response.get("nextPageToken"),
        }

    async def approve_plan(self, session_id: str) -> None:
        """Approve a plan in a session asynchronously."""
        if not session_id.startswith("sessions/"):
            session_id = f"sessions/{session_id}"

        await self.client.post(f"{session_id}:approvePlan")

    async def send_message(self, session_id: str, prompt: str) -> None:
        """Send a message from the user to a session asynchronously."""
        if not session_id.startswith("sessions/"):
            session_id = f"sessions/{session_id}"

        await self.client.post(f"{session_id}:sendMessage", json={"prompt": prompt})

    async def wait_for_completion(
        self, session_id: str, poll_interval: int = 5, timeout: Optional[int] = None
    ) -> Session:
        """Poll a session asynchronously until it completes or fails."""
        start_time = asyncio.get_event_loop().time()
        terminal_states = {
            SessionState.COMPLETED,
            SessionState.FAILED,
        }

        while True:
            session = await self.get(session_id)

            if session.state in terminal_states:
                if session.state == SessionState.FAILED:
                    raise JulesAPIError(f"Session failed: {session_id}")
                return session

            if timeout and (asyncio.get_event_loop().time() - start_time) > timeout:
                raise TimeoutError(f"Session polling timed out after {timeout} seconds")

            await asyncio.sleep(poll_interval)


class AsyncActivitiesAPI:
    """Async API client for managing session activities."""

    def __init__(self, client: AsyncBaseClient) -> None:
        """Initialize the async Activities API."""
        self.client = client

    async def get(self, session_id: str, activity_id: str) -> Activity:
        """Get a single activity by ID asynchronously."""
        if not session_id.startswith("sessions/"):
            session_id = f"sessions/{session_id}"

        path = f"{session_id}/activities/{activity_id}"
        response = await self.client.get(path)
        return Activity.from_dict(response)

    async def list(
        self,
        session_id: str,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List activities for a session asynchronously."""
        if not session_id.startswith("sessions/"):
            session_id = f"sessions/{session_id}"

        params: Dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token

        path = f"{session_id}/activities"
        response = await self.client.get(path, params=params)

        activities = []
        if response.get("activities"):
            activities = [Activity.from_dict(a) for a in response["activities"]]

        return {
            "activities": activities,
            "nextPageToken": response.get("nextPageToken"),
        }

    async def list_all(self, session_id: str) -> List[Activity]:
        """List all activities for a session asynchronously (handles pagination)."""
        all_activities: List[Activity] = []
        page_token: Optional[str] = None

        while True:
            result = await self.list(session_id, page_token=page_token)
            all_activities.extend(result["activities"])

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_activities


class AsyncSourcesAPI:
    """Async API client for managing Jules sources."""

    def __init__(self, client: AsyncBaseClient) -> None:
        """Initialize the async Sources API."""
        self.client = client

    async def get(self, source_id: str) -> Source:
        """Get a single source by ID asynchronously."""
        if not source_id.startswith("sources/"):
            source_id = f"sources/{source_id}"

        response = await self.client.get(source_id)
        return Source.from_dict(response)

    async def list(
        self,
        filter_str: Optional[str] = None,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List sources asynchronously."""
        params: Dict[str, Any] = {}
        if filter_str:
            params["filter"] = filter_str
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token

        response = await self.client.get("sources", params=params)

        sources = []
        if response.get("sources"):
            sources = [Source.from_dict(s) for s in response["sources"]]

        return {
            "sources": sources,
            "nextPageToken": response.get("nextPageToken"),
        }

    async def list_all(self, filter_str: Optional[str] = None) -> List[Source]:
        """List all sources asynchronously (handles pagination)."""
        all_sources: List[Source] = []
        page_token: Optional[str] = None

        while True:
            result = await self.list(filter_str=filter_str, page_token=page_token)
            all_sources.extend(result["sources"])

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_sources


class AsyncJulesClient:
    """Async client for interacting with the Jules API.

    This client provides async/await support for all Jules API operations.

    Example:
        >>> import asyncio
        >>> from jules_agent_sdk import AsyncJulesClient
        >>>
        >>> async def main():
        ...     async with AsyncJulesClient(api_key="your-api-key") as client:
        ...         # Create a session
        ...         session = await client.sessions.create(
        ...             prompt="Fix the login bug",
        ...             source="sources/my-repo-id",
        ...             starting_branch="main"
        ...         )
        ...
        ...         # Wait for completion
        ...         completed = await client.sessions.wait_for_completion(session.id)
        ...
        ...         # Get activities
        ...         activities = await client.activities.list_all(session.id)
        ...         for activity in activities:
        ...             print(activity.description)
        >>>
        >>> asyncio.run(main())

    Attributes:
        sessions: Async API client for session operations
        activities: Async API client for activity operations
        sources: Async API client for source operations
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        """Initialize the async Jules API client.

        Args:
            api_key: Your Jules API key for authentication
            base_url: Optional custom base URL

        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("API key is required")

        self._base_client = AsyncBaseClient(api_key=api_key, base_url=base_url)
        self.sessions = AsyncSessionsAPI(self._base_client)
        self.activities = AsyncActivitiesAPI(self._base_client)
        self.sources = AsyncSourcesAPI(self._base_client)

    async def close(self) -> None:
        """Close the HTTP session."""
        await self._base_client.close()

    async def __aenter__(self) -> "AsyncJulesClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()
