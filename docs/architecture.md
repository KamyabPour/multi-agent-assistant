# Multi-Agent Life Assistant Architecture

## Goals
- One orchestration backend for all clients
- Computer app (web desktop experience) and mobile app
- Multi-agent routing with specialist agents
- Clean separation of concerns for scaling

## Layers
1. Client layer
- apps/web for desktop/browser
- apps/mobile for mobile

2. Orchestration layer
- services/orchestrator handles routing and policy
- Coordinator routes message to specialized agent

3. Agent layer
- Planner, Calendar, Finance, Wellness, General
- Each agent returns summary and action list

## Next upgrades
- Add LLM router with confidence score
- Add memory store (Redis or Postgres)
- Add auth (Clerk/Auth0/Cognito)
- Add task tools (calendar API, notes, reminders)
- Add Gmail tools (send reminders, summaries, and escalation emails)
- Add observability (OpenTelemetry + Grafana)
