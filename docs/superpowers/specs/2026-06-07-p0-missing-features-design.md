# 2026-06-07 P0 缺失功能修复设计

## 概述

修复 GuiGraph 项目中 P0 级别的两个缺失功能：
1. **权限矩阵页面** — 前端可视化展示
2. **AI 智能检索页面** — RAG 搜索 + 文档分析

## 权限矩阵页面

### 需求
- 静态展示表格，6 角色 × 9 资源
- 绿色 ✓ 表示有权限，灰色 × 表示无权限
- 悬停单元格显示具体操作列表

### 后端 API
新增 `GET /api/v1/permissions/matrix` 返回权限矩阵数据：

```json
{
  "code": "OK",
  "data": {
    "roles": ["system_admin", "dept_admin", "team_admin", "editor", "viewer", "auditor"],
    "resources": ["org", "change", "git", "jenkins", "ai", "audit", "upgrade", "minio", "mcp"],
    "matrix": {
      "system_admin": {
        "org": ["create", "read", "update", "delete", "manage_members"],
        "change": ["create", "read", "update", "delete", "approve"],
        ...
      },
      ...
    }
  }
}
```

### 前端实现
- 路径：`frontend/src/pages/permissions/Matrix.vue`
- 使用 Element Plus Table 渲染矩阵
- 左侧固定列：角色名 + 描述
- 顶部表头：资源名
- 单元格：✓/× + hover 显示操作列表

## AI 智能检索页面

### 需求
- 左栏：搜索框 + 搜索结果卡片列表
- 右栏：文档分析输入框 + 分析结果展示
- 复用现有 `aiAPI.ragSearch` 和 `aiAPI.ragAnalyze`

### 前端实现
- 路径：`frontend/src/pages/ai/Research.vue`
- 左右双栏布局（`el-row` + `el-col`）
- 搜索功能：输入 query → POST `/api/v1/ai/rag/search` → 展示结果
- 分析功能：输入文档 → POST `/api/v1/ai/rag/analyze` → 展示分析结果
- 加载状态：loading 动画

## 文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `backend/app/modules/permissions/router.py` | 新建 | 权限矩阵 API 路由 |
| `backend/app/modules/permissions/service.py` | 新建 | 权限矩阵服务层 |
| `backend/app/modules/permissions/__init__.py` | 新建 | 模块初始化 |
| `frontend/src/pages/permissions/Matrix.vue` | 新建 | 权限矩阵页面 |
| `frontend/src/pages/ai/Research.vue` | 新建 | AI 智能检索页面 |
| `frontend/src/api/permissions.ts` | 新建 | 权限矩阵 API 封装 |

## 依赖
- 后端：FastAPI, SQLAlchemy
- 前端：Vue 3, Element Plus, Axios
