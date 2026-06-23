import smtplib

from fastapi import APIRouter, HTTPException

from app.core.coordinator import Coordinator
from app.core.config import get_settings
from app.core.schemas import ChatRequest, ChatResponse, EmailTestRequest, EmailTestResponse
from app.integrations.gmail_smtp import EmailConfigError, GmailSmtpClient

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
