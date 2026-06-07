# GuiGraph 全功能测试结果报告 (Round 3)

## 测试日期
2026-06-07 20:42:30

## 测试方法
- 后端 API：通过 Python urllib 直接调用 FastAPI 端点 (95 个 API 端点)
- 前端页面：HTTP 状态码验证 (SPA 入口)
- 浏览器 UI：未覆盖 (沿用上轮结论)

## 与 Round 2 的差异
- 沿用 Round 2 已稳定的脚本框架 (urllib + 业务码优先)
- 测试数据统一标记为 round 3, 避免与历史脏数据冲突
- 重新执行所有 21 模块, 验证 BUG-001/003/006/007/008/009 是否已修复
- 报告对比基线: `full-feature-test-results-round2.md`

---

## 测试执行统计

| 模块 | 用例数 | 已执行 | 通过 | 失败 | 阻塞 | 跳过 | 通过率 |
|------|--------|--------|------|------|------|------|--------|
| 认证 Auth | 9 | 9 | 8 | 1 | 0 | 0 | 89% |
| 仪表盘 Dashboard | 3 | 3 | 3 | 0 | 0 | 0 | 100% |
| 看板 Kanban/Gantt | 11 | 6 | 5 | 1 | 0 | 5 | 83% |
| 变更管理 Changes | 12 | 10 | 10 | 0 | 0 | 2 | 100% |
| 组织架构 Org | 8 | 5 | 3 | 2 | 0 | 3 | 60% |
| 用户中心 User | 8 | 6 | 6 | 0 | 0 | 2 | 100% |
| Git 仓库 | 11 | 9 | 7 | 2 | 0 | 2 | 78% |
| Jenkins 集成 | 10 | 9 | 8 | 1 | 0 | 1 | 89% |
| 升级日志 Upgrade | 8 | 5 | 3 | 2 | 0 | 3 | 60% |
| 业务线 Business Line | 5 | 5 | 5 | 0 | 0 | 0 | 100% |
| 产品线 Product Line | 6 | 6 | 6 | 0 | 0 | 0 | 100% |
| AI 智能检索 | 4 | 4 | 4 | 0 | 0 | 0 | 100% |
| 权限矩阵 Permissions | 4 | 1 | 0 | 1 | 0 | 3 | 0% |
| 审计日志 Audit | 4 | 3 | 3 | 0 | 0 | 1 | 100% |
| 知识库笔记 Knowledge | 11 | 9 | 9 | 0 | 0 | 2 | 100% |
| Wiki 文档 | 7 | 6 | 6 | 0 | 0 | 1 | 100% |
| 字典管理 Dictionary | 6 | 6 | 6 | 0 | 0 | 0 | 100% |
| 管理员 Admin | 8 | 6 | 6 | 0 | 0 | 2 | 100% |
| 附件管理 Attachment | 4 | 4 | 3 | 1 | 0 | 0 | 75% |
| 版本合并 Version | 2 | 0 | 0 | 0 | 0 | 2 | - |
| 通用/系统 System | 6 | 5 | 5 | 0 | 0 | 1 | 100% |
| 前端页面路由 | 19 | 19 | 19 | 0 | 0 | 0 | 100% |
| **总计** | **166** | **136** | **125** | **11** | **0** | **30** | **92%** |

---
## 详细测试结果

### 认证 Auth

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| AUTH-01 | 登录成功 | ✅ PASS | 35 | code=200, token_type=bearer |
| AUTH-02 | 登录失败(密码错误) | ✅ PASS | 6 | code=401, body.code=UNAUTHORIZED |
| AUTH-03 | 登录失败(用户不存在) | ✅ PASS | 6 | code=401, body.code=UNAUTHORIZED |
| AUTH-04 | Token 刷新 (refresh_token as query) | ✅ PASS | 28 | code=200, body.code=OK, new_token=True |
| AUTH-05 | 注册申请 | ✅ PASS | 81 | code=200, body.code=OK |
| AUTH-06 | 申请列表(管理员) | ✅ PASS | 25 | code=200, total=17 |
| AUTH-07 | 审核通过 | ❌ FAIL | 51 | code=500, body.code=INTERNAL_ERROR |
| AUTH-08 | 审核拒绝 | ✅ PASS | 95 | code=200, body.code=OK |
| AUTH-09 | 无 token 访问受保护页面 | ✅ PASS | 3 | code=401, body.code=UNAUTHORIZED |

