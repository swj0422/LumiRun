# 逐光成长系统 (LumiRun) - Windows 系统兼容性说明

## 支持的 Windows 版本

### 完全支持
- **Windows 10** (版本 1607 及以上)
- **Windows 11** (所有版本)
- **Windows Server 2016** 及以上
- **Windows Server 2019**
- **Windows Server 2022**

### 系统要求
- **处理器**: 64位处理器，1.4 GHz 或更快
- **内存**: 最低 4GB RAM，推荐 8GB 或更多
- **磁盘空间**: 最低 10GB 可用空间
- **网络**: 支持本地网络连接

## 软件依赖版本

### Python
- **最低版本**: 3.8
- **推荐版本**: 3.10 或 3.11
- **下载地址**: https://www.python.org/downloads/

### Node.js
- **最低版本**: 16.0
- **推荐版本**: 18 LTS 或 20 LTS
- **下载地址**: https://nodejs.org/

### MySQL
- **最低版本**: 8.0
- **推荐版本**: 8.0.x 最新稳定版
- **下载地址**: https://dev.mysql.com/downloads/mysql/

### Redis
- **最低版本**: 7.0
- **Windows 替代方案**:
  - Memurai (Redis 的 Windows 兼容版本)
  - Docker Desktop 运行 Redis 容器
  - WSL2 运行 Redis

## Windows 特殊配置

### 1. 路径处理
系统使用 `pathlib.Path` 处理文件路径，确保在 Windows 上正确处理：
- 反斜杠和正斜杠兼容
- 长路径支持（超过 260 字符）
- UNC 路径支持

### 2. 文件编码
所有文件使用 UTF-8 编码：
- 配置文件: UTF-8
- 数据库: utf8mb4 字符集
- 日志文件: UTF-8 with BOM

### 3. 服务端口
默认端口配置：
- 后端 API: 8000
- 前端开发服务器: 5173
- MySQL: 3306
- Redis: 6379

### 4. 权限要求
- 需要管理员权限运行部署和启动脚本
- 应用需要对以下目录有读写权限：
  - `backend/uploads`
  - `backend/logs`
  - `data/mysql` (如使用本地 MySQL)
  - `data/redis` (如使用本地 Redis)

## Windows Server 特殊配置

### 1. 防火墙配置
在 Windows Server 上，需要添加防火墙规则：

```powershell
# 允许后端端口
New-NetFirewallRule -DisplayName "LumiRun Backend" `
    -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# 允许前端端口（如需要）
New-NetFirewallRule -DisplayName "LumiRun Frontend" `
    -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow

# 允许 MySQL 端口（如需要远程访问）
New-NetFirewallRule -DisplayName "MySQL" `
    -Direction Inbound -LocalPort 3306 -Protocol TCP -Action Allow
```

### 2. Windows 服务注册
推荐将后端注册为 Windows 服务，实现开机自启动：

```bash
# 使用 NSSM 安装服务
nssm install LumiRunBackend "C:\Python310\python.exe" "D:\LumiRun\LumiRun\backend\main.py"
nssm set LumiRunBackend AppDirectory "D:\LumiRun\LumiRun\backend"
nssm set LumiRunBackend DisplayName "逐光成长系统后端"
nssm set LumiRunBackend Description "LumiRun Backend Service"
nssm set LumiRunBackend Start SERVICE_AUTO_START
nssm start LumiRunBackend
```

### 3. 性能优化
在 Windows Server 上，可以调整以下参数：

**MySQL 配置** (my.ini):
```ini
[mysqld]
# 增加连接数
max_connections = 200

# 缓冲池大小（根据服务器内存调整）
innodb_buffer_pool_size = 2G

# 日志设置
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
```

**Python 性能**:
- 使用 PyPy 替代 CPython（可选）
- 启用 uvloop（需要安装）
- 使用 Gunicorn + Uvicorn Workers

## 常见 Windows 问题解决

### 1. 长路径问题
Windows 默认路径长度限制为 260 字符，解决方案：

```powershell
# 启用长路径支持
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### 2. Python 脚本编码问题
确保脚本文件使用 UTF-8 编码保存，并在脚本开头添加：
```python
# -*- coding: utf-8 -*-
```

### 3. MySQL 连接问题
如果遇到 MySQL 连接错误：
1. 检查 MySQL 服务是否运行
2. 验证连接字符串中的主机名和端口
3. 确保用户权限正确
4. 检查防火墙设置

