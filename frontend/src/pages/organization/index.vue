<template>
  <div class="organization-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>组织架构</span>
          <div>
            <el-upload
              :auto-upload="true"
              :show-file-list="false"
              :http-request="handleUpload"
              accept=".json"
            >
              <el-button :icon="Upload">导入组织结构</el-button>
            </el-upload>
            <el-button @click="fetchData" :icon="Refresh">刷新</el-button>
            <el-button type="primary" @click="openAddRoot" :icon="Plus">新建公司</el-button>
          </div>
        </div>
      </template>

      <el-tree
        :data="orgTree"
        :props="treeProps"
        node-key="id"
        v-loading="loading"
        :expand-on-click-node="false"
        default-expand-all
      >
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span class="node-label">
              <el-icon style="margin-right: 4px">
                <OfficeBuilding v-if="data.type === 'company'" />
                <Flag v-else-if="data.type === 'department'" />
                <User v-else-if="data.type === 'team'" />
                <UserFilled v-else />
              </el-icon>
              {{ node.label }}
              <el-tag
                v-if="data.type === 'team' && data.members"
                size="small"
                type="info"
                style="margin-left: 8px"
              >{{ data.members.length }} 人</el-tag>
            </span>
            <span class="node-actions">
              <template v-if="data.type === 'company'">
                <el-button link type="primary" size="small" @click="openAddDept(data)">添加部门</el-button>
                <el-button link type="primary" size="small" @click="openEdit(data)">编辑</el-button>
                <el-button link type="danger" size="small" @click="handleDelete(data)">删除</el-button>
              </template>
              <template v-else-if="data.type === 'department'">
                <el-button link type="primary" size="small" @click="openAddTeam(data)">添加团队</el-button>
                <el-button link type="primary" size="small" @click="openEdit(data)">编辑</el-button>
                <el-button link type="danger" size="small" @click="handleDelete(data)">删除</el-button>
              </template>
              <template v-else-if="data.type === 'team'">
                <el-button link type="primary" size="small" @click="openMembers(data)">成员管理</el-button>
                <el-button link type="primary" size="small" @click="openEdit(data)">编辑</el-button>
                <el-button link type="danger" size="small" @click="handleDelete(data)">删除</el-button>
              </template>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="类型">
          <el-tag>{{ typeLabel(form.type) }}</el-tag>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入编码（唯一）" />
        </el-form-item>
        <el-form-item v-if="form.type === 'team'" label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 团队成员管理 -->
    <el-dialog v-model="membersVisible" :title="`团队成员 - ${currentTeam?.name}`" width="600px">
      <div class="members-toolbar">
        <el-button type="primary" :icon="Plus" size="small" @click="openAddMember">添加成员</el-button>
        <el-button :icon="Refresh" size="small" @click="loadMembers">刷新</el-button>
      </div>
      <el-table :data="memberList" v-loading="membersLoading" border>
        <el-table-column label="用户名" prop="username" />
        <el-table-column label="昵称" prop="nickname" />
        <el-table-column label="邮箱" prop="email" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="团队角色" width="120">
          <template #default="{ row }">
            <el-select v-model="row.team_role" size="small" @change="(v) => changeMemberRole(row, v)">
              <el-option label="管理员" value="admin" />
              <el-option label="成员" value="member" />
              <el-option label="观察者" value="viewer" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="removeMember(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 添加成员对话框 -->
    <el-dialog v-model="addMemberVisible" title="添加团队成员" width="450px">
      <el-form :model="addMemberForm" label-width="80px">
        <el-form-item label="选择用户">
          <el-select v-model="addMemberForm.user_id" placeholder="请选择用户" filterable>
            <el-option
              v-for="u in availableUsers"
              :key="u.id"
              :label="`${u.username} (${u.nickname || '-'})`"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="团队角色">
          <el-select v-model="addMemberForm.role">
            <el-option label="管理员" value="admin" />
            <el-option label="成员" value="member" />
            <el-option label="观察者" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addMemberVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddMember">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Plus, OfficeBuilding, Flag, User, UserFilled, Upload,
} from '@element-plus/icons-vue'
import { orgAPI, userAdminAPI } from '@/api/organization'

const loading = ref(false)
const orgTree = ref<any[]>([])
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref()
const currentNode = ref<any>(null)

