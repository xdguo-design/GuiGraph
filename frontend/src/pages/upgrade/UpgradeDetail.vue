<template>
  <div class="upgrade-detail-page" v-loading="loading">
    <el-card v-if="upgrade">
      <template #header>
        <div class="card-header">
          <span>升级详情 - {{ upgrade.version }}</span>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>

      <!-- 基本信息 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="版本号">{{ upgrade.version }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTypeMap[upgrade.status] || 'info'">
            {{ statusTextMap[upgrade.status] || upgrade.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="变更数量">{{ upgrade.change_count }}</el-descriptions-item>
        <el-descriptions-item label="执行人">{{ upgrade.created_by }}</el-descriptions-item>
        <el-descriptions-item label="执行时间">{{ formatDate(upgrade.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="耗时">{{ upgrade.duration }}</el-descriptions-item>
      </el-descriptions>

      <!-- 关联变更 -->
      <el-divider content-position="left">关联变更</el-divider>
      <el-table :data="upgrade.changes" size="small" border>
        <el-table-column prop="id" label="变更 ID" width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="changeTypeMap[row.type] || 'default'" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="变更内容" show-overflow-tooltip />
        <el-table-column prop="git_commit" label="Git Commit" width="200" show-overflow-tooltip />
      </el-table>

      <!-- Git Commits -->
      <el-divider content-position="left">Git 提交记录</el-divider>
      <el-timeline v-if="upgrade.commits && upgrade.commits.length > 0">
        <el-timeline-item
          v-for="commit in upgrade.commits"
          :key="commit.id"
          :timestamp="formatDate(commit.timestamp)"
          placement="top"
        >
          <el-card>
            <div>
              <code>{{ commit.hash }}</code>
              <span style="margin-left: 8px">{{ commit.message }}</span>
            </div>
            <div style="margin-top: 4px; color: #666; font-size: 12px">作者: {{ commit.author }}</div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无 Git 提交记录" :image-size="60" />

      <!-- Jenkins 构建记录 -->
      <el-divider content-position="left">Jenkins 构建</el-divider>
      <el-descriptions :column="2" border v-if="upgrade.jenkins_build">
        <el-descriptions-item label="Job 名称">{{ upgrade.jenkins_build.job_name }}</el-descriptions-item>
        <el-descriptions-item label="构建编号">#{{ upgrade.jenkins_build.build_number }}</el-descriptions-item>
        <el-descriptions-item label="构建状态">
          <el-tag :type="upgrade.jenkins_build.status === 'SUCCESS' ? 'success' : 'danger'">
            {{ upgrade.jenkins_build.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="构建时间">{{ formatDate(upgrade.jenkins_build.timestamp) }}</el-descriptions-item>
        <el-descriptions-item label="构建日志" :span="2">
          <pre style="max-height: 200px; overflow: auto; background: #f5f5f5; padding: 8px">{{ upgrade.jenkins_build.log }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <el-empty v-else description="暂无 Jenkins 构建记录" :image-size="60" />

      <!-- 操作栏 -->
      <div class="action-bar" v-if="upgrade.status === 'success'">
        <el-button type="danger" @click="handleRollback">回滚此版本</el-button>
      </div>
    </el-card>
    <el-empty v-else-if="!loading" description="升级记录不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { upgradeAPI } from '@/api/upgrade'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const upgrade = ref<any>(null)

const statusTypeMap: Record<string, any> = {
  success: 'success',
  failed: 'danger',
  rolled_back: 'warning',
}

const statusTextMap: Record<string, string> = {
  success: '成功',
  failed: '失败',
  rolled_back: '已回滚',
}

const changeTypeMap: Record<string, any> = {
  'DB 变更': 'danger',
  'API 变更': 'warning',
  '配置变更': 'info',
  '代码变更': 'success',
  '基础设施': 'default',
}

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

async function fetchUpgradeDetail() {
  loading.value = true
  try {
    const id = route.params.id as string
    // TODO: 调用实际 API
    // const response = await upgradeAPI.get(id)
    // upgrade.value = response.data

    // Mock 数据
    upgrade.value = {
      id: 'UPG-2026-001',
      version: 'v1.2.0',
      status: 'success',
      change_count: 2,
      created_by: 'guoxudong',
      created_at: '2026-06-05 14:00:00',
      duration: '2m 30s',
      changes: [
        {
          id: 'CHG-2026-001',
          type: 'DB 变更',
          content: '添加用户表昵称索引',
          git_commit: 'a1b2c3d4',
        },
        {
          id: 'CHG-2026-002',
          type: 'API 变更',
          content: '优化登录接口响应速度',
          git_commit: 'e5f6g7h8',
        },
      ],
      commits: [
        {
          id: 'commit_1',
          hash: 'a1b2c3d4',
          message: '添加用户表昵称索引',
          author: 'guoxudong',
          timestamp: '2026-06-05 14:01:00',
        },
        {
          id: 'commit_2',
          hash: 'e5f6g7h8',
          message: '优化登录接口响应速度',
          author: 'guoxudong',
          timestamp: '2026-06-05 14:02:00',
        },
      ],
      jenkins_build: {
        job_name: 'guigraph-build',
        build_number: 123,
        status: 'SUCCESS',
        timestamp: '2026-06-05 14:05:00',
        log: '[INFO] Building guigraph...\n[INFO] Build success.\n[INFO] Deploying to production...',
      },
    }
  } catch (error) {
    ElMessage.error('获取升级详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function handleRollback() {
  try {
    await ElMessageBox.confirm(
      `确认回滚到版本 ${upgrade.value.version}？此操作将撤销当前版本的所有变更。`,
      '回滚确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await upgradeAPI.rollback(upgrade.value.id)
    ElMessage.success('回滚成功')
    fetchUpgradeDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('回滚失败')
      console.error(error)
    }
  }
}

onMounted(() => {
  fetchUpgradeDetail()
})
</script>

<style scoped>
.upgrade-detail-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.action-bar {
  margin-top: 24px;
  text-align: right;
}
</style>
