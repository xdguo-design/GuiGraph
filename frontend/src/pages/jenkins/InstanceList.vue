<template>
  <div class="jenkins-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Jenkins 实例</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加实例
          </el-button>
        </div>
      </template>
      
      <el-table :data="instances" v-loading="loading" stripe border>
        <el-table-column prop="name" label="实例名称" min-width="150" />
        <el-table-column prop="url" label="URL" min-width="300" show-overflow-tooltip />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleTest(row)" :loading="row.testing">
              <el-icon><Connection /></el-icon>
              测试连接
            </el-button>
            <el-button link type="primary" @click="viewBuilds(row.id)">
              <el-icon><Clock /></el-icon>
              构建历史
            </el-button>
            <el-button link type="primary" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadInstances"
          @current-change="loadInstances"
        />
      </div>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑实例' : '添加实例'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="实例名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入实例名称" />
        </el-form-item>
        
        <el-form-item label="Jenkins URL" prop="url">
          <el-input v-model="formData.url" placeholder="http://jenkins.example.com:8080" />
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名（可选）" />
        </el-form-item>
        
        <el-form-item label="API Token" prop="token">
          <el-input
            v-model="formData.token"
            type="password"
            show-password
            placeholder="请输入 API Token（可选）"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Edit, Delete, Connection, Clock } from '@element-plus/icons-vue'
import { jenkinsAPI, type JenkinsInstance } from '@/api/jenkins'

const loading = ref(false)
const instances = ref<JenkinsInstance[]>([])
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const currentEditId = ref<string | null>(null)

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const formData = reactive({
  name: '',
  url: '',
  username: '',
  token: '',
  description: '',
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入实例名称', trigger: 'blur' },
  ],
  url: [
    { required: true, message: '请输入 Jenkins URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的 URL 地址', trigger: 'blur' },
  ],
}

const isEdit = computed(() => !!currentEditId.value)

onMounted(() => {
  loadInstances()
})

async function loadInstances() {
  loading.value = true
  try {
    const response = await jenkinsAPI.list()
    instances.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载实例列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  currentEditId.value = null
  dialogVisible.value = true
}

function handleEdit(row: JenkinsInstance) {
  currentEditId.value = row.id || null
  Object.assign(formData, {
    name: row.name,
    url: row.url,
    username: row.username || '',
    token: row.token || '',
    description: row.description || '',
  })
  dialogVisible.value = true
}

async function handleDelete(row: JenkinsInstance) {
  try {
    await ElMessageBox.confirm(
      `确定要删除实例 "${row.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await jenkinsAPI.delete(row.id!)
    ElMessage.success('删除成功')
    loadInstances()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const data = { ...formData }
    
    if (isEdit.value) {
      await jenkinsAPI.update(currentEditId.value!, data)
      ElMessage.success('更新成功')
    } else {
      await jenkinsAPI.create(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadInstances()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      console.error(error)
    }
  } finally {
    submitting.value = false
  }
}

async function handleTest(row: JenkinsInstance) {
  try {
    row.testing = true
    const response = await jenkinsAPI.test({
      name: row.name,
      url: row.url,
      username: row.username,
      token: row.token,
    })
    if (response.data.success) {
      ElMessage.success(response.data.message || '连接成功')
    } else {
      ElMessage.error(response.data.message || '连接失败')
    }
  } catch (error) {
    ElMessage.error('连接测试失败')
    console.error(error)
  } finally {
    row.testing = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
  Object.assign(formData, {
    name: '',
    url: '',
    username: '',
    token: '',
    description: '',
  })
}

function viewBuilds(instanceId: string) {
  // TODO: 跳转到构建历史页面
  ElMessage.info('构建历史功能开发中')
}
</script>

<style scoped>
.jenkins-list-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