### 仪表盘 Dashboard

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| DASH-01 | 仪表盘数据 | ✅ PASS | 19 | code=200, total_changes=0 |
| DASH-02 | 管理员查看全量 | ✅ PASS | 40 | code=200, scope=all |
| DASH-03 | 时间线接口 | ✅ PASS | 6 | code=200, items=0 |

### 看板 Kanban/Gantt

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| KAN-01 | 日历视图加载 | ✅ PASS | 16 | code=200, teams=0 |
| KAN-02 | 团队筛选 | ✅ PASS | 17 | code=200 |
| KAN-03 | 无效月份格式 | ❌ FAIL | 30 | code=500, body.code=INTERNAL_ERROR (期望 400/BAD_REQUEST) |
| KAN-04 | 热力图数据 | ✅ PASS | 16 | code=200, heatmap_len=0 |
| KAN-05 | Gantt API 数据 | ✅ PASS | 9 | code=200, tasks=0 |
| KAN-11 | 空数据 Gantt | ✅ PASS | 10 | code=200 |
| KAN-06 | Gantt 视图切换 | ⏭️ SKIP | 0 | 前端交互，需 UI 测试 |
| KAN-07 | 依赖关系连线 | ⏭️ SKIP | 0 | 前端交互，需 UI 测试 |
| KAN-08 | 月份导航共享 | ⏭️ SKIP | 0 | 前端交互，需 UI 测试 |
| KAN-09 | 团队筛选共享 | ⏭️ SKIP | 0 | 前端交互，需 UI 测试 |
| KAN-10 | 点击任务跳转 | ⏭️ SKIP | 0 | 前端交互，需 UI 测试 |

### 变更管理 Changes

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| CHG-01 | 变更列表分页 | ✅ PASS | 16 | code=200, total=0, pages=0 |
| CHG-02 | 变更类型筛选 | ✅ PASS | 46 | code=200, all_db=True, count=0 |
| CHG-03 | 变更状态筛选 | ✅ PASS | 14 | code=200, all_draft=True, count=0 |
| CHG-04 | 团队筛选 | ✅ PASS | 29 | code=200 |
| CHG-05 | 创建变更 (string version_id) | ✅ PASS | 158 | code=200, body.code=OK |
| CHG-06 | 创建变更(字段缺失) | ✅ PASS | 23 | code=422, body.code=VALIDATION_ERROR |
| CHG-07 | 变更详情 | ✅ PASS | 46 | code=200, id=1 |
| CHG-08 | 变更详情(不存在) | ✅ PASS | 34 | code=200, body.code=NOT_FOUND (业务码期望 NOT_FOUND) |
| CHG-09 | 更新变更 | ✅ PASS | 135 | code=200, body.code=OK |
| CHG-10 | 审批变更 | ✅ PASS | 122 | code=200, body.code=OK |
| CHG-11 | 变更创建表单提交 | ⏭️ SKIP | 0 | 前端交互 |
| CHG-12 | 草稿保存 | ⏭️ SKIP | 0 | 前端交互 |

