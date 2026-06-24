# multi-agent-assistant

A multi-agent personal assistant that helps manage your daily life, tasks, schedule, and work context using AI-powered memory and planning agents.

Production-style AI project scaffold for a life assistant with:

Production-style AI project scaffold for a life assistant with:
- Multi-agent orchestration backend (Python + FastAPI)
- Computer version (web app for desktop/browser)
- Mobile version (React Native Expo)

## Project Structure

```text
multi-agent-assistant/
  services/
    orchestrator/        # Multi-agent backend API
  apps/
    web/                 # Desktop/browser client (Next.js)
    mobile/              # Mobile client (Expo React Native)
  docs/
    architecture.md
  .env.example
  docker-compose.yml
```

## Quick Start

⚡ **Interactive Installation** (Recommended - 5 minutes)

```bash
# macOS/Linux
python install.py

# Windows
install.bat
```

The installer will guide you through:
- ✓ GitHub account & token setup
- ✓ GitHub Models API (AI brain) configuration
- ✓ Gmail integration (optional)
- ✓ Profile creation (assistant + your goals/constraints)
- ✓ Testing & validation

👉 **[Read QUICKSTART.md](QUICKSTART.md)** for detailed walkthrough

---

## Manual Setup

For experienced users, follow [INSTALLATION.md](INSTALLATION.md).

## 1) Backend

```powershell
cd services/orchestrator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:
- GET http://localhost:8000/api/v1/health

Chat endpoint:
- POST http://localhost:8000/api/v1/chat

Example body:
```json
{
  "user_id": "najmeh",
  "message": "Help me plan my week and reduce stress",
  "context": {}
}
```

## 2) Web App (computer)

```powershell
cd apps/web
npm install
npm run dev
```

Open:
- http://localhost:3000

## 3) Mobile App

```powershell
cd apps/mobile
npm install
npm run start
```

Then run on:
- iOS simulator / Android emulator / Expo Go

## Best-practice direction
- Keep agents small and testable
- Add memory layer for user context and preferences
- Use confidence-based routing and fallback
- Add guardrails and action allow-lists
- Add structured logs, traces, and evaluation harness
