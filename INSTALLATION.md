# Installation Guide

Complete setup for **multi-agent-assistant** with GitHub Models AI brain and Gmail integration.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Git
- GitHub account
- Gmail account (for email notifications)

## Step 1: Clone & Environment Setup

```bash
# Clone repository
git clone https://github.com/KamyabPour/multi-agent-assistant.git
cd multi-agent-assistant

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create .env from template
cp .env.example .env
```

## Step 2: Configure GitHub Models (AI Brain)

The assistant uses GitHub Models API as its brain for intelligent responses.

### 2a. Create/Verify GitHub Account

1. Go to [github.com/signup](https://github.com/signup) if needed
2. Log in to your GitHub account
3. Verify email is confirmed

### 2b. Generate Personal Access Token

1. Go to GitHub Settings → [Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Fill in:
   - **Name**: `multi-agent-assistant`
   - **Expiration**: 90 days
   - **Scopes**: `read:models` (only this scope needed)
4. Copy the token (you won't see it again)

### 2c. Update .env with GitHub Token

```bash
# Edit .env and add:
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_MODELS_ENABLED=true
GITHUB_MODELS_MODEL=gpt-4o-mini
```

### 2d. Test GitHub Connection

```bash
# Start backend (from venv)
cd services/orchestrator
pip install -r requirements.txt

python -m uvicorn app.main:app --reload
# In another terminal:
curl -X POST http://localhost:8000/api/v1/models/test-connection
```

Expected response:
```json
{
  "success": true,
  "message": "GitHub Models API connection successful.",
  "response": "OK"
}
```

For detailed troubleshooting, see [docs/github_models_setup.md](docs/github_models_setup.md).

## Step 3: Configure Gmail (Optional - for email notifications)

The assistant can send email notifications and reminders.

### 3a. Create/Verify Gmail Account

1. Go to [gmail.com](https://gmail.com) to create a free account, or use existing
2. Verify email and add phone number for recovery

### 3b. Enable 2-Step Verification

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Click "2-Step Verification" and complete setup
3. Add recovery methods (phone, backup email)

### 3c. Generate App-Specific Password

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Windows Computer" (or your device)
3. Click "Generate"
4. Copy the 16-character password

### 3d. Update .env with Gmail Credentials

```bash
# Edit .env and add:
ASSISTANT_EMAIL_ENABLED=true
ASSISTANT_EMAIL_FROM=your-email@gmail.com
ASSISTANT_EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

### 3e. Test Gmail Connection

```bash
# Backend still running from Step 2
curl -X POST http://localhost:8000/api/v1/email/send-test \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@gmail.com",
    "subject": "Test Email",
    "body": "Testing Gmail integration from assistant."
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Test email sent successfully."
}
```

For detailed troubleshooting, see [docs/gmail_setup.md](docs/gmail_setup.md).

## Step 4: Set Up Assistant Identity & User Profile

The assistant needs to know its skills and the user (boss) context for personalized responses.

### 4a. Update Assistant Profile

```bash
curl -X POST http://localhost:8000/api/v1/profiles/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-assistant@gmail.com",
    "skills": [
      {"skill": "planning", "level": "advanced", "description": "Goal setting and roadmap creation"},
      {"skill": "scheduling", "level": "advanced", "description": "Calendar and time management"}
    ],
    "instructions": "Be concise and actionable.",
    "guardrails": ["No scheduling past 9pm"]
  }'
```

### 4b. Create Boss (User) Profile

```bash
curl -X POST http://localhost:8000/api/v1/profiles/boss/user123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Najmeh",
    "email": "your-email@example.com",
    "timezone": "Australia/Sydney",
    "goals": ["Ship production system", "Improve work-life balance"],
    "constraints": ["Max 50 hours/week coding"],
    "summary": "PhD engineer, robotics background. Prefers deep work blocks."
  }'
```

See [docs/profiles_and_skills.md](docs/profiles_and_skills.md) for full profile reference.

## Step 5: Install Backend Dependencies

```bash
cd services/orchestrator

# If not already done:
pip install -r requirements.txt

# Run tests (optional)
pytest -v
```

## Step 6: Install & Run Web Frontend

```bash
cd apps/web

npm install
npm run dev
# Opens on http://localhost:3000
```

## Step 7: Install & Run Mobile Frontend (Optional)

```bash
cd apps/mobile

npm install
# For iOS simulator:
npm start
# Then press 'i' for iOS or 'a' for Android

# Or use Expo Go app on real phone
npm start
```

## Step 8: Try the Application

1. **Web**: Go to http://localhost:3000
2. **Backend**: Running on http://localhost:8000
3. **Test message**: "Help me plan my week"
   - Routes to Planner agent
   - GitHub Models brain generates response
   - Assistant context + boss context included for personalization

## Project Structure

```
multi-agent-assistant/
├── services/orchestrator/          # FastAPI backend
│   ├── app/
│   │   ├── core/                   # Config, schemas, coordinator
│   │   ├── agents/                 # Specialist agents
│   │   ├── integrations/           # Gmail, GitHub Models
│   │   ├── profiles/               # Assistant & boss profiles
│   │   └── api/                    # Routes & endpoints
│   ├── requirements.txt
│   └── tests/
├── apps/web/                       # Next.js frontend
├── apps/mobile/                    # Expo React Native
├── docs/
│   ├── github_models_setup.md      # AI brain configuration
│   ├── gmail_setup.md              # Email integration
│   └── profiles_and_skills.md      # Context & personalization
└── .env.example
```

## Configuration Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes | - | GitHub personal access token |
| `GITHUB_MODELS_ENABLED` | Yes | false | Enable AI brain |
| `GITHUB_MODELS_MODEL` | No | gpt-4o-mini | Model to use |
| `ASSISTANT_EMAIL_ENABLED` | No | false | Enable email notifications |
| `ASSISTANT_EMAIL_FROM` | If email enabled | - | Gmail address for sending |
| `ASSISTANT_EMAIL_APP_PASSWORD` | If email enabled | - | Gmail app-specific password |

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --upgrade pip
pip install -r services/orchestrator/requirements.txt
```

### GitHub Models connection fails
- Check `GITHUB_TOKEN` is set correctly in `.env`
- Verify token has `read:models` scope
- Test at [github.com/models](https://github.com/models)
- See [docs/github_models_setup.md](docs/github_models_setup.md)

### Gmail connection fails
- Verify 2-Step Verification is enabled
- Check app-specific password is correct (no spaces when pasting)
- Ensure `ASSISTANT_EMAIL_ENABLED=true`
- See [docs/gmail_setup.md](docs/gmail_setup.md)

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check `NEXT_PUBLIC_API_BASE_URL` in `.env`
- Check CORS is not blocking (should be enabled in FastAPI)

## Next Steps

1. **Configure profiles** with your actual goals and skills
2. **Test each agent** by sending different types of messages
3. **Set up email notifications** for important actions
4. **Customize agent behavior** by updating specialist prompts
5. **Deploy to production** (see DevOps docs)

## Support

For detailed documentation:
- [GitHub Models Setup](docs/github_models_setup.md) — AI brain configuration
- [Gmail Setup](docs/gmail_setup.md) — Email notifications
- [Profiles & Skills](docs/profiles_and_skills.md) — Context personalization
- [Architecture](README.md) — System design

## Contributing

Pull requests welcome! Please test locally before submitting.

```bash
# Run all tests
pytest services/orchestrator/tests -v
npm run test --workspace apps/web
```
