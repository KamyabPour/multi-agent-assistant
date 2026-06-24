# Gmail Setup for Multi-Agent Assistant

This setup creates a dedicated Gmail identity for the assistant and makes it part of standard installation.

## 1. Create a dedicated Gmail account
- Create a separate account for the assistant, for example: yourproject.assistant@gmail.com
- Do not use your personal main email account.

## 2. Secure the account
- Enable 2-Step Verification on the Gmail account.
- Use a unique password and recovery methods.

## 3. Create a Gmail App Password
- In Google Account settings, go to Security.
- Under 2-Step Verification, open App passwords.
- Create an app password for Mail.
- Copy the 16-character app password.

## 4. Configure environment values
Set these values in your local .env file:

- ASSISTANT_EMAIL_ENABLED=true
- ASSISTANT_EMAIL_PROVIDER=gmail_smtp
- ASSISTANT_EMAIL_FROM=yourproject.assistant@gmail.com
- ASSISTANT_EMAIL_APP_PASSWORD=your_16_char_app_password
- ASSISTANT_EMAIL_SMTP_HOST=smtp.gmail.com
- ASSISTANT_EMAIL_SMTP_PORT=587
- ASSISTANT_EMAIL_USE_STARTTLS=true

## 5. Validate email during installation
After backend startup, send a test message with:

POST /api/v1/email/send-test

Example body:

{
  "to_email": "your_personal_email@example.com",
  "subject": "Assistant setup test",
  "body": "Gmail integration is configured and working."
}

If this works, Gmail is properly integrated into your assistant workflow.
