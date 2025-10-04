"""Activities API module."""

from typing import Optional, List, Dict, Any
from jules_agent_sdk.models import Activity
from jules_agent_sdk.base import BaseClient


class ActivitiesAPI:
    """API client for managing session activities."""

    def __init__(self, client: BaseClient) -> None:
        """Initialize the Activities API.

        Args:
            client: Base HTTP client instance
        """
        self.client = client

    def get(self, session_id: str, activity_id: str) -> Activity:
        """Get a single activity by ID.

        Args:
            session_id: The session ID or full name
            activity_id: The activity ID

        Returns:
            Activity object

        Example:
            >>> activity = client.activities.get("session123", "activity456")
            >>> print(activity.description)
        """
        if not session_id.startswith("sessions/"):
            session_id = f"sessions/{session_id}"

        path = f"{session_id}/activities/{activity_id}"
        response = self.client.get(path)
        return Activity.from_dict(response)

    def list(
        self,
        session_id: str,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List activities for a session.

        Args:
            session_id: The session ID or full name
            page_size: Maximum number of activities to return
            page_token: Token for pagination

        Returns:
            Dictionary with 'activities' list and optional 'nextPageToken'

        Example:
            >>> result = client.activities.list("session123", page_size=20)
            >>> for activity in result['activities']:
            ...     print(activity.description)
            >>> # Get next page if available
            >>> if result['nextPageToken']:
            ...     next_page = client.activities.list(
            ...         "session123",
            ...         page_token=result['nextPageToken']
            ...     )
        """
        if not session_id.startswith("sessions/"):
            session_id = f"sessions/{session_id}"

        params: Dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token

        path = f"{session_id}/activities"
        response = self.client.get(path, params=params)

        activities = []
        if response.get("activities"):
            activities = [Activity.from_dict(a) for a in response["activities"]]

        return {
            "activities": activities,
            "nextPageToken": response.get("nextPageToken"),
        }

    def list_all(self, session_id: str) -> List[Activity]:
        """List all activities for a session (handles pagination automatically).

        Args:
            session_id: The session ID or full name

        Returns:
            List of all Activity objects

        Example:
            >>> all_activities = client.activities.list_all("session123")
            >>> print(f"Total activities: {len(all_activities)}")
        """
        all_activities: List[Activity] = []
        page_token: Optional[str] = None

        while True:
            result = self.list(session_id, page_token=page_token)
            all_activities.extend(result["activities"])

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_activities
