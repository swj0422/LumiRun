# 逐光成长系统 (LumiRun)

一款面向管理者与成员的轻量化成长管理工具，核心用于记录成员成长轨迹、量化成长表现（成长值体系）、实现成长奖励兑换。

## 系统特点

- **轻量化设计**：简单易用，快速上手
- **多终端适配**：响应式网页设计，支持PC、手机、平板
- **成长值体系**：累计成长值 + 可用成长值双轨制
- **奖励兑换**：成长奖励小店，支持线下核销
- **数据隔离**：管理者数据完全隔离，保障隐私
- **模块化架构**：支持功能扩展，易于维护
- **意见征集**：成员与助理可发布、查看、管理意见帖子
- **多角色支持**：管理者、成员、组织助理多身份切换

## 技术栈

### 后端
- **FastAPI**: 现代化、高性能Python Web框架
- **MySQL 8.0**: 企业级关系型数据库
- **Redis**: 缓存与消息队列
- **SQLAlchemy**: ORM框架（异步模式）
- **JWT**: 无状态认证

### 前端
- **Vue 3**: 现代化前端框架（Composition API）
- **TypeScript**: 类型安全
- **TailwindCSS**: 原子化CSS框架
- **Pinia**: 状态管理
- **Vite**: 构建工具

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 6.0+（可选）

### Windows 部署（推荐）

#### 快速部署
```bash
# 1. 以管理员身份运行部署脚本
deploy-windows.bat

# 2. 运行测试脚本检查环境
test-windows.bat

# 3. 启动系统
start-all.bat

# 4. 访问系统
# 前端: http://localhost:5173
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

**部署脚本会自动完成**：
- 环境检查（Python、Node.js、MySQL）
- 依赖安装（支持国内镜像）
- 数据库表结构初始化
- **角色、用户和权限数据初始化**
- 默认账号创建（admin、manager、student）

详细部署指南请参考 [WINDOWS-DEPLOY.md](WINDOWS-DEPLOY.md)

### Linux 部署

```bash
# 1. 赋予执行权限
chmod +x deploy.sh

# 2. 运行部署脚本
./deploy.sh

# 3. 启动系统
# 后端: cd backend && source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000
# 前端: cd frontend && npm run dev
```

### 默认账号

部署完成后，系统会自动初始化以下账号：

| 邮箱 | 用户名 | 密码 | 角色 |
| --- | --- | --- | --- |
| admin@example.com | admin | Password123 | 超级管理员 |
| manager@example.com | manager | Password123 | 管理者 |
| student@example.com | student | Password123 | 成员 |

**安全提示**：⚠️ 首次登录后请立即修改默认密码！

### Docker 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 本地开发

#### 1. 克隆项目
```bash
git clone <repository-url>
cd lumirun
```

#### 2. 启动后端
```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# Windows
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 启动前端
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 访问系统
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 系统模块

### 核心模块（必开）
1. **用户管理**: 角色分配、注册登录、权限控制
2. **组织管理**: 创建组织、二维码绑定、状态管理
3. **成员绑定**: 扫码绑定、解绑管理
4. **成长值管理**: 录入成长值、流水查询、原因管理
5. **成长奖励小店**: 奖励创建、兑换、核销
6. **系统日志**: 操作记录、日志查询
7. **意见征集**: 帖子发布、查看、管理

### 可选模块
1. **排行榜**: 组织排名、全成员排名
2. **消息通知**: 解绑通知、补货通知
3. **数据导出**: Excel导出功能
4. **心愿墙**: 成员心愿提交与管理

## 项目结构

```
lumirun/
├── backend/                # 后端项目
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/        # API路由（版本1）
│   │   ├── core/          # 核心配置（缓存、数据库、安全等）
│   │   ├── middleware/    # 中间件
│   │   ├── models/        # 数据库模型
│   │   ├── schemas/       # Pydantic模型
│   │   └── services/      # 业务逻辑层
│   ├── migrations/        # 数据库迁移脚本
│   ├── main.py            # 入口文件
│   ├── requirements.txt   # Python依赖
│   ├── .env.example       # 环境变量模板
│   └── Dockerfile         # Docker配置
│
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── api/           # API接口定义
│   │   ├── components/    # 公共组件
│   │   ├── hooks/         # 自定义Hooks
│   │   ├── layouts/       # 布局组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # Pinia状态管理
│   │   ├── styles/        # 全局样式
│   │   ├── types/         # TypeScript类型定义
│   │   ├── utils/         # 工具函数
│   │   └── views/         # 页面组件
│   │       ├── pc/        # PC端页面
│   │       └── mobile/    # 移动端页面
│   ├── package.json       # Node.js依赖
│   ├── vite.config.ts     # Vite配置
│   └── tailwind.config.js # TailwindCSS配置
│
├── docker-compose.yml     # Docker编排
├── .gitignore            # Git忽略规则
├── README.md             # 项目说明
└── WINDOWS-DEPLOY.md     # Windows部署指南
```

## 角色与权限

| 角色 | 核心权限 |
|------|----------|
| 超级管理员 | 全权限：管理所有用户、组织、奖励、日志 |
| 管理员 | 管理所有管理者/成员账号、查看全量日志 |
| 管理者 | 管理自己的组织、成员、成长值、奖励、订单 |
| 组织助理 | 协助管理者管理组织、录入成长值、查看操作记录 |
| 成员 | 绑定组织、查看成长值、兑换奖励、提交心愿、发布意见 |

## 开发规范

### 代码规范
- 后端: PEP 8
- 前端: ESLint + Prettier
- 提交信息: Conventional Commits

### 分支管理
- main: 生产分支
- develop: 开发分支
- feature/*: 功能分支
- bugfix/*: 修复分支

## 更新日志

### v1.0.0 (2026-04-28)
- 项目初始化完成
- 基础架构搭建
- 用户管理模块（注册、登录、角色分配）
- 组织管理模块（创建、二维码绑定）
- 成员绑定模块（扫码绑定、解绑）
- 成长值管理模块（录入、流水查询）
- 成长奖励小店（奖励创建、兑换、核销）
- 排行榜模块（组织排名、全成员排名）
- 意见征集模块（帖子发布、查看、管理）
- 组织助理角色支持
- 多终端适配（PC端、移动端）

## 支持与联系

如有问题或建议，欢迎提交Issue或联系开发团队。

---

**路虽远行则将至，事虽难做则必成；逐光而上，每一步成长都值得被看见。**