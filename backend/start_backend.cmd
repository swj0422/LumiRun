@echo off
echo Stopping processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process %%a
    taskkill /F /PID %%a 2>nul
)
echo Waiting for port to be released...
timeout /t 3 /nobreak >nul
echo Starting backend server...
python -m uvicorn main:app --host 0.0.0.0 --port 8000