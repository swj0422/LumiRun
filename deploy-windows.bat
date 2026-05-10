@echo off
chcp 65001 >nul
echo ==============================================
echo     逐光成长系统 (LumiRun) Windows 部署脚本
echo ==============================================
echo.

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员身份运行此脚本！
    pause
    exit /b 1
)

:: 设置变量
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"
set "PYTHON_EXE=python"

echo [1/5] 检查系统环境...

:: 检查 Python
where %PYTHON_EXE% >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误：未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo ✓ Python 已安装

:: 检查 Node.js
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误：未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
echo ✓ Node.js 已安装

echo.
echo [2/5] 创建目录结构...

if not exist "%PROJECT_DIR%logs" mkdir "%PROJECT_DIR%logs"
if not exist "%PROJECT_DIR%backend\uploads" mkdir "%PROJECT_DIR%backend\uploads"
echo ✓ 目录结构已创建

echo.
echo [3/5] 配置后端环境...

:: 检查虚拟环境
if not exist "%VENV_DIR%" (
    echo 创建 Python 虚拟环境...
    %PYTHON_EXE% -m venv "%VENV_DIR%"
    echo ✓ 虚拟环境已创建
)

:: 激活虚拟环境并安装依赖
call "%VENV_DIR%\Scripts\activate.bat"
echo 安装 Python 依赖...
pip install -r "%BACKEND_DIR%\requirements.txt"
echo ✓ Python 依赖已安装

echo.
echo [4/5] 配置前端环境...

cd "%FRONTEND_DIR%"
echo 安装 Node.js 依赖...
npm install
echo ✓ Node.js 依赖已安装

echo 构建前端项目...
npm run build
echo ✓ 前端项目已构建

echo.
echo [5/5] 配置环境变量...

:: 复制环境变量模板
if not exist "%BACKEND_DIR%\.env" (
    copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env"
    echo ✓ 后端环境配置已创建
)

if not exist "%FRONTEND_DIR%\.env.local" (
    copy "%FRONTEND_DIR%\.env.example" "%FRONTEND_DIR%\.env.local"
    echo ✓ 前端环境配置已创建
)

echo.
echo ==============================================
echo 部署完成！
echo ==============================================
echo.
echo 启动方式：
echo 1. 启动后端服务：
echo    cd backend
echo    .venv\Scripts\activate
echo    uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo 2. 启动前端开发服务器：
echo    cd frontend
echo    npm run dev
echo.
echo 访问地址：http://localhost:3003
echo.
pause