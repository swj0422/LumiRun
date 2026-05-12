# 逐光成长系统 (LumiRun) - Windows 部署指南

## 系统要求

- **操作系统**: Windows 10/11 或 Windows Server 2016+
- **Python**: 3.10 或更高版本
- **Node.js**: 18.0 或更高版本（LTS 版本）
- **MySQL**: 8.0 或更高版本
- **Redis**: 6.0 或更高版本（可选，用于缓存）

## 快速开始

### 1. 安装必要软件

#### Python
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载并安装 Python 3.10+
3. 安装时勾选 "Add Python to PATH" 和 "Install for all users"

#### Node.js
1. 访问 [Node.js官网](https://nodejs.org/)
2. 下载并安装 LTS 版本（推荐 18.x 或 20.x）

#### MySQL
1. 访问 [MySQL官网](https://dev.mysql.com/downloads/mysql/)
2. 下载并安装 MySQL 8.0+
3. 记住设置的 root 密码
4. 确保 MySQL 服务已启动

#### Redis（可选）
1. 访问 [Redis官网](https://redis.io/download) 下载 Windows 版本，或使用 WSL
2. 或使用 [Memurai](https://www.memurai.com/)（Redis 的 Windows 兼容版本）
3. 或使用 Docker 运行 Redis

### 2. 部署系统

#### 方法一：使用自动部署脚本（推荐）

1. 以管理员身份运行 `deploy-windows.bat`
2. 脚本会自动：
   - 检查系统环境
   - 创建必要目录
   - 创建虚拟环境（位于项目根目录 `.venv`）
   - 安装依赖（支持国内镜像自动切换）
   - 配置环境文件
   - **初始化数据库表结构**
   - **初始化角色、用户和权限数据**

> **国内镜像支持**：
> - 如果默认源安装失败，脚本会自动尝试使用国内镜像
> - Python 依赖使用：阿里云 PyPI 镜像
> - Node.js 依赖使用：npmmirror 镜像

> **数据初始化**：
> - 脚本会自动创建数据库表结构
> - 自动初始化 4 个角色（超级管理员、管理员、导师、学员）
> - 自动创建 3 个测试账号（admin、teacher、student）
> - 自动初始化完整的权限体系（12个菜单权限 + 44个按钮权限）

#### 方法二：手动部署

**后端部署**
```powershell
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置文件
copy .env.example .env

# 编辑 .env 文件，配置数据库连接
notepad .env

# 初始化数据库表结构
python init_db.py

# 初始化角色、用户和权限数据
python init_data.py

# 启动后端服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

**前端部署**
```powershell
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产模式构建
npm run build
```

### 3. 启动系统

#### 使用启动脚本（推荐）

**启动后端服务**：
```cmd
cd /d "D:\LumiRun-master\backend"
start_backend.cmd
```

**启动前端服务**：
```cmd
cd /d "D:\LumiRun-master\frontend"
npm run dev
```

> **说明**：
> - 启动脚本会自动读取 `.env` 文件中的配置（如 PORT）
> - 不需要手动激活虚拟环境，脚本会自动使用虚拟环境中的 Python
> - 后端默认端口：8000，前端默认端口：3002

#### 手动启动
```cmd
# 终端1 - 启动后端
cd /d "D:\LumiRun-master"
.venv\Scripts\activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# 终端2 - 启动前端
cd /d "D:\LumiRun-master\frontend"
npm run dev
```

### 4. 访问系统

- **前端页面**: http://localhost:3002
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/swagger

### 5. 默认账号

部署完成后，系统会自动初始化以下账号：

| 邮箱 | 用户名 | 密码 | 角色 |
| --- | --- | --- | --- |
| admin@example.com | admin | Password123 | 超级管理员 |
| teacher@example.com | teacher | Password123 | 导师 |
| student@example.com | student | Password123 | 学员 |

**角色权限说明**：
- **超级管理员**：拥有系统所有权限，包括用户管理、角色管理、权限管理、系统设置等
- **管理员**：可管理用户、班级、学员、礼品、订单等业务数据，但不能管理角色和权限
- **导师**：可管理自己的班级、学员、成长值、奖励等
- **学员**：可查看自己的成长值、兑换奖励等

**安全提示**：
⚠️ 首次登录后请立即修改默认密码！

**手动初始化数据**：
如果需要重新初始化数据，可以运行以下命令：
```powershell
cd backend
python init_db.py      # 初始化数据库表结构
python init_data.py    # 初始化角色、用户和权限数据
```

## 配置说明

### 后端配置 (.env)

```env
# 应用配置
APP_NAME=LumiRun
APP_NAME_CN=逐光成长系统
DEBUG=false
VERSION=1.0.0

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=mysql+aiomysql://lumirun:your_password@localhost:3306/lumirun?charset=utf8mb4
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis配置（可选）
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 文件上传配置
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# 邮件发送配置（可选）
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_FROM=your-email@example.com
SMTP_USE_TLS=True

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/lumirun.log
```

### 前端配置 (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## 数据库初始化

### 方法一：使用初始化脚本（推荐）
```powershell
cd backend
python init_db.py
```

### 方法二：手动创建
1. 创建数据库：
```sql
CREATE DATABASE lumirun CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 创建用户：
```sql
CREATE USER 'lumirun'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON lumirun.* TO 'lumirun'@'localhost';
FLUSH PRIVILEGES;
```

3. 执行初始化脚本：
```powershell
mysql -u root -p lumirun < backend/migrations/init.sql
```

## Windows 服务配置（可选）

### 将后端注册为 Windows 服务

使用 NSSM (Non-Sucking Service Manager)：

1. 下载 NSSM: https://nssm.cc/download
2. 将 nssm.exe 放入系统 PATH 或当前目录
3. 安装服务：
```powershell
nssm install LumiRunBackend "D:\LumiRun\LumiRun\backend\.venv\Scripts\python.exe" "D:\LumiRun\LumiRun\backend\main.py"
nssm set LumiRunBackend AppDirectory "D:\LumiRun\LumiRun\backend"
nssm set LumiRunBackend DisplayName "LumiRun Backend Service"
nssm set LumiRunBackend Description "逐光成长系统后端服务"
nssm set LumiRunBackend Start SERVICE_AUTO_START
nssm start LumiRunBackend
```

## 防火墙配置

如果需要远程访问，请添加防火墙规则：

```powershell
# 允许后端端口
New-NetFirewallRule -DisplayName "LumiRun Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# 允许前端端口（开发环境）
New-NetFirewallRule -DisplayName "LumiRun Frontend" -Direction Inbound -LocalPort 3002 -Protocol TCP -Action Allow
```

## 常见问题

### 1. Python 路径问题
确保 Python 和虚拟环境已添加到系统 PATH 环境变量中。

### 2. MySQL 连接失败
- 检查 MySQL 服务是否启动
- 验证数据库连接字符串中的用户名和密码
- 确保 MySQL 用户权限正确
- 检查 MySQL 是否允许本地连接

### 3. 端口被占用
修改配置文件中的端口号：
- 后端：修改 `backend/.env` 中的 `PORT`
- 前端：修改 `frontend/vite.config.ts` 中的 `server.port`

### 4. 文件权限问题
确保应用对以下目录有读写权限：
- `backend/uploads` - 上传文件目录
- `backend/logs` - 日志目录

### 5. Redis 连接失败
如果不需要缓存功能，可以暂时禁用 Redis：
- 在 `backend/.env` 中将 `REDIS_URL` 留空或注释掉

### 6. 依赖安装失败
- 确保网络连接正常
- 尝试使用国内 PyPI 镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 性能优化

### 1. 使用生产级服务器
```powershell
# 安装 gunicorn（Linux）或使用 waitress（Windows）
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 main:app
```

### 2. 启用数据库连接池
已在配置中启用，调整 `DATABASE_POOL_SIZE` 和 `DATABASE_MAX_OVERFLOW` 参数。

### 3. 使用 Nginx 反向代理
参考 `frontend/nginx.conf` 配置文件配置反向代理和静态文件服务。

### 4. 启用 Gzip 压缩
在 Nginx 或应用层面启用响应压缩。

## 备份与恢复

### 数据库备份
```powershell
mysqldump -u root -p lumirun > "backup_$(Get-Date -Format 'yyyyMMdd').sql"
```

### 数据库恢复
```powershell
mysql -u root -p lumirun < backup_20260428.sql
```

### 文件备份
```powershell
# 备份上传的文件
xcopy backend\uploads backup\uploads\ /E /I /Y

# 备份日志
xcopy backend\logs backup\logs\ /E /I /Y
```

## 监控与日志

### 查看日志
```powershell
# 实时查看日志（最后50行）
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
2. **启用 HTTPS**: 在生产环境使用 SSL 证书（推荐使用 Let's Encrypt）
3. **限制访问**: 配置防火墙规则，限制不必要的访问
4. **定期更新**: 及时更新系统和依赖包
5. **备份数据**: 定期备份数据库和重要文件
6. **禁用 DEBUG 模式**: 生产环境设置 `DEBUG=false`

## 技术支持

如遇到问题，请查看：
1. 日志文件：`backend/logs/lumirun.log`
2. API 文档：http://localhost:8000/docs
3. 系统文档：README.md

## 更新升级

### 更新代码
```powershell
git pull origin main
```

### 更新依赖
```powershell
cd backend
.venv\Scripts\activate
pip install -r requirements.txt --upgrade

cd ..\frontend
npm update
```

### 数据库迁移
```powershell
cd backend
python update_db.py
```

## 卸载

1. 停止服务：
```powershell
stop-all.bat
```

2. 删除 Windows 服务（如果已安装）：
```powershell
nssm remove LumiRunBackend confirm
```

3. 删除项目目录
4. 删除数据库（可选）：
```sql
DROP DATABASE lumirun;
DROP USER 'lumirun'@'localhost';
```

---

**部署完成后，请确保：**
- 数据库连接正常
- Redis 服务已启动（如果使用）
- 防火墙规则已配置
- 日志目录可写
- 上传目录可写