from abc import ABC, abstractmethod

from app.core.schemas import AgentResult, AgentType


class BaseAgent(ABC):
    agent_type: AgentType

    def __init__(self, brain=None) -> None:
        """
        Initialize agent with optional brain (GitHub Models client).
        If no brain is provided, agent uses fallback responses.
        """
        self.brain = brain

    @property
    def system_prompt(self) -> str:
        """Override in subclasses to define agent-specific instructions."""
        return "You are a helpful assistant."

    @abstractmethod
    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        raise NotImplementedError

