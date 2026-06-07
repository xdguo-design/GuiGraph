<template>
  <div class="upgrade-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>升级日志</span>
          <el-button @click="fetchData" :icon="Refresh">刷新</el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="版本号">
          <el-input v-model="filters.version" placeholder="输入版本号" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="回滚" value="rolled_back" />
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
      <el-table :data="upgrades" v-loading="loading" stripe border>
        <el-table-column prop="version" label="版本号" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status] || 'info'">
              {{ statusTextMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="change_count" label="变更数" width="80" align="center" />
        <el-table-column prop="created_by" label="执行人" width="100" />
        <el-table-column prop="created_at" label="执行时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看详情</el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="handleRollback(row)"
              v-if="row.status === 'success'"
            >
              回滚
            </el-button>
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { upgradeAPI } from '@/api/upgrade'

const router = useRouter()
const loading = ref(false)
const upgrades = ref<any[]>([])

const filters = reactive({
  version: '',
  status: '',
  dateRange: [],
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

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

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    if (filters.version) params.version = filters.version
    if (filters.status) params.status = filters.status
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_time = filters.dateRange[0]
      params.end_time = filters.dateRange[1]
    }

    const response = await upgradeAPI.list(params)
    // Map backend fields to table fields
    upgrades.value = (response.items || []).map((item: any) => ({
      id: item.id,
      version: item.version_to,
      status: item.status,
      change_count: (item.change_items || []).length,
      created_by: item.operator_id,
      created_at: item.start_time,
      duration: item.duration_sec ? formatDuration(item.duration_sec) : '-',
    }))
    pagination.total = response.total || 0
  } catch (error) {
    ElMessage.error('获取升级日志失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return sec > 0 ? `${min}m ${sec}s` : `${min}m`
}

function handleQuery() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  Object.assign(filters, {
    version: '',
    status: '',
    dateRange: [],
  })
  handleQuery()
}

function handleView(row: any) {
  router.push(`/upgrades/${row.id}`)
}

async function handleRollback(row: any) {
  try {
    await ElMessageBox.confirm(
      `确认回滚到版本 ${row.version}？此操作将撤销当前版本的所有变更。`,
      '回滚确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await upgradeAPI.rollback(row.id)
    ElMessage.success('回滚成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('回滚失败')
      console.error(error)
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.upgrade-list-page {
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
