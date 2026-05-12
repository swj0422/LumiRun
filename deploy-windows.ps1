param(
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "    LumiRun System Windows Deployment Script" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[CHECK] Administrator privileges..." -ForegroundColor Yellow
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: Please run this script as Administrator!" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host "OK: Running as Administrator" -ForegroundColor Green

$PROJECT_DIR = (Get-Location).Path + "\"
$VENV_DIR = $PROJECT_DIR + ".venv"
$BACKEND_DIR = $PROJECT_DIR + "backend"
$FRONTEND_DIR = $PROJECT_DIR + "frontend"

Write-Host ""
Write-Host "[STEP 1/5] Checking system environment..." -ForegroundColor Cyan

Write-Host "[CHECK] Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Python not found" }
    Write-Host "OK: Python $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python not found! Please install Python 3.10+ first." -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "[CHECK] Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "OK: Node.js $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Node.js not found! Please install Node.js 18+ first." -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "[STEP 2/5] Creating directory structure..." -ForegroundColor Cyan

if (-not (Test-Path -Path "$PROJECT_DIR\logs")) {
    Write-Host "[CREATE] logs directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "$PROJECT_DIR\logs" | Out-Null
    Write-Host "OK: logs directory created" -ForegroundColor Green
} else {
    Write-Host "OK: logs directory exists" -ForegroundColor Green
}

if (-not (Test-Path -Path "$BACKEND_DIR\uploads")) {
    Write-Host "[CREATE] backend/uploads directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "$BACKEND_DIR\uploads" | Out-Null
    Write-Host "OK: backend/uploads directory created" -ForegroundColor Green
} else {
    Write-Host "OK: backend/uploads directory exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "[STEP 3/5] Configuring backend environment..." -ForegroundColor Cyan

if (-not (Test-Path -Path "$VENV_DIR") -or $Force) {
    Write-Host "[CREATE] Python virtual environment..." -ForegroundColor Yellow
    python -m venv "$VENV_DIR"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    Write-Host "OK: Virtual environment created successfully" -ForegroundColor Green
} else {
    Write-Host "OK: Virtual environment already exists" -ForegroundColor Green
}

Write-Host "[INSTALL] Python dependencies..." -ForegroundColor Yellow
$activateScript = "$VENV_DIR\Scripts\Activate.ps1"
& "$activateScript"
pip install -r "$BACKEND_DIR\requirements.txt"
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Python dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "WARN: Trying China mirror..." -ForegroundColor Yellow
    pip install -r "$BACKEND_DIR\requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Python dependencies installed with China mirror" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to install Python dependencies!" -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

Write-Host ""
Write-Host "[STEP 4/5] Configuring frontend environment..." -ForegroundColor Cyan

Set-Location "$FRONTEND_DIR"

Write-Host "[INSTALL] Node.js dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Node.js dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "WARN: Trying China mirror..." -ForegroundColor Yellow
    npm config set registry https://registry.npmmirror.com/
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Node.js dependencies installed with China mirror" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to install Node.js dependencies!" -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

Write-Host "[BUILD] Frontend project..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Frontend project built successfully" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to build frontend project!" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "[STEP 5/6] Configuring environment variables..." -ForegroundColor Cyan

if (-not (Test-Path -Path "$BACKEND_DIR\.env")) {
    Write-Host "[COPY] Backend environment config..." -ForegroundColor Yellow
    Copy-Item -Path "$BACKEND_DIR\.env.example" -Destination "$BACKEND_DIR\.env"
    Write-Host "OK: Backend environment config created" -ForegroundColor Green
} else {
    Write-Host "OK: Backend environment config exists" -ForegroundColor Green
}

if (-not (Test-Path -Path "$FRONTEND_DIR\.env.local")) {
    Write-Host "[COPY] Frontend environment config..." -ForegroundColor Yellow
    Copy-Item -Path "$FRONTEND_DIR\.env.example" -Destination "$FRONTEND_DIR\.env.local"
    Write-Host "OK: Frontend environment config created" -ForegroundColor Green
} else {
    Write-Host "OK: Frontend environment config exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "[STEP 6/6] Initializing database..." -ForegroundColor Cyan

Write-Host "[INIT] Creating database tables..." -ForegroundColor Yellow
python "$BACKEND_DIR\init_db.py"
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Database tables created successfully" -ForegroundColor Green
} else {
    Write-Host "WARN: Failed to create database tables. Check database configuration." -ForegroundColor Yellow
}

Write-Host "[INIT] Initializing roles, users and permissions..." -ForegroundColor Yellow
python "$BACKEND_DIR\init_data.py"
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Database data initialized successfully" -ForegroundColor Green
} else {
    Write-Host "WARN: Failed to initialize database data. Check database configuration." -ForegroundColor Yellow
}

Set-Location $PROJECT_DIR

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Default Accounts:" -ForegroundColor Gray
Write-Host "admin@example.com / admin / Password123" -ForegroundColor Gray
Write-Host "teacher@example.com / teacher / Password123" -ForegroundColor Gray
Write-Host "student@example.com / student / Password123" -ForegroundColor Gray
Write-Host ""
Write-Host "Security: Please change default passwords after first login!" -ForegroundColor Yellow
Write-Host ""
Write-Host "How to start:" -ForegroundColor Gray
Write-Host "1. Backend: cd backend && start_backend.cmd" -ForegroundColor Gray
Write-Host "2. Frontend: cd frontend && npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
