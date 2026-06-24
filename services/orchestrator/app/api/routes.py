import smtplib
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from app.core.config import get_settings
from app.core.coordinator import Coordinator
from app.core.schemas import (
    AgentResult,
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


def _extract_open_path(details: str) -> str | None:
    if not details.startswith("Open:"):
        return None
    return details.split("Open:", 1)[1].strip()


def _to_download_url(local_path: str, request: Request) -> str | None:
    try:
        resolved = Path(local_path).resolve()
        relative = resolved.relative_to(settings.data_dir.resolve())
    except Exception:
        return None

    relative_url = relative.as_posix()
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/api/v1/downloads/{relative_url}"


def _enrich_action_download_links(result: AgentResult, request: Request) -> AgentResult:
    for action in result.actions:
        local_path = _extract_open_path(action.details)
        if not local_path:
            continue

        download_url = _to_download_url(local_path, request)
        if not download_url:
            continue

        action.download_url = download_url
    return result


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    route, result = coordinator.run(
        user_id=payload.user_id,
        message=payload.message,
        context=payload.context,
    )
    result = _enrich_action_download_links(result, request)
    return ChatResponse(route=route, result=result)


@router.post("/chat/upload", response_model=ChatResponse)
async def chat_with_uploads(
    request: Request,
    user_id: str = Form(...),
    message: str = Form(...),
    business_file: str | None = Form(default=None),
    source_urls: str | None = Form(default=None),
    context_json: str | None = Form(default=None),
    files: list[UploadFile] = File(default_factory=list),
) -> ChatResponse:
    if not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required.")
    if not message.strip():
        raise HTTPException(status_code=400, detail="message is required.")

    context: dict = {}
    if context_json:
        try:
            parsed_context = json.loads(context_json)
            if isinstance(parsed_context, dict):
                context.update(parsed_context)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid context_json payload.") from exc

    upload_dir = settings.data_dir / "uploads" / (
        f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
    )
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_files: list[Path] = []
    for item in files:
        original_name = Path(item.filename or "uploaded_file").name
        target = upload_dir / original_name
        payload = await item.read()
        target.write_bytes(payload)
        saved_files.append(target)

    resolved_business_file = (business_file or "").strip()
    if resolved_business_file and not (upload_dir / resolved_business_file).exists():
        raise HTTPException(
            status_code=400,
            detail=f"Selected business file not found in uploads: {resolved_business_file}",
        )

    if not resolved_business_file:
        for candidate in saved_files:
            suffix = candidate.suffix.lower()
            if suffix in {".md", ".txt"}:
                resolved_business_file = candidate.name
                break

    if saved_files:
        context["shared_folder"] = str(upload_dir)
        if resolved_business_file:
            context["business_file"] = resolved_business_file

    if source_urls:
        parsed_urls = [
            x.strip()
            for x in source_urls.replace("\r", "").replace("\n", ",").split(",")
            if x.strip()
        ]
        if parsed_urls:
            existing = context.get("source_urls") or []
            if not isinstance(existing, list):
                existing = []
            context["source_urls"] = [*existing, *parsed_urls]

    route, result = coordinator.run(
        user_id=user_id.strip(),
        message=message,
        context=context,
    )
    result = _enrich_action_download_links(result, request)
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
