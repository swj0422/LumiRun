$ErrorActionPreference = 'SilentlyContinue'
# 查找并停止占用8000端口的进程
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
foreach ($proc in $processes) {
    $pid = $proc.OwningProcess
    Write-Host "正在停止进程 $pid..."
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2
Write-Host "端口8000已释放"

# 启动后端服务
Write-Host "正在启动后端服务..."
$env:PYTHONPATH = "d:\LumiRun\LumiRun\backend"
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory "d:\LumiRun\LumiRun\backend" -WindowStyle Normal
Write-Host "后端服务启动命令已执行"