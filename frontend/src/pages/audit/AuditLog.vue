<template>
  <div class="audit-log-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审计日志</span>
          <el-button @click="fetchData" :icon="Refresh">刷新</el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="操作用户">
          <el-input v-model="filters.user_id" placeholder="用户 ID" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="filters.operation" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="op in operationOptions" :key="op" :label="op" :value="op" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="logs" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="timestamp" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="user_id" label="操作用户" width="120" />
        <el-table-column prop="agent_role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.agent_role" size="small" type="info">{{ roleTextMap[row.agent_role] || row.agent_role }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="operation" label="操作类型" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ row.operation }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource" label="操作资源" min-width="200" show-overflow-tooltip />
        <el-table-column prop="result" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.result === 'success' ? 'success' : row.result === 'fail' ? 'danger' : 'warning'" size="small">
              {{ row.result === 'success' ? '成功' : row.result === 'fail' ? '失败' : row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="来源 IP" width="140">
          <template #default="{ row }">
            {{ row.ip_address || '-' }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { auditAPI } from '@/api/audit'
import { formatDateTime } from '@/utils/pageTools'

const loading = ref(false)
const logs = ref<any[]>([])

const operationOptions = [
  'login', 'logout', 'create', 'update', 'delete',
  'approve', 'reject', 'upload', 'download', 'rollback',
]

const roleTextMap: Record<string, string> = {
  system_admin: '系统管理员',
  dept_admin: '部门管理员',
  team_admin: '团队管理员',
  editor: '编辑者',
  viewer: '查看者',
  auditor: '审计员',
}

const filters = reactive({
  user_id: '',
  operation: '',
  dateRange: [] as string[],
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

async function fetchData() {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    if (filters.user_id) params.user_id = filters.user_id
    if (filters.operation) params.operation = filters.operation
    if (filters.dateRange?.length === 2) {
      params.start_time = filters.dateRange[0] + 'T00:00:00'
      params.end_time = filters.dateRange[1] + 'T23:59:59'
    }
    const res: any = await auditAPI.listLogs(params)
    logs.value = res?.items || []
    pagination.total = res?.total || 0
  } catch (error: any) {
    ElMessage.error('获取审计日志失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleQuery() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  Object.assign(filters, { user_id: '', operation: '', dateRange: [] })
  handleQuery()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.audit-log-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-form {
  margin-bottom: 16px;
}
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