const form = reactive({
  type: '' as '' | 'company' | 'department' | 'team',
  name: '',
  code: '',
  description: '',
  parent_id: '',
  parent_type: '',
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
}

const treeProps = {
  label: 'name',
  children: 'children',
}

const submitting = ref(false)
const dialogTitle = computed(() =>
  dialogMode.value === 'create' ? `新建${typeLabel(form.type)}` : '编辑'
)

function typeLabel(t: string) {
  return { company: '公司', department: '部门', team: '团队' }[t] || t
}

async function fetchData() {
  loading.value = true
  try {
    const r = await orgAPI.tree()
    orgTree.value = r.data || []
  } catch (e) {
    ElMessage.error('获取组织架构失败')
  } finally {
    loading.value = false
  }
}

function resetForm(type: string, parent?: any) {
  form.type = (type || '') as any
  form.name = ''
  form.code = ''
  form.description = ''
  form.parent_id = parent?.id || ''
  form.parent_type = parent?.type || ''
}

function openAddRoot() {
  dialogMode.value = 'create'
  resetForm('company')
  dialogVisible.value = true
}

function openAddDept(node: any) {
  dialogMode.value = 'create'
  resetForm('department', node)
  dialogVisible.value = true
}

function openAddTeam(node: any) {
  dialogMode.value = 'create'
  resetForm('team', node)
  dialogVisible.value = true
}

function openEdit(node: any) {
  dialogMode.value = 'edit'
  currentNode.value = node
  Object.assign(form, {
    type: node.type,
    name: node.name,
    code: node.code,
    description: node.description || '',
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      if (form.type === 'company') {
        await orgAPI.createCompany({ name: form.name, code: form.code })
      } else if (form.type === 'department') {
        await orgAPI.createDepartment({
          name: form.name, code: form.code,
          company_id: form.parent_id,
        })
      } else if (form.type === 'team') {
        await orgAPI.createTeam({
          name: form.name, code: form.code,
          department_id: form.parent_id,
          description: form.description,
        })
      }
      ElMessage.success('创建成功')
    } else {
      const id = currentNode.value.id
      if (form.type === 'company') {
        await orgAPI.updateCompany(id, { name: form.name, code: form.code })
      } else if (form.type === 'department') {
        await orgAPI.updateDepartment(id, { name: form.name, code: form.code })
      } else if (form.type === 'team') {
        await orgAPI.updateTeam(id, {
          name: form.name, code: form.code, description: form.description,
        })
      }
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(node: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除【${node.name}】？此操作不可恢复`,
      '警告', { type: 'warning' }
    )
  } catch { return }
  try {
    if (node.type === 'company') await orgAPI.deleteCompany(node.id)
    else if (node.type === 'department') await orgAPI.deleteDepartment(node.id)
    else if (node.type === 'team') await orgAPI.deleteTeam(node.id)
    ElMessage.success('删除成功')
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

// ── 成员管理 ──

const membersVisible = ref(false)
const membersLoading = ref(false)
const memberList = ref<any[]>([])
const currentTeam = ref<any>(null)
const allUsers = ref<any[]>([])

async function openMembers(team: any) {
  currentTeam.value = team
  membersVisible.value = true
  await loadMembers()
  if (allUsers.value.length === 0) {
    try {
      const r = await userAdminAPI.list()
      allUsers.value = r.data || []
    } catch {}
  }
}

async function loadMembers() {
  if (!currentTeam.value) return
  membersLoading.value = true
  try {
    const r = await orgAPI.teamMembers(currentTeam.value.id)
    memberList.value = r.data || []
  } catch {
    ElMessage.error('获取成员失败')
  } finally {
    membersLoading.value = false
  }
}

const addMemberVisible = ref(false)
const addMemberForm = reactive({ user_id: '', role: 'member' })
const availableUsers = computed(() => {
  const memberIds = new Set(memberList.value.map((m) => String(m.user_id)))
  return allUsers.value.filter((u) => !memberIds.has(String(u.id)))
})

function openAddMember() {
  addMemberForm.user_id = ''
  addMemberForm.role = 'member'
  addMemberVisible.value = true
}

async function confirmAddMember() {
  if (!addMemberForm.user_id) {
    ElMessage.warning('请选择用户')
    return
  }
  try {
    await orgAPI.addTeamMember(currentTeam.value.id, {
      user_id: addMemberForm.user_id,
      role: addMemberForm.role,
    })
    ElMessage.success('添加成功')
    addMemberVisible.value = false
    await loadMembers()
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '添加失败')
  }
}

async function changeMemberRole(row: any, role: string) {
  try {
    await orgAPI.updateTeamMember(currentTeam.value.id, row.user_id, { role })
    ElMessage.success('已更新')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '更新失败')
    await loadMembers()
  }
}

async function removeMember(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定将【${row.username}】移出团队？`, '警告', { type: 'warning' }
    )
  } catch { return }
  try {
    await orgAPI.removeTeamMember(currentTeam.value.id, row.user_id)
    ElMessage.success('已移除')
    await loadMembers()
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '移除失败')
  }
}

// ── 上传 ──
async function handleUpload(opts: any) {
  try {
    const r = await orgAPI.upload(opts.file)
    ElMessage.success(
      `上传完成：公司 ${r.data.created.companies} 个，部门 ${r.data.created.departments} 个，团队 ${r.data.created.teams} 个`
    )
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '上传失败')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.organization-page { padding: 0; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 16px;
  width: 100%;
}
.node-actions {
  display: none;
}
.custom-tree-node:hover .node-actions {
  display: inline-block;
}
.members-toolbar {
  margin-bottom: 12px;
  display: flex;
  gap: 8px;
}
</style>
