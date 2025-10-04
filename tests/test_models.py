"""Tests for data models."""

import pytest
from jules_agent_sdk.models import (
    Session,
    SessionState,
    Source,
    GitHubRepo,
    Activity,
    SourceContext,
    GitHubRepoContext,
)


class TestModels:
    """Test cases for data models."""

    def test_session_from_dict(self):
        """Test Session.from_dict() parsing."""
        data = {
            "name": "sessions/test123",
            "id": "test123",
            "prompt": "Fix bug",
            "sourceContext": {
                "source": "sources/repo1",
                "githubRepoContext": {"startingBranch": "main"},
            },
            "state": "IN_PROGRESS",
            "title": "Bug Fix Session",
        }

        session = Session.from_dict(data)
        assert session.id == "test123"
        assert session.prompt == "Fix bug"
        assert session.state == SessionState.IN_PROGRESS
        assert session.title == "Bug Fix Session"
        assert session.source_context.source == "sources/repo1"
        assert session.source_context.github_repo_context.starting_branch == "main"

    def test_session_to_dict(self):
        """Test Session.to_dict() serialization."""
        session = Session(
            prompt="Fix bug",
            source_context=SourceContext(
                source="sources/repo1",
                github_repo_context=GitHubRepoContext(starting_branch="main"),
            ),
            title="Bug Fix",
        )

        data = session.to_dict()
        assert data["prompt"] == "Fix bug"
        assert data["sourceContext"]["source"] == "sources/repo1"
        assert data["sourceContext"]["githubRepoContext"]["startingBranch"] == "main"
        assert data["title"] == "Bug Fix"

    def test_source_from_dict(self):
        """Test Source.from_dict() parsing."""
        data = {
            "name": "sources/src1",
            "id": "src1",
            "githubRepo": {
                "owner": "testuser",
                "repo": "testrepo",
                "isPrivate": True,
                "defaultBranch": {"displayName": "main"},
            },
        }

        source = Source.from_dict(data)
        assert source.id == "src1"
        assert source.github_repo is not None
        assert source.github_repo.owner == "testuser"
        assert source.github_repo.repo == "testrepo"
        assert source.github_repo.is_private is True
        assert source.github_repo.default_branch.display_name == "main"

    def test_activity_from_dict(self):
        """Test Activity.from_dict() parsing."""
        data = {
            "name": "sessions/s1/activities/a1",
            "id": "a1",
            "description": "Code change",
            "originator": "agent",
            "agentMessaged": {"agentMessage": "I fixed the bug"},
        }

        activity = Activity.from_dict(data)
        assert activity.id == "a1"
        assert activity.description == "Code change"
        assert activity.originator == "agent"
        assert activity.agent_messaged == {"agentMessage": "I fixed the bug"}

    def test_session_state_enum(self):
        """Test SessionState enum values."""
        assert SessionState.QUEUED.value == "QUEUED"
        assert SessionState.IN_PROGRESS.value == "IN_PROGRESS"
        assert SessionState.COMPLETED.value == "COMPLETED"
        assert SessionState.FAILED.value == "FAILED"

    def test_github_repo_serialization(self):
        """Test GitHubRepo serialization roundtrip."""
        original_data = {
            "owner": "testuser",
            "repo": "testrepo",
            "isPrivate": False,
        }

        repo = GitHubRepo.from_dict(original_data)
        serialized = repo.to_dict()

        assert serialized["owner"] == original_data["owner"]
        assert serialized["repo"] == original_data["repo"]
        assert serialized["isPrivate"] == original_data["isPrivate"]
