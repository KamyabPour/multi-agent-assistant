"""Tests for GitHub Models integration."""

import pytest
import httpx
from app.integrations.github_models import GitHubModelsClient, GitHubModelsError
from app.core.config import Settings
from unittest.mock import Mock, patch


class TestGitHubModelsClient:
    """Test GitHub Models client integration."""

    def test_init_no_token(self):
        """Test client initialization fails without token."""
        settings = Settings(github_token=None, github_models_enabled=True)
        with pytest.raises(GitHubModelsError, match="GITHUB_TOKEN not set"):
            GitHubModelsClient(settings)

    def test_init_disabled(self):
        """Test client initialization fails when disabled."""
        settings = Settings(github_token="ghp_test", github_models_enabled=False)
        with pytest.raises(GitHubModelsError, match="GitHub Models integration not enabled"):
            GitHubModelsClient(settings)

    def test_init_success(self):
        """Test successful client initialization."""
        settings = Settings(
            github_token="ghp_test",
            github_models_enabled=True,
            github_models_model="gpt-4o-mini",
        )
        client = GitHubModelsClient(settings)
        assert client.token == "ghp_test"
        assert client.model == "gpt-4o-mini"

    @patch("httpx.Client.post")
    def test_generate_response_success(self, mock_post):
        """Test successful response generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response

        settings = Settings(
            github_token="ghp_test", github_models_enabled=True
        )
        client = GitHubModelsClient(settings)
        response = client.generate_response("System prompt", "User message")

        assert response == "Test response"
        mock_post.assert_called_once()

    @patch("httpx.Client.post")
    def test_generate_response_with_context(self, mock_post):
        """Test response generation includes context."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response with context"}}]
        }
        mock_post.return_value = mock_response

        settings = Settings(
            github_token="ghp_test", github_models_enabled=True
        )
        client = GitHubModelsClient(settings)
        response = client.generate_response(
            "System prompt",
            "User message",
            context={
                "boss_context": "Najmeh, goals: [ship system]",
                "assistant_skills": "planning: advanced",
            },
        )

        assert response == "Response with context"
        call_args = mock_post.call_args
        payload = call_args.kwargs["json"]
        assert "Boss Context:" in payload["messages"][1]["content"]

    @patch("httpx.Client.post")
    def test_generate_response_api_error(self, mock_post):
        """Test error handling for API failures."""
        mock_post.side_effect = httpx.HTTPError("Connection failed")

        settings = Settings(
            github_token="ghp_test", github_models_enabled=True
        )
        client = GitHubModelsClient(settings)

        with pytest.raises(GitHubModelsError, match="GitHub Models API error"):
            client.generate_response("System prompt", "User message")

    @patch("httpx.Client.post")
    def test_test_connection_success(self, mock_post):
        """Test connection test succeeds."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OK"}}]
        }
        mock_post.return_value = mock_response

        settings = Settings(
            github_token="ghp_test", github_models_enabled=True
        )
        client = GitHubModelsClient(settings)
        result = client.test_connection()

        assert result["success"] is True
        assert "GitHub Models API connection successful" in result["message"]

    def test_test_connection_error(self):
        """Test connection setup fails when token missing."""
        settings = Settings(
            github_token=None, github_models_enabled=True
        )
        with pytest.raises(GitHubModelsError):
            GitHubModelsClient(settings)


class TestSpecialistAgentsWithBrain:
    """Test agents using GitHub Models brain."""

    def test_planner_agent_uses_brain(self):
        """Test planner agent calls brain."""
        from app.agents.specialists import PlannerAgent

        mock_brain = Mock()
        mock_brain.generate_response.return_value = (
            "Create a plan|Action 1: Details (high)|Action 2: Details"
        )

        agent = PlannerAgent(brain=mock_brain)
        result = agent.run(
            user_id="test_user",
            message="Plan my week",
            context={"boss_context": "test context"},
        )

        assert result.summary == "Create a plan"
        assert len(result.actions) >= 1
        mock_brain.generate_response.assert_called_once()

    def test_agent_fallback_when_brain_unavailable(self):
        """Test agent returns fallback when brain fails."""
        from app.agents.specialists import PlannerAgent

        mock_brain = Mock()
        mock_brain.generate_response.side_effect = Exception("API error")

        agent = PlannerAgent(brain=mock_brain)
        result = agent.run(
            user_id="test_user",
            message="Plan my week",
            context={},
        )

        # Should return fallback response
        assert result.summary is not None
        assert len(result.actions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
