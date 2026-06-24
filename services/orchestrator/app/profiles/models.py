from pydantic import BaseModel, Field


class SkillSet(BaseModel):
    skill: str = Field(..., min_length=1)
    level: str = Field(default="intermediate", pattern="^(beginner|intermediate|advanced|expert)$")
    description: str | None = None


class AssistantProfile(BaseModel):
    """Profile of the assistant itself."""

    assistant_name: str = "multi-agent-assistant"
    email: str | None = None
    version: str = "0.1.0"
    skills: list[SkillSet] = Field(default_factory=list)
    supported_agents: list[str] = Field(
        default_factory=lambda: [
            "planner",
            "calendar",
            "finance",
            "wellness",
            "compliance",
            "general",
        ]
    )
    instructions: str | None = None
    guardrails: list[str] = Field(default_factory=list)

    def skill_summary(self) -> str:
        """Compact skill summary for token reduction."""
        if not self.skills:
            return "No skills configured."
        skills_str = ", ".join([f"{s.skill} ({s.level})" for s in self.skills])
        return f"Skills: {skills_str}"

    def capabilities_summary(self) -> str:
        """Summarize capabilities for context."""
        agents = ", ".join(self.supported_agents)
        return f"Agents: {agents}. Email: {self.email or 'not configured'}."


class BossProfile(BaseModel):
    """Profile of the user (the boss) for context-aware assistance."""

    boss_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    email: str | None = None
    timezone: str = "UTC"
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    preferences: dict = Field(default_factory=dict)
    summary: str | None = None

    def context_summary(self) -> str:
        """Compact user context for token reduction."""
        parts = [f"Boss: {self.name}"]
        if self.goals:
            goals_str = ", ".join(self.goals[:3])
            parts.append(f"Goals: {goals_str}")
        if self.constraints:
            constraint_str = ", ".join(self.constraints[:2])
            parts.append(f"Constraints: {constraint_str}")
        if self.summary:
            parts.append(f"Context: {self.summary}")
        return " | ".join(parts)
