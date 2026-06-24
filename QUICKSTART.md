# Quick Start - Interactive Installation with Browser Automation

**One command to set up everything:**

## macOS / Linux
```bash
python install.py
```

## Windows
```bash
install.bat
```

---

## What the Installer Does

The installer guides you through all setup steps with **browser automation**:

1. ✅ **Python & Dependencies Check**
   - Verifies Python 3.11+
   - Checks git, pip, curl availability
   - Installs Python dependencies (including Playwright for browser automation)

2. ✅ **GitHub Account & Token (Browser Automated)**
   - Automatically opens GitHub signup in your browser
   - Pre-fills your email
   - **You only need to**: Create password, verify email
   - Automatically opens GitHub token settings page
   - **You only need to**: Select scopes and copy token

3. ✅ **GitHub Models API (AI Brain)**
   - Tests token connectivity
   - Sets up the LLM brain for intelligent responses
   - Selects gpt-4o-mini as default (free, fast)

4. ✅ **Gmail Setup (Browser Automated, Optional)**
   - Automatically opens Gmail signup (if needed)
   - Automatically opens Gmail app passwords page
   - **You only need to**: Generate and copy app password

5. ✅ **Profile Configuration**
   - Creates assistant profile (skills, email)
   - Creates your (boss) profile (name, goals, constraints)
   - Auto-fills your email from Gmail setup (if enabled)
   - Saves profiles to `data/` directory

6. ✅ **Configuration & Testing**
   - Writes `.env` file with all settings
   - Verifies backend connectivity
   - Creates `data/` directory structure

---

## Step-by-Step Walkthrough

### Step 1: Start the Installer

**Python (recommended):**
```bash
python install.py
```

**Windows Batch:**
```bash
install.bat
```

The installer will display a welcome message and check your system.

---

### Step 2: Check Dependencies

The installer verifies:
- ✓ Python 3.11+
- ✓ Git
- ✓ pip

If any are missing, install them and run again.


---

### Step 3: GitHub Account (Browser Automation)

**If you DON'T have a GitHub account:**
1. Installer **automatically opens** GitHub signup in your browser
2. Your email is **pre-filled** in the signup form
3. **You only need to:**
   - Create a strong password
   - Enter a username
   - Verify your email address
4. Press Enter when done

**If you ALREADY have a GitHub account:**
- Just press `y` and continue

---

### Step 4: Generate GitHub Token (Browser Automation)

1. Installer **automatically opens** GitHub token creation page
2. The page shows where to set:
   - Token name: `multi-agent-assistant`
   - Expiration: `90 days`
   - Scope: `read:models` (ONLY)
3. **You only need to:**
   - Check the `read:models` checkbox
   - Click "Generate token"
   - Copy the token from the page
4. Paste it into the terminal

**Why only `read:models`?** It's the minimal permission needed for security.

---

### Step 5: Gmail Setup (Browser Automation, Optional)

**If you want email notifications:**

1. Installer **automatically opens** Gmail signup (if needed)
2. **You only need to:** Create account and verify

3. Installer **automatically opens** Gmail app passwords page
4. **You only need to:**
   - Select "Mail" and "Windows Computer" dropdowns
   - Click "Generate"
   - Copy the 16-character password
5. Paste it into the terminal

**Skip this step?** Press `n` to skip email setup.

---

### Step 6: Create Your Profiles

**Assistant Profile:**
- Email address (for notifications)
- Skills (planning, scheduling, etc.)

**Boss Profile (You):**
- Name
- Email (**auto-filled from Gmail setup** if enabled)
- Timezone
- Goals (e.g., "Ship system by Friday", "Learn Rust")
- Constraints (e.g., "Max 50 hours/week")

The installer saves these for personalized responses.

---

### Step 7: Configuration Saved

The installer creates:
```
.env                          ← All environment variables
data/
  ├── assistant_profile.json  ← Assistant skills & email
  └── boss_profile.json       ← Your goals & constraints
```

---

## Next: Start the Application

Once installation completes:

### Terminal 1: Backend
```bash
cd services/orchestrator
python -m uvicorn app.main:app --reload
```

Backend runs on http://localhost:8000

### Terminal 2: Frontend
```bash
cd apps/web
npm install
npm run dev
```

Frontend runs on http://localhost:3000

---

## Test It

```bash
# Quick validation
python test_quick.py --verbose
```

Expected output:
```
✓ PASS | Health check
✓ PASS | GitHub Models test-connection
✓ PASS | Chat (basic)
✓ PASS | Get assistant profile
✓ PASS | Create boss profile
✓ PASS | Chat (with context)

Summary: 6/6 test categories passed ✅
```

---

## Troubleshooting

### "Python 3.11+ required"
Install Python 3.11 or higher from https://python.org

### "Git not found"
Install Git from https://git-scm.com

### "Failed to install dependencies"
```bash
cd services/orchestrator
pip install --upgrade pip
pip install -r requirements.txt
```

### GitHub token test fails
- Check token starts with `ghp_`
- Verify token has `read:models` scope
- Go to https://github.com/settings/tokens to check

### Gmail test fails
- Verify 2-Step Verification is enabled
- Check app-specific password (not your regular password)
- Ensure ASSISTANT_EMAIL_ENABLED=true in .env

---

## What's Automated vs. Manual

### Automated (Installer Does It)
✅ Python dependency installation
✅ .env file creation
✅ Profile JSON generation
✅ Connectivity testing
✅ Configuration validation

### Guided (Installer Prompts You)
📝 GitHub account creation (opens browser, you create)
📝 GitHub token generation (opens settings page, you copy)
📝 Gmail setup (opens security page, you enable 2FA)
📝 Profile information (you enter your goals/constraints)

---

## Advanced Options

### Skip GitHub Models
```bash
python install.py --skip-github-models
# Assistant will use fallback responses instead of AI
```

### Skip Gmail
```bash
python install.py --skip-gmail
# No email notifications (can enable later manually)
```

### Reconfigure Later

To update settings after installation:

**Edit .env:**
```bash
# Update environment variables
nano .env
# Restart backend
```

**Update profiles:**
```bash
# API endpoints
curl -X POST http://localhost:8000/api/v1/profiles/assistant ...
curl -X POST http://localhost:8000/api/v1/profiles/boss/user123 ...
```

---

## File Overview

| File | Purpose |
|------|---------|
| `install.py` | Interactive installer (Python) |
| `install.bat` | Interactive installer (Windows batch) |
| `.env` | Generated environment variables |
| `data/assistant_profile.json` | Generated assistant configuration |
| `data/boss_profile.json` | Generated user profile |

---

## Questions?

- **Setup help**: See [INSTALLATION.md](INSTALLATION.md)
- **GitHub Models details**: See [docs/github_models_setup.md](docs/github_models_setup.md)
- **Testing**: See [docs/TESTING.md](docs/TESTING.md)
- **Profile system**: See [docs/profiles_and_skills.md](docs/profiles_and_skills.md)

---

**Ready to install?**

```bash
python install.py
```

or (Windows)

```bash
install.bat
```
