<template>
  <div class="change-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>变更管理</span>
          <el-button type="primary" @click="$router.push('/changes/create')">
            <el-icon><Plus /></el-icon> 新建变更
          </el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="变更类型">
          <el-select v-model="filters.type" placeholder="全部" clearable>
            <el-option label="DB 变更" value="db" />
            <el-option label="API 变更" value="api" />
            <el-option label="配置变更" value="config" />
            <el-option label="代码变更" value="code" />
            <el-option label="基础设施" value="infra" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已审批" value="approved" />
            <el-option label="已发布" value="released" />
            <el-option label="已回滚" value="rolled_back" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="handleSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="changes" v-loading="loading">
        <el-table-column prop="id" label="变更 ID" width="100" />
        <el-table-column prop="change_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.change_type)">{{ row.change_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="变更内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="change_reason" label="原因" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row.id)">详情</el-button>
            <el-button link type="primary" @click="editChange(row.id)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { changeAPI } from '@/api/change'

const loading = ref(false)
const changes = ref([])

const filters = reactive({
  type: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

function getTypeTag(type: string) {
  const map: Record<string, any> = {
    db: 'danger',
    api: 'warning',
    config: 'info',
    code: 'success',
    infra: '',
  }
  return map[type] || ''
}

function getStatusTag(status: string) {
  const map: Record<string, any> = {
    draft: '',
    approved: 'success',
    released: 'success',
    rolled_back: 'danger',
  }
  return map[status] || ''
}

async function loadData() {
  loading.value = true
  try {
    // TODO: 实际调用 API
    // const data = await changeAPI.list({ ...filters, ...pagination })
    // changes.value = data.items
    // pagination.total = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleSizeChange() {
  loadData()
}

function handlePageChange() {
  loadData()
}

function viewDetail(id: string) {
  // TODO: 路由跳转
}

function editChange(id: string) {
  // TODO: 路由跳转
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.change-list-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-form {
  margin-bottom: 16px;
}
.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
