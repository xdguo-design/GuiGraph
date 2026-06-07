# GuiGraph 全功能测试流程文档

## 文档信息

| 项目 | 内容 |
|------|------|
| **版本** | v1.0.0 |
| **总后端 API 数** | 95 |
| **总前端页面数** | 24 |
| **测试负责人** | [待分配] |
| **创建日期** | 2026-06-07 |

---

## 1. 测试环境

### 1.1 环境要求

| 组件 | 配置 |
|------|------|
| **后端** | `http://127.0.0.1:8000` / Python 3.11+ / FastAPI |
| **前端** | `http://localhost:10010` / Node.js 20+ / Vue 3 |
| **数据库** | SQLite (`backend/guigraph.db`) |
| **浏览器** | Chrome 120+, Firefox 120+ |

### 1.2 测试账号

| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| guoxudong | 1234 | system_admin | 全系统权限 |

### 1.3 API Token

所有 API 测试需要使用 Bearer Token：
```bash
# 获取 Token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"guoxudong","password":"1234"}' | python -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")
```

---

## 2. 测试用例

---

### 2.1 认证模块 (Auth)

**相关页面**: `/login`, `/apply`
**API**: `POST /auth/login`, `POST /auth/refresh`, `POST /auth/apply`, `GET /auth/applications`, `POST/POST /auth/applications/{id}/approve|reject`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| AUTH-01 | 登录成功 | POST `/auth/login` 正确用户名密码 | 返回 access_token, refresh_token, token_type=bearer | P0 |
| AUTH-02 | 登录失败(密码错误) | POST `/auth/login` 错误密码 | 返回 401 / code=UNAUTHORIZED | P0 |
| AUTH-03 | 登录失败(用户不存在) | POST `/auth/login` 不存在的用户名 | 返回 401 / code=UNAUTHORIZED | P0 |
| AUTH-04 | Token 刷新 | POST `/auth/refresh` 携带 refresh_token | 返回新 access_token | P1 |
| AUTH-05 | 注册申请 | POST `/auth/apply` 提交注册信息 | 返回 OK，申请单创建 | P1 |
| AUTH-06 | 申请列表(管理员) | GET `/auth/applications` 管理员 token | 返回申请列表 | P1 |
| AUTH-07 | 审核通过 | POST `/auth/applications/{id}/approve` | 状态变为 approved | P1 |
| AUTH-08 | 审核拒绝 | POST `/auth/applications/{id}/reject` | 状态变为 rejected | P1 |
| AUTH-09 | 无 token 访问受保护页面 | 访问 `/kanban` 无 token | 重定向到 `/login` | P0 |

---

### 2.2 仪表盘 (Dashboard)

**相关页面**: `/dashboard`
**API**: `GET /dashboard`, `GET /dashboard/timeline`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| DASH-01 | 仪表盘数据 | GET `/dashboard` 带 token | 返回 stats (total_changes, pending_changes 等) 和 recent_changes | P0 |
| DASH-02 | 管理员查看全量 | 管理员登录查看统计 | `scope = "all"` | P1 |
| DASH-03 | 时间线接口 | GET `/dashboard/timeline` | 返回 items 数组 | P2 |

---

### 2.3 看板日历 & Gantt (Kanban)

