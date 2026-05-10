@echo off
chcp 65001 >nul
echo ==============================================
echo     LumiRun System Windows Deployment Script
echo ==============================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this script as Administrator!
    pause
    exit /b 1
)

:: Set variables
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"
set "PYTHON_EXE=python"

echo [1/5] Checking system environment...

:: Check Python
where %PYTHON_EXE% >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Python not found. Please install Python 3.10+ first.
    pause
    exit /b 1
)
echo OK: Python installed

:: Check Node.js
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Node.js not found. Please install Node.js 18+ first.
    pause
    exit /b 1
)
echo OK: Node.js installed

echo.
echo [2/5] Creating directory structure...

if not exist "%PROJECT_DIR%logs" mkdir "%PROJECT_DIR%logs"
if not exist "%PROJECT_DIR%backend\uploads" mkdir "%PROJECT_DIR%backend\uploads"
echo OK: Directory structure created

echo.
echo [3/5] Configuring backend environment...

:: Check virtual environment
if not exist "%VENV_DIR%" (
    echo Creating Python virtual environment...
    %PYTHON_EXE% -m venv "%VENV_DIR%"
    echo OK: Virtual environment created
)

:: Activate virtual environment and install dependencies
call "%VENV_DIR%\Scripts\activate.bat"
echo Installing Python dependencies...
pip install -r "%BACKEND_DIR%\requirements.txt"
echo OK: Python dependencies installed

echo.
echo [4/5] Configuring frontend environment...

cd "%FRONTEND_DIR%"
echo Installing Node.js dependencies...
npm install
echo OK: Node.js dependencies installed

echo Building frontend project...
npm run build
echo OK: Frontend project built

echo.
echo [5/5] Configuring environment variables...

:: Copy environment templates
if not exist "%BACKEND_DIR%\.env" (
    copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env"
    echo OK: Backend environment config created
)

if not exist "%FRONTEND_DIR%\.env.local" (
    copy "%FRONTEND_DIR%\.env.example" "%FRONTEND_DIR%\.env.local"
    echo OK: Frontend environment config created
)

echo.
echo ==============================================
echo Deployment completed successfully!
echo ==============================================
echo.
echo How to start:
echo 1. Start backend service:
echo    cd backend
echo    .venv\Scripts\activate
echo    uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo 2. Start frontend development server:
echo    cd frontend
echo    npm run dev
echo.
echo Access URL: http://localhost:3003
echo.
pause