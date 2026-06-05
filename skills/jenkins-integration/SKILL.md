# Skill: Jenkins 集成

## 概述

提供 Jenkins 构建系统的完整集成能力，包括 Job 触发、状态查询、构建日志获取等。

---

## 核心功能

### 1. Jenkins 实例管理

| 操作 | 说明 |
|------|------|
| `add_instance` | 添加 Jenkins 实例配置 |
| `remove_instance` | 删除 Jenkins 实例 |
| `list_instances` | 列出所有 Jenkins 实例 |
| `test_connection` | 测试 Jenkins 连接 |

### 2. Job 管理

| 操作 | 说明 |
|------|------|
| `list_jobs` | 获取 Jenkins 所有 Job |
| `get_job_info` | 获取 Job 详细信息 |
| `create_job_template` | 创建 Job 模板（与 Git 仓库关联） |
| `update_job_template` | 更新 Job 模板 |

### 3. 构建操作

| 操作 | 说明 |
|------|------|
| `trigger_build` | 触发 Job 构建 |
| `get_build_status` | 获取构建状态 |
| `get_build_log` | 获取构建日志 |
| `stop_build` | 停止运行中的构建 |
| `retry_build` | 重试失败构建 |

### 4. 状态回写

| 操作 | 说明 |
|------|------|
| `update_change_status` | 回写构建状态到变更条目 |
| `get_build_history` | 获取构建历史 |

---

## 权限边界

### 允许的操作

- ✅ 触发已授权的 Job 构建
- ✅ 查看构建状态和日志
- ✅ 停止自己触发的构建
- ✅ 重试失败的构建

### 禁止的操作

- ❌ 修改 Jenkins 全局配置
- ❌ 删除 Job
- ❌ 触发未授权的 Job
- ❌ 访问 Jenkins 敏感信息（凭据、密钥）
- ❌ 执行脚本安全绕过

---

## API 接口

### 触发构建

```
POST /api/v1/jenkins/build

Body:
{
  "jenkins_instance_id": 1,
  "job_name": "pay-service-ci",
  "parameters": {
    "BRANCH": "dev",
    "CHANGE_ID": "1001",
    "GIT_COMMIT": "a1b2c3d4e5f6..."
  }
}

Response:
{
  "build_id": 12345,
  "queue_id": 678,
  "status": "queued",
  "url": "http://jenkins.company.com/job/pay-service-ci/12345/"
}
```

### 获取构建状态

```
GET /api/v1/jenkins/build/{buildId}/status

Response:
{
  "build_id": 12345,
  "status": "building|success|failed|aborted",
  "result": "SUCCESS|FAILURE|UNSTABLE",
  "duration_ms": 154000,
  "url": "http://jenkins.company.com/job/pay-service-ci/12345/",
  "parameters": {
    "BRANCH": "dev",
    "CHANGE_ID": "1001"
  },
  "artifacts": [
    {"name": "pay-service.jar", "url": "..."}
  ]
}
```

### 获取构建日志

```
GET /api/v1/jenkins/build/{buildId}/log

Response:
{
  "log": "[Pipeline] Start of Pipeline\n[Pipeline] stage\n...",
  "truncated": false,
  "url": "http://jenkins.company.com/job/pay-service-ci/12345/console"
}
```

### 回写状态到变更条目

```
POST /api/v1/changes/{changeId}/jenkins-status

Body:
{
  "build_id": 12345,
  "build_url": "http://jenkins.company.com/job/pay-service-ci/12345/",
  "status": "success|failed",
  "result": "SUCCESS|FAILURE",
  "duration_ms": 154000
}
```

---

## Jenkins REST API 调用规范

### 认证方式

```javascript
// Basic Auth（推荐）
const auth = Buffer.from(`${username}:${apiToken}`).toString('base64');
headers['Authorization'] = `Basic ${auth}`;

// 或 Token Auth
headers['Authorization'] = `Bearer ${apiToken}`;
```

### 触发构建（带参数）

```bash
curl -X POST \
  "${JENKINS_URL}/job/${JOB_NAME}/buildWithParameters" \
  -H "Authorization: Basic ${AUTH_HEADER}" \
  -d "BRANCH=${BRANCH}&CHANGE_ID=${CHANGE_ID}"
```

### 获取构建状态

```bash
curl -X GET \
  "${JENKINS_URL}/job/${JOB_NAME}/${BUILD_NUMBER}/api/json" \
  -H "Authorization: Basic ${AUTH_HEADER}"
```

### 获取构建日志

```bash
curl -X GET \
  "${JENKINS_URL}/job/${JOB_NAME}/${BUILD_NUMBER}/logText/progressiveText" \
  -H "Authorization: Basic ${AUTH_HEADER}"
```

---

## 构建状态机

```
queued → building → success | failed | aborted | unstable
                              ↓
                        回写状态到变更条目
                              ↓
                        通知相关人员
```