**相关页面**: `/kanban`
**API**: `GET /dashboard/kanban`, `GET /dashboard/gantt`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| KAN-01 | 日历视图加载 | GET `/dashboard/kanban?month=2026-06` | 返回 teams, items_by_day, heatmap | P0 |
| KAN-02 | 团队筛选 | GET `/kanban?month=2026-06&team_id=X` | 返回 filtered teams+data | P0 |
| KAN-03 | 无效月份格式 | GET `/kanban?month=invalid` | 返回 400 / BAD_REQUEST | P1 |
| KAN-04 | 热力图数据 | 跨月请求，观察 heatmap | 返回近 12 个月数据 | P1 |
| KAN-05 | Gantt API 数据 | GET `/dashboard/gantt?start_date=2026-06-01&end_date=2026-06-30` | 返回 tasks + dependencies 数组 | P0 |
| KAN-06 | Gantt 视图切换 | 前端切换到 Gantt 视图 | 时间轴按天显示，任务条着色 | P0 |
| KAN-07 | 依赖关系连线 | 查看有依赖的任务 | 箭头从前置到后置任务 | P1 |
| KAN-08 | 月份导航共享 | 日历/Gantt 切换月份 | 月份在两者间保持同步 | P0 |
| KAN-09 | 团队筛选共享 | 日历/Gantt 切换团队 | 筛选在两者间保持同步 | P0 |
| KAN-10 | 点击任务跳转 | 点击 Gantt 任务条 | 跳转到变更详情 | P0 |
| KAN-11 | 空数据 Gantt | 查询无数据月份 | 不报错，显示空状态 | P1 |

---

### 2.4 变更管理 (Changes)

**相关页面**: `/changes`, `/changes/create`, `/changes/:id`
**API**: `GET /changes`, `POST /changes`, `GET /changes/{id}`, `PUT /changes/{id}`, `POST /changes/{id}/approve`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| CHG-01 | 变更列表分页 | GET `/changes?page=1&page_size=10` | 返回 items + total + total_pages | P0 |
| CHG-02 | 变更类型筛选 | GET `/changes?change_type=db` | 只返回 db 类型变更 | P0 |
| CHG-03 | 变更状态筛选 | GET `/changes?status=draft` | 只返回 draft 状态变更 | P0 |
| CHG-04 | 团队筛选 | GET `/changes?team_id=X` | 只返回指定团队变更 | P1 |
| CHG-05 | 创建变更 | POST `/changes` 提交完整表单 | 返回 201，包含新变更数据 | P0 |
| CHG-06 | 创建变更(字段缺失) | POST `/changes` 缺少必填字段 | 返回 422 | P1 |
| CHG-07 | 变更详情 | GET `/changes/1` | 返回变更完整信息 | P0 |
| CHG-08 | 变更详情(不存在) | GET `/changes/99999` | 返回 404 / NOT_FOUND | P0 |
| CHG-09 | 更新变更 | PUT `/changes/1` 更新 content | 返回 OK | P1 |
| CHG-10 | 审批变更 | POST `/changes/1/approve` | 状态变为 approved | P1 |
| CHG-11 | 变更创建表单提交 | 前端填写创建变更表单 | 成功提交并跳转 | P0 |
| CHG-12 | 草稿保存 | 前端保存变更草稿 | 状态为 draft | P2 |

---

### 2.5 组织架构 (Organization)

**相关页面**: `/org`
**API**: 公司/部门/团队 CRUD，成员管理，组织树

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| ORG-01 | 组织树 | GET `/org/tree` | 返回嵌套的公司→部门→团队结构 | P0 |
| ORG-02 | 公司 CRUD | POST/GET/PUT/DELETE `/org/companies` | 完整 CRUD 流程 | P0 |
| ORG-03 | 部门 CRUD | POST/GET/PUT/DELETE `/org/departments` | 完整 CRUD 流程 | P0 |
| ORG-04 | 团队 CRUD | POST/GET/PUT/DELETE `/org/teams` | 完整 CRUD 流程 | P0 |
| ORG-05 | 添加成员 | POST `/org/teams/{id}/members` | 成员加入团队 | P0 |
| ORG-06 | 更新成员角色 | PUT `/org/teams/{id}/members/{user_id}` | 角色更新 | P1 |
| ORG-07 | 移除成员 | DELETE `/org/teams/{id}/members/{user_id}` | 成员被移除 | P1 |
| ORG-08 | 部门层级 | 创建子部门 | 支持 parent_id 嵌套 | P1 |

---

### 2.6 用户中心 (User)

