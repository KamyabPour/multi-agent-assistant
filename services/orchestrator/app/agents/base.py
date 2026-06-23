from abc import ABC, abstractmethod

from app.core.schemas import AgentResult, AgentType


class BaseAgent(ABC):
    agent_type: AgentType

    @abstractmethod
    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        raise NotImplementedError