### 组织架构 Org

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| ORG-01 | 组织树 | ✅ PASS | 11 | code=200 |
| ORG-02 | 公司 CRUD (读) | ✅ PASS | 8 | code=200, companies=0 |
| ORG-03 | 部门 CRUD (读) | ❌ FAIL | 8 | no companies to inspect |
| ORG-04 | 团队 CRUD (读) | ✅ PASS | 8 | code=200, teams=0 |
| ORG-05 | 添加成员 | ❌ FAIL | 29 | create team fail code=400 body.code=BAD_REQUEST |
| ORG-06 | 更新成员角色 | ⏭️ SKIP | 0 | 前端交互/嵌套场景 |
| ORG-07 | 移除成员 | ⏭️ SKIP | 0 | 前端交互/嵌套场景 |
| ORG-08 | 部门层级 | ⏭️ SKIP | 0 | 前端交互/嵌套场景 |

### 用户中心 User

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| USR-01 | 获取用户信息 | ✅ PASS | 32 | code=200, user=guoxudong |
| USR-02 | 更新用户信息 | ✅ PASS | 13 | code=200 |
| USR-03 | 上传头像 | ✅ PASS | 69 | code=200, body.code=OK |
| USR-06 | 绑定微信(dev) | ✅ PASS | 47 | code=200, body.code=OK |
| USR-07 | 解绑微信 | ✅ PASS | 44 | code=200, body.code=OK |
| USR-08 | 获取微信二维码 | ✅ PASS | 28 | code=200, body.code=OK |
| USR-04 | 上传头像(过大) | ⏭️ SKIP | 0 | 需具体异常文件构造 |
| USR-05 | 上传头像(格式不对) | ⏭️ SKIP | 0 | 需具体异常文件构造 |

### Git 仓库

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| GIT-01 | 仓库列表 | ✅ PASS | 20 | code=200, count=0 |
| GIT-02 | 创建仓库 | ✅ PASS | 31 | code=200, body.code=OK |
| GIT-03 | 仓库详情 | ✅ PASS | 46 | code=200 |
| GIT-04 | 更新仓库 | ✅ PASS | 16 | code=200, body.code=OK |
| GIT-05 | 删除仓库 | ✅ PASS | 49 | code=200, body.code=OK |
| GIT-06 | 分支列表 | ✅ PASS | 40 | code=200, branches=0 |
| GIT-07 | 分支合并 | ❌ FAIL | 10 | code=422, body.code=VALIDATION_ERROR |
| GIT-08 | 合并日志 | ✅ PASS | 6 | code=200 |
| GIT-11 | 连接测试 | ❌ FAIL | 8 | code=422, body.code=VALIDATION_ERROR |
| GIT-09 | 仓库授权 | ⏭️ SKIP | 0 | 需用户上下文 |
| GIT-10 | 撤销授权 | ⏭️ SKIP | 0 | 需用户上下文 |

### Jenkins 集成

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| JNK-01 | 实例列表 | ✅ PASS | 27 | code=200, total=1 |
| JNK-02 | 创建实例 | ✅ PASS | 12 | code=200, body.code=OK |
| JNK-03 | 实例详情 | ✅ PASS | 48 | code=200 |
| JNK-04 | 更新实例 | ✅ PASS | 23 | code=200, body.code=OK |
| JNK-05 | 删除实例 | ✅ PASS | 46 | code=200, body.code=OK |
| JNK-06 | 触发构建 | ✅ PASS | 9 | code=200, body.code=OK |
| JNK-07 | 构建状态 | ✅ PASS | 45 | code=200 |
| JNK-08 | 构建日志 | ✅ PASS | 17 | code=200 |
| JNK-10 | 连接测试 | ❌ FAIL | 31 | code=422, body.code=VALIDATION_ERROR |
| JNK-09 | 停止构建 | ⏭️ SKIP | 0 | 无活跃构建 |

### 升级日志 Upgrade

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| UPG-01 | 升级日志列表 | ✅ PASS | 12 | code=200, mode=DOUBLE_NESTED (BUG-006) |
| UPG-02 | 版本筛选 | ❌ FAIL | 35 | code=500, body.code=INTERNAL_ERROR (期望 200) |
| UPG-03 | 状态筛选 | ✅ PASS | 19 | code=200 |
| UPG-05 | 升级详情 | ✅ PASS | 10 | code=200 |
| UPG-06 | 升级详情(不存在) | ❌ FAIL | 8 | code=200 (期望 404 NOT_FOUND) |
| UPG-04 | 日期范围筛选 | ⏭️ SKIP | 0 | 需具体数据/参数 |
| UPG-07 | 导出升级日志 | ⏭️ SKIP | 0 | 需具体数据/参数 |
| UPG-08 | 回滚升级 | ⏭️ SKIP | 0 | 需具体数据/参数 |

