# GuiGraph 工程目录结构设计文档

> **技术栈**: Python FastAPI (后端) + Vue 3 (前端) | **日期**: 2026-06-04

---

## 1. 顶层目录

```
GuiGraph/
├── backend/            # 后端项目 (FastAPI)
├── frontend/           # 前端项目 (Vue 3)
├── skills/             # AI Skill 定义（已有）
├── docs/               # 全局文档
├── docker-compose.yml  # 本地开发/部署编排
└── README.md           # 项目总览
```

---

## 2. 后端目录结构 (backend/)

### 2.1 顶层

```
backend/
├── app/                          # 业务源码
├── alembic/                      # 数据库迁移
├── tests/                        # 测试
├── docs/                         # 后端专属文档
├── scripts/                      # 工具脚本
├── requirements/                 # 依赖管理
├── pyproject.toml
├── Dockerfile
└── .env.example
```

### 2.2 app/ 核心层 — `app/core/`

```
app/core/
├── security/
│   ├── __init__.py
│   ├── jwt.py                    # JWT 生成/验证
│   ├── crypto.py                 # 加密工具 (Token/SSH Key 加密存储)
│   └── wechat.py                 # 微信 OAuth2.0 逻辑
├── database/
│   ├── __init__.py
│   ├── session.py                # SQLAlchemy 会话管理
│   ├── base.py                   # 声明性基类
│   └── dialect/                  # 多数据库方言适配层
│       ├── __init__.py
│       ├── base_dialect.py       # 方言抽象接口
│       ├── mysql_dialect.py
│       ├── postgres_dialect.py
│       └── oracle_dialect.py     # 后续扩展 Oracle/DM
├── middleware/
│   ├── __init__.py
│   ├── cors.py
│   ├── request_log.py            # 请求日志审计
│   └── rate_limit.py
├── deps/
│   ├── __init__.py
│   └── auth.py                   # FastAPI Depends: get_current_user, check_permission
├── exceptions/
│   ├── __init__.py
│   └── handlers.py               # 全局异常处理
├── utils/
│   ├── __init__.py
│   ├── pagination.py
│   ├── response.py               # 统一响应格式
│   └── helpers.py
└── __init__.py
```

### 2.3 app/ 配置层 — `app/config/`

```
app/config/
├── __init__.py
├── settings.py                   # 全局配置 (pydantic-settings, 环境变量)
├── permissions.py                # 权限矩阵配置 (角色 × 资源 × 操作)
└── logger.py                     # 日志配置
```

### 2.4 app/ 业务模块 — `app/modules/`

每个模块遵循 **router → schemas → service → models** 四层结构：

