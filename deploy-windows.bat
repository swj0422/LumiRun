@echo off
setlocal enabledelayedexpansion

:: Skip Node.js platform check for older Windows versions
set NODE_SKIP_PLATFORM_CHECK=1

:: Set UTF-8 encoding
chcp 65001 >nul

echo ==============================================
echo     LumiRun System Windows Deployment Script
echo ==============================================
echo.

:: Check if running as administrator
echo [CHECK] Administrator privileges...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    pause
    exit /b 1
)
echo OK: Running as Administrator

:: Set variables
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"
set "PYTHON_EXE=python"

echo.
echo [STEP 1/5] Checking system environment...

:: Check Python
echo [CHECK] Python installation...
where %PYTHON_EXE% >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.10+ first.
    echo        Download: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%a in ('python --version') do set PYTHON_VERSION=%%a
echo OK: Python %PYTHON_VERSION% installed

:: Check Node.js
echo [CHECK] Node.js installation...
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Node.js not found! Please install Node.js 18+ first.
    echo        Download: https://nodejs.org/zh-cn/download/
    pause
    exit /b 1
)
for /f "tokens=1 delims=v" %%a in ('node --version') do set NODE_VERSION=%%a
echo OK: Node.js v%NODE_VERSION% installed

echo.
echo [STEP 2/5] Creating directory structure...

if not exist "%PROJECT_DIR%logs" (
    echo [CREATE] logs directory...
    mkdir "%PROJECT_DIR%logs"
    if !errorLevel! equ 0 (
        echo OK: logs directory created
    ) else (
        echo ERROR: Failed to create logs directory
        pause
        exit /b 1
    )
) else (
    echo OK: logs directory exists
)

if not exist "%BACKEND_DIR%\uploads" (
    echo [CREATE] backend/uploads directory...
    mkdir "%BACKEND_DIR%\uploads"
    if !errorLevel! equ 0 (
        echo OK: backend/uploads directory created
    ) else (
        echo ERROR: Failed to create backend/uploads directory
        pause
        exit /b 1
    )
) else (
    echo OK: backend/uploads directory exists
)

echo.
echo [STEP 3/5] Configuring backend environment...

:: Check virtual environment
if not exist "%VENV_DIR%" (
    echo [CREATE] Python virtual environment...
    %PYTHON_EXE% -m venv "%VENV_DIR%"
    if !errorLevel! equ 0 (
        echo OK: Virtual environment created successfully
    ) else (
        echo ERROR: Failed to create virtual environment!
        echo        Please check Python installation or try: python -m venv .venv
        pause
        exit /b 1
    )
) else (
    echo OK: Virtual environment already exists
)

:: Activate virtual environment and install dependencies
echo [INSTALL] Python dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
if !errorLevel! neq 0 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

set "PIP_MIRROR=https://mirrors.aliyun.com/pypi/simple/"

pip install -r "%BACKEND_DIR%\requirements.txt"
if !errorLevel! equ 0 (
    echo OK: Python dependencies installed successfully
) else (
    echo WARN: Failed to install with default source, trying China mirror...
    pip install -r "%BACKEND_DIR%\requirements.txt" -i %PIP_MIRROR% --trusted-host mirrors.aliyun.com
    if !errorLevel! equ 0 (
        echo OK: Python dependencies installed successfully with China mirror
    ) else (
        echo ERROR: Failed to install Python dependencies!
        echo        Please check network connection or try manual installation
        pause
        exit /b 1
    )
)

echo.
echo [STEP 4/5] Configuring frontend environment...

cd "%FRONTEND_DIR%"
set "NPM_MIRROR=https://registry.npmmirror.com/"

echo [INSTALL] Node.js dependencies...
npm install
if !errorLevel! equ 0 (
    echo OK: Node.js dependencies installed successfully
) else (
    echo WARN: Failed to install with default registry, trying China mirror...
    npm config set registry %NPM_MIRROR%
    npm install
    if !errorLevel! equ 0 (
        echo OK: Node.js dependencies installed successfully with China mirror
    ) else (
        echo ERROR: Failed to install Node.js dependencies!
        echo        Please check network connection
        pause
        exit /b 1
    )
)

echo [BUILD] Frontend project...
npm run build
if !errorLevel! equ 0 (
    echo OK: Frontend project built successfully
) else (
    echo ERROR: Failed to build frontend project!
    pause
    exit /b 1
)

echo.
echo [STEP 5/5] Configuring environment variables...

:: Copy environment templates
if not exist "%BACKEND_DIR%\.env" (
    echo [COPY] Backend environment config...
    copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env"
    if !errorLevel! equ 0 (
        echo OK: Backend environment config created
    ) else (
        echo ERROR: Failed to create backend environment config!
    )
) else (
    echo OK: Backend environment config exists
)

if not exist "%FRONTEND_DIR%\.env.local" (
    echo [COPY] Frontend environment config...
    copy "%FRONTEND_DIR%\.env.example" "%FRONTEND_DIR%\.env.local"
    if !errorLevel! equ 0 (
        echo OK: Frontend environment config created
    ) else (
        echo ERROR: Failed to create frontend environment config!
    )
) else (
    echo OK: Frontend environment config exists
)

echo.
echo ==============================================
echo DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ==============================================
echo.
echo How to start the application:
echo -----------------------------
echo 1. Open a new Command Prompt
echo 2. Run these commands:
echo    cd /d "d:\LumiRun\LumiRun"
echo    cd backend
echo    .venv\Scripts\activate
echo    uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo 3. Open another Command Prompt
echo 4. Run these commands:
echo    cd /d "d:\LumiRun\LumiRun"
echo    cd frontend
echo    npm run dev
echo.
echo Access URL: http://localhost:3003
echo.
pause