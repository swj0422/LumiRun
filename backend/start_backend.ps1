$ErrorActionPreference = 'SilentlyContinue'

# 停止占用8000端口的进程
Write-Host "Stopping processes on port 8000..."
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
foreach ($proc in $processes) {
    if ($proc.OwningProcess -ne 0) {
        Write-Host "Stopping process $($proc.OwningProcess)..."
        try {
            Stop-Process -Id $proc.OwningProcess -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Host "Failed to stop process $($proc.OwningProcess)"
        }
    }
}

# 等待端口释放
Write-Host "Waiting for port to be released..."
Start-Sleep -Seconds 3

# 启动后端服务
Write-Host "Starting backend server..."
$scriptBlock = {
    Set-Location "d:\LumiRun\LumiRun\backend"
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", $scriptBlock

Write-Host "Backend server started in a new window"