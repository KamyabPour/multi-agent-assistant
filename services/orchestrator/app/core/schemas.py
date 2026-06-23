from enum import Enum

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    planner = "planner"
    calendar = "calendar"
    finance = "finance"
    wellness = "wellness"
    general = "general"


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    context: dict = Field(default_factory=dict)


class AgentAction(BaseModel):
    title: str
    details: str
    priority: str = "medium"


class AgentResult(BaseModel):
    agent: AgentType
    summary: str
    actions: list[AgentAction] = Field(default_factory=list)


class ChatResponse(BaseModel):
    route: AgentType
    result: AgentResult