**相关页面**: `/user`
**API**: `GET /user/profile`, `PUT /user/profile`, `POST /user/avatar`, `POST /user/bind-wechat`, `POST /user/unbind-wechat`, `GET /user/wechat-qrcode`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| USR-01 | 获取用户信息 | GET `/user/profile` 带 token | 返回 id, username, nickname 等 | P0 |
| USR-02 | 更新用户信息 | PUT `/user/profile` 更新 nickname/email | 返回更新后信息 | P1 |
| USR-03 | 上传头像 | POST `/user/avatar` 上传图片文件 (2MB 内) | 返回 avatar_url | P1 |
| USR-04 | 上传头像(文件过大) | POST `/user/avatar` 上传 >2MB 文件 | 返回 400 | P1 |
| USR-05 | 上传头像(格式不对) | POST `/user/avatar` 上传 txt 文件 | 返回 400 | P1 |
| USR-06 | 绑定微信(dev) | POST `/user/bind-wechat` 提交 mock code | 绑定成功, mode=mock | P1 |
| USR-07 | 解绑微信 | POST `/user/unbind-wechat` | 解绑成功 | P1 |
| USR-08 | 获取微信二维码 | GET `/user/wechat-qrcode` | 返回 mode 和 tip | P2 |

---

### 2.7 Git 仓库

**相关页面**: `/git`
**API**: `GET/POST/PUT/DELETE /git/repos`, `POST /git/repos/{id}/auth`, `DELETE /git/repos/{id}/auth/{user_id}`, `GET /git/repos/{id}/branches`, `POST /git/merge`, `GET /git/merge/logs`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| GIT-01 | 仓库列表 | GET `/git/repos` | 返回仓库列表 | P0 |
| GIT-02 | 创建仓库 | POST `/git/repos` 提交仓库信息 | 返回新仓库 | P0 |
| GIT-03 | 仓库详情 | GET `/git/repos/1` | 返回仓库信息 | P1 |
| GIT-04 | 更新仓库 | PUT `/git/repos/1` 更新名称 | 更新成功 | P1 |
| GIT-05 | 删除仓库 | DELETE `/git/repos/1` | 删除成功 | P1 |
| GIT-06 | 分支列表 | GET `/git/repos/1/branches` | 返回分支数组 | P0 |
| GIT-07 | 分支合并 | POST `/git/merge` 提交 source/target | 合并成功或返回错误 | P1 |
| GIT-08 | 合并日志 | GET `/git/merge/logs` | 返回日志列表 | P2 |
| GIT-09 | 仓库授权 | POST `/git/repos/1/auth` | 授权成功 | P1 |
| GIT-10 | 撤销授权 | DELETE `/git/repos/1/auth/2` | 授权被撤销 | P1 |
| GIT-11 | 连接测试 | POST `/git/repos/test` 测试仓库连通性 | 返回测试结果 | P2 |

---

### 2.8 Jenkins 集成

**相关页面**: `/jenkins`
**API**: 实例 CRUD, Build 触发/状态/日志/停止

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| JNK-01 | 实例列表 | GET `/jenkins/instances` | 返回分页实例列表 | P0 |
| JNK-02 | 创建实例 | POST `/jenkins/instances` 提交 Jenkins URL+认证 | 返回新实例 | P0 |
| JNK-03 | 实例详情 | GET `/jenkins/instances/1` | 返回实例信息 | P1 |
| JNK-04 | 更新实例 | PUT `/jenkins/instances/1` | 更新成功 | P1 |
| JNK-05 | 删除实例 | DELETE `/jenkins/instances/1` | 删除成功 | P1 |
| JNK-06 | 触发构建 | POST `/jenkins/build` 指定 job_name | 返回 build_id (mock 或真实) | P0 |
| JNK-07 | 构建状态 | GET `/jenkins/build/{build_id}/status` | 返回状态信息 (mock) | P1 |
| JNK-08 | 构建日志 | GET `/jenkins/build/{build_id}/log` | 返回日志 (mock) | P1 |
| JNK-09 | 停止构建 | POST `/jenkins/build/{build_id}/stop` | 停止成功 | P1 |
| JNK-10 | 连接测试 | POST `/jenkins/instances/test` | 返回测试结果 | P2 |

