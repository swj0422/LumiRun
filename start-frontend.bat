@echo off
setlocal

set "NODE_SKIP_PLATFORM_CHECK=1"
set "NODE_OPTIONS=--openssl-legacy-provider"

cd /d "%~dp0frontend"

echo Starting frontend development server...
echo.

npm run dev

pause