| 状态 | 说明 | 后续动作 |
|------|------|----------|
| `queued` | 已排队，等待执行 | 轮询状态 |
| `building` | 正在构建 | 轮询状态 |
| `success` | 构建成功 | 回写成功状态，通知 |
| `failed` | 构建失败 | 回写失败状态，通知 |
| `unstable` | 构建不稳定（测试失败等） | 回写不稳定状态，通知 |
| `aborted` | 构建被中止 | 回写中止状态 |

---

## 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| `CONNECTION_FAILED` | 无法连接 Jenkins | 检查网络/URL |
| `AUTH_FAILED` | 认证失败 | 检查凭据 |
| `JOB_NOT_FOUND` | Job 不存在 | 检查 Job 名称 |
| `BUILD_FAILED` | 构建失败 | 返回日志，提示查看 |
| `TIMEOUT` | 构建超时 | 提示手动检查 |
| `PERMISSION_DENIED` | 无权限触发 | 提示申请权限 |

---

## 使用示例

### 示例 1：Git 合并成功后触发构建

```javascript
// Git 合并成功后
const mergeResult = await git.merge({
  repo_id: 1,
  source_branch: "feature/pay-v2",
  target_branch: "dev",
  change_id: 1001
});

if (mergeResult.status === 'success') {
  // 触发 Jenkins 构建
  const build = await jenkins.triggerBuild({
    jenkins_instance_id: 1,
    job_name: "pay-service-ci",
    parameters: {
      BRANCH: "dev",
      CHANGE_ID: "1001",
      GIT_COMMIT: mergeResult.commit_sha
    }
  });

  // 更新变更条目
  await change.update(1001, {
    jenkins_build_id: build.build_id,
    jenkins_build_url: build.url,
    merge_status: 'success'
  });
}
```

### 示例 2：轮询构建状态

```javascript
async function waitForBuild(buildId, timeout = 300000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const status = await jenkins.getBuildStatus(buildId);
    
    if (status.status !== 'building' && status.status !== 'queued') {
      return status;  // 构建完成
    }
    
    await sleep(5000);  // 5 秒轮询
  }
  
  throw new Error('TIMEOUT');
}

// 使用
const result = await waitForBuild(12345);
if (result.status === 'success') {
  console.log('构建成功！');
} else {
  console.log('构建失败，请查看日志：', result.url);
}
```

---

## Jenkinsfile 模板

```groovy
pipeline {
    agent any
    parameters {
        string(name: 'BRANCH', defaultValue: 'dev', description: '构建分支')
        string(name: 'CHANGE_ID', defaultValue: '', description: '关联变更 ID')
        string(name: 'GIT_COMMIT', defaultValue: '', description: 'Git Commit SHA')
    }
    environment {
        CHANGE_MANAGEMENT_URL = credentials('change-management-url')
        API_TOKEN = credentials('change-management-api-token')
    }
    stages {
        stage('拉取代码') {
            steps {
                script {
                    git branch: "${params.BRANCH}", 
                        url: "${env.GIT_REPO_URL}",
                        credentialsId: 'git-credentials'
                }
            }
        }
        stage('构建') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        stage('测试') {
            steps {
                sh 'mvn test'
            }
            post {
                always {
                    junit 'target/surefire-reports/*.xml'
                }
            }
        }
        stage('部署') {
            steps {
                sh './deploy.sh ${params.BRANCH}'
            }
        }
    }
    post {
        always {
            // 回写状态到变更管理系统
            script {
                if (params.CHANGE_ID) {
                    def status = currentBuild.result == null ? 'SUCCESS' : currentBuild.result
                    sh """
                        curl -X POST "${CHANGE_MANAGEMENT_URL}/api/v1/changes/${params.CHANGE_ID}/jenkins-status" \\
                            -H "Authorization: Bearer ${API_TOKEN}" \\
                            -H "Content-Type: application/json" \\
                            -d '{"build_id": "${env.BUILD_NUMBER}", "status": "${status}", "url": "${env.BUILD_URL}", "duration_ms": ${env.BUILD_DURATION_MS}}'
                    """
                }
            }
        }
        failure {
            // 构建失败时发送通知
            emailext {
                subject "构建失败：${env.JOB_NAME} #${env.BUILD_NUMBER}"
                body "变更 ID: ${params.CHANGE_ID}\n构建日志: ${env.BUILD_URL}console"
                to "${env.CHANGE_OWNER_EMAIL}"
            }
        }
    }
}
```

---

## 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `jenkins.timeout` | 构建超时时间（秒） | 600 |
| `jenkins.poll_interval` | 状态轮询间隔（秒） | 5 |
| `jenkins.max_retries` | 失败重试次数 | 1 |
| `jenkins.log_lines` | 日志获取行数 | 200 |

---

## 更新日志

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-06-04 | v1.0 | 初始版本 |