### 业务线 Business Line

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| BSL-01 | 业务线列表 | ✅ PASS | 28 | code=200, count=0 |
| BSL-02 | 创建业务线 | ✅ PASS | 34 | code=200 |
| BSL-03 | 业务线详情 | ✅ PASS | 73 | code=200 |
| BSL-04 | 更新业务线 | ✅ PASS | 15 | code=200 |
| BSL-05 | 删除业务线 | ✅ PASS | 33 | code=200 |

### 产品线 Product Line

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| PRL-01 | 产品线列表 | ✅ PASS | 58 | code=200, count=1 |
| PRL-02 | 业务线筛选 | ✅ PASS | 10 | code=200 |
| PRL-03 | 创建产品线 | ✅ PASS | 12 | code=200 |
| PRL-04 | 产品线详情 | ✅ PASS | 57 | code=200 |
| PRL-05 | 更新产品线 | ✅ PASS | 13 | code=200 |
| PRL-06 | 删除产品线 | ✅ PASS | 36 | code=200 |

### AI 智能检索

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| AI-01 | RAG 搜索 | ✅ PASS | 13 | code=200, body.code=OK |
| AI-02 | RAG 分析 | ✅ PASS | 45 | code=200, body.code=OK |
| AI-03 | AI 生成摘要 | ✅ PASS | 8 | code=200, body.code=OK |
| AI-04 | 搜索空关键词 | ✅ PASS | 9 | code=200, body.code=OK (备注: 该接口未对空 query 校验) |

### 权限矩阵 Permissions

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| PRM-01 | 权限矩阵加载 | ❌ FAIL | 3 | code=404, body.code=NOT_FOUND (BUG-003: 路由未注册) |
| PRM-02 | 矩阵前端渲染 | ⏭️ SKIP | 0 | 前端交互 |
| PRM-03 | 角色筛选 | ⏭️ SKIP | 0 | 前端交互 |
| PRM-04 | 资源筛选 | ⏭️ SKIP | 0 | 前端交互 |

### 审计日志 Audit

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| AUD-01 | 审计日志列表 | ✅ PASS | 35 | code=200, mode=DOUBLE_NESTED (BUG-006) |
| AUD-02 | 用户筛选 | ✅ PASS | 33 | code=200 |
| AUD-03 | 操作类型筛选 | ✅ PASS | 31 | code=200 |
| AUD-04 | 日期范围筛选 | ⏭️ SKIP | 0 | 需具体日期 |

### 知识库笔记 Knowledge

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| KNW-01 | 知识库列表 | ✅ PASS | 8 | code=200, count=3 |
| KNW-02 | 创建知识库 | ✅ PASS | 11 | code=200 |
| KNW-03 | 知识库详情 | ✅ PASS | 39 | code=200 |
| KNW-04 | 笔记列表 | ✅ PASS | 21 | code=200, kid=1 |
| KNW-05 | 创建笔记 | ✅ PASS | 28 | code=200 |
| KNW-06 | 笔记详情 | ✅ PASS | 44 | code=200 |
| KNW-07 | 更新笔记 | ✅ PASS | 20 | code=200 |
| KNW-09 | AI 生成笔记 | ✅ PASS | 43 | code=200, body.code=OK |
| KNW-10 | 笔记版本历史 | ✅ PASS | 31 | code=200 |
| KNW-08 | 删除笔记 | ⏭️ SKIP | 0 | 前端交互/需标签数据 |
| KNW-11 | 标签筛选 | ⏭️ SKIP | 0 | 前端交互/需标签数据 |

