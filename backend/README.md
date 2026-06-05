# GuiGraph 后端

版本变更管理系统后端服务。

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements/base.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入实际配置

# 4. 运行开发服务器
uvicorn app.main:app --reload --port 8000

# 5. 运行测试
pytest tests/
```

## 目录结构

详见 `docs/directory-structure-design.md`

## 开发环境

- Python 3.11+
- PostgreSQL 14+ (MVP)
- MinIO (对象存储)
- RAGFlow (RAG 引擎)
- GraphRAG (知识图谱)
