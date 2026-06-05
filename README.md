# GuiGraph

版本变更管理系统 — 开源、私有化、分阶段落地。

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python FastAPI + SQLAlchemy (async) |
| 前端 | Vue 3 + TypeScript + Element Plus + Vite |
| 数据库 | SQLite (dev) / PostgreSQL / Oracle |
| 对象存储 | MinIO |
| RAG 引擎 | RAGFlow |
| 知识图谱 | GraphRAG |
| 容器编排 | Docker Compose |

## 快速开始

### 方式一：一键启动脚本（推荐本地开发）

```bash
# Windows 双击运行或命令行执行
start.bat
```

脚本会自动完成：
1. 检查 Python / Node.js 环境
2. 创建后端 Python 虚拟环境并安装依赖
3. 安装前端 npm 依赖
4. 在独立窗口启动后端 (10011) 和前端 (10010) 服务

### 方式二：Docker Compose

```bash
docker-compose up -d
```

### 方式三：手动启动

```bash
# 后端
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements/base.txt
uvicorn app.main:app --host 0.0.0.0 --port 10011 --reload

# 前端
cd frontend
npm install
npm run dev
```

### 方式四：分别启动后端/前端

```bash
start-backend.bat    # 仅启动后端
start-frontend.bat   # 仅启动前端
```

## 服务地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:10010 |
| 后端 API | http://localhost:10011 |
| API 文档 (Swagger) | http://localhost:10011/docs |
| API 文档 (ReDoc) | http://localhost:10011/redoc |
| 健康检查 | http://localhost:10011/health |
| MinIO 控制台 | http://localhost:9001 |

## 环境切换

后端支持多环境配置（`.env.dev` / `.env.test` / `.env.prod`）：

```bash
cd backend
switch_env.bat dev    # 切换到开发环境
switch_env.bat test   # 切换到测试环境
switch_env.bat prod   # 切换到生产环境
```

## 项目结构

```
GuiGraph/
├── start.bat                  # 一键启动脚本
├── start-backend.bat          # 仅启动后端
├── start-frontend.bat         # 仅启动前端
├── docker-compose.yml         # Docker 编排
├── backend/                   # 后端 (FastAPI)
│   ├── app/
│   │   ├── main.py            # 应用入口
│   │   ├── config/            # 配置管理 (settings, logger, permissions)
│   │   ├── core/              # 核心模块 (database, middleware, security, deps)
│   │   ├── modules/           # 业务模块
│   │   │   ├── auth/          # 认证
│   │   │   ├── user/          # 用户管理
│   │   │   ├── organization/  # 组织管理
│   │   │   ├── change/        # 变更管理
│   │   │   ├── git/           # Git 集成
│   │   │   ├── jenkins/       # Jenkins 集成
│   │   │   ├── ai/            # AI 模块 (model, skill, mcp, rag)
│   │   │   ├── knowledge/     # 知识库
│   │   │   ├── wiki/          # Wiki
│   │   │   ├── audit/         # 审计日志
│   │   │   ├── upgrade/       # 升级管理
│   │   │   ├── dictionary/    # 数据字典
│   │   │   ├── dashboard/     # 仪表盘
│   │   │   └── attachment/    # 附件管理
│   │   ├── integrations/      # 外部集成
│   │   └── shared/            # 共享工具
│   ├── requirements/          # Python 依赖
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试用例
│   ├── .env.dev               # 开发环境配置
│   ├── .env.test              # 测试环境配置
│   ├── .env.prod              # 生产环境配置
│   └── switch_env.bat         # 环境切换脚本
├── frontend/                  # 前端 (Vue 3 + Vite)
│   ├── src/
│   │   ├── api/               # API 请求
│   │   ├── assets/            # 静态资源
│   │   ├── components/        # 公共组件
│   │   ├── composables/       # 组合式函数
│   │   ├── layouts/           # 布局组件
│   │   ├── pages/             # 页面
│   │   │   ├── login/         # 登录
│   │   │   ├── dashboard/     # 仪表盘
│   │   │   ├── change/        # 变更管理
│   │   │   ├── organization/  # 组织管理
│   │   │   ├── user/          # 用户管理
│   │   │   ├── ai/            # AI 模块
│   │   │   ├── knowledge/     # 知识库
│   │   │   ├── wiki/          # Wiki
│   │   │   ├── git/           # Git
│   │   │   ├── jenkins/       # Jenkins
│   │   │   ├── audit/         # 审计日志
│   │   │   ├── upgrade/       # 升级管理
│   │   │   └── dictionary/    # 数据字典
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── types/             # TypeScript 类型
│   │   ├── utils/             # 工具函数
│   │   ├── App.vue            # 根组件
│   │   └── main.ts            # 入口文件
│   ├── public/                # 公共资源
│   ├── .env.development       # 开发环境变量
│   ├── .env.production        # 生产环境变量
│   └── vite.config.ts         # Vite 配置
└── docs/                      # 文档
```

## API 概览

后端 API 遵循 RESTful 规范，统一前缀 `/api/v1`。

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/v1/auth` | 登录、JWT、微信 OAuth |
| 用户 | `/api/v1/users` | 用户 CRUD、角色分配 |
| 组织 | `/api/v1/organizations` | 组织/部门管理 |
| 变更 | `/api/v1/changes` | 变更单全生命周期 |
| Git | `/api/v1/git` | GitLab 仓库集成 |
| Jenkins | `/api/v1/jenkins` | CI/CD 流水线 |
| 知识库 | `/api/v1/knowledge` | 知识库管理 |
| Wiki | `/api/v1/wiki` | Wiki 文档 |
| AI | `/api/v1/ai` | AI 模型、技能、MCP、RAG |
| 审计 | `/api/v1/audit` | 操作审计日志 |
| 升级 | `/api/v1/upgrade` | 升级记录管理 |
| 数据字典 | `/api/v1/dictionary` | 字典维护 |
| 附件 | `/api/v1/attachments` | MinIO 文件管理 |

## 开发指南

### 后端开发

```bash
cd backend
.venv\Scripts\activate

# 运行开发服务器
uvicorn app.main:app --host 0.0.0.0 --port 10011 --reload

# 运行测试
pytest

# 数据库迁移
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

### 前端开发

```bash
cd frontend

# 开发服务器
npm run dev

# 构建生产包
npm run build

# 代码检查
npm run lint

# 预览构建结果
npm run preview
```

## 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

## 开发计划

- [x] 项目目录结构设计
- [x] 后端核心框架 (FastAPI)
- [x] MVP 模块 (auth, user, organization, change, git, jenkins)
- [x] 前端初始化 (Vue 3)
- [x] 核心页面 (login, dashboard, change, organization, user)
- [x] 一键启动脚本
- [ ] 数据库模型定义
- [ ] 多数据库方言适配
- [ ] AI 模块 (model/skill/mcp/rag)
- [ ] 知识库/Wiki 模块
- [ ] 审计日志/升级日志模块
- [ ] 权限矩阵完整实现
- [ ] 微信 OAuth 集成
- [ ] MinIO 文件上传
- [ ] RAGFlow/GraphRAG 集成
- [ ] 测试用例
