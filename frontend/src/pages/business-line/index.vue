<template>
  <div class="business-line-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📊 业务线管理</span>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog">新建业务线</el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-form :inline="true" :model="filters">
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px" @change="fetchData">
              <el-option label="启用" value="active" />
              <el-option label="停用" value="inactive" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <el-table :data="lines" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑业务线' : '新建业务线'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="输入业务线名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="输入唯一编码，如 BL-001" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="可选描述" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="form.owner_id" type="number" placeholder="负责人 ID" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input v-model="form.sort_order" type="number" placeholder="数值越小越靠前" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { businessLineAPI } from '@/api/business-line'
import { formatDateTime, confirmDanger, msgSuccess, msgError } from '@/utils/pageTools'

const loading = ref(false)
const lines = ref<any[]>([])
const dialogVisible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const formRef = ref()

const filters = reactive({
  status: '',
})

const form = reactive({
  id: '',
  name: '',
  code: '',
  description: '',
  owner_id: 0,
  status: 'active',
  sort_order: 0,
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
}

async function fetchData() {
  loading.value = true
  try {
    const res: any = await businessLineAPI.listLines(filters)
    lines.value = res?.items || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false
  Object.assign(form, {
    id: '',
    name: '',
    code: '',
    description: '',
    owner_id: 0,
    status: 'active',
    sort_order: 0,
  })
  dialogVisible.value = true
}

function handleEdit(row: any) {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await businessLineAPI.updateLine(parseInt(form.id), form)
      msgSuccess('更新成功')
    } else {
      await businessLineAPI.createLine(form)
      msgSuccess('创建成功')
    }
    dialogVisible.value = false
    await fetchData()
  } catch (e: any) {
    msgError(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: any) {
  const ok = await confirmDanger(`确认删除业务线「${row.name}」？`)
  if (!ok) return
  try {
    await businessLineAPI.deleteLine(parseInt(row.id))
    msgSuccess('删除成功')
    await fetchData()
  } catch (e: any) {
    msgError(e?.message || '删除失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.business-line-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-bar {
  margin-bottom: 16px;
}
</style>
