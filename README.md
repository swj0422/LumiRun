# 逐光成长系统 (LumiRun)

一款面向导师与学员的轻量化成长管理工具，核心用于记录学员成长轨迹、量化成长表现（成长值体系）、实现成长奖励兑换。

## 系统特点

- **轻量化设计**：简单易用，快速上手
- **多终端适配**：响应式网页设计，支持PC、手机、平板
- **成长值体系**：累计成长值 + 可用成长值双轨制
- **奖励兑换**：成长奖励小店，支持线下核销
- **数据隔离**：导师数据完全隔离，保障隐私
- **模块化架构**：支持功能扩展，易于维护

## 技术栈

### 后端
- **FastAPI**: 现代化、高性能Python Web框架
- **MySQL 8.0**: 企业级关系型数据库
- **Redis**: 缓存与消息队列
- **SQLAlchemy**: ORM框架
- **JWT**: 无状态认证

### 前端
- **Vue 3**: 现代化前端框架
- **TypeScript**: 类型安全
- **TailwindCSS**: 原子化CSS框架
- **Pinia**: 状态管理
- **Vite**: 构建工具

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Redis 7.0+（可选）

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

详细部署指南请参考 [WINDOWS-DEPLOY.md](WINDOWS-DEPLOY.md)

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
python -m venv venv

# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env

# 启动服务
python main.py
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
2. **班级管理**: 创建班级、二维码绑定、状态管理
3. **学员绑定**: 扫码绑定、解绑管理
4. **成长值管理**: 录入成长值、流水查询、原因管理
5. **成长奖励小店**: 奖励创建、兑换、核销
6. **系统日志**: 操作记录、日志查询

### 可选模块
1. **排行榜**: 班级排名、全学员排名
2. **消息通知**: 解绑通知、补货通知
3. **数据导出**: Excel导出功能

## 项目结构

```
lumirun/
├── backend/                # 后端项目
│   ├── app/
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据库模型
│   │   ├── schemas/       # Pydantic模型
│   │   ├── api/           # API路由
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── tests/             # 测试
│   ├── migrations/        # 数据库迁移
│   ├── main.py            # 入口文件
│   ├── requirements.txt   # 依赖
│   └── Dockerfile         # Docker配置
│
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── api/          # API接口
│   │   ├── assets/       # 静态资源
│   │   ├── components/   # 组件
│   │   ├── layouts/      # 布局
│   │   ├── router/       # 路由
│   │   ├── stores/       # 状态管理
│   │   ├── styles/       # 样式
│   │   ├── utils/        # 工具函数
│   │   └── views/        # 页面
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml     # Docker编排
└── README.md
```

## 角色与权限

| 角色 | 核心权限 |
|------|----------|
| 超级管理员 | 全权限：管理所有用户、班级、奖励、日志 |
| 管理员 | 管理所有导师/学员账号、查看全量日志 |
| 导师 | 管理自己的班级、学员、成长值、奖励、订单 |
| 学员 | 绑定班级、查看成长值、兑换奖励、提交心愿 |

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

### v1.0.0 (2026-04-02)
- 项目初始化
- 基础架构搭建
- 用户管理模块
- 班级管理模块

## 支持与联系

如有问题或建议，欢迎提交Issue或联系开发团队。

---

**路虽远行则将至，事虽难做则必成；逐光而上，每一步成长都值得被看见。**
