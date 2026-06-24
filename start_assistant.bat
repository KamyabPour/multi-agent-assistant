@echo off
setlocal
title AI Assistant - Starting...
cd /d "%~dp0"

echo.
echo ============================================================
echo   AI Assistant - Launching
echo ============================================================
echo.

REM Check .env exists
if not exist ".env" (
    echo ERROR: .env not found. Run install.bat first.
    pause
    exit /b 1
)

REM Check if frontend node_modules exist
set "FRONTEND_READY=0"
if exist "apps\web\node_modules" set "FRONTEND_READY=1"

REM Start backend in a new window
echo Starting backend...
start "AI Assistant - Backend" cmd /k "cd /d "%~dp0services\orchestrator" && python -m uvicorn app.main:app --reload"

REM Install frontend deps if needed (first run)
if "%FRONTEND_READY%"=="0" (
    echo Installing frontend dependencies for first time...
    cd apps\web
    call npm install --silent
    cd ..\..
)

REM Start frontend in a new window
echo Starting frontend...
start "AI Assistant - Frontend" cmd /k "cd /d "%~dp0apps\web" && npm run dev"

REM Wait for backend to be ready then open browser
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo Opening assistant in browser...
start http://localhost:3000

echo.
echo ============================================================
echo   AI Assistant is running!
echo   Backend:  http://localhost:8000
echo   Chat UI:  http://localhost:3000
echo ============================================================
echo.
echo Close the Backend and Frontend windows to stop the assistant.
echo.
pause
