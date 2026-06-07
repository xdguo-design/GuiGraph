<template>
  <div class="product-line-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📦 产品线管理</span>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog">新建产品线</el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-form :inline="true" :model="filters">
          <el-form-item label="业务线">
            <el-select v-model="filters.business_line_id" placeholder="全部" clearable style="width: 160px" @change="fetchData">
              <el-option v-for="bl in businessLines" :key="bl.id" :label="bl.name" :value="parseInt(bl.id)" />
            </el-select>
          </el-form-item>
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
        <el-table-column label="所属业务线" min-width="120">
          <template #default="{ row }">
            {{ getBusinessLineName(row.business_line_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑产品线' : '新建产品线'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="所属业务线" prop="business_line_id">
          <el-select v-model="form.business_line_id" placeholder="选择业务线" style="width: 100%">
            <el-option v-for="bl in businessLines" :key="bl.id" :label="bl.name" :value="parseInt(bl.id)" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="输入产品线名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="输入编码，如 PL-001" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { productLineAPI } from '@/api/product-line'
import { businessLineAPI } from '@/api/business-line'
import { formatDateTime, confirmDanger, msgSuccess, msgError } from '@/utils/pageTools'

const loading = ref(false)
const lines = ref<any[]>([])
const businessLines = ref<any[]>([])
const dialogVisible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const formRef = ref()

const filters = reactive({
  business_line_id: '',
  status: '',
})

const form = reactive({
  id: '',
  business_line_id: 0,
  name: '',
  code: '',
  description: '',
  owner_id: 0,
  status: 'active',
  sort_order: 0,
})

const rules = {
  business_line_id: [{ required: true, message: '请选择业务线', trigger: 'change' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
}

function getBusinessLineName(id: string | number) {
  const bl = businessLines.value.find(b => b.id === String(id))
  return bl?.name || '-'
}

async function fetchBusinessLines() {
  try {
    const res: any = await businessLineAPI.listLines()
    businessLines.value = res?.items || []
  } catch (e) {
    console.error(e)
  }
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = {}
    if (filters.business_line_id) params.business_line_id = filters.business_line_id
    if (filters.status) params.status = filters.status
    const res: any = await productLineAPI.listLines(params)
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
    business_line_id: 0,
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
      await productLineAPI.updateLine(parseInt(form.id), form)
      msgSuccess('更新成功')
    } else {
      await productLineAPI.createLine(form)
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
  const ok = await confirmDanger(`确认删除产品线「${row.name}」？`)
  if (!ok) return
  try {
    await productLineAPI.deleteLine(parseInt(row.id))
    msgSuccess('删除成功')
    await fetchData()
  } catch (e: any) {
    msgError(e?.message || '删除失败')
  }
}

onMounted(async () => {
  await fetchBusinessLines()
  await fetchData()
})
</script>

<style scoped>
.product-line-page {
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
