<template>
  <div class="applications-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>账号申请审核</span>
          <div class="actions">
            <el-radio-group v-model="statusFilter" @change="fetchList">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="pending">待审核</el-radio-button>
              <el-radio-button value="approved">已通过</el-radio-button>
              <el-radio-button value="rejected">已拒绝</el-radio-button>
            </el-radio-group>
            <el-button :icon="Refresh" @click="fetchList">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="applications" stripe>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="140" />
        <el-table-column prop="email" label="邮箱" min-width="160" />
        <el-table-column prop="phone" label="手机" width="130" />
        <el-table-column label="申请原因" min-width="220">
          <template #default="{ row }">
            <span class="reason-text">{{ row.reason || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'pending'" type="warning">待审核</el-tag>
            <el-tag v-else-if="row.status === 'approved'" type="success">已通过</el-tag>
            <el-tag v-else type="danger">已拒绝</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="reviewed_at" label="审核时间" width="170">
          <template #default="{ row }">{{ row.reviewed_at ? formatDateTime(row.reviewed_at) : '—' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" size="small" @click="openApproveDialog(row)">通过</el-button>
              <el-button type="danger" size="small" @click="openRejectDialog(row)">拒绝</el-button>
            </template>
            <span v-else class="muted">
              {{ row.assigned_role ? '→ ' + row.assigned_role : '—' }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 通过对话框 -->
    <el-dialog v-model="approveDialog" title="审核通过" width="540px">
      <el-form :model="approveForm" label-width="100px">
        <el-form-item label="用户名">
          <span class="readonly">{{ current?.username }}</span>
        </el-form-item>
        <el-form-item label="分配角色" required>
          <el-select v-model="approveForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="编辑者 (editor)" value="editor" />
            <el-option label="查看者 (viewer)" value="viewer" />
            <el-option label="团队管理员 (team_admin)" value="team_admin" />
            <el-option label="部门管理员 (dept_admin)" value="dept_admin" />
            <el-option label="系统管理员 (system_admin)" value="system_admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属公司">
          <el-select
            v-model="approveForm.company_id"
            placeholder="请选择公司"
            clearable
            style="width: 100%"
            @change="onCompanyChange"
          >
            <el-option
              v-for="c in companies"
              :key="c.id"
              :label="`${c.name} (${c.code})`"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属部门">
          <el-select
            v-model="approveForm.department_id"
            placeholder="请选择部门"
            clearable
            style="width: 100%"
            @change="onDeptChange"
          >
            <el-option
              v-for="d in filteredDepartments"
              :key="d.id"
              :label="`${d.name} (${d.code})`"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属团队">
          <el-select
            v-model="approveForm.team_id"
            placeholder="请选择团队（可留空）"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="t in filteredTeams"
              :key="t.id"
              :label="`${t.name} (${t.code})`"
              :value="t.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="审核备注">
          <el-input v-model="approveForm.comment" type="textarea" :rows="2" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleApprove">确认通过</el-button>
      </template>
    </el-dialog>

    <!-- 拒绝对话框 -->
    <el-dialog v-model="rejectDialog" title="拒绝申请" width="480px">
      <p>将拒绝用户 <strong>{{ current?.username }}</strong> 的注册申请</p>
      <el-form>
        <el-form-item label="拒绝原因">
          <el-input v-model="rejectComment" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialog = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="handleReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { applicationAPI } from '@/api/application'
import { msgSuccess, msgError, confirmDanger } from '@/utils/pageTools'
import { formatDateTime } from '@/utils/pageTools'

const loading = ref(false)
const submitting = ref(false)
const applications = ref<any[]>([])
const statusFilter = ref<string>('pending')

const approveDialog = ref(false)
const rejectDialog = ref(false)
const current = ref<any>(null)
const rejectComment = ref('')

const approveForm = reactive({
  role: 'editor',
  company_id: '',
  department_id: '',
  team_id: '',
  comment: '',
})

async function fetchList() {
  loading.value = true
  try {
    const res: any = await applicationAPI.list(statusFilter.value as any)
    applications.value = res?.list || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openApproveDialog(row: any) {
  current.value = row
  Object.assign(approveForm, {
    role: 'editor',
    company_id: '',
    department_id: '',
    team_id: '',
    comment: '',
  })
  approveDialog.value = true
}

function openRejectDialog(row: any) {
  current.value = row
  rejectComment.value = ''
  rejectDialog.value = true
}

async function handleApprove() {
  if (!approveForm.role) {
    msgError('请选择角色')
    return
  }
  submitting.value = true
  try {
    await applicationAPI.approve(current.value.id, approveForm)
    msgSuccess('已通过申请，账号已创建')
    approveDialog.value = false
    await fetchList()
  } catch {
    // 错误由拦截器处理
  } finally {
    submitting.value = false
  }
}

async function handleReject() {
  const ok = await confirmDanger(`确定要拒绝 ${current.value.username} 的注册申请吗？`, '拒绝申请')
  if (!ok) return
  submitting.value = true
  try {
    await applicationAPI.reject(current.value.id, { comment: rejectComment.value })
    msgSuccess('已拒绝申请')
    rejectDialog.value = false
    await fetchList()
  } catch {
    // 错误由拦截器处理
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchList()
  fetchOrgOptions()
})
</script>

<style scoped>
.applications-page {
  padding: 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.reason-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #5a6e7a;
}
.readonly {
  color: #303133;
  font-weight: 500;
}
.muted {
  color: #909399;
  font-size: 12px;
}
</style>
