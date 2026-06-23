import smtplib
from email.message import EmailMessage

from app.core.config import Settings


class EmailConfigError(Exception):
    pass


class GmailSmtpClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _validate(self) -> None:
        if not self.settings.assistant_email_enabled:
            raise EmailConfigError("Email integration is disabled. Set ASSISTANT_EMAIL_ENABLED=true.")

        if self.settings.assistant_email_provider != "gmail_smtp":
            raise EmailConfigError("Unsupported provider. Set ASSISTANT_EMAIL_PROVIDER=gmail_smtp.")

        if not self.settings.assistant_email_from:
            raise EmailConfigError("ASSISTANT_EMAIL_FROM is required.")

        if not self.settings.assistant_email_app_password:
            raise EmailConfigError("ASSISTANT_EMAIL_APP_PASSWORD is required.")

    def send_email(self, to_email: str, subject: str, body: str) -> None:
        self._validate()

        msg = EmailMessage()
        msg["From"] = self.settings.assistant_email_from
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(
            self.settings.assistant_email_smtp_host,
            self.settings.assistant_email_smtp_port,
            timeout=25,
        ) as smtp:
            smtp.ehlo()
            if self.settings.assistant_email_use_starttls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(self.settings.assistant_email_from, self.settings.assistant_email_app_password)
            smtp.send_message(msg)
