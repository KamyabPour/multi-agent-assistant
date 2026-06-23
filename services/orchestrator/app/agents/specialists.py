from app.agents.base import BaseAgent
from app.core.schemas import AgentAction, AgentResult, AgentType


class PlannerAgent(BaseAgent):
    agent_type = AgentType.planner

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Created a practical plan with milestones.",
            actions=[
                AgentAction(title="Define weekly goals", details="Break the goal into 3 concrete outcomes."),
                AgentAction(title="Schedule deep work", details="Reserve 90-minute blocks for high-priority work."),
            ],
        )


class CalendarAgent(BaseAgent):
    agent_type = AgentType.calendar

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Prepared scheduling recommendations.",
            actions=[
                AgentAction(title="Focus block", details="Add one morning focus block tomorrow.", priority="high"),
                AgentAction(title="Buffer time", details="Add 15-minute buffers between meetings."),
            ],
        )


class FinanceAgent(BaseAgent):
    agent_type = AgentType.finance

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Generated budget-focused next actions.",
            actions=[
                AgentAction(title="Track top expenses", details="Tag the top 5 expense categories this week."),
                AgentAction(title="Savings rule", details="Set an automatic transfer to savings after payday."),
            ],
        )


class WellnessAgent(BaseAgent):
    agent_type = AgentType.wellness

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Built a balanced wellbeing action list.",
            actions=[
                AgentAction(title="Daily walk", details="Schedule a 20-minute walk in daylight."),
                AgentAction(title="Sleep prep", details="Set a wind-down reminder 1 hour before bed."),
            ],
        )


class GeneralAgent(BaseAgent):
    agent_type = AgentType.general

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Handled request with a general assistant path.",
            actions=[
                AgentAction(title="Clarify objective", details="Confirm expected outcome and deadline."),
            ],
        )
