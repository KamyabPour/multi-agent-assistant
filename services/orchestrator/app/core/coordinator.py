from app.agents.specialists import (
    CalendarAgent,
    ComplianceAgent,
    FinanceAgent,
    GeneralAgent,
    PlannerAgent,
    WellnessAgent,
)
from app.core.config import Settings
from app.core.schemas import AgentResult, AgentType
from app.integrations.github_models import GitHubModelsClient, GitHubModelsError
from app.profiles.store import ProfileStore


class Coordinator:
    def __init__(
        self, profile_store: ProfileStore | None = None, settings: Settings | None = None
    ) -> None:
        self.profile_store = profile_store
        self.settings = settings
        self.brain = None

        if settings and settings.github_models_enabled:
            try:
                self.brain = GitHubModelsClient(settings)
            except GitHubModelsError:
                pass

        self.agent_map = {
            AgentType.planner: PlannerAgent(brain=self.brain),
            AgentType.calendar: CalendarAgent(brain=self.brain),
            AgentType.finance: FinanceAgent(brain=self.brain),
            AgentType.wellness: WellnessAgent(brain=self.brain),
            AgentType.compliance: ComplianceAgent(brain=self.brain),
            AgentType.general: GeneralAgent(brain=self.brain),
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
        if any(
            word in text
            for word in [
                "compliance",
                "regulation",
                "regulatory",
                "legal",
                "import",
                "export",
                "customs",
                "sanction",
                "trade law",
            ]
        ):
            return AgentType.compliance
        return AgentType.general

    def run(self, user_id: str, message: str, context: dict) -> tuple[AgentType, AgentResult]:
        route = self.route(message)
        enriched_context = context.copy()

        if self.profile_store:
            assistant = self.profile_store.load_assistant()
            boss = self.profile_store.load_boss(user_id)
            enriched_context["assistant_context"] = assistant.capabilities_summary()
            enriched_context["assistant_skills"] = assistant.skill_summary()
            if boss:
                enriched_context["boss_context"] = boss.context_summary()

        result = self.agent_map[route].run(user_id=user_id, message=message, context=enriched_context)
        return route, result