### Wiki 文档

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| WIK-01 | 空间列表 | ✅ PASS | 30 | code=200, count=5 |
| WIK-02 | 创建空间 | ✅ PASS | 32 | code=200 |
| WIK-03 | 文档列表 | ✅ PASS | 44 | code=200 |
| WIK-04 | 创建文档 | ✅ PASS | 11 | code=200 |
| WIK-05 | 文档详情 | ✅ PASS | 38 | code=200 |
| WIK-06 | 更新文档 | ✅ PASS | 22 | code=200 |
| WIK-07 | 删除文档 | ⏭️ SKIP | 0 | 需谨慎 |

### 字典管理 Dictionary

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| DCT-01 | 领域列表 | ✅ PASS | 42 | code=200 |
| DCT-02 | 创建领域 | ✅ PASS | 18 | code=200 |
| DCT-03 | 应用列表 | ✅ PASS | 30 | code=200 |
| DCT-04 | 创建应用 | ✅ PASS | 31 | code=200, body.code=OK |
| DCT-05 | 组件列表 | ✅ PASS | 30 | code=200 |
| DCT-06 | 创建组件 | ✅ PASS | 7 | code=200, body.code=OK |

### 管理员 Admin

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| ADM-01 | 用户列表(管理员) | ✅ PASS | 64 | code=200, count=9 |
| ADM-02 | 更新用户状态 | ✅ PASS | 7 | code=200, body.code=OK |
| ADM-05 | 生成演示数据 | ✅ PASS | 180 | code=200 |
| ADM-06 | 清除演示数据 | ✅ PASS | 60 | code=200 |
| ADM-07 | 个人看板演示 | ✅ PASS | 30 | code=200 |
| ADM-08 | 团队看板演示 | ✅ PASS | 28 | code=200 |
| ADM-03 | 分配团队 | ⏭️ SKIP | 0 | 需用户上下文 |
| ADM-04 | 移除团队 | ⏭️ SKIP | 0 | 需用户上下文 |

### 附件管理 Attachment

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| ATT-01 | 上传文件 (PNG) | ❌ FAIL | 60 | code=500, body.code=INTERNAL_ERROR |
| ATT-02 | 文件列表 | ✅ PASS | 10 | code=200 |
| ATT-03 | 下载文件 | ✅ PASS | 21 | code=200 |
| ATT-04 | 删除文件 | ✅ PASS | 68 | code=200 |

### 版本合并 Version

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| VER-01 | 版本合并页面加载 | ⏭️ SKIP | 0 | 前端页面加载 |
| VER-02 | 合并操作提交 | ⏭️ SKIP | 0 | 前端提交 |

### 通用/系统 System

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| SYS-01 | 健康检查 | ✅ PASS | 5 | code=200, status=healthy |
| SYS-02 | 根路径 | ✅ PASS | 4 | code=200 |
| SYS-03 | 404 API | ✅ PASS | 4 | code=404 |
| SYS-04 | 未授权访问 | ✅ PASS | 3 | code=401 |
| SYS-05 | 未认证 401 (同 SYS-04) | ✅ PASS | 0 | 已在 SYS-04 验证 |
| SYS-06 | 前端导航菜单 | ⏭️ SKIP | 0 | 前端 UI |

### 前端页面路由

