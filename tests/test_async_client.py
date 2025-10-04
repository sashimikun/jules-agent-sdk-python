"""Tests for the async Jules client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from jules_agent_sdk import AsyncJulesClient
from jules_agent_sdk.exceptions import JulesAuthenticationError


class TestAsyncJulesClient:
    """Test cases for AsyncJulesClient."""

    def test_async_client_initialization(self):
        """Test async client initializes correctly."""
        client = AsyncJulesClient(api_key="test-api-key")
        assert client is not None
        assert client.sessions is not None
        assert client.activities is not None
        assert client.sources is not None

    def test_async_client_requires_api_key(self):
        """Test async client raises error without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            AsyncJulesClient(api_key="")

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self):
        """Test async client works as context manager."""
        async with AsyncJulesClient(api_key="test-api-key") as client:
            assert client is not None

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sessions_create(self, mock_request):
        """Test async session creation."""
        mock_request.return_value = {
            "name": "sessions/test123",
            "id": "test123",
            "prompt": "Fix bug",
            "sourceContext": {"source": "sources/repo1"},
            "state": "QUEUED",
        }

        client = AsyncJulesClient(api_key="test-api-key")
        session = await client.sessions.create(
            prompt="Fix bug", source="sources/repo1", starting_branch="main"
        )

        assert session.id == "test123"
        assert session.prompt == "Fix bug"

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sessions_list(self, mock_request):
        """Test async listing sessions."""
        mock_request.return_value = {
            "sessions": [
                {
                    "name": "sessions/test1",
                    "id": "test1",
                    "prompt": "Task 1",
                    "sourceContext": {"source": "sources/repo1"},
                }
            ]
        }

        client = AsyncJulesClient(api_key="test-api-key")
        result = await client.sessions.list()

        assert len(result["sessions"]) == 1
        assert result["sessions"][0].id == "test1"

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_activities_list_all(self, mock_request):
        """Test async listing all activities with pagination."""
        mock_request.side_effect = [
            {
                "activities": [
                    {"name": "sessions/s1/activities/a1", "id": "a1", "description": "Act 1"}
                ],
                "nextPageToken": "token1",
            },
            {
                "activities": [
                    {"name": "sessions/s1/activities/a2", "id": "a2", "description": "Act 2"}
                ]
            },
        ]

        client = AsyncJulesClient(api_key="test-api-key")
        activities = await client.activities.list_all("s1")

        assert len(activities) == 2
        assert activities[0].id == "a1"
        assert activities[1].id == "a2"