```
app/modules/
├── auth/                         # 用户认证
│   ├── __init__.py
│   ├── router.py                 # POST /api/v1/auth/login, /wechat/qrcode, /refresh, /logout
│   ├── schemas.py                # LoginRequest, TokenResponse, WechatQRCode
│   └── service.py                # 认证业务逻辑
│
├── user/                         # 用户中心
│   ├── __init__.py
│   ├── router.py                 # GET/PUT /api/v1/user/profile, POST avatar, bind-wechat
│   ├── schemas.py                # UserProfile, AvatarUpload, BindWechat
│   ├── service.py
│   └── models.py                 # SysUser ORM 模型
│
├── organization/                 # 组织架构
│   ├── __init__.py
│   ├── router.py                 # GET /org/structure, POST/PUT departments/teams, members
│   ├── schemas.py                # Company, Department, Team, Member
│   ├── service.py
│   └── models.py                 # SysCompany, BizDepartment, BizTeam, BizTeamMember
│
├── change/                       # 变更管理
│   ├── __init__.py
│   ├── router.py                 # CRUD /api/v1/changes, POST approve
│   ├── schemas.py                # ChangeItem, ChangeCreate, ChangeApprove
│   ├── service.py
│   └── models.py                 # BizChangeItem ORM 模型
│
├── git/                          # Git 集成
│   ├── __init__.py
│   ├── router.py                 # /git/repos, /git/merge, /git/branches
│   ├── schemas.py                # GitRepo, BranchInfo, MergeRequest
│   ├── service.py                # GitPython 操作封装
│   └── models.py                 # BizGitRepo, BizUserGitAuth
│
├── jenkins/                      # Jenkins 集成
│   ├── __init__.py
│   ├── router.py                 # /jenkins/instances, /jenkins/build
│   ├── schemas.py                # JenkinsInstance, BuildRequest, BuildStatus
│   ├── service.py                # Jenkins REST API 封装
│   └── models.py                 # SysJenkinsInstance, BizJenkinsJob
│
├── attachment/                   # 附件管理 (MinIO)
│   ├── __init__.py
│   ├── router.py                 # POST upload, GET download, DELETE
│   ├── schemas.py                # FileUpload, FileInfo
│   ├── service.py                # MinIO 操作 + 异步 RAGFlow 推送
│   └── models.py                 # BizAttachFile
│
├── ai/                           # AI 能力（含三个子模块）
│   ├── __init__.py
│   ├── router.py                 # /ai/... 全局 AI 路由
│   ├── schemas.py
│   ├── service.py                # AI 选择引擎核心逻辑
│   ├── models.py                 # AiModelConfig, ScenarioBinding
│   │
│   ├── model_manager/            # AI 模型管理
│   │   ├── __init__.py
│   │   ├── router.py             # /ai/models CRUD
│   │   ├── schemas.py
│   │   └── service.py            # 多模型提供商适配 (OpenAI/DeepSeek/Qwen)
│   │
│   ├── skill/                    # Skill 管理
│   │   ├── __init__.py
│   │   ├── router.py             # /ai/skills CRUD + 启用/禁用
│   │   ├── schemas.py
│   │   └── service.py            # Skill 加载/注册/权限绑定
│   │
│   ├── mcp/                      # MCP 管理
│   │   ├── __init__.py
│   │   ├── router.py             # /admin/mcp CRUD + connect + tools
│   │   ├── schemas.py
│   │   ├── service.py            # MCP 协议客户端 (stdio/sse/http)
│   │   └── models.py             # SysMcpServer, SysMcpToolAuth
│   │
│   └── rag/                      # RAGFlow & GraphRAG 集成
│       ├── __init__.py
│       ├── router.py             # /ai/rag/search, /ai/rag/analyze
│       ├── schemas.py
│       └── service.py            # RAGFlow API 封装 + GraphRAG 推理
│
├── audit/                        # 审计日志
│   ├── __init__.py
│   ├── router.py                 # GET /api/v1/audit/logs
│   ├── schemas.py
│   ├── service.py
│   └── models.py                 # AuditLog
│
├── upgrade/                      # 升级日志
│   ├── __init__.py
│   ├── router.py                 # /api/v1/upgrade/logs CRUD + rollback + export
│   ├── schemas.py
│   ├── service.py
│   └── models.py                 # SysUpgradeLog
│
├── dictionary/                   # 字典管理
│   ├── __init__.py
│   ├── router.py                 # /api/v1/dict/domains, /applications, /components
│   ├── schemas.py
│   ├── service.py
│   └── models.py                 # BizDomain, BizApplication, BizComponent
│
├── knowledge/                    # 知识库笔记
│   ├── __init__.py
│   ├── router.py                 # CRUD 笔记 + AI 辅助
│   ├── schemas.py
│   ├── service.py                # 笔记管理 + 版本历史 + AI 生成/润色
│   └── models.py                 # KnowledgeBase, Note, NoteVersion
│
├── wiki/                         # Wiki 结构化文档
│   ├── __init__.py
│   ├── router.py                 # /wiki/spaces, /wiki/docs CRUD + 版本管理
│   ├── schemas.py
│   ├── service.py
│   └── models.py                 # WikiSpace, WikiDoc, WikiDocVersion
│
└── dashboard/                    # 看板/时间线
    ├── __init__.py
    ├── router.py                 # 聚合查询
    ├── schemas.py
    └── service.py                # 多模块数据聚合
```

### 2.5 app/ 外部集成 — `app/integrations/`

```
app/integrations/
├── __init__.py
├── minio/
│   ├── __init__.py
│   └── client.py                 # MinIO SDK 封装 (上传/下载/签名URL/缩略图)
├── wechat/
│   ├── __init__.py
│   └── client.py                 # 微信 API 封装 (QR码/回调/Token刷新)
├── ragflow/
│   ├── __init__.py
│   └── client.py                 # RAGFlow REST API 封装
└── graphrag/
    ├── __init__.py
    └── client.py                 # GraphRAG 查询/推理 API
```

### 2.6 app/ 共享资源 — `app/shared/`

```
app/shared/
├── __init__.py
├── enums.py                      # 全局枚举 (ChangeType, Status, Role, LoginMethod...)
└── constants.py                  # 全局常量
```

### 2.7 后端文档目录 — `backend/docs/`