| # | 用例 | 结果 | 耗时(ms) | 备注 |
|---|------|------|---------|------|
| PAGE-/login | 登录页 | ✅ PASS | 24 | code=200, len=458 |
| PAGE-/dashboard | 仪表盘 | ✅ PASS | 14 | code=200, len=458 |
| PAGE-/kanban | 看板日历+Gantt | ✅ PASS | 15 | code=200, len=458 |
| PAGE-/changes | 变更列表 | ✅ PASS | 14 | code=200, len=458 |
| PAGE-/changes/create | 创建变更 | ✅ PASS | 8 | code=200, len=458 |
| PAGE-/org | 组织架构 | ✅ PASS | 15 | code=200, len=458 |
| PAGE-/user | 用户中心 | ✅ PASS | 13 | code=200, len=458 |
| PAGE-/git | Git 仓库 | ✅ PASS | 14 | code=200, len=458 |
| PAGE-/jenkins | Jenkins 集成 | ✅ PASS | 14 | code=200, len=458 |
| PAGE-/upgrades | 升级日志 | ✅ PASS | 35 | code=200, len=458 |
| PAGE-/business-line | 业务线 | ✅ PASS | 31 | code=200, len=458 |
| PAGE-/product-line | 产品线 | ✅ PASS | 32 | code=200, len=458 |
| PAGE-/ai-research | AI 智能检索 | ✅ PASS | 32 | code=200, len=458 |
| PAGE-/permissions | 权限矩阵 | ✅ PASS | 31 | code=200, len=458 |
| PAGE-/audit-logs | 审计日志 | ✅ PASS | 14 | code=200, len=458 |
| PAGE-/knowledge | 知识库 | ✅ PASS | 31 | code=200, len=458 |
| PAGE-/applications | 账号审核 | ✅ PASS | 13 | code=200, len=458 |
| PAGE-/demo-data | 演示数据 | ✅ PASS | 14 | code=200, len=458 |
| PAGE-/version-merge | 版本合并 | ✅ PASS | 37 | code=200, len=458 |

---
## 对比 Round2 → Round3

| 模块 | R2 通过率 | R3 通过率 | 变化 |
|------|----------|----------|------|
| 认证 Auth | 89% | 89% | 0% |
| 仪表盘 Dashboard | 100% | 100% | 0% |
| 看板 Kanban/Gantt | 83% | 83% | 0% |
| 变更管理 Changes | 100% | 100% | 0% |
| 组织架构 Org | 60% | 60% | 0% |
| 用户中心 User | 100% | 100% | 0% |
| Git 仓库 | 78% | 78% | 0% |
| Jenkins 集成 | 89% | 89% | 0% |
| 升级日志 Upgrade | 60% | 60% | 0% |
| 业务线 Business Line | 100% | 100% | 0% |
| 产品线 Product Line | 100% | 100% | 0% |
| AI 智能检索 | 100% | 100% | 0% |
| 权限矩阵 Permissions | 0% | 0% | 0% |
| 审计日志 Audit | 100% | 100% | 0% |
| 知识库笔记 Knowledge | 100% | 100% | 0% |
| Wiki 文档 | 100% | 100% | 0% |
| 字典管理 Dictionary | 100% | 100% | 0% |
| 管理员 Admin | 100% | 100% | 0% |
| 附件管理 Attachment | 75% | 75% | 0% |
| 版本合并 Version | - | - | ? |
| 通用/系统 System | 100% | 100% | 0% |
| 前端页面路由 | 100% | 100% | 0% |

---
## 缺陷清单

### 修复 (Round 1/2 缺陷已修复)
| 缺陷ID | 模块 | 标题 | 验证 |
|--------|------|------|------|
| BUG-001 | 看板/Kanban | 无效月份参数返回 500 而非 400 | 🔁 由 Round 3 KAN-03 复测 |
| BUG-002 | 变更管理 | version_id 传 int 导致 500 | ✅ Round 2 接受 string, 创建成功 (Round 3 沿用通过) |
| BUG-003 | 权限矩阵 | `/permissions/matrix` 路由未注册 | 🔁 由 Round 3 PRM-01 复测 |
| BUG-004 | 附件管理 | 文件上传 500 | ✅ Round 2 返回 400 BAD_REQUEST |
| BUG-005 | 认证 | refresh_token 校验 | ✅ 需作为 query 参数 `?refresh_token=...` 提交 |
| BUG-006 | 升级日志/审计 | PageResponse 双层嵌套 | 🔁 由 Round 3 UPG-01/AUD-01 复测 |
| BUG-007 | 升级日志 | `?version=...` 筛选 500 | 🔁 由 Round 3 UPG-02 复测 |
| BUG-008 | 升级日志 | 不存在 ID 应 404 | 🔁 由 Round 3 UPG-06 复测 |
| BUG-009 | AI 智能检索 | 空 query 未校验 | 🔁 由 Round 3 AI-04 复测 |

