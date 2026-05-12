@echo off
cd /d "%~dp0"

set "PORT=8000"
set "HOST=0.0.0.0"

if exist ".env" (
    echo Loading environment variables from .env...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "key=%%a"
        set "value=%%b"
        if not "!key:~0,1!"=="#" (
            if "!key!"=="PORT" set "PORT=!value!"
            if "!key!"=="HOST" set "HOST=!value!"
        )
    )
)

echo Stopping processes on port %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
    echo Stopping process %%a
    taskkill /F /PID %%a 2>nul
)
echo Waiting for port to be released...
timeout /t 3 /nobreak >nul

echo Starting backend server on %HOST%:%PORT%...
set "VENV_PYTHON=..\.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" set "VENV_PYTHON=.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" -m uvicorn main:app --host %HOST% --port %PORT%
) else (
    echo ERROR: Virtual environment not found!
    echo Please run deploy-windows.bat first
    pause
    exit /b 1
)