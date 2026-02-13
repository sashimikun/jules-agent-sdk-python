"""Tests for the Jules client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import JulesAuthenticationError, JulesValidationError


class TestJulesClient:
    """Test cases for JulesClient."""

    def test_client_initialization(self):
        """Test client initializes correctly."""
        client = JulesClient(api_key="test-api-key")
        assert client is not None
        assert client.sessions is not None
        assert client.activities is not None
        assert client.sources is not None

    def test_client_requires_api_key(self):
        """Test client raises error without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            JulesClient(api_key="")

    def test_client_context_manager(self):
        """Test client works as context manager."""
        with JulesClient(api_key="test-api-key") as client:
            assert client is not None

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sessions_create(self, mock_request):
        """Test session creation."""
        mock_request.return_value = {
            "name": "sessions/test123",
            "id": "test123",
            "prompt": "Fix bug",
            "sourceContext": {"source": "sources/repo1"},
            "state": "QUEUED",
        }

        client = JulesClient(api_key="test-api-key")
        session = client.sessions.create(
            prompt="Fix bug", source="sources/repo1", starting_branch="main"
        )

        assert session.id == "test123"
        assert session.prompt == "Fix bug"
        mock_request.assert_called_once()

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sessions_get(self, mock_request):
        """Test getting a session."""
        mock_request.return_value = {
            "name": "sessions/test123",
            "id": "test123",
            "prompt": "Fix bug",
            "sourceContext": {"source": "sources/repo1"},
            "state": "IN_PROGRESS",
        }

        client = JulesClient(api_key="test-api-key")
        session = client.sessions.get("test123")

        assert session.id == "test123"
        assert session.state.value == "IN_PROGRESS"

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sessions_list(self, mock_request):
        """Test listing sessions."""
        mock_request.return_value = {
            "sessions": [
                {
                    "name": "sessions/test1",
                    "id": "test1",
                    "prompt": "Task 1",
                    "sourceContext": {"source": "sources/repo1"},
                },
                {
                    "name": "sessions/test2",
                    "id": "test2",
                    "prompt": "Task 2",
                    "sourceContext": {"source": "sources/repo2"},
                },
            ],
            "nextPageToken": "next-page",
        }

        client = JulesClient(api_key="test-api-key")
        result = client.sessions.list(page_size=10)

        assert len(result["sessions"]) == 2
        assert result["nextPageToken"] == "next-page"

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_activities_list(self, mock_request):
        """Test listing activities."""
        mock_request.return_value = {
            "activities": [
                {
                    "name": "sessions/s1/activities/a1",
                    "id": "a1",
                    "description": "Activity 1",
                },
                {
                    "name": "sessions/s1/activities/a2",
                    "id": "a2",
                    "description": "Activity 2",
                },
            ]
        }

        client = JulesClient(api_key="test-api-key")
        result = client.activities.list("s1")

        assert len(result["activities"]) == 2
        assert result["activities"][0].id == "a1"

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sessions_approve_plan(self, mock_request):
        """Test approving a session plan."""
        client = JulesClient(api_key="test-api-key")
        client.sessions.approve_plan("s1")
        mock_request.assert_called_once()
        assert mock_request.call_args[0] == ("POST", "sessions/s1:approvePlan")

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sessions_send_message(self, mock_request):
        """Test sending a message to a session."""
        client = JulesClient(api_key="test-api-key")
        client.sessions.send_message("s1", "Hello")
        mock_request.assert_called_once()
        assert mock_request.call_args[0] == ("POST", "sessions/s1:sendMessage")
        assert mock_request.call_args[1]["json"] == {"prompt": "Hello"}

    @patch("jules_agent_sdk.sessions.time.sleep", return_value=None)
    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sessions_wait_for_completion_success(self, mock_request, mock_sleep):
        """Test waiting for session completion successfully."""
        mock_request.side_effect = [
            {"state": "IN_PROGRESS"},
            {"state": "COMPLETED", "id": "s1"},
        ]
        client = JulesClient(api_key="test-api-key")
        session = client.sessions.wait_for_completion("s1")
        assert session.id == "s1"
        assert mock_request.call_count == 2

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sessions_list_all(self, mock_request):
        """Test listing all sessions with pagination."""
        mock_request.side_effect = [
            {
                "sessions": [{"id": "s1"}],
                "nextPageToken": "next",
            },
            {"sessions": [{"id": "s2"}]},
        ]
        client = JulesClient(api_key="test-api-key")
        sessions = client.sessions.list_all()
        assert len(sessions) == 2
        assert sessions[0].id == "s1"
        assert sessions[1].id == "s2"

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_activities_get(self, mock_request):
        """Test getting a single activity."""
        mock_request.return_value = {"id": "a1", "description": "Activity 1"}
        client = JulesClient(api_key="test-api-key")
        activity = client.activities.get("s1", "a1")
        assert activity.id == "a1"
        mock_request.assert_called_once()
        assert mock_request.call_args[0] == ("GET", "sessions/s1/activities/a1")

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_activities_list_all(self, mock_request):
        """Test listing all activities with pagination."""
        mock_request.side_effect = [
            {
                "activities": [{"id": "a1"}],
                "nextPageToken": "next",
            },
            {"activities": [{"id": "a2"}]},
        ]
        client = JulesClient(api_key="test-api-key")
        activities = client.activities.list_all("s1")
        assert len(activities) == 2
        assert activities[0].id == "a1"
        assert activities[1].id == "a2"

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sources_get(self, mock_request):
        """Test getting a single source."""
        mock_request.return_value = {"id": "src1", "githubRepo": {"owner": "test"}}
        client = JulesClient(api_key="test-api-key")
        source = client.sources.get("src1")
        assert source.id == "src1"
        mock_request.assert_called_once()
        assert mock_request.call_args[0] == ("GET", "sources/src1")

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sources_list_all(self, mock_request):
        """Test listing all sources with pagination."""
        mock_request.side_effect = [
            {
                "sources": [{"id": "src1"}],
                "nextPageToken": "next",
            },
            {"sources": [{"id": "src2"}]},
        ]
        client = JulesClient(api_key="test-api-key")
        sources = client.sources.list_all()
        assert len(sources) == 2
        assert sources[0].id == "src1"
        assert sources[1].id == "src2"

    @patch("jules_agent_sdk.base.BaseClient._request")
    def test_sources_list(self, mock_request):
        """Test listing sources."""
        mock_request.return_value = {
            "sources": [
                {
                    "name": "sources/src1",
                    "id": "src1",
                    "githubRepo": {"owner": "test", "repo": "repo1"},
                }
            ]
        }

        client = JulesClient(api_key="test-api-key")
        result = client.sources.list()

        assert len(result["sources"]) == 1
        assert result["sources"][0].id == "src1"
        assert result["sources"][0].github_repo.owner == "test"


class TestErrorHandling:
    """Test error handling."""

    @patch("jules_agent_sdk.base.requests.Session.request")
    def test_authentication_error(self, mock_request):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
        mock_request.return_value = mock_response

        client = JulesClient(api_key="invalid-key")

        with pytest.raises(JulesAuthenticationError):
            client.sessions.list()

    @patch("jules_agent_sdk.base.requests.Session.request")
    def test_validation_error(self, mock_request):
        """Test validation error handling."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Invalid request"}}
        mock_request.return_value = mock_response

        client = JulesClient(api_key="test-key")

        with pytest.raises(JulesValidationError):
            client.sessions.create(prompt="", source="")
