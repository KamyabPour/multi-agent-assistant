from fastapi import APIRouter

from app.core.coordinator import Coordinator
from app.core.schemas import ChatRequest, ChatResponse

router = APIRouter()
coordinator = Coordinator()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    route, result = coordinator.run(
        user_id=payload.user_id,
        message=payload.message,
        context=payload.context,
    )
    return ChatResponse(route=route, result=result)
