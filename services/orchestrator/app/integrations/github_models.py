"""GitHub Models API integration for LLM inference (assistant brain)."""

import json

import httpx

from app.core.config import Settings


class GitHubModelsError(Exception):
    """Base exception for GitHub Models errors."""

    pass


class GitHubModelsClient:
    """Client for GitHub Models API (inference endpoint)."""

    BASE_URL = "https://models.inference.ai.azure.com"

    def __init__(self, settings: Settings) -> None:
        if not settings.github_token:
            raise GitHubModelsError("GITHUB_TOKEN not set in environment.")
        if not settings.github_models_enabled:
            raise GitHubModelsError("GitHub Models integration not enabled.")

        self.token = settings.github_token
        self.model = settings.github_models_model
        self.timeout = settings.github_models_timeout

    def generate_response(
        self, system_prompt: str, user_message: str, context: dict | None = None
    ) -> str:
        """
        Call GitHub Models API to generate a response.

        Args:
            system_prompt: System instructions for the model
            user_message: User's input message
            context: Optional context dict with boss_context, assistant_skills, etc.

        Returns:
            Generated response text

        Raises:
            GitHubModelsError: If API call fails
        """
        context_str = ""
        if context:
            if "boss_context" in context:
                context_str += f"Boss Context: {context['boss_context']}\n"
            if "assistant_skills" in context:
                context_str += f"Assistant Skills: {context['assistant_skills']}\n"

        full_message = f"{context_str}\n{user_message}".strip()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_message},
            ],
            "temperature": 0.7,
            "top_p": 1.0,
            "max_tokens": 500,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except httpx.HTTPError as exc:
            raise GitHubModelsError(f"GitHub Models API error: {exc}") from exc
        except (KeyError, json.JSONDecodeError) as exc:
            raise GitHubModelsError(f"Invalid GitHub Models response: {exc}") from exc

    def test_connection(self) -> dict:
        """Test the GitHub Models API connection."""
        try:
            response = self.generate_response(
                system_prompt="You are a helpful assistant. Respond with 'OK' if working.",
                user_message="Say OK",
            )
            return {"success": True, "message": "GitHub Models API connection successful.", "response": response}
        except GitHubModelsError as exc:
            return {"success": False, "message": str(exc)}
