<template>
  <div class="dashboard-page">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon"><el-icon><Document /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_changes }}</div>
              <div class="stat-label">总变更数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon"><el-icon><Clock /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_changes }}</div>
              <div class="stat-label">待审批</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon"><el-icon><CircleCheck /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.released_changes }}</div>
              <div class="stat-label">已发布</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon"><el-icon><Warning /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.rolled_back_changes }}</div>
              <div class="stat-label">已回滚</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近变更</span>
              <el-link type="primary" @click="$router.push('/changes')">查看全部</el-link>
            </div>
          </template>
          <el-empty v-if="recentChanges.length === 0" description="暂无变更数据" />
          <el-table v-else :data="recentChanges" size="default">
            <el-table-column prop="title" label="内容" show-overflow-tooltip />
            <el-table-column prop="type" label="类型" width="80" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ row.created_at?.substring(0, 16).replace('T', ' ') }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>快速操作</template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/changes/create')">新建变更</el-button>
            <el-button @click="$router.push('/org')">组织架构</el-button>
            <el-button @click="$router.push('/kanban')">个人/团队看板</el-button>
          </div>
        </el-card>
        <el-card style="margin-top: 16px">
          <template #header>升级日志</template>
          <div class="upgrade-info">
            <div class="stat-value">{{ stats.upgrade_logs }}</div>
            <div class="stat-label">升级记录数</div>
            <el-link type="primary" @click="$router.push('/upgrades')" style="margin-top: 12px; display: block">查看详情</el-link>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import request from '@/api/request'

const stats = reactive({
  total_changes: 0,
  pending_changes: 0,
  released_changes: 0,
  rolled_back_changes: 0,
  upgrade_logs: 0,
})
const recentChanges = ref<any[]>([])

const statusMap: Record<string, { label: string; type: string }> = {
  draft: { label: '草稿', type: 'info' },
  approved: { label: '已审批', type: 'warning' },
  released: { label: '已发布', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
  rolled_back: { label: '已回滚', type: 'danger' },
}
function statusLabel(s: string) {
  return statusMap[s]?.label || s
}
function statusTagType(s: string) {
  return statusMap[s]?.type || 'info'
}

async function load() {
  try {
    const data: any = await request.get('/dashboard')
    Object.assign(stats, data.stats || {})
    recentChanges.value = data.recent_changes || []
  } catch (e) {
    console.error('仪表盘加载失败', e)
  }
}

onMounted(load)
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-icon {
  font-size: 32px;
  color: #2980b9;
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1a5276;
}
.stat-label {
  font-size: 12px;
  color: #7f8c8d;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.upgrade-info {
  text-align: center;
  padding: 8px 0;
}
</style>
