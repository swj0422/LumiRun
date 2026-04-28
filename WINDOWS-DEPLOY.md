# 逐光成长系统 (LumiRun) - Windows 部署指南

## 系统要求

- **操作系统**: Windows 10/11 或 Windows Server 2016+
- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **MySQL**: 8.0 或更高版本
- **Redis**: 7.0 或更高版本（可选，用于缓存）

## 快速开始

### 1. 安装必要软件

#### Python
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载并安装 Python 3.8+
3. 安装时勾选 "Add Python to PATH"

#### Node.js
1. 访问 [Node.js官网](https://nodejs.org/)
2. 下载并安装 LTS 版本

#### MySQL
1. 访问 [MySQL官网](https://dev.mysql.com/downloads/mysql/)
2. 下载并安装 MySQL 8.0+
3. 记住设置的 root 密码

#### Redis（可选）
1. 访问 [Redis官网](https://redis.io/download)
2. 下载 Windows 版本或使用 Docker
3. 或使用 Memurai（Redis 的 Windows 兼容版本）

### 2. 部署系统

#### 方法一：使用自动部署脚本（推荐）

1. 以管理员身份运行 `deploy-windows.bat`
2. 脚本会自动：
   - 检查系统环境
   - 创建必要目录
   - 安装依赖
   - 配置环境文件

#### 方法二：手动部署

**后端部署**
```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
# 编辑 .env 文件，配置数据库连接
python main.py
```

**前端部署**
```bash
cd frontend
npm install
npm run dev
```

### 3. 启动系统

#### 使用启动脚本（推荐）
```bash
start-all.bat
```

#### 手动启动
```bash
# 终端1 - 启动后端
cd backend
python main.py

# 终端2 - 启动前端
cd frontend
npm run dev
```

### 4. 访问系统

- **前端页面**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 配置说明

### 后端配置 (.env)

```env
# 应用配置
APP_NAME=LumiRun
DEBUG=false

# 数据库配置
DATABASE_URL=mysql+aiomysql://lumirun:password@localhost:3306/lumirun

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key-change-in-production

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

### 前端配置 (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 数据库初始化

1. 创建数据库：
```sql
CREATE DATABASE lumirun CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 创建用户：
```sql
CREATE USER 'lumirun'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON lumirun.* TO 'lumirun'@'localhost';
FLUSH PRIVILEGES;
```

3. 执行初始化脚本：
```bash
mysql -u root -p lumirun < backend/migrations/init.sql
```

## Windows 服务配置（可选）

### 将后端注册为 Windows 服务

使用 NSSM (Non-Sucking Service Manager)：

1. 下载 NSSM: https://nssm.cc/download
2. 安装服务：
```bash
nssm install LumiRunBackend "C:\Python38\python.exe" "D:\LumiRun\LumiRun\backend\main.py"
nssm set LumiRunBackend AppDirectory "D:\LumiRun\LumiRun\backend"
nssm set LumiRunBackend DisplayName "LumiRun Backend Service"
nssm set LumiRunBackend Description "逐光成长系统后端服务"
nssm start LumiRunBackend
```

## 防火墙配置

如果需要远程访问，请添加防火墙规则：

```powershell
# 允许后端端口
New-NetFirewallRule -DisplayName "LumiRun Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# 允许前端端口（开发环境）
New-NetFirewallRule -DisplayName "LumiRun Frontend" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
```

## 常见问题

### 1. Python 路径问题
确保 Python 已添加到系统 PATH 环境变量中。

### 2. MySQL 连接失败
- 检查 MySQL 服务是否启动
- 验证数据库连接字符串
- 确保用户权限正确

### 3. 端口被占用
修改配置文件中的端口号：
- 后端：修改 `backend/.env` 中的 `PORT`
- 前端：修改 `frontend/vite.config.ts` 中的 `server.port`

### 4. 文件权限问题
确保应用对以下目录有读写权限：
- `backend/uploads`
- `backend/logs`

### 5. Redis 连接失败
如果不需要缓存功能，可以暂时禁用 Redis：
在 `backend/app/core/cache.py` 中添加降级逻辑。

## 性能优化

### 1. 使用生产级 WSGI 服务器
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### 2. 启用数据库连接池
已在配置中启用，调整 `DATABASE_POOL_SIZE` 参数。

### 3. 使用 Nginx 反向代理
参考 `frontend/nginx.conf` 配置文件。

## 备份与恢复

### 数据库备份
```bash
mysqldump -u root -p lumirun > backup_$(date +%Y%m%d).sql
```

### 数据库恢复
```bash
mysql -u root -p lumirun < backup_20240101.sql
```

### 文件备份
```bash
# 备份上传的文件
xcopy backend\uploads backup\uploads\ /E /I /Y

# 备份日志
xcopy backend\logs backup\logs\ /E /I /Y
```

## 监控与日志

### 查看日志
```bash
# 实时查看日志
Get-Content backend\logs\lumirun.log -Wait -Tail 50
```

### 性能监控
使用 Windows 任务管理器或第三方工具监控：
- CPU 使用率
- 内存使用
- 磁盘 I/O
- 网络流量

## 安全建议

1. **修改默认密码**: 更改数据库和应用的默认密码
2. **启用 HTTPS**: 在生产环境使用 SSL 证书
3. **限制访问**: 配置防火墙规则，限制不必要的访问
4. **定期更新**: 及时更新系统和依赖包
5. **备份数据**: 定期备份数据库和重要文件

## 技术支持

如遇到问题，请查看：
1. 日志文件：`backend/logs/lumirun.log`
2. API 文档：http://localhost:8000/docs
3. 系统文档：README.md

## 更新升级

### 更新代码
```bash
git pull
```

### 更新依赖
```bash
cd backend
pip install -r requirements.txt --upgrade

cd ../frontend
npm update
```

### 数据库迁移
```bash
cd backend
alembic upgrade head
```

## 卸载

1. 停止服务：
```bash
stop-all.bat
```

2. 删除 Windows 服务（如果已安装）：
```bash
nssm remove LumiRunBackend
```

3. 删除文件和目录
4. 删除数据库（可选）
