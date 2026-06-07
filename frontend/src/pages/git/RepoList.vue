<template>
  <div class="repo-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Git 仓库</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加仓库
          </el-button>
        </div>
      </template>
      
      <el-table :data="repos" v-loading="loading" stripe border>
        <el-table-column prop="name" label="仓库名称" min-width="150" />
        <el-table-column prop="url" label="仓库地址" min-width="300" show-overflow-tooltip />
        <el-table-column prop="default_branch" label="默认分支" width="120" />
        <el-table-column prop="auth_type" label="认证方式" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.auth_type === 'none'" type="info">无</el-tag>
            <el-tag v-else-if="row.auth_type === 'ssh'" type="success">SSH</el-tag>
            <el-tag v-else-if="row.auth_type === 'token'" type="warning">Token</el-tag>
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
            <el-button link type="primary" @click="viewBranches(row.id)">
              <el-icon><Link /></el-icon>
              分支
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
          @size-change="loadRepos"
          @current-change="loadRepos"
        />
      </div>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑仓库' : '添加仓库'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入仓库名称" />
        </el-form-item>
        
        <el-form-item label="仓库地址" prop="url">
          <el-input v-model="formData.url" placeholder="https://github.com/user/repo 或 git@github.com:user/repo.git" />
        </el-form-item>
        
        <el-form-item label="默认分支" prop="default_branch">
          <el-input v-model="formData.default_branch" placeholder="main 或 master" />
        </el-form-item>
        
        <el-form-item label="认证方式" prop="auth_type">
          <el-select v-model="formData.auth_type" placeholder="请选择认证方式">
            <el-option label="无需认证" value="none" />
            <el-option label="SSH 密钥" value="ssh" />
            <el-option label="Access Token" value="token" />
          </el-select>
        </el-form-item>
        
        <el-form-item
          v-if="formData.auth_type && formData.auth_type !== 'none'"
          label="认证凭据"
          prop="credentials"
        >
          <el-input
            v-model="formData.credentials"
            type="textarea"
            :rows="4"
            :placeholder="formData.auth_type === 'ssh' ? '请输入 SSH 私钥内容' : '请输入 Access Token'"
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
import { Plus, Edit, Delete, Connection, GitBranch } from '@element-plus/icons-vue'
import { gitAPI, type GitRepo } from '@/api/git'

const loading = ref(false)
const repos = ref<GitRepo[]>([])
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
  default_branch: 'main',
  auth_type: 'none' as 'none' | 'ssh' | 'token',
  credentials: '',
  description: '',
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入仓库名称', trigger: 'blur' },
  ],
  url: [
    { required: true, message: '请输入仓库地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的 URL 地址', trigger: 'blur' },
  ],
  default_branch: [
    { required: true, message: '请输入默认分支', trigger: 'blur' },
  ],
  credentials: [
    {
      validator: (rule, value, callback) => {
        if (formData.auth_type !== 'none' && !value) {
          callback(new Error('请输入认证凭据'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

const isEdit = computed(() => !!currentEditId.value)

onMounted(() => {
  loadRepos()
})

async function loadRepos() {
  loading.value = true
  try {
    const response = await gitAPI.list()
    repos.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载仓库列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  currentEditId.value = null
  dialogVisible.value = true
}

function handleEdit(row: GitRepo) {
  currentEditId.value = row.id || null
  Object.assign(formData, {
    name: row.name,
    url: row.url,
    default_branch: row.default_branch,
    auth_type: row.auth_type || 'none',
    credentials: row.credentials || '',
    description: row.description || '',
  })
  dialogVisible.value = true
}

async function handleDelete(row: GitRepo) {
  try {
    await ElMessageBox.confirm(
      `确定要删除仓库 "${row.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await gitAPI.delete(row.id!)
    ElMessage.success('删除成功')
    loadRepos()
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
      await gitAPI.update(currentEditId.value!, data)
      ElMessage.success('更新成功')
    } else {
      await gitAPI.create(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadRepos()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      console.error(error)
    }
  } finally {
    submitting.value = false
  }
}

async function handleTest(row: GitRepo) {
  try {
    row.testing = true
    const response = await gitAPI.test({
      name: row.name,
      url: row.url,
      default_branch: row.default_branch,
      auth_type: row.auth_type,
      credentials: row.credentials,
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
    default_branch: 'main',
    auth_type: 'none',
    credentials: '',
    description: '',
  })
}

function viewBranches(repoId: string) {
  // TODO: 跳转到分支管理页面
  ElMessage.info('分支管理功能开发中')
}
</script>

<style scoped>
.repo-list-page {
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
