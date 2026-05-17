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

$PROJECT_DIR = (Get-Location).Path
$PYTHON_EXE = "$PROJECT_DIR\.venv\Scripts\python.exe"

if (-not (Test-Path -Path $PYTHON_EXE)) {
    Write-Host "ERROR: Python virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run the full deployment script first." -ForegroundColor Yellow
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "[RUN] Core deployment logic..." -ForegroundColor Cyan
& $PYTHON_EXE "$PROJECT_DIR\deploy-core.py" --project-dir "$PROJECT_DIR"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==============================================" -ForegroundColor Cyan
    Write-Host "DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "==============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "How to start:" -ForegroundColor Gray
    Write-Host "1. Backend: cd backend && start_backend.cmd" -ForegroundColor Gray
    Write-Host "2. Frontend: cd frontend && npm run dev" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Deployment failed! Please check the error messages above." -ForegroundColor Red
    Write-Host ""
}

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")