---

### 2.9 升级日志

**相关页面**: `/upgrades`, `/upgrades/:id`
**API**: `GET /upgrades`, `GET /upgrades/{id}`, `POST /upgrades/{id}/export|rollback`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| UPG-01 | 升级日志列表 | GET `/upgrades` 分页参数 | 返回 items + total | P0 |
| UPG-02 | 版本筛选 | GET `/upgrades?version=v2.0` | 按版本号过滤 | P1 |
| UPG-03 | 状态筛选 | GET `/upgrades?status=success` | 按状态过滤 | P1 |
| UPG-04 | 日期范围筛选 | GET `/upgrades?start_time=X&end_time=Y` | 按日期过滤 | P1 |
| UPG-05 | 升级详情 | GET `/upgrades/1` | 返回变更列表、Git commits、构建信息 | P0 |
| UPG-06 | 升级详情(不存在) | GET `/upgrades/99999` | 返回 404 | P0 |
| UPG-07 | 导出升级日志 | POST `/upgrades/{id}/export` | 导出成功 | P2 |
| UPG-08 | 回滚升级 | POST `/upgrades/{id}/rollback` | 回滚成功 | P1 |

---

### 2.10 业务线 (Business Line)

**相关页面**: `/business-line`
**API**: 全 CRUD

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| BSL-01 | 业务线列表 | GET `/business-line` | 返回 items 数组 | P0 |
| BSL-02 | 创建业务线 | POST `/business-line` 提交 name+code | 返回新业务线 | P0 |
| BSL-03 | 业务线详情 | GET `/business-line/1` | 返回详情 | P1 |
| BSL-04 | 更新业务线 | PUT `/business-line/1` | 更新成功 | P1 |
| BSL-05 | 删除业务线 | DELETE `/business-line/1` | 删除成功 | P1 |

---

### 2.11 产品线 (Product Line)

**相关页面**: `/product-line`
**API**: 全 CRUD

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| PRL-01 | 产品线列表 | GET `/product-line` | 返回 items | P0 |
| PRL-02 | 业务线筛选 | GET `/product-line?business_line_id=1` | 按业务线过滤 | P0 |
| PRL-03 | 创建产品线 | POST `/product-line` 提交 name+code+business_line_id | 返回新产品线 | P0 |
| PRL-04 | 产品线详情 | GET `/product-line/1` | 返回详情 | P1 |
| PRL-05 | 更新产品线 | PUT `/product-line/1` | 更新成功 | P1 |
| PRL-06 | 删除产品线 | DELETE `/product-line/1` | 删除成功 | P1 |

---

### 2.12 AI 智能检索

**相关页面**: `/ai-research`
**API**: `POST /ai/rag/search`, `POST /ai/rag/analyze`, `POST /ai/generate/summary`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| AI-01 | RAG 搜索 | POST `/ai/rag/search` 提交 query | 返回搜索结果 | P0 |
| AI-02 | RAG 分析 | POST `/ai/rag/analyze` 提交文档内容 | 返回分析结果 | P0 |
| AI-03 | AI 生成摘要 | POST `/ai/generate/summary` 提交内容 | 返回摘要 | P2 |
| AI-04 | 搜索空关键词 | POST `/ai/rag/search` 空 query | 返回 422 或合理错误 | P1 |

---

### 2.13 权限矩阵

**相关页面**: `/permissions`
**API**: `GET /permissions/matrix`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| PRM-01 | 权限矩阵加载 | GET `/permissions/matrix` | 返回 roles + resources + matrix | P0 |
| PRM-02 | 矩阵前端渲染 | 前端页面显示矩阵表格 | 角色×资源的 ✓/× 网格 | P0 |
| PRM-03 | 角色筛选 | 选择特定角色 | 只显示该列 | P1 |
| PRM-04 | 资源筛选 | 选择特定资源 | 只显示该行 | P1 |

