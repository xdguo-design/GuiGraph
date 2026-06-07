<template>
  <div class="change-detail-page" v-loading="loading">
    <el-card v-if="change">
      <template #header>
        <div class="card-header">
          <span>变更详情 #{{ change.id }}</span>
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
        <el-descriptions-item label="所属版本">v{{ change.version_id }}</el-descriptions-item>
        <el-descriptions-item label="所属团队">{{ change.team_name || '未分配' }}</el-descriptions-item>
        <el-descriptions-item label="变更类型">
          <el-tag :type="changeTypeMap[change.change_type] || changeTypeMap[change.type] || 'default'">
            {{ changeTypeText[change.change_type || change.type] || change.change_type || change.type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="变更原因">{{ reasonText[change.change_reason || change.reason] || change.change_reason || change.reason }}</el-descriptions-item>
        <el-descriptions-item label="变更内容" :span="2">
          <div class="content-text">{{ change.content }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="影响范围" :span="2" v-if="change.effect_scope || change.impact">
          {{ change.effect_scope || change.impact }}
        </el-descriptions-item>
        <el-descriptions-item label="关联需求号" v-if="change.related_requirement_no || change.requirement_id">
          {{ change.related_requirement_no || change.requirement_id }}
        </el-descriptions-item>
        <el-descriptions-item label="审批人" v-if="change.approved_by">{{ change.approved_by }}</el-descriptions-item>
        <el-descriptions-item label="审批时间" v-if="change.approved_at">{{ formatDate(change.approved_at) }}</el-descriptions-item>
        <el-descriptions-item label="创建人">#{{ change.created_by }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(change.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(change.updated_at) }}</el-descriptions-item>
        <el-descriptions-item v-if="change.change_reason_detail" label="原因 / 审批备注" :span="2">
          <div class="content-text">{{ change.change_reason_detail }}</div>
        </el-descriptions-item>
        <el-descriptions-item v-if="change.img_list && change.img_list.length" label="变更图片" :span="2">
          <div class="img-list">
            <el-image
              v-for="(img, i) in change.img_list"
              :key="i"
              :src="img"
              :preview-src-list="change.img_list"
              :initial-index="i"
              fit="cover"
              style="width: 96px; height: 96px; margin-right: 8px; border-radius: 4px;"
            />
          </div>
        </el-descriptions-item>
        <el-descriptions-item v-if="change.file_ref && change.file_ref.length" label="关联文档" :span="2">
          <el-link
            v-for="(f, i) in change.file_ref"
            :key="i"
            :href="f"
            target="_blank"
            type="primary"
            style="margin-right: 12px;"
          >文档 {{ i + 1 }}</el-link>
        </el-descriptions-item>
      </el-descriptions>
      <div class="action-bar" v-if="canApprove">
        <el-button type="primary" @click="handleApprove">审批通过</el-button>
        <el-button type="danger" @click="handleReject">驳回</el-button>
      </div>

      <!-- 关联知识库笔记 -->
      <el-card v-if="relatedNotes.length > 0" class="related-knowledge-card">
        <template #header>
          <span class="related-title">📖 关联知识库</span>
        </template>
        <div v-for="note in relatedNotes" :key="note.id" class="related-note-item">
          <el-link type="primary" @click="goToKnowledge(note)">
            {{ note.title }}
          </el-link>
          <span class="related-note-meta">
            <el-tag size="small" v-for="tag in (note.tags || []).slice(0, 3)" :key="tag" style="margin-left: 6px">{{ tag }}</el-tag>
          </span>
        </div>
      </el-card>
    </el-card>
    <el-empty v-else-if="!loading" description="变更不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { changeAPI } from '@/api/change'
import { knowledgeAPI } from '@/api/knowledge'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const change = ref<any>(null)
const relatedNotes = ref<any[]>([])

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
  db: 'danger',
  api: 'warning',
  config: 'info',
  code: 'success',
  infra: 'default',
}

const changeTypeText: Record<string, string> = {
  db: 'DB 变更',
  api: 'API 变更',
  config: '配置变更',
  code: '代码变更',
  infra: '基础设施',
}

const reasonText: Record<string, string> = {
  requirement: '需求变更',
  bug_fix: 'BUG 修复',
  performance: '性能优化',
  compliance: '合规要求',
  tech_debt: '技术债务',
  other: '其他',
}

// 判断是否有审批权限（管理员角色）
const canApprove = computed(() => {
  const role = authStore.userInfo?.role
  return (role === 'admin' || role === 'system_admin') && change.value?.status === 'draft'
})

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

async function fetchChangeDetail() {
  loading.value = true
  try {
    const id = route.params.id as string
    const res: any = await changeAPI.get(id)
    // 兼容 Response.ok 包裹
    change.value = res?.data ?? res

    // 获取关联的知识库笔记
    relatedNotes.value = []
    try {
      const notesRes: any = await knowledgeAPI.listNotes()
      const allNotes: any[] = notesRes?.items ?? []
      relatedNotes.value = allNotes.filter(
        (n: any) => n.related_change_ids && n.related_change_ids.includes(route.params.id)
      )
    } catch (e) {
      // 知识库获取失败不阻塞主流程
      console.warn('获取关联笔记失败', e)
    }
  } catch (error) {
    change.value = null
    ElMessage.error('获取变更详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function goToKnowledge(note: any) {
  router.push(`/knowledge?kb_id=${note.knowledge_base_id}&note_id=${note.id}`)
}

async function handleApprove() {
  try {
    await ElMessageBox.confirm('确认批准此变更申请？', '审批确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await changeAPI.approve(change.value.id, { approved: true, comment: '审批通过' })
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

    await changeAPI.approve(change.value.id, { approved: false, comment: reason })
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
.img-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.related-knowledge-card {
  margin-top: 16px;
}
.related-title {
  font-weight: 600;
}
.related-note-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  gap: 8px;
}
.related-note-item + .related-note-item {
  border-top: 1px solid var(--el-border-color-lighter);
}
.related-note-meta {
  margin-left: auto;
  display: flex;
  gap: 4px;
}
.no-link {
  color: #999;
}
</style>
