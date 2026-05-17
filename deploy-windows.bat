@echo off
setlocal enabledelayedexpansion

set "NODE_SKIP_PLATFORM_CHECK=1"
chcp 65001 >nul

echo ==============================================
echo     LumiRun System Windows Deployment Script
echo ==============================================
echo.

echo [CHECK] Administrator privileges...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    pause
    exit /b 1
)
echo OK: Running as Administrator

set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=%PROJECT_DIR%.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo ERROR: Python virtual environment not found!
    echo Please run the full deployment script first.
    pause
    exit /b 1
)

echo.
echo [RUN] Core deployment logic...
"%PYTHON_EXE%" "%PROJECT_DIR%deploy-core.py" --project-dir "%PROJECT_DIR%"

if %errorLevel% equ 0 (
    echo.
    echo ==============================================
    echo DEPLOYMENT COMPLETED SUCCESSFULLY!
    echo ==============================================
    echo.
    echo How to start:
    echo 1. Backend: cd backend ^&^& start_backend.cmd
    echo 2. Frontend: cd frontend ^&^& npm run dev
    echo.
) else (
    echo.
    echo ERROR: Deployment failed! Please check the error messages above.
    echo.
)

pause