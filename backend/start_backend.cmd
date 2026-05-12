@echo off
cd /d "%~dp0"

set "PORT=8000"
set "HOST=0.0.0.0"
set "ENV_FILE=.env"

echo ==============================================
echo LumiRun Backend Server Starter
echo ==============================================
echo.

:: Check if .env file exists
if exist "%ENV_FILE%" (
    echo [INFO] Found .env file: %ENV_FILE%
    echo [INFO] Loading environment variables...
    
    :: Read .env file with better parsing
    for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
        set "key=%%a"
        set "value=%%b"
        
        :: Skip comments and empty lines
        if not "!key!"=="" (
            if not "!key:~0,1!"=="#" (
                if "!key!"=="PORT" (
                    set "PORT=!value!"
                    echo [INFO] Loaded PORT=%PORT% from .env
                )
                if "!key!"=="HOST" (
                    set "HOST=!value!"
                    echo [INFO] Loaded HOST=%HOST% from .env
                )
            )
        )
    )
) else (
    echo [WARN] .env file not found, using default settings
    echo [INFO] PORT=%PORT% (default)
    echo [INFO] HOST=%HOST% (default)
)

echo.
echo [INFO] Stopping processes on port %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
    echo [INFO] Stopping process PID %%a
    taskkill /F /PID %%a 2>nul
)
echo [INFO] Waiting for port to be released...
timeout /t 3 /nobreak >nul

echo.
echo [INFO] Starting backend server on %HOST%:%PORT%...
echo [INFO] Using Python from virtual environment...
set "VENV_PYTHON=..\.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    set "VENV_PYTHON=.venv\Scripts\python.exe"
)

if exist "%VENV_PYTHON%" (
    echo [INFO] Found Python: %VENV_PYTHON%
    echo.
    "%VENV_PYTHON%" -m uvicorn main:app --host %HOST% --port %PORT%
) else (
    echo [ERROR] Virtual environment not found!
    echo [ERROR] Expected path: %VENV_PYTHON%
    echo [ERROR] Please run deploy-windows.bat first
    pause
    exit /b 1
)