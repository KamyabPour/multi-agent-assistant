# GitHub Models Setup (AI Brain)

The assistant uses GitHub Models API as its brain for AI-powered decision making. GitHub Models provides free access to models like `gpt-4o-mini`, `claude-3.5-sonnet`, and `llama-2-70b` for testing and development.

## 1. Create GitHub Account (if not already done)

1. Go to [github.com/signup](https://github.com/signup)
2. Create a free personal account (or use existing account)
3. Verify email address
4. Enable two-factor authentication (recommended)

## 2. Access GitHub Models

1. Visit [github.com/models](https://github.com/models) or navigate within GitHub
2. You should see available models:
   - `gpt-4o-mini` (free, recommended for testing)
   - `claude-3.5-sonnet` 
   - `llama-2-70b`
   - Others

3. Click on any model to open the inference playground

## 3. Generate GitHub Personal Access Token

1. Go to GitHub Settings → [Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token" → "Generate new token (classic)"
3. Fill in:
   - **Token name**: `multi-agent-assistant`
   - **Expiration**: 90 days (or your preference)
   - **Scopes**: Select only `read:models` (for GitHub Models API access)
4. Click "Generate token"
5. **Copy the token immediately** (you won't see it again)

## 4. Update Environment Configuration

1. Open your `.env` file in the project root (copy from `.env.example` if needed)

2. Add/update GitHub Models settings:
   ```env
   GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   GITHUB_MODELS_ENABLED=true
   GITHUB_MODELS_MODEL=gpt-4o-mini
   GITHUB_MODELS_TIMEOUT=30
   ```

   - `GITHUB_TOKEN`: Your personal access token from step 3
   - `GITHUB_MODELS_ENABLED`: Set to `true` to enable the brain
   - `GITHUB_MODELS_MODEL`: Choose from available models:
     - `gpt-4o-mini` (fastest, recommended)
     - `claude-3.5-sonnet` (more capable)
     - `phi-3.5-mini`
     - `llama-2-70b`
   - `GITHUB_MODELS_TIMEOUT`: Request timeout in seconds

## 5. Test the Connection

### Option A: Using curl

```bash
curl -X POST http://localhost:8000/api/v1/models/test-connection
```

Expected success response:
```json
{
  "success": true,
  "message": "GitHub Models API connection successful.",
  "response": "OK"
}
```

Expected error response (if not configured):
```json
{
  "success": false,
  "message": "GITHUB_TOKEN not set in environment."
}
```

### Option B: Using Python

```python
import httpx

response = httpx.post("http://localhost:8000/api/v1/models/test-connection")
print(response.json())
```

### Option C: In the web UI

1. Start the backend: `python -m uvicorn app.main:app --reload`
2. Start the frontend: `npm run dev` (from `apps/web`)
3. Visit http://localhost:3000
4. Send a message in chat (it will use GitHub Models as the brain)

## 6. How It Works

When you send a message:

1. **Router**: Coordinator identifies which agent should handle it (Planner, Calendar, Finance, etc.)
2. **Agent Brain**: The selected agent calls GitHub Models API with:
   - **System prompt**: Agent-specific instructions ("You are a planning expert...")
   - **User message**: Your input
   - **Context**: Boss profile summary + assistant skills (token-optimized)
3. **Response**: GitHub Models generates a summary + action list
4. **Formatting**: Agent parses the response and returns structured actions

Example flow:
```
User: "Help me plan my week"
   ↓
Router: "This is a planning question → PlannerAgent"
   ↓
PlannerAgent.brain.generate_response(
  system_prompt="You are a planning expert...",
  user_message="Help me plan my week",
  context={boss_context: "Najmeh, wants to ship by Friday", ...}
)
   ↓
GitHub Models API (gpt-4o-mini) generates response
   ↓
Agent formats: "SUMMARY|Action1: Details|Action2: Details"
   ↓
Returns structured AgentResult to frontend
```

## 7. Model Selection Guide

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| `gpt-4o-mini` | ⚡⚡⚡ | ⭐⭐⭐ | Free | General assistant, first choice |
| `claude-3.5-sonnet` | ⚡⚡ | ⭐⭐⭐⭐ | Free (limited) | Complex reasoning, code review |
| `llama-2-70b` | ⚡ | ⭐⭐⭐ | Free | Specialized tasks, offline capable |
| `phi-3.5-mini` | ⚡⚡⚡ | ⭐⭐ | Free | Lightweight, edge devices |

Start with `gpt-4o-mini` for development and testing.

## 8. Troubleshooting

### Error: "GITHUB_TOKEN not set"
- Check your `.env` file has `GITHUB_TOKEN=ghp_...`
- Restart backend after updating `.env`
- Ensure token is not wrapped in quotes: `GITHUB_TOKEN=ghp_ABC` (not `GITHUB_TOKEN="ghp_ABC"`)

### Error: "Token does not have permission"
- Ensure token has `read:models` scope
- Token may need to be regenerated with correct scopes

### Error: "Model not found"
- Check `GITHUB_MODELS_MODEL` value matches available models
- Verify at [github.com/models](https://github.com/models)

### Request timeout
- Increase `GITHUB_MODELS_TIMEOUT` (e.g., 60 seconds for slower networks)
- Check internet connection

### Fallback responses instead of AI
- Check `/api/v1/models/test-connection` for detailed error
- Verify token is valid at [github.com/settings/tokens](https://github.com/settings/tokens)
- Ensure `GITHUB_MODELS_ENABLED=true` in `.env`

## 9. Privacy & Rate Limits

- **Free tier**: Limited rate (monitor at [github.com/models](https://github.com/models))
- **Data**: Requests go to Microsoft/GitHub infrastructure, not stored long-term
- **Local storage**: Boss profiles and assistant skills stay on your machine (in `data/` directory)
- **Tokens sent**: Only context summaries sent with requests (optimized for token efficiency)

## 10. Switching Models

To switch models without restarting:

1. Update `.env`:
   ```env
   GITHUB_MODELS_MODEL=claude-3.5-sonnet
   ```

2. Restart backend (if not using `--reload`)

3. Test: `curl -X POST http://localhost:8000/api/v1/models/test-connection`

## References

- [GitHub Models Documentation](https://docs.github.com/en/github-cli/github-cli-extensions/github-cli-extension-development)
- [Available Models](https://github.com/models)
- [GitHub API Reference](https://docs.github.com/en/rest)
