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
    async def test_async_sessions_get(self, mock_request):
        """Test async getting a session."""
        mock_request.return_value = {"id": "s1"}
        client = AsyncJulesClient(api_key="test-api-key")
        session = await client.sessions.get("s1")
        assert session.id == "s1"

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sessions_approve_plan(self, mock_request):
        """Test async approving a plan."""
        client = AsyncJulesClient(api_key="test-api-key")
        await client.sessions.approve_plan("s1")
        mock_request.assert_called_once()
        assert mock_request.call_args[0] == ("POST", "sessions/s1:approvePlan")

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sessions_send_message(self, mock_request):
        """Test async sending a message."""
        client = AsyncJulesClient(api_key="test-api-key")
        await client.sessions.send_message("s1", "Test")
        mock_request.assert_called_once()
        assert mock_request.call_args[0] == ("POST", "sessions/s1:sendMessage")
        assert mock_request.call_args[1]["json"] == {"prompt": "Test"}

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_client.asyncio.sleep", new_callable=AsyncMock)
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sessions_wait_for_completion(self, mock_request, mock_sleep):
        """Test async waiting for completion."""
        mock_request.side_effect = [
            {"state": "IN_PROGRESS"},
            {"state": "COMPLETED", "id": "s1"},
        ]
        client = AsyncJulesClient(api_key="test-api-key")
        session = await client.sessions.wait_for_completion("s1")
        assert session.id == "s1"

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_activities_get(self, mock_request):
        """Test async getting an activity."""
        mock_request.return_value = {"id": "a1"}
        client = AsyncJulesClient(api_key="test-api-key")
        activity = await client.activities.get("s1", "a1")
        assert activity.id == "a1"

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_activities_list(self, mock_request):
        """Test async listing activities."""
        mock_request.return_value = {"activities": [{"id": "a1"}]}
        client = AsyncJulesClient(api_key="test-api-key")
        result = await client.activities.list("s1")
        assert len(result["activities"]) == 1

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

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sources_get(self, mock_request):
        """Test async getting a source."""
        mock_request.return_value = {"id": "src1"}
        client = AsyncJulesClient(api_key="test-api-key")
        source = await client.sources.get("src1")
        assert source.id == "src1"

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sources_list(self, mock_request):
        """Test async listing sources."""
        mock_request.return_value = {"sources": [{"id": "src1"}]}
        client = AsyncJulesClient(api_key="test-api-key")
        result = await client.sources.list()
        assert len(result["sources"]) == 1

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sessions_list_all(self, mock_request):
        """Test async listing all sessions with pagination."""
        mock_request.side_effect = [
            {
                "sessions": [{"id": "s1"}],
                "nextPageToken": "next",
            },
            {"sessions": [{"id": "s2"}]},
        ]
        client = AsyncJulesClient(api_key="test-api-key")
        sessions = await client.sessions.list_all()
        assert len(sessions) == 2
        assert sessions[0].id == "s1"
        assert sessions[1].id == "s2"

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.AsyncBaseClient._request")
    async def test_async_sources_list_all(self, mock_request):
        """Test async listing all sources with pagination."""
        mock_request.side_effect = [
            {"sources": [{"id": "src1"}], "nextPageToken": "next"},
            {"sources": [{"id": "src2"}]},
        ]
        client = AsyncJulesClient(api_key="test-api-key")
        sources = await client.sources.list_all()
        assert len(sources) == 2
        assert sources[0].id == "src1"
        assert sources[1].id == "src2"


class TestAsyncErrorHandling:
    """Test error handling for the async client."""

    @pytest.mark.asyncio
    @patch("jules_agent_sdk.async_base.aiohttp.ClientSession.request")
    async def test_async_authentication_error(self, mock_request):
        """Test async authentication error."""
        mock_response = AsyncMock()
        mock_response.ok = False
        mock_response.status = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
        mock_request.return_value.__aenter__.return_value = mock_response

        client = AsyncJulesClient(api_key="invalid-key")
        with pytest.raises(JulesAuthenticationError):
            await client.sessions.list()

        await client.close()