```
backend/docs/
├── api/                          # API 设计文档 (OpenAPI 之外的补充)
├── sql/                          # DDL SQL 脚本 + 迁移说明
├── prompts/                      # AI 提示词模板
│   ├── change-summary.md         # 变更总结提示词
│   ├── doc-analysis.md           # 文档分析提示词
│   ├── note-generate.md          # 笔记生成提示词
│   └── ...
├── skills/                       # AI Skill 定义
│   ├── git-management.md
│   ├── jenkins-integration.md
│   └── ...
└── mcp/                          # MCP 服务器配置文件/模板
    ├── servers/
    │   ├── git-server.json
    │   └── jenkins-server.json
    └── tool-auth-template.json
```

### 2.8 依赖管理 — `backend/requirements/`

```
requirements/
├── base.txt                      # 生产依赖
├── dev.txt                       # 开发依赖 (from base.txt + pytest/httpx)
└── prod.txt                      # 生产锁定版本
```

---

## 3. 前端目录结构 (frontend/)

### 3.1 顶层

```
frontend/
├── public/
│   ├── favicon.ico
│   └── index.html
├── src/
├── .env.development
├── .env.production
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── package.json
├── pnpm-lock.yaml
├── Dockerfile
└── .eslintrc.cjs
```

### 3.2 src/ 核心结构

```
src/
├── api/                          # API 请求层
│   ├── request.ts                # Axios 封装 (拦截器/Token刷新/错误处理)
│   ├── auth.ts
│   ├── user.ts
│   ├── organization.ts
│   ├── change.ts
│   ├── git.ts
│   ├── jenkins.ts
│   ├── attachment.ts
│   ├── ai/
│   │   ├── model.ts
│   │   ├── skill.ts
│   │   └── mcp.ts
│   ├── audit.ts
│   ├── upgrade.ts
│   ├── dictionary.ts
│   ├── knowledge.ts
│   ├── wiki.ts
│   └── dashboard.ts
│
├── assets/
│   ├── styles/
│   │   ├── variables.scss         # 主题变量
│   │   └── global.scss            # 全局样式
│   └── images/
│
├── components/                   # 共享组件
│   ├── common/                   # 通用 UI 组件
│   │   ├── PageHeader.vue
│   │   ├── SearchForm.vue
│   │   ├── DataTable.vue
│   │   ├── StatusTag.vue
│   │   ├── AvatarUpload.vue
│   │   ├── ConfirmDialog.vue
│   │   └── EmptyState.vue
│   ├── layout/                   # 布局组件
│   │   ├── AppLayout.vue
│   │   ├── Sidebar.vue
│   │   ├── HeaderBar.vue
│   │   └── BreadCrumb.vue
│   └── business/                 # 业务组件
│       ├── ChangeForm.vue
│       ├── GitBranchSelector.vue
│       ├── JenkinsStatusBadge.vue
│       ├── ModelSelector.vue
│       ├── TimelineView.vue
│       ├── GraphView.vue
│       └── RichEditor.vue
│
├── composables/                  # Composition API 组合式函数
│   ├── useAuth.ts
│   ├── usePermission.ts
│   ├── usePagination.ts
│   └── useDebounce.ts
│
├── layouts/                      # 页面布局
│   ├── DefaultLayout.vue         # 默认布局 (侧边栏 + 顶部栏)
│   ├── AdminLayout.vue           # 管理员布局
│   └── BlankLayout.vue           # 空白布局 (登录页)
│
├── pages/                        # 页面（按模块分）
│   ├── login/
│   │   └── index.vue
│   ├── dashboard/
│   │   └── index.vue
│   ├── organization/
│   │   ├── CompanyView.vue
│   │   ├── DepartmentView.vue
│   │   └── TeamView.vue
│   ├── change/
│   │   ├── ChangeList.vue
│   │   ├── ChangeCreate.vue
│   │   ├── ChangeDetail.vue
│   │   └── ChangeApprove.vue
│   ├── user/
│   │   ├── UserCenter.vue
│   │   └── UserProfile.vue
│   ├── git/
│   │   ├── RepoList.vue
│   │   ├── RepoDetail.vue
│   │   └── MergeRequest.vue
│   ├── jenkins/
│   │   ├── InstanceList.vue
│   │   ├── BuildHistory.vue
│   │   └── BuildDetail.vue
│   ├── ai/
│   │   ├── ModelList.vue
│   │   ├── SkillList.vue
│   │   ├── MCPList.vue
│   │   └── RAGSearch.vue
│   ├── audit/
│   │   └── AuditLog.vue
│   ├── upgrade/
│   │   ├── UpgradeLog.vue
│   │   ├── UpgradeDetail.vue
│   │   └── RollbackConfirm.vue
│   ├── knowledge/
│   │   ├── KnowledgeBase.vue
│   │   ├── NoteEditor.vue
│   │   └── NoteDetail.vue
│   ├── wiki/
│   │   ├── WikiSpace.vue
│   │   ├── WikiEditor.vue
│   │   └── WikiDocDetail.vue
│   └── dictionary/
│       ├── DomainList.vue
│       ├── ApplicationList.vue
│       └── ComponentList.vue
│
├── router/
│   ├── index.ts                  # 路由实例
│   ├── routes.ts                 # 路由配置
│   └── guard.ts                  # 路由守卫 (认证/权限)
│
├── stores/                       # Pinia 状态管理
│   ├── auth.ts                   # 认证状态
│   ├── user.ts                   # 用户信息
│   ├── app.ts                    # 应用状态 (主题/侧边栏)
│   └── permission.ts             # 权限状态
│
├── types/                        # TypeScript 类型
│   ├── api.d.ts                  # API 通用响应类型
│   ├── user.d.ts
│   ├── change.d.ts
│   ├── organization.d.ts
│   └── ...
│
└── utils/
    ├── format.ts                 # 格式化工具 (日期/金额/文件大小)
    ├── validate.ts               # 表单校验规则
    └── constants.ts              # 前端常量
```