### 4. 端口占用问题
检查端口是否被占用：
```powershell
# 检查 8000 端口
netstat -ano | findstr :8000

# 终止占用端口的进程
taskkill /PID <进程ID> /F
```

### 5. 文件权限问题
如果遇到文件读写权限问题：
```powershell
# 以管理员身份运行 PowerShell
# 设置目录权限
icacls "D:\LumiRun\LumiRun\backend\uploads" /grant Users:F
icacls "D:\LumiRun\LumiRun\backend\logs" /grant Users:F
```

## Windows 特定功能

### 1. 事件日志集成
可以将应用日志集成到 Windows 事件日志：

```python
import win32evtlog
import win32con

def log_to_windows_event(message, event_type=win32con.EVENTLOG_INFORMATION_TYPE):
    handle = win32evtlog.OpenEventLog(None, "LumiRun")
    win32evtlog.ReportEvent(
        handle,
        event_type,
        0,
        1,
        None,
        [message],
        None
    )
    win32evtlog.CloseEventLog(handle)
```

### 2. 任务计划程序
可以使用 Windows 任务计划程序定期执行任务：

```powershell
# 创建定时任务
$action = New-ScheduledTaskAction -Execute "python" -Argument "D:\LumiRun\LumiRun\backend\scripts\cleanup.py"
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
Register-ScheduledTask -TaskName "LumiRun Cleanup" -Action $action -Trigger $trigger -RunLevel Highest
```

### 3. 性能监控
使用 Windows 性能监视器监控应用性能：

```powershell
# 创建性能计数器
$counter = "\Process(python)\% Processor Time"
Get-Counter -Counter $counter -SampleInterval 5 -MaxSamples 10
```

## 安全建议

### 1. Windows 安全更新
- 定期安装 Windows 更新
- 启用 Windows Defender 或其他安全软件
- 定期扫描系统漏洞

### 2. 网络安全
- 使用强密码
- 启用 Windows 防火墙
- 限制远程访问
- 使用 HTTPS（生产环境）

### 3. 文件系统安全
- 定期备份重要数据
- 设置适当的文件权限
- 启用 Windows 文件历史记录

## 备份与恢复

### 1. 自动备份脚本
创建 Windows 批处理脚本实现自动备份：

```batch
@echo off
set BACKUP_DIR=D:\Backups\LumiRun
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%

mkdir "%BACKUP_DIR%\%DATE%"

# 备份数据库
mysqldump -u root -p lumirun > "%BACKUP_DIR%\%DATE%\database.sql"

# 备份上传文件
xcopy "D:\LumiRun\LumiRun\backend\uploads" "%BACKUP_DIR%\%DATE%\uploads\" /E /I /Y

# 备份日志
xcopy "D:\LumiRun\LumiRun\backend\logs" "%BACKUP_DIR%\%DATE%\logs\" /E /I /Y
```

### 2. 恢复脚本
```batch
@echo off
set BACKUP_DIR=D:\Backups\LumiRun\20240101

# 恢复数据库
mysql -u root -p lumirun < "%BACKUP_DIR%\database.sql"

# 恢复文件
xcopy "%BACKUP_DIR%\uploads" "D:\LumiRun\LumiRun\backend\uploads\" /E /I /Y
```

## 性能基准

### 推荐配置
- **小型部署**（< 100 用户）:
  - CPU: 2 核
  - 内存: 4GB
  - 磁盘: 20GB SSD

- **中型部署**（100-500 用户）:
  - CPU: 4 核
  - 内存: 8GB
  - 磁盘: 50GB SSD

- **大型部署**（> 500 用户）:
  - CPU: 8 核+
  - 内存: 16GB+
  - 磁盘: 100GB+ SSD

### 性能优化建议
1. 使用 SSD 存储数据库和上传文件
2. 增加数据库连接池大小
3. 启用 Redis 缓存
4. 使用 Nginx 作为反向代理
5. 启用 HTTP/2 和 Gzip 压缩

## 技术支持

如遇到 Windows 特定问题，请提供以下信息：
1. Windows 版本和构建号
2. Python 和 Node.js 版本
3. 错误日志（backend/logs/lumirun.log）
4. 系统事件日志
5. 复现步骤

## 更新日志

### v1.0.0 (2026-04-03)
- 初始 Windows 兼容性支持
- Windows 部署脚本
- Windows 服务配置
- 路径和编码兼容性处理
