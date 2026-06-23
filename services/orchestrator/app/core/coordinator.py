from app.agents.specialists import (
    CalendarAgent,
    FinanceAgent,
    GeneralAgent,
    PlannerAgent,
    WellnessAgent,
)
from app.core.schemas import AgentResult, AgentType


class Coordinator:
    def __init__(self) -> None:
        self.agent_map = {
            AgentType.planner: PlannerAgent(),
            AgentType.calendar: CalendarAgent(),
            AgentType.finance: FinanceAgent(),
            AgentType.wellness: WellnessAgent(),
            AgentType.general: GeneralAgent(),
        }

    def route(self, message: str) -> AgentType:
        text = message.lower()

        if any(word in text for word in ["plan", "project", "roadmap", "goal"]):
            return AgentType.planner
        if any(word in text for word in ["meeting", "calendar", "schedule", "time"]):
            return AgentType.calendar
        if any(word in text for word in ["budget", "money", "expense", "finance"]):
            return AgentType.finance
        if any(word in text for word in ["health", "sleep", "exercise", "stress", "wellness"]):
            return AgentType.wellness
        return AgentType.general

    def run(self, user_id: str, message: str, context: dict) -> tuple[AgentType, AgentResult]:
        route = self.route(message)
        result = self.agent_map[route].run(user_id=user_id, message=message, context=context)
        return route, result
