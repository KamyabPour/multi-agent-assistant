# Testing Guide - GitHub Models Integration

Complete testing instructions for the assistant's AI brain and profile system.

## Quick Start Testing (No Setup Required)

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```
Expected: `{"status": "ok"}`

---

## Part A: Manual Testing (curl)

### A1. Test GitHub Models Configuration

**Without Token (should fail):**
```bash
curl -X POST http://localhost:8000/api/v1/models/test-connection
```
Expected error: `{"success": false, "message": "GITHUB_TOKEN not set in environment."}`

**With Token (after .env setup):**
```bash
curl -X POST http://localhost:8000/api/v1/models/test-connection
```
Expected success:
```json
{
  "success": true,
  "message": "GitHub Models API connection successful.",
  "response": "OK"
}
```

### A2. Test Chat Endpoint

**Basic chat (without brain):**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Help me plan my week",
    "context": {}
  }'
```

Expected response structure:
```json
{
  "route": "planner",
  "result": {
    "agent": "planner",
    "summary": "Created a practical plan...",
    "actions": [
      {
        "title": "Define weekly goals",
        "details": "Break the goal into 3 concrete outcomes.",
        "priority": "medium"
      }
    ]
  }
}
```

**Chat with context (boss profile):**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "najmeh",
    "message": "I need to ship a production system this week",
    "context": {
      "boss_context": "Najmeh, goals: [Ship system, Rest more]",
      "assistant_skills": "planning: advanced, scheduling: advanced"
    }
  }'
```

### A3. Test Profile Management

**Get assistant profile:**
```bash
curl http://localhost:8000/api/v1/profiles/assistant
```

Expected:
```json
{
  "assistant_name": "multi-agent-assistant",
  "email": null,
  "version": "0.1.0",
  "skills": [],
  "supported_agents": ["planner", "calendar", "finance", "wellness", "general"],
  "instructions": null,
  "guardrails": []
}
```

**Create/update assistant profile:**
```bash
curl -X POST http://localhost:8000/api/v1/profiles/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "email": "assistant@example.com",
    "skills": [
      {
        "skill": "planning",
        "level": "advanced",
        "description": "Goal setting and roadmap creation"
      },
      {
        "skill": "scheduling",
        "level": "advanced",
        "description": "Calendar and time management"
      }
    ],
    "instructions": "Be concise and actionable. Prioritize deep work.",
    "guardrails": ["No scheduling past 9pm", "Protect morning focus time"]
  }'
```

**Create boss (user) profile:**
```bash
curl -X POST http://localhost:8000/api/v1/profiles/boss/najmeh \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Najmeh",
    "email": "najmeh@example.com",
    "timezone": "Australia/Sydney",
    "goals": ["Ship production system by Friday", "Improve work-life balance", "Learn Rust"],
    "constraints": ["Max 50 hours/week coding", "No meetings before 10am"],
    "summary": "PhD engineer, robotics background. Prefers deep work blocks."
  }'
```

**Get boss profile:**
```bash
curl http://localhost:8000/api/v1/profiles/boss/najmeh
```

**Chat with populated profiles:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "najmeh",
    "message": "I have 3 days to deliver. Help me prioritize.",
    "context": {}
  }'
```

The brain will now have access to:
- Assistant skills: planning (advanced), scheduling (advanced)
- Boss context: Najmeh, goals include shipping system, constraints include max hours

---

## Part B: Unit Tests

### B1. Run All Tests
```bash
cd services/orchestrator
pip install pytest pytest-httpx

# Run all tests
pytest tests/ -v

# Run only GitHub Models tests
pytest tests/test_github_models.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### B2. Run Specific Test
```bash
# Test GitHub Models client initialization
pytest tests/test_github_models.py::TestGitHubModelsClient::test_init_success -v

# Test health endpoint
pytest tests/test_health.py -v

# Test agent with brain
pytest tests/test_github_models.py::TestSpecialistAgentsWithBrain -v
```

### B3. View Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # macOS
# or
start htmlcov\index.html  # Windows
```

---

## Part C: Integration Tests (End-to-End)

### C1. Full Chat Flow Test

Create `test_e2e.py`:
```python
import httpx
import os

BASE_URL = "http://localhost:8000/api/v1"

def test_full_flow():
    """Test complete flow: profiles → chat → models."""
    
    # 1. Create assistant profile
    resp = httpx.post(
        f"{BASE_URL}/profiles/assistant",
        json={
            "email": "assistant@test.com",
            "skills": [
                {"skill": "planning", "level": "advanced", "description": "Planning"}
            ]
        }
    )
    assert resp.status_code == 200
    print("✓ Assistant profile created")
    
    # 2. Create boss profile
    resp = httpx.post(
        f"{BASE_URL}/profiles/boss/test_user",
        json={
            "name": "Test User",
            "goals": ["Complete project"],
            "constraints": ["Max 8 hours/day"]
        }
    )
    assert resp.status_code == 200
    print("✓ Boss profile created")
    
    # 3. Send chat message
    resp = httpx.post(
        f"{BASE_URL}/chat",
        json={
            "user_id": "test_user",
            "message": "Help me plan my project",
            "context": {}
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    assert "summary" in data["result"]
    assert "actions" in data["result"]
    print("✓ Chat endpoint returned result")
    
    # 4. Test GitHub Models connection
    resp = httpx.post(f"{BASE_URL}/models/test-connection")
    if os.getenv("GITHUB_MODELS_ENABLED") == "true":
        assert resp.status_code == 200
        data = resp.json()
        print(f"✓ GitHub Models: {data['message']}")
    else:
        print("⊘ GitHub Models not enabled (skipped)")

if __name__ == "__main__":
    test_full_flow()
    print("\n✅ All integration tests passed!")
```

