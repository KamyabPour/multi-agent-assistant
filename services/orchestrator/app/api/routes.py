import smtplib

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.core.coordinator import Coordinator
from app.core.schemas import (
    ChatRequest,
    ChatResponse,
    EmailTestRequest,
    EmailTestResponse,
    UpdateAssistantProfileRequest,
    UpdateBossProfileRequest,
)
from app.integrations.gmail_smtp import EmailConfigError, GmailSmtpClient
from app.integrations.github_models import GitHubModelsError, GitHubModelsClient
from app.profiles.models import AssistantProfile, BossProfile, SkillSet
from app.profiles.store import ProfileStore

router = APIRouter()
settings = get_settings()
profile_store = ProfileStore(settings.data_dir)
coordinator = Coordinator(profile_store=profile_store, settings=settings)


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


@router.post("/email/send-test", response_model=EmailTestResponse)
def send_test_email(payload: EmailTestRequest) -> EmailTestResponse:
    settings = get_settings()
    client = GmailSmtpClient(settings)

    try:
        client.send_email(
            to_email=payload.to_email,
            subject=payload.subject,
            body=payload.body,
        )
    except EmailConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except smtplib.SMTPException as exc:
        raise HTTPException(status_code=502, detail=f"SMTP error: {exc}") from exc

    return EmailTestResponse(success=True, message="Test email sent successfully.")


@router.post("/models/test-connection")
def test_github_models() -> dict:
    """Test GitHub Models API connection and authentication."""
    try:
        client = GitHubModelsClient(settings)
        result = client.test_connection()
        status_code = 200 if result["success"] else 400
        return result
    except GitHubModelsError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub Models not configured: {exc}",
        ) from exc


@router.get("/profiles/assistant")
def get_assistant_profile() -> AssistantProfile:
    return profile_store.load_assistant()


@router.post("/profiles/assistant", response_model=AssistantProfile)
def update_assistant_profile(payload: UpdateAssistantProfileRequest) -> AssistantProfile:
    profile = profile_store.load_assistant()

    if payload.email:
        profile.email = payload.email
    if payload.skills:
        profile.skills = [SkillSet(**s) for s in payload.skills]
    if payload.instructions:
        profile.instructions = payload.instructions
    if payload.guardrails:
        profile.guardrails = payload.guardrails

    profile_store.save_assistant(profile)
    return profile


@router.get("/profiles/boss/{boss_id}")
def get_boss_profile(boss_id: str) -> BossProfile:
    profile = profile_store.load_boss(boss_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Boss profile {boss_id} not found.")
    return profile


@router.post("/profiles/boss/{boss_id}", response_model=BossProfile)
def update_boss_profile(boss_id: str, payload: UpdateBossProfileRequest) -> BossProfile:
    profile = profile_store.load_boss(boss_id)

    if not profile:
        if not payload.name:
            raise HTTPException(
                status_code=400, detail="Must provide name to create new boss profile."
            )
        profile = BossProfile(boss_id=boss_id, name=payload.name)

    if payload.name:
        profile.name = payload.name
    if payload.email:
        profile.email = payload.email
    if payload.goals is not None:
        profile.goals = payload.goals
    if payload.constraints is not None:
        profile.constraints = payload.constraints
    if payload.summary:
        profile.summary = payload.summary

    profile_store.save_boss(profile)
    return profile