---

## 4. 根级 skills/ 目录（已有，强化）

```
skills/
├── README.md                     # 技能注册表（已存在）
├── git-management/
│   └── SKILL.md                  # Git 管理 Skill
├── jenkins-integration/
│   └── SKILL.md                  # Jenkins 集成 Skill
├── agent-policy/
│   └── SKILL.md                  # Agent 权限策略 Skill
├── upgrade-log/
│   └── SKILL.md                  # 升级日志管理 Skill
├── change-management/            # 新建：变更管理 Skill
│   └── SKILL.md
├── mcp-server/                   # 新建：MCP 服务 Skill
│   └── SKILL.md
└── organization/                 # 新建：组织管理 Skill
    └── SKILL.md
```

---

## 5. 目录设计原则

### 5.1 后端模块四层架构

每个业务模块严格遵循四层分离：

| 层级 | 文件 | 职责 | 依赖 |
|------|------|------|------|
| **Router** | `router.py` | 路由定义 + 请求参数校验 | 依赖 schemas + service |
| **Schemas** | `schemas.py` | Pydantic 请求/响应模型 | 无业务依赖 |
| **Service** | `service.py` | 业务逻辑 + 事务管理 | 依赖 models + integrations |
| **Models** | `models.py` | SQLAlchemy ORM 模型 | 依赖 core/database |

### 5.2 前端按模块分页

- 每个业务模块在 `pages/` 下独立文件夹
- 共享业务组件放 `components/business/`
- 通用 UI 组件放 `components/common/`
- API 调用统一在 `api/` 下按模块切分

### 5.3 AI/Skill/MCP/提示词隔离

| 目录 | 内容 | 使用者 |
|------|------|--------|
| `backend/docs/prompts/` | AI 提示词模板 (.md) | 后端 ai/ 模块 |
| `backend/docs/skills/` | Skill 定义文档 | 后端 ai/skill 模块 |
| `backend/docs/mcp/` | MCP 配置模板 (.json) | 后端 ai/mcp 模块 |
| `skills/` (根级) | **可加载的** Skill 定义 | Agent 系统 + 后端 |

---

## 6. API 路由前缀规划

| 前缀 | 模块 | 权限 |
|------|------|------|
| `/api/v1/auth/` | 认证 | 公开 + JWT |
| `/api/v1/user/` | 用户中心 | 登录 |
| `/api/v1/org/` | 组织架构 | 管理员+ |
| `/api/v1/changes/` | 变更管理 | 编辑者+ |
| `/api/v1/git/` | Git 集成 | 编辑者+ |
| `/api/v1/jenkins/` | Jenkins 集成 | 编辑者+ |
| `/api/v1/attachment/` | 附件管理 | 登录 |
| `/api/v1/ai/` | AI 能力 | 按子模块 |
| `/api/v1/admin/mcp/` | MCP 管理 | 系统管理员 |
| `/api/v1/admin/ai/` | AI 模型管理 | 系统管理员 |
| `/api/v1/audit/` | 审计日志 | 审计员+ |
| `/api/v1/upgrade/` | 升级日志 | 按角色 |
| `/api/v1/dict/` | 字典管理 | 登录 |
| `/api/v1/knowledge/` | 知识库笔记 | 按权限 |
| `/api/v1/wiki/` | Wiki 文档 | 按权限 |
| `/api/v1/dashboard/` | 看板 | 登录 |
