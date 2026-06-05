# GuiGraph

版本变更管理系统 — 开源、私有化、分阶段落地。

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python FastAPI |
| 前端 | Vue 3 + TypeScript + Element Plus |
| 数据库 | PostgreSQL (MVP) |
| 对象存储 | MinIO |
| RAG 引擎 | RAGFlow |
| 知识图谱 | GraphRAG |
| 容器编排 | Docker Compose |

## 快速开始

```bash
# 1. 启动所有服务
docker-compose up -d

# 2. 访问系统
# 前端: http://localhost
# 后端 API: http://localhost:8000
# 后端文档: http://localhost:8000/docs
# MinIO 控制台: http://localhost:9001

# 3. 本地开发
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/base.txt
cp .env.example .env
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 目录结构

详见 [docs/directory-structure-design.md](docs/directory-structure-design.md)

## 开发计划

- [x] 项目目录结构设计
- [x] 后端核心框架 (FastAPI)
- [x] MVP 模块 (auth, user, organization, change, git, jenkins)
- [x] 前端初始化 (Vue 3)
- [x] 核心页面 (login, dashboard, change, organization, user)
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
