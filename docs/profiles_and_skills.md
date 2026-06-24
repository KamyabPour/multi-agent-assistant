# Profile & Skill-Set System

The assistant has two key profiles to reduce token usage and personalize responses:

## 1. Assistant Profile
Describes what the assistant knows about itself.

**Fields:**
- `assistant_name`: Name of the assistant (default: "multi-agent-assistant")
- `email`: Email address for notifications and communication
- `version`: Version number
- `skills`: List of skills with level (beginner/intermediate/advanced/expert)
- `supported_agents`: List of agent types available
- `instructions`: Special instructions or mode
- `guardrails`: Constraints and safety rules

**Endpoints:**
- `GET /api/v1/profiles/assistant` — Fetch current profile
- `POST /api/v1/profiles/assistant` — Update profile

**Example:**
```json
{
  "email": "assistant@example.com",
  "skills": [
    {"skill": "planning", "level": "advanced", "description": "Goal setting and roadmap creation"},
    {"skill": "scheduling", "level": "advanced", "description": "Calendar and time management"},
    {"skill": "financial_tracking", "level": "intermediate"}
  ],
  "instructions": "Be concise and actionable. Prioritize health and focus.",
  "guardrails": ["No scheduling past 9pm", "Protect time for deep work 9-12am"]
}
```

## 2. Boss Profile
Describes the user (the "boss") and their context to make the assistant more personalized.

**Fields:**
- `boss_id`: Unique user ID
- `name`: User's name
- `email`: User's email
- `timezone`: User's timezone
- `goals`: List of current goals (max 3 shown in context)
- `constraints`: List of constraints (max 2 shown in context)
- `preferences`: Custom preferences as JSON object
- `summary`: Short human-context summary (e.g., "Workaholic recovering, needs rest. Prefers mornings.")

**Endpoints:**
- `GET /api/v1/profiles/boss/{boss_id}` — Fetch boss profile
- `POST /api/v1/profiles/boss/{boss_id}` — Create or update boss profile

**Example:**
```json
{
  "name": "Najmeh",
  "email": "najmeh@example.com",
  "timezone": "Australia/Sydney",
  "goals": ["Ship production system", "Improve work-life balance", "Learn Rust"],
  "constraints": ["Max 50 hours/week coding", "No meetings before 10am", "Friday is learning day"],
  "summary": "PhD engineer, robotics background. Prefers deep work blocks. Values autonomous systems and practical AI.",
  "preferences": {
    "communication_style": "direct_and_concise",
    "planning_window": "weekly",
    "risk_tolerance": "medium"
  }
}
```

## How It Works

When the assistant receives a message:
1. It loads the assistant profile and boss profile
2. It creates compact summaries:
   - `assistant_context`: Email, agents available
   - `assistant_skills`: Top 3 skills at highest levels
   - `boss_context`: Name, top goals, key constraints, summary
3. These summaries are added to the context passed to agents
4. Agents use condensed context instead of full histories to reduce token usage

## Token Optimization

Instead of storing full conversation history:
- Assistant profile summary: ~50 tokens
- Boss profile context: ~80 tokens
- Saves hundreds of tokens per multi-agent call by eliminating redundant context

## Setup During Installation

1. After backend startup, set the assistant profile:
   ```bash
   curl -X POST http://localhost:8000/api/v1/profiles/assistant \
     -H "Content-Type: application/json" \
     -d '{"email": "assistant@yourdomain.com", ...}'
   ```

2. Set the boss profile (one per user):
   ```bash
   curl -X POST http://localhost:8000/api/v1/profiles/boss/your-user-id \
     -H "Content-Type: application/json" \
     -d '{"name": "Your Name", "goals": [...], ...}'
   ```

3. Verify profiles are used in agent responses.

## Data Storage

Profiles are stored in JSON files in the `data/` directory:
- `data/assistant_profile.json`
- `data/boss_profile.json`

For production, replace with a proper database (PostgreSQL, MongoDB, etc.).
