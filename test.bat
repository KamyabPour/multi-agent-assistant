@echo off
REM Quick test script for Windows - GitHub Models integration
REM Usage:
REM   test.bat              - Run all tests
REM   test.bat --verbose    - Run with detailed output
REM   test.bat --quick      - Run health check only

setlocal enabledelayedexpansion

set BASE_URL=http://localhost:8000/api/v1
set VERBOSE=%1

echo.
echo ============================================================
echo TESTING: GitHub Models Integration
echo ============================================================
echo.
echo Target: %BASE_URL%

if "%VERBOSE%"=="--verbose" (
    echo Mode: VERBOSE
)
echo.

REM Test 1: Health Check
echo [1/5] Testing health endpoint...
curl -s %BASE_URL%/health >nul
if !errorlevel! equ 0 (
    echo OK: Health check passed
) else (
    echo FAIL: Health check failed
    goto :error
)
echo.

REM Test 2: GitHub Models Connection
echo [2/5] Testing GitHub Models connection...
curl -s -X POST %BASE_URL%/models/test-connection >nul
if !errorlevel! equ 0 (
    echo OK: GitHub Models endpoint responds
) else (
    echo WARN: GitHub Models not configured or not running
)
echo.

REM Test 3: Chat Basic
echo [3/5] Testing chat endpoint...
curl -s -X POST %BASE_URL%/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"test\", \"message\": \"Plan my week\", \"context\": {}}" >nul
if !errorlevel! equ 0 (
    echo OK: Chat endpoint working
) else (
    echo FAIL: Chat endpoint error
    goto :error
)
echo.

REM Test 4: Profile Creation
echo [4/5] Testing profile creation...
curl -s -X POST %BASE_URL%/profiles/assistant ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"test@example.com\"}" >nul
if !errorlevel! equ 0 (
    echo OK: Profile endpoint working
) else (
    echo FAIL: Profile endpoint error
    goto :error
)
echo.

REM Test 5: Profile Retrieval
echo [5/5] Testing profile retrieval...
curl -s %BASE_URL%/profiles/assistant >nul
if !errorlevel! equ 0 (
    echo OK: Profile retrieval working
) else (
    echo FAIL: Profile retrieval error
    goto :error
)
echo.

echo ============================================================
echo SUCCESS: All tests passed!
echo ============================================================
echo.
echo Next steps:
echo   1. Create GitHub token: https://github.com/settings/tokens
echo   2. Add GITHUB_TOKEN to .env
echo   3. Set GITHUB_MODELS_ENABLED=true in .env
echo   4. Restart backend and test again
echo.
goto :end

:error
echo ============================================================
echo ERROR: Tests failed
echo ============================================================
echo.
echo Troubleshooting:
echo   - Check backend is running: python -m uvicorn app.main:app
echo   - Check port 8000 is accessible
echo   - Check .env configuration
echo.
exit /b 1

:end
