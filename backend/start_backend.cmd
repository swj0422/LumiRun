@echo off
cd /d "%~dp0"

:: 读取 .env 文件中的配置
set "PORT=8000"
set "HOST=0.0.0.0"

if exist ".env" (
    echo Loading environment variables from .env...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="PORT" set "PORT=%%b"
        if "%%a"=="HOST" set "HOST=%%b"
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
if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host %HOST% --port %PORT%
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn app.main:app --host %HOST% --port %PORT%
) else (
    echo ERROR: Virtual environment not found!
    echo Please run deploy-windows.bat first
    pause
    exit /b 1
)