Run it:
```bash
python test_e2e.py
```

---

## Part D: Load Testing (Optional)

### D1. Test Agent Response Time

```bash
# Measure response time
time curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Plan my week", "context": {}}'
```

### D2. Concurrent Requests

```bash
# Install Apache Bench
# macOS: brew install httpd
# Windows: Download from Apache

# Test 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/api/v1/health
```

---

## Part E: Environment Configuration Testing

### E1. Test Different Models

```bash
# In .env, try different models:
# GITHUB_MODELS_MODEL=gpt-4o-mini        (fast, default)
# GITHUB_MODELS_MODEL=claude-3.5-sonnet  (better reasoning)
# GITHUB_MODELS_MODEL=llama-2-70b        (open source)

# After changing, restart backend and test:
curl -X POST http://localhost:8000/api/v1/models/test-connection
```

### E2. Test Profile Persistence

```bash
# Create profile
curl -X POST http://localhost:8000/api/v1/profiles/boss/test \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "goals": ["Goal1"]}'

# Restart backend (kill process, start again)

# Verify profile still exists
curl http://localhost:8000/api/v1/profiles/boss/test
# Should return the profile you created
```

---

## Part F: Debugging & Logging

### F1. Enable Verbose Logging

```bash
# Run backend with debug logging
cd services/orchestrator
python -m uvicorn app.main:app --reload --log-level debug
```

### F2. Check Log Output

Look for:
- `GitHubModelsClient initialized with token`
- `Calling GitHub Models API with model: gpt-4o-mini`
- `Profile loaded: BossProfile(boss_id=...)`
- `Coordinator routing message to: planner`

### F3. Inspect API Requests

```bash
# Install httpie for cleaner output
pip install httpie

# Test with HTTPie
http POST http://localhost:8000/api/v1/chat \
  user_id=test \
  message="Plan my week" \
  context:='{}' \
  -v  # Shows request/response headers
```

---

## Test Checklist

Use this checklist when testing:

### Configuration
- [ ] Backend starts without errors
- [ ] Health check returns `{"status": "ok"}`
- [ ] `test-connection` endpoint works

### GitHub Models
- [ ] Models test returns success when `GITHUB_MODELS_ENABLED=true` and `GITHUB_TOKEN` set
- [ ] Models test returns error when token missing
- [ ] Chat endpoint returns valid response structure
- [ ] Agent routing works (planner/calendar/finance/wellness/general)

### Profiles
- [ ] Create assistant profile with skills
- [ ] Create boss profile with goals/constraints
- [ ] Profiles persist after restart
- [ ] Chat includes profile context in response

### Brain Integration
- [ ] Chat responses differ when brain enabled vs disabled
- [ ] Brain provides context-aware responses (respects boss constraints)
- [ ] Fallback works when brain API fails

### Edge Cases
- [ ] Empty message handling
- [ ] Unknown user_id (uses default profile)
- [ ] Very long context
- [ ] Special characters in goals/constraints
- [ ] Missing required profile fields

---

## Debugging Common Issues

### Issue: "GITHUB_TOKEN not set"
```bash
# Check .env
cat .env | grep GITHUB_TOKEN
# Should output: GITHUB_TOKEN=ghp_XXXXXXXXX (not blank)

# Restart backend after updating .env
```

### Issue: Chat returns placeholder responses instead of AI
```bash
# Check if models are enabled
curl -X POST http://localhost:8000/api/v1/models/test-connection

# Check token is valid
# Go to https://github.com/settings/tokens to verify

# Check model name is correct
# Should match available models at https://github.com/models
```

### Issue: Profile not persisting
```bash
# Check data directory exists
ls -la data/
# Should exist after first profile save

# Check file permissions
chmod 755 data/

# View saved profile
cat data/boss_profile.json
```

### Issue: Slow responses
```bash
# Increase timeout in .env
GITHUB_MODELS_TIMEOUT=60

# Check internet connection
curl -I https://models.inference.ai.azure.com

# Test different model (faster)
GITHUB_MODELS_MODEL=gpt-4o-mini  # Fastest
```

---

## Production Testing

Before deploying:

1. **Run full test suite**
   ```bash
   pytest tests/ -v --cov=app
   ```

2. **Test in staging environment**
   ```bash
   APP_ENV=staging python -m uvicorn app.main:app
   ```

3. **Load test with production settings**
   ```bash
   ab -n 1000 -c 50 http://staging:8000/api/v1/health
   ```

4. **Verify profiles are backed up**
   ```bash
   cp data/assistant_profile.json backups/
   cp data/boss_profile.json backups/
   ```

5. **Test failover (brain unavailable)**
   - Temporarily disable `GITHUB_MODELS_ENABLED=false`
   - Verify fallback responses work

---

## Questions?

For detailed troubleshooting, see:
- [INSTALLATION.md](../INSTALLATION.md) — Setup issues
- [docs/github_models_setup.md](../docs/github_models_setup.md) — Model configuration
- [docs/profiles_and_skills.md](../docs/profiles_and_skills.md) — Profile reference