---

### 2.14 审计日志

**相关页面**: `/audit-logs`
**API**: `GET /audit`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| AUD-01 | 审计日志列表 | GET `/audit` 分页参数 | 返回 items + total | P0 |
| AUD-02 | 用户筛选 | GET `/audit?user_id=X` | 按用户过滤 | P1 |
| AUD-03 | 操作类型筛选 | GET `/audit?operation=create` | 按操作类型过滤 | P1 |
| AUD-04 | 日期范围筛选 | GET `/audit?start_time=X&end_time=Y` | 按日期过滤 | P1 |

---

### 2.15 知识库笔记

**相关页面**: `/knowledge`
**API**: 知识库 CRUD + 笔记 CRUD + AI 生成 + 版本

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| KNW-01 | 知识库列表 | GET `/knowledge/bases` | 返回知识库列表 | P0 |
| KNW-02 | 创建知识库 | POST `/knowledge/bases` 提交 name+code | 返回新知识库 | P0 |
| KNW-03 | 知识库详情 | GET `/knowledge/bases/1` | 返回知识库信息 | P1 |
| KNW-04 | 笔记列表 | GET `/knowledge/notes?kb_id=1` | 返回指定知识库的笔记 | P0 |
| KNW-05 | 创建笔记 | POST `/knowledge/notes` 提交 title+content+kb_id | 返回新笔记 | P0 |
| KNW-06 | 笔记详情 | GET `/knowledge/notes/1` | 返回笔记内容 | P1 |
| KNW-07 | 更新笔记 | PUT `/knowledge/notes/1` | 更新成功 | P1 |
| KNW-08 | 删除笔记 | DELETE `/knowledge/notes/1` | 删除成功 | P1 |
| KNW-09 | AI 生成笔记 | POST `/knowledge/notes/1/ai-generate` | 返回 AI 生成内容 | P2 |
| KNW-10 | 笔记版本历史 | GET `/knowledge/notes/1/versions` | 返回版本列表 | P2 |
| KNW-11 | 标签筛选 | 创建带标签的笔记并筛选 | 按标签过滤正确 | P1 |

---

### 2.16 Wiki 文档

**相关页面**: 路由已配置 (`/wiki/spaces`, `/wiki/docs`)
**API**: 空间 CRUD + 文档 CRUD

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| WIK-01 | 空间列表 | GET `/wiki/spaces` | 返回空间列表 | P0 |
| WIK-02 | 创建空间 | POST `/wiki/spaces` 提交 name+key | 返回新空间 | P0 |
| WIK-03 | 文档列表 | GET `/wiki/docs?space_id=1` | 返回空间下文档 | P0 |
| WIK-04 | 创建文档 | POST `/wiki/docs` 提交 title+content+space_id | 返回新文档 | P0 |
| WIK-05 | 文档详情 | GET `/wiki/1` | 返回文档内容 | P1 |
| WIK-06 | 更新文档 | PUT `/wiki/docs/1` | 更新成功 | P1 |
| WIK-07 | 删除文档 | DELETE `/wiki/docs/1` | 删除成功 | P1 |

---

### 2.17 字典管理

**相关页面**: 路由已配置
**API**: 领域/应用/组件 CRUD

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| DCT-01 | 领域列表 | GET `/dict/domains` | 返回领域列表 | P1 |
| DCT-02 | 创建领域 | POST `/dict/domains` 提交 name+code+team_id | 返回新领域 | P1 |
| DCT-03 | 应用列表 | GET `/dict/applications` | 返回应用列表 | P1 |
| DCT-04 | 创建应用 | POST `/dict/applications` | 返回新应用 | P1 |
| DCT-05 | 组件列表 | GET `/dict/components` | 返回组件列表 | P1 |
| DCT-06 | 创建组件 | POST `/dict/components` | 返回新组件 | P1 |

