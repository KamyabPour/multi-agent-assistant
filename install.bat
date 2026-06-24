@echo off
REM Interactive Installation Script for Windows
REM Run this to set up multi-agent-assistant with all dependencies

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Colors and formatting
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BOLD=[1m"
set "RESET=[0m"

title Multi-Agent Assistant - Installation

cls
echo.
echo ============================================================
echo Multi-Agent Assistant - Interactive Setup
echo ============================================================
echo.
echo This script will set up your assistant with:
echo   * GitHub account and personal access token
echo   * GitHub Models API ^(AI brain^)
echo   * Gmail integration ^(required^)
echo   * Assistant profile configuration
echo.
echo Requirements: Python 3.11+, Git, pip
echo.
pause

REM Check Python version
echo.
echo [1] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+ from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Python version: %PYVER%
echo.

REM Check dependencies
echo [2] Checking system dependencies...
where git >nul 2>&1
if errorlevel 1 (
    echo WARNING: Git not found. Install from git-scm.com
) else (
    echo Git: Found
)

where pip >nul 2>&1
if errorlevel 1 (
    echo WARNING: pip not found. Install Python packaging tools.
) else (
    echo pip: Found
)
echo.

REM Install backend dependencies
echo [3] Installing Python dependencies...
pip install -q playwright
cd services\orchestrator
pip install -q -e ".[dev]"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Python dependencies installed.
cd ..\..
echo.

REM GitHub setup
echo [4] GitHub Account Setup (Browser Automated)
echo.
echo GitHub is required for GitHub Models API ^(assistant brain^).
echo This installer is configured for a BRAND NEW assistant GitHub account.
echo.
set /p ASSISTANT_GITHUB_NAME="Boss input - new assistant GitHub username: "
if "%ASSISTANT_GITHUB_NAME%"=="" (
    echo ERROR: assistant GitHub username is required
    pause
    exit /b 1
)

set /p signup_email="Boss input - assistant email for GitHub ^(default: aiassistance@gmail.com^): "
if "%signup_email%"=="" set "signup_email=aiassistance@gmail.com"

echo.
echo Opening GitHub signup in your browser...
start https://github.com/signup?email=!signup_email!^&user_login=!ASSISTANT_GITHUB_NAME!
echo Browser opened to GitHub signup.
echo.
echo IMPORTANT:
echo   1. If browser is logged into a personal account, sign out first.
echo   2. Create a NEW account for assistant username: !ASSISTANT_GITHUB_NAME!
echo   3. Use assistant email: !signup_email!
echo   4. Verify email and finish signup before continuing.
echo.
pause

REM GitHub token
echo.
echo [5] GitHub Personal Access Token (Browser Automated)
echo.
echo Opening GitHub token creation page in your browser...
start https://github.com/settings/tokens/new
echo Browser opened.
echo.
echo Please complete these steps in the browser:
echo   1. Token name: multi-agent-assistant
echo   2. Expiration: 90 days
echo   3. Scopes: Check ONLY 'read:models'
echo   4. Click 'Generate token'
echo   5. Copy the token ^(shown only once!^)
echo.
set /p GITHUB_TOKEN="Paste your GitHub token: "

if "%GITHUB_TOKEN%"=="" (
    echo ERROR: GitHub token required
    pause
    exit /b 1
)
echo.

REM Gmail setup
echo [6] Gmail Setup (Browser Automated, Required)
echo.
set GMAIL_ENABLED=true
set GMAIL_FROM=
set GMAIL_PASSWORD=

echo This installer is configured for a BRAND NEW assistant Gmail account.
set /p GMAIL_FROM="Boss input - new assistant Gmail address ^(default: aiassistance@gmail.com^): "
if "%GMAIL_FROM%"=="" set "GMAIL_FROM=aiassistance@gmail.com"

echo.
echo Opening Gmail signup in your browser...
start https://accounts.google.com/signup/v2/webcreateaccount
echo Browser opened to Gmail signup.
echo.
echo IMPORTANT:
echo   1. If browser is logged into personal Gmail, sign out first.
echo   2. Create a NEW Gmail account using: %GMAIL_FROM%
echo   3. Complete phone/email verification before continuing.
echo.
pause

echo.
echo.
echo Opening Gmail app passwords in your browser...
start https://myaccount.google.com/apppasswords
echo Browser opened.
echo.
echo Please complete these steps in the browser:
echo   1. Select 'Mail' from the 'Select app' dropdown
echo   2. Select 'Windows Computer' from the 'Select device' dropdown
echo   3. Click 'Generate'
echo   4. Copy the 16-character password shown
echo.
set /p GMAIL_PASSWORD="Paste the app-specific password: "
echo.

REM Profiles
echo [7] Create Assistant Profile
echo.
echo Assistant Profile:
set /p ASSISTANT_EMAIL="Assistant email for profile ^(default: %GMAIL_FROM%^): "
if "%ASSISTANT_EMAIL%"=="" set "ASSISTANT_EMAIL=%GMAIL_FROM%"
set /p ASSISTANT_NAME="Assistant name (default: multi-agent-assistant): "
if "%ASSISTANT_NAME%"=="" set "ASSISTANT_NAME=multi-agent-assistant"

REM Save sensitive credentials to user home folder (NEVER in the repo)
set "CRED_DIR=%USERPROFILE%\.assistant"
if not exist "%CRED_DIR%" mkdir "%CRED_DIR%"

(
    echo # Assistant credentials - DO NOT SHARE OR COMMIT
    echo # Saved outside the repo at %USERPROFILE%\.assistant\credentials
    echo GITHUB_TOKEN=%GITHUB_TOKEN%
    echo GITHUB_USERNAME=%ASSISTANT_GITHUB_NAME%
    echo GMAIL_ADDRESS=%GMAIL_FROM%
    echo GMAIL_APP_PASSWORD=%GMAIL_PASSWORD%
) > "%CRED_DIR%\credentials"

echo Credentials saved to %CRED_DIR%\credentials ^(outside repo, never published^)

REM Write .env file - loads credentials from user space at runtime
echo.
echo [8] Writing configuration...

(
    echo # Generated by installation script
    echo # Secrets are stored in %%USERPROFILE%%\.assistant\credentials
    echo APP_ENV=dev
    echo APP_HOST=0.0.0.0
    echo APP_PORT=8000
    echo GITHUB_TOKEN=%GITHUB_TOKEN%
    echo GITHUB_MODELS_ENABLED=true
    echo GITHUB_MODELS_MODEL=gpt-4o-mini
    echo GITHUB_MODELS_TIMEOUT=30
    echo ASSISTANT_EMAIL_ENABLED=%GMAIL_ENABLED%
    echo ASSISTANT_EMAIL_FROM=%GMAIL_FROM%
    echo ASSISTANT_EMAIL_APP_PASSWORD=%GMAIL_PASSWORD%
    echo NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
    echo EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
) > .env

echo .env file created ^(also gitignored^).

REM Create data directory and profiles - non-sensitive only
if not exist data mkdir data

(
    echo {
    echo   "assistant_name": "%ASSISTANT_NAME%",
    echo   "email": "%ASSISTANT_EMAIL%",
    echo   "version": "0.1.0",
    echo   "skills": [
    echo     {"skill": "planning", "level": "advanced", "description": "Goal setting and roadmap creation"},
    echo     {"skill": "scheduling", "level": "advanced", "description": "Calendar management"}
    echo   ],
    echo   "supported_agents": ["planner", "calendar", "finance", "wellness", "general"],
    echo   "instructions": "Be concise and actionable.",
    echo   "guardrails": []
    echo }
) > data\assistant_profile.json

echo Profiles created.
echo.

REM Summary
cls
echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Configuration saved to:
echo   * %USERPROFILE%\.assistant\credentials  ^(PRIVATE - token + gmail password^)
echo   * .env                                 ^(gitignored - loaded by app^)
echo   * data/assistant_profile.json          ^(gitignored - non-sensitive profile^)
echo.
echo Next steps:
echo.
echo 1. Start the backend:
echo    cd services\orchestrator
echo    python -m uvicorn app.main:app --reload
echo.
echo 2. In another terminal, start the web frontend:
echo    cd apps\web
echo    npm install
echo    npm run dev
echo.
echo 3. Visit http://localhost:3000
echo.
echo Test the setup:
echo    python test_quick.py --verbose
echo.
echo Documentation:
echo    * INSTALLATION.md - Setup guide
echo    * docs/TESTING.md - Testing reference
echo    * docs/github_models_setup.md - GitHub Models details
echo.
pause
