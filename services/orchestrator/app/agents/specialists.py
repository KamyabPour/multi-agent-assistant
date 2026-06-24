import json

from app.agents.base import BaseAgent
from app.core.schemas import AgentAction, AgentResult, AgentType


class PlannerAgent(BaseAgent):
    agent_type = AgentType.planner

    @property
    def system_prompt(self) -> str:
        return (
            "You are a planning expert. Analyze the user's goal and provide a concise summary "
            "(1-2 sentences) of the practical plan. Format response as: SUMMARY|ACTION1|ACTION2 "
            "where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Created a practical plan."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
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

    @property
    def system_prompt(self) -> str:
        return (
            "You are a scheduling expert. Provide a concise summary (1-2 sentences) of scheduling recommendations. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Prepared scheduling recommendations."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
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

    @property
    def system_prompt(self) -> str:
        return (
            "You are a financial advisor. Provide a concise summary (1-2 sentences) of budget-focused actions. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Generated budget-focused next actions."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
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

    @property
    def system_prompt(self) -> str:
        return (
            "You are a wellness coach. Provide a concise summary (1-2 sentences) of balanced wellbeing actions. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details (priority)'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Built a balanced wellbeing action list."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
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

    @property
    def system_prompt(self) -> str:
        return (
            "You are a general assistant. Provide a concise summary (1-2 sentences) and actionable next steps. "
            "Format: SUMMARY|ACTION1|ACTION2 where each action is 'Title: Details'."
        )

    def run(self, user_id: str, message: str, context: dict) -> AgentResult:
        if self.brain:
            try:
                response = self.brain.generate_response(self.system_prompt, message, context)
                return self._parse_response(response)
            except Exception:
                pass
        return self._fallback_response()

    def _parse_response(self, response: str) -> AgentResult:
        parts = response.split("|")
        summary = parts[0].strip() if len(parts) > 0 else "Handled request with a general assistant path."
        actions = []
        for part in parts[1:]:
            if ":" in part:
                title, rest = part.split(":", 1)
                priority = "medium"
                if "(high)" in rest:
                    priority = "high"
                    rest = rest.replace("(high)", "")
                elif "(low)" in rest:
                    priority = "low"
                    rest = rest.replace("(low)", "")
                actions.append(AgentAction(title=title.strip(), details=rest.strip(), priority=priority))
        if not actions:
            actions = self._fallback_response().actions
        return AgentResult(agent=self.agent_type, summary=summary, actions=actions)

    def _fallback_response(self) -> AgentResult:
        return AgentResult(
            agent=self.agent_type,
            summary="Handled request with a general assistant path.",
            actions=[
                AgentAction(title="Clarify objective", details="Confirm expected outcome and deadline."),
            ],
        )