---

### 2.18 管理员功能

**相关页面**: `/applications`(账号审核), `/demo-data`(演示数据)
**API**: 用户管理, 演示数据种子

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| ADM-01 | 用户列表(管理员) | GET `/user-admin/list` | 返回用户列表 | P0 |
| ADM-02 | 更新用户状态 | PUT `/user-admin/1/status` | 状态更新成功 | P1 |
| ADM-03 | 分配团队 | POST `/user-admin/1/teams` | 用户加入团队 | P1 |
| ADM-04 | 移除团队 | DELETE `/user-admin/1/teams/1` | 用户移出团队 | P1 |
| ADM-05 | 生成演示数据 | POST `/demo/seed` | 生成演示数据 | P1 |
| ADM-06 | 清除演示数据 | DELETE `/demo/seed` | 清除所有演示数据 | P1 |
| ADM-07 | 个人看板演示 | GET `/demo/kanban/personal` | 返回个人演示看板 | P2 |
| ADM-08 | 团队看板演示 | GET `/demo/kanban/teams` + GET `/demo/kanban/team/1` | 返回团队演示看板 | P2 |

---

### 2.19 附件管理

**相关页面**: 无独立页面（嵌入其他模块）
**API**: `POST /attachment/upload`, `GET /attachment/list`, `GET /attachment/download/{id}`, `DELETE /attachment/delete/{id}`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| ATT-01 | 上传文件 | POST `/attachment/upload` 上传图片 | 返回 file_id + url | P1 |
| ATT-02 | 文件列表 | GET `/attachment/list` | 返回文件列表 | P1 |
| ATT-03 | 下载文件 | GET `/attachment/download/1` | 返回文件内容 | P1 |
| ATT-04 | 删除文件 | DELETE `/attachment/delete/1` | 删除成功 | P1 |

---

### 2.20 版本合并

**相关页面**: `/version-merge`

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| VER-01 | 版本合并页面加载 | 前端访问 `/version-merge` | 页面正常加载 | P0 |
| VER-02 | 合并操作提交 | 前端提交合并请求 | 调用 `/git/merge` API | P1 |

---

### 2.21 通用/系统

| # | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| SYS-01 | 健康检查 | GET `/health` | 返回 `{"status":"healthy"}` | P0 |
| SYS-02 | 根路径 | GET `/` | 返回 API 欢迎信息 | P0 |
| SYS-03 | 404 页面 | 访问不存在的路由 | 显示 404 页面 | P0 |
| SYS-04 | 403 页面 | 普通用户访问管理员页面 | 显示 403 页面 | P0 |
| SYS-05 | 未认证 401 | 无 token 调用 API | 返回 401 / UNAUTHORIZED | P0 |
| SYS-06 | 前端导航菜单 | 访问所有侧边栏菜单项 | 页面正常加载 | P0 |

---

## 3. 缺陷报告模板

### 3.1 缺陷记录表

| 缺陷ID | 所属模块 | 关联用例 | 缺陷标题 | 严重程度 | 状态 | 发现人 | 指派给 | 发现日期 |
|--------|---------|---------|---------|----------|------|--------|--------|----------|
| BUG-001 | - | - | - | P0/P1/P2 | 新建 | - | - | - |

**严重程度定义:**
- **P0 (Critical)**: 主流程阻断，阻塞发布
- **P1 (Major)**: 功能受损，但有绕过方案
- **P2 (Minor)**: 次要问题，不影响功能
- **P3 (Trivial)**: UI 细节、文案、兼容性

---

## 4. 测试执行记录

### 4.1 执行统计表

