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
set "VENV_DIR=%PROJECT_DIR%.venv"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"

echo.
echo [STEP 1/6] Checking system environment...

echo [CHECK] Python installation...
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.10+ first.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%a in ('python --version') do set PYTHON_VERSION=%%a
echo OK: Python %PYTHON_VERSION% installed

echo [CHECK] Node.js installation...
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Node.js not found! Please install Node.js 18+ first.
    pause
    exit /b 1
)
for /f "tokens=1 delims=v" %%a in ('node --version') do set NODE_VERSION=%%a
echo OK: Node.js v%NODE_VERSION% installed

echo.
echo [STEP 2/6] Creating directory structure...

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
echo [STEP 3/6] Configuring backend environment...

if not exist "%VENV_DIR%" (
    echo [CREATE] Python virtual environment...
    python -m venv "%VENV_DIR%"
    if !errorLevel! equ 0 (
        echo OK: Virtual environment created successfully
    ) else (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
) else (
    echo OK: Virtual environment already exists
)

echo [INSTALL] Python dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
if !errorLevel! neq 0 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

pip install -r "%BACKEND_DIR%\requirements.txt"
if !errorLevel! equ 0 (
    echo OK: Python dependencies installed successfully
) else (
    echo WARN: Trying China mirror...
    pip install -r "%BACKEND_DIR%\requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    if !errorLevel! equ 0 (
        echo OK: Python dependencies installed with China mirror
    ) else (
        echo ERROR: Failed to install Python dependencies!
        pause
        exit /b 1
    )
)

echo.
echo [STEP 4/6] Configuring frontend environment...

cd /d "%FRONTEND_DIR%"

echo [INSTALL] Node.js dependencies...
npm install --loglevel=error
if !errorLevel! equ 0 (
    echo OK: Node.js dependencies installed successfully
) else (
    echo WARN: Trying China mirror...
    npm config set registry https://registry.npmmirror.com/
    npm install --loglevel=error
    if !errorLevel! equ 0 (
        echo OK: Node.js dependencies installed with China mirror
    ) else (
        echo WARN: Failed to install Node.js dependencies! Continuing with database initialization...
    )
)

echo [BUILD] Frontend project...
npm run build --loglevel=error
if !errorLevel! equ 0 (
    echo OK: Frontend project built successfully
) else (
    echo WARN: Frontend build failed! Continuing with database initialization...
)

echo.
echo [STEP 5/6] Configuring environment variables...

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
echo [STEP 6/6] Initializing database...

cd /d "%BACKEND_DIR%"

echo [INIT] Creating database tables...
echo Running: "%VENV_DIR%\Scripts\python.exe" "%BACKEND_DIR%\init_db.py"
"%VENV_DIR%\Scripts\python.exe" "%BACKEND_DIR%\init_db.py"
if !errorLevel! equ 0 (
    echo OK: Database tables created successfully
) else (
    echo ERROR: Failed to create database tables!
    echo Please check:
    echo 1. MySQL server is running
    echo 2. Database credentials in backend/.env are correct
    echo 3. Database 'lumirun' exists
    pause
    exit /b 1
)

echo [INIT] Initializing roles, users and permissions...
echo Running: "%VENV_DIR%\Scripts\python.exe" "%BACKEND_DIR%\init_data.py"
"%VENV_DIR%\Scripts\python.exe" "%BACKEND_DIR%\init_data.py"
if !errorLevel! equ 0 (
    echo OK: Database data initialized successfully
) else (
    echo ERROR: Failed to initialize database data!
    echo Please check:
    echo 1. MySQL server is running
    echo 2. Database credentials in backend/.env are correct
    pause
    exit /b 1
)

echo.
echo ==============================================
echo DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ==============================================
echo.
echo Default Accounts:
echo admin@example.com / admin / Password123
echo teacher@example.com / teacher / Password123
echo student@example.com / student / Password123
echo.
echo Security: Please change default passwords after first login!
echo.
echo How to start:
echo 1. Backend: cd backend && start_backend.cmd
echo 2. Frontend: cd frontend && npm run dev
echo.
pause