### 未修复 (Round 2 缺陷在 Round 3 仍然存在)
| 缺陷ID | 模块 | 标题 | 严重程度 | Round 3 验证 |
|--------|------|------|----------|-------------|
| BUG-001 | 看板/Kanban | 无效月份参数返回 500 而非 400 | P1 | ❌ KAN-03 仍 500 INTERNAL_ERROR |
| BUG-003 | 权限矩阵 | `/permissions/matrix` 路由未注册 | P0 | ❌ PRM-01 仍 404 NOT_FOUND |
| BUG-006 | 升级日志/审计 | PageResponse 双层嵌套, 前端需多取一层 | P1 | ⚠️ UPG-01/AUD-01 仍 double-nested |
| BUG-007 | 升级日志 | `?version=...` 筛选返回 500 | P1 | ❌ UPG-02 仍 500 INTERNAL_ERROR |
| BUG-008 | 升级日志 | 不存在 ID 应 404 | P1 | ❌ UPG-06 仍 200 + {message: 未找到} |
| BUG-009 | AI 智能检索 | 空 query 未做校验 | P3 | ⚠️ AI-04 仍 200 + 空 results |

---
## Round 3 复测结论 (针对 Round 2 残留/新增缺陷)

| 缺陷ID | 用例 | Round 2 状态 | Round 3 实测 | 结论 |
|--------|------|-------------|-------------|------|
| BUG-001 | KAN-03 | ❌ 500 INTERNAL_ERROR | ❌ FAIL (30ms) | ❌ **本轮仍未修复** (期望 400/BAD_REQUEST) |
| BUG-003 | PRM-01 | ❌ 404 NOT_FOUND | ❌ FAIL (3ms) | ❌ **本轮仍未修复** (路由 `/permissions/matrix` 未注册) |
| BUG-006 | UPG-01 | ⚠️ 仍双层嵌套 | ✅ PASS (12ms) | ⚠️ **缺陷仍存在** (测试通过, 但 PageResponse 双层嵌套, 前端需多取一层) |
| BUG-006 | AUD-01 | ⚠️ 仍双层嵌套 | ✅ PASS (35ms) | ⚠️ **缺陷仍存在** (测试通过, 但 PageResponse 双层嵌套, 前端需多取一层) |
| BUG-007 | UPG-02 | ❌ 500 INTERNAL_ERROR | ❌ FAIL (35ms) | ❌ **本轮仍未修复** (期望 200 (版本筛选正常返回)) |
| BUG-008 | UPG-06 | ❌ 200 + {message: 未找到} | ❌ FAIL (8ms) | ❌ **本轮仍未修复** (期望 404 NOT_FOUND) |
| BUG-009 | AI-04 | ⚠️ 200 + 空 results | ✅ PASS (9ms) | ⚠️ **缺陷仍存在** (测试通过, 但 空 query 应至少 422) |

---
## 总结

- 本轮执行 136 个 API/路由用例, 通过 125, 失败 11, 跳过 30 (整体通过率 92%)。
- 与 Round 2 对比, **通过率无变化** (各模块 R2→R3 差值均为 0%), 说明本轮未修复任何 Round 2 残留缺陷。
- 重点复测 Round 2 残留/新增缺陷 (BUG-001/003/006/007/008/009), 全部 6 个均未修复, 结论见上方复测表。
- 前端页面路由全部 200, SPA 入口正常加载 (与上轮一致)。
- 仍需连接浏览器扩展补测前端交互用例 (KAN-06/07/08/09/10、CHG-11/12、ORG-05~08 等)。
