<template>
  <div class="version-merge-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>版本合并</span>
          <div>
            <el-button @click="fetchData" :icon="Refresh">刷新</el-button>
            <el-button type="primary" @click="handleMerge" :disabled="selectedChanges.length === 0" :loading="merging">
              执行合并 ({{ selectedChanges.length }})
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：待合并变更列表 -->
        <el-col :span="16">
          <el-table
            :data="pendingChanges"
            v-loading="loading"
            @selection-change="handleSelectionChange"
            stripe
            border
          >
            <el-table-column type="selection" width="50" />
            <el-table-column prop="id" label="变更 ID" width="120" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="changeTypeMap[row.type] || 'default'">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="变更内容" show-overflow-tooltip />
            <el-table-column prop="reason" label="原因" width="120" />
            <el-table-column prop="created_by" label="创建人" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-col>

        <!-- 右侧：版本清单和合并日志 -->
        <el-col :span="8">
          <el-card shadow="never">
            <template #header>版本清单 ({{ selectedChanges.length }})</template>
            <el-empty v-if="selectedChanges.length === 0" description="未选择任何变更" :image-size="80" />
            <el-table :data="selectedChanges" max-height="300" size="small">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="type" label="类型" width="70">
                <template #default="{ row }">
                  <el-tag :type="changeTypeMap[row.type] || 'default'" size="small">{{ row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="content" label="内容" show-overflow-tooltip />
            </el-table>
          </el-card>

          <el-card shadow="never" style="margin-top: 16px">
            <template #header>合并日志</template>
            <el-timeline v-if="mergeLogs.length > 0">
              <el-timeline-item
                v-for="log in mergeLogs"
                :key="log.id"
                :timestamp="formatDate(log.timestamp)"
                :type="log.status === 'success' ? 'success' : log.status === 'failed' ? 'danger' : 'primary'"
              >
                <div>
                  <strong>{{ log.change_id }}</strong>
                  <el-tag :type="statusTypeMap[log.status]" size="small" style="margin-left: 8px">
                    {{ statusTextMap[log.status] }}
                  </el-tag>
                </div>
                <div style="margin-top: 4px; color: #666; font-size: 12px">{{ log.message }}</div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无合并日志" :image-size="60" />
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

const loading = ref(false)
const merging = ref(false)
const pendingChanges = ref<any[]>([])
const selectedChanges = ref<any[]>([])
const mergeLogs = ref<any[]>([])

const changeTypeMap: Record<string, any> = {
  'DB 变更': 'danger',
  'API 变更': 'warning',
  '配置变更': 'info',
  '代码变更': 'success',
  '基础设施': 'default',
}

const statusTypeMap: Record<string, any> = {
  pending: 'info',
  success: 'success',
  failed: 'danger',
  skipped: 'warning',
}

const statusTextMap: Record<string, string> = {
  pending: '待处理',
  success: '合并成功',
  failed: '合并失败',
  skipped: '已跳过',
}

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

function handleSelectionChange(selection: any[]) {
  selectedChanges.value = selection
}

async function fetchData() {
  loading.value = true
  try {
    // TODO: 调用实际 API
    // const response = await changeAPI.list({ status: 'approved' })
    // pendingChanges.value = response.data.items
    
    // Mock 数据
    pendingChanges.value = [
      {
        id: 'CHG-2026-001',
        type: 'DB 变更',
        content: '添加用户表昵称索引',
        reason: '性能优化',
        created_by: 'guoxudong',
        created_at: '2026-06-05 10:00:00',
      },
      {
        id: 'CHG-2026-002',
        type: 'API 变更',
        content: '优化登录接口响应速度',
        reason: '性能优化',
        created_by: 'test_user',
        created_at: '2026-06-05 11:00:00',
      },
    ]
  } catch (error) {
    ElMessage.error('获取待合并变更失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function handleMerge() {
  try {
    await ElMessageBox.confirm(
      `确认合并 ${selectedChanges.value.length} 个变更？此操作将执行 Git 合并并触发 Jenkins 构建。`,
      '合并确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    merging.value = true
    
    // TODO: 调用实际 API
    // const response = await changeAPI.merge({ change_ids: selectedChanges.value.map(c => c.id) })
    
    // Mock 合并日志
    mergeLogs.value = selectedChanges.value.map((change, index) => ({
      id: `log_${index}`,
      change_id: change.id,
      timestamp: new Date().toISOString(),
      status: index === 0 ? 'success' : 'failed',
      message: index === 0 ? '合并成功，已触发 Jenkins 构建' : 'Git 分支存在冲突',
    }))

    ElMessage.success('合并操作已执行')
    
    // 重新加载数据
    await fetchData()
    selectedChanges.value = []
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('合并失败')
      console.error(error)
    }
  } finally {
    merging.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.version-merge-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