| 模块 | 用例数 | 已执行 | 通过 | 失败 | 阻塞 | 通过率 |
|------|--------|--------|------|------|------|--------|
| 认证 Auth | 9 | 0 | 0 | 0 | 0 | - |
| 仪表盘 Dashboard | 3 | 0 | 0 | 0 | 0 | - |
| 看板 Kanban/Gantt | 11 | 0 | 0 | 0 | 0 | - |
| 变更管理 Changes | 12 | 0 | 0 | 0 | 0 | - |
| 组织架构 Org | 8 | 0 | 0 | 0 | 0 | - |
| 用户中心 User | 8 | 0 | 0 | 0 | 0 | - |
| Git 仓库 | 11 | 0 | 0 | 0 | 0 | - |
| Jenkins 集成 | 10 | 0 | 0 | 0 | 0 | - |
| 升级日志 Upgrade | 8 | 0 | 0 | 0 | 0 | - |
| 业务线 Business Line | 5 | 0 | 0 | 0 | 0 | - |
| 产品线 Product Line | 6 | 0 | 0 | 0 | 0 | - |
| AI 智能检索 | 4 | 0 | 0 | 0 | 0 | - |
| 权限矩阵 Permissions | 4 | 0 | 0 | 0 | 0 | - |
| 审计日志 Audit | 4 | 0 | 0 | 0 | 0 | - |
| 知识库笔记 Knowledge | 11 | 0 | 0 | 0 | 0 | - |
| Wiki 文档 | 7 | 0 | 0 | 0 | 0 | - |
| 字典管理 Dictionary | 6 | 0 | 0 | 0 | 0 | - |
| 管理员 Admin | 8 | 0 | 0 | 0 | 0 | - |
| 附件管理 Attachment | 4 | 0 | 0 | 0 | 0 | - |
| 版本合并 Version | 2 | 0 | 0 | 0 | 0 | - |
| 通用/系统 System | 6 | 0 | 0 | 0 | 0 | - |
| **总计** | **147** | **0** | **0** | **0** | **0** | **-** |

---

## 5. 验收标准

### 5.1 功能验收

- [ ] 所有 P0 级别用例 (40+) 全部通过
- [ ] 认证流程完整（登录/刷新/注册/审核）
- [ ] 看板日历和 Gantt 视图正常切换显示
- [ ] 变更管理完整 CRUD
- [ ] 组织架构树形结构正确
- [ ] 所有 CRUD 页面创建/编辑/删除正常
- [ ] 各筛选条件正确过滤数据

### 5.2 性能验收

- [ ] API 响应时间 < 500ms (单次查询)
- [ ] 列表页分页加载 < 2s
- [ ] Gantt 图渲染 < 2s

### 5.3 兼容性验收

- [ ] Chrome 120+ 正常显示
- [ ] Firefox 120+ 正常显示
- [ ] 移动端 (375px+) 布局可读

### 5.4 稳定性验收

- [ ] 连续切换页面 20 次无报错
- [ ] 快速点击操作按钮无异常
- [ ] 输入特殊字符/超长文本无崩溃

---

## 6. API 调用速查表

```bash
# 登录
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"guoxudong","password":"1234"}' | python -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")

# API 测试模板
curl -s http://127.0.0.1:8000/api/v1/<endpoint> \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# POST 请求示例
curl -s -X POST http://127.0.0.1:8000/api/v1/changes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version_id":1,"change_type":"db","content":"测试变更","change_reason":"requirement"}' | python -m json.tool
```

---

## 7. 已知限制

| 限制 | 说明 |
|------|------|
| Jenkins build | 无真实 Jenkins 实例时返回 mock 数据 |
| Git branch/merge | 无真实 Git 仓库时返回 mock 数据 |
| RAG Search/Analyze | 需要 RAGFlow 服务，无则返回错误 |
| WeChat OAuth | 开发模式使用 mock openid |
| Avatar Upload | 本地文件存储，非 MinIO |
| Gantt end_date | 与 start_date 相同（单日任务），待扩展 |

---

**文档版本历史**

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| v1.0.0 | 2026-06-07 | Dev Team | 首次发布，覆盖 21 模块 147 用例 |

---

*本文档归 GuiGraph 项目组所有*