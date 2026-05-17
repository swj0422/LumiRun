@echo off
setlocal enabledelayedexpansion

set "NODE_SKIP_PLATFORM_CHECK=1"
chcp 65001 >nul

echo ==============================================
echo     LumiRun - Database Initialization Only
echo ==============================================
echo.

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "BACKEND_DIR=%PROJECT_DIR%backend"

echo [CHECK] Administrator privileges...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    pause
    exit /b 1
)
echo OK: Running as Administrator

cd /d "%BACKEND_DIR%"

echo.
echo [STEP 1/2] Creating database tables...
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

echo.
echo [STEP 2/2] Initializing roles, users and permissions...
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
echo DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!
echo ==============================================
echo.
echo Default Accounts:
echo admin@example.com / admin / Password123
echo teacher@example.com / teacher / Password123
echo student@example.com / student / Password123
echo.
echo Security: Please change default passwords after first login!
echo.
pause
