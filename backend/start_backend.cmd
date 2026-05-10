@echo off
cd /d "%~dp0"

echo Stopping processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process %%a
    taskkill /F /PID %%a 2>nul
)
echo Waiting for port to be released...
timeout /t 3 /nobreak >nul

echo Starting backend server...
echo Using virtual environment Python...

:: Activate virtual environment and start server
if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
) else (
    echo ERROR: Virtual environment not found!
    echo Please run deploy-windows.bat first
    pause
    exit /b 1
)