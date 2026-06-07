<template>
  <div class="change-detail-page" v-loading="loading">
    <el-card v-if="change">
      <template #header>
        <div class="card-header">
          <span>变更详情</span>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="变更 ID">{{ change.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTypeMap[change.status] || 'info'">
            {{ statusTextMap[change.status] || change.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="变更类型">
          <el-tag :type="changeTypeMap[change.type] || 'default'">
            {{ change.type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="变更原因">{{ change.reason }}</el-descriptions-item>
        <el-descriptions-item label="变更内容" :span="2">
          <div class="content-text">{{ change.content }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="影响范围" :span="2" v-if="change.impact">
          {{ change.impact }}
        </el-descriptions-item>
        <el-descriptions-item label="关联需求号" v-if="change.requirement_id">
          {{ change.requirement_id }}
        </el-descriptions-item>
        <el-descriptions-item label="创建人">{{ change.created_by }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(change.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(change.updated_at) }}</el-descriptions-item>
      </el-descriptions>
      <div class="action-bar" v-if="canApprove">
        <el-button type="primary" @click="handleApprove">审批通过</el-button>
        <el-button type="danger" @click="handleReject">驳回</el-button>
      </div>
    </el-card>
    <el-empty v-else-if="!loading" description="变更不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { changeAPI } from '@/api/change'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const change = ref<any>(null)

// 状态映射
const statusTypeMap: Record<string, any> = {
  draft: 'info',
  approved: 'success',
  rejected: 'danger',
  released: 'success',
  rolled_back: 'warning',
}

const statusTextMap: Record<string, string> = {
  draft: '草稿',
  approved: '已批准',
  rejected: '已驳回',
  released: '已发布',
  rolled_back: '已回滚',
}

const changeTypeMap: Record<string, any> = {
  'DB 变更': 'danger',
  'API 变更': 'warning',
  '配置变更': 'info',
  '代码变更': 'success',
  '基础设施': 'default',
}

// 判断是否有审批权限（管理员角色）
const canApprove = computed(() => {
  return authStore.userInfo?.role === 'admin' && change.value?.status === 'draft'
})

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

async function fetchChangeDetail() {
  loading.value = true
  try {
    const id = route.params.id as string
    const response = await changeAPI.get(id)
    change.value = response.data
  } catch (error) {
    ElMessage.error('获取变更详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function handleApprove() {
  try {
    await ElMessageBox.confirm('确认批准此变更申请？', '审批确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    await changeAPI.approve(change.value.id, { action: 'approve' })
    ElMessage.success('审批成功')
    await fetchChangeDetail() // 刷新数据
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('审批失败')
      console.error(error)
    }
  }
}

async function handleReject() {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入驳回理由', '驳回变更', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '驳回理由不能为空',
    })
    
    await changeAPI.approve(change.value.id, { action: 'reject', reason })
    ElMessage.success('驳回成功')
    await fetchChangeDetail() // 刷新数据
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('驳回失败')
      console.error(error)
    }
  }
}

onMounted(() => {
  fetchChangeDetail()
})
</script>

<style scoped>
.change-detail-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.content-text {
  white-space: pre-wrap;
}
.action-bar {
  margin-top: 16px;
  text-align: right;
}
</style>
