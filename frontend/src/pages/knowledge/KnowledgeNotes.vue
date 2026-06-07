<template>
  <div class="knowledge-page">
    <!-- 视图切换 -->
    <el-radio-group v-model="viewMode" class="view-switcher" @change="handleViewChange">
      <el-radio-button value="all">全部知识库</el-radio-button>
      <el-radio-button value="team">团队知识库</el-radio-button>
    </el-radio-group>

    <el-row :gutter="16" style="margin-top: 16px">
      <!-- 左侧：知识库列表 -->
      <el-col :span="6">
        <el-card class="kb-sidebar">
          <template #header>
            <div class="sidebar-header">
              <span>{{ viewMode === 'team' ? '团队知识库' : '知识库' }}</span>
              <el-button v-if="viewMode === 'all'" type="primary" size="small" :icon="Plus" @click="showCreateKbDialog">新建</el-button>
            </div>
          </template>
          <div v-loading="kbLoading">
            <div
              v-for="kb in filteredKBs"
              :key="kb.id"
              class="kb-item"
              :class="{ active: currentKbId === kb.id }"
              @click="selectKb(kb)"
            >
              <el-icon><Folder /></el-icon>
              <span class="kb-name">{{ kb.name }}</span>
            </div>
            <el-empty v-if="!kbLoading && filteredKBs.length === 0" description="暂无知识库" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：笔记列表 + 编辑 -->
      <el-col :span="18">
        <el-card v-if="!currentKbId" class="empty-hint">
          <el-empty :description="viewMode === 'team' ? '请从左侧选择团队知识库' : '请选择左侧知识库'" :image-size="100" />
        </el-card>

        <template v-else>
          <!-- 笔记列表 -->
          <el-card v-if="!editingNote">
            <template #header>
              <div class="card-header">
                <span>{{ currentKbName }} - 笔记列表</span>
                <el-button v-if="viewMode === 'all'" type="primary" size="small" :icon="Plus" @click="createNewNote">新建笔记</el-button>
              </div>
            </template>
            <el-table :data="notes" v-loading="notesLoading" stripe border>
              <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
              <el-table-column prop="tags" label="标签" width="200">
                <template #default="{ row }">
                  <el-tag v-for="tag in (row.tags || []).slice(0, 3)" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="关联变更" width="120" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.related_change_ids?.length" type="warning" size="small">
                    {{ row.related_change_ids.length }} 个
                  </el-tag>
                  <span v-else class="no-link">-</span>
                </template>
              </el-table-column>
              <el-table-column prop="is_published" label="状态" width="90">
                <template #default="{ row }">
                  <el-tag :type="row.is_published ? 'success' : 'info'" size="small">
                    {{ row.is_published ? '已发布' : '草稿' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="170">
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="170" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="editNote(row)">编辑</el-button>
                  <el-button link type="danger" size="small" @click="handleDeleteNote(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 笔记编辑 -->
          <el-card v-else>
            <template #header>
              <div class="card-header">
                <span>{{ isNewNote ? '新建笔记' : '编辑笔记' }}</span>
                <div>
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveNote" :loading="saving">保存</el-button>
                </div>
              </div>
            </template>
            <el-form :model="noteForm" label-width="80px">
              <el-form-item label="标题">
                <el-input v-model="noteForm.title" placeholder="输入笔记标题" />
              </el-form-item>
              <el-form-item label="标签">
                <el-select
                  v-model="noteForm.tags"
                  multiple
                  filterable
                  allow-create
                  default-first-option
                  placeholder="输入标签后回车"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="内容">
                <el-input
                  v-model="noteForm.content"
                  type="textarea"
                  :autosize="{ minRows: 12, maxRows: 30 }"
                  placeholder="支持 Markdown 格式"
                />
              </el-form-item>
              <el-form-item label="发布">
                <el-switch v-model="noteForm.is_published" active-text="发布" inactive-text="草稿" />
              </el-form-item>
            </el-form>
          </el-card>
        </template>
      </el-col>
    </el-row>

    <!-- 新建知识库弹窗 -->
    <el-dialog v-model="kbDialogVisible" title="新建知识库" width="460px" destroy-on-close>
      <el-form :model="kbForm" label-width="90px">
        <el-form-item label="名称">
          <el-input v-model="kbForm.name" placeholder="输入知识库名称" />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="kbForm.code" placeholder="唯一标识，如 team-wiki" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="kbForm.description" type="textarea" :rows="3" placeholder="可选描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="kbDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateKb" :loading="kbCreating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Folder } from '@element-plus/icons-vue'
import { knowledgeAPI } from '@/api/knowledge'
import { formatDateTime, confirmDanger, msgSuccess, msgError } from '@/utils/pageTools'

// ── 视图切换 ──
const viewMode = ref<'all' | 'team'>('all')

// ── 知识库 ──
const kbLoading = ref(false)
const knowledgeBases = ref<any[]>([])
const currentKbId = ref<string | null>(null)
const currentKbName = computed(() => {
  const kb = knowledgeBases.value.find((k) => k.id === currentKbId.value)
  return kb?.name || ''
})

/** 团队知识库：owner_type=team 且 code 以 team_ 开头 */
const teamKBs = computed(() =>
  knowledgeBases.value.filter((kb: any) => kb.owner_type === 'team' && String(kb.code || '').startsWith('team_'))
)

/** 根据当前视图过滤的知识库列表 */
const filteredKBs = computed(() =>
  viewMode.value === 'team' ? teamKBs.value : knowledgeBases.value
)

function handleViewChange() {
  currentKbId.value = null
}

async function fetchKnowledgeBases() {
  kbLoading.value = true
  try {
    const res: any = await knowledgeAPI.listKnowledgeBases()
    knowledgeBases.value = res?.items || []
  } catch (e) {
    console.error(e)
  } finally {
    kbLoading.value = false
  }
}

function selectKb(kb: any) {
  currentKbId.value = kb.id
  editingNote.value = false
  fetchNotes()
}

// 新建知识库弹窗
const kbDialogVisible = ref(false)
const kbCreating = ref(false)
const kbForm = reactive({ name: '', code: '', description: '' })

function showCreateKbDialog() {
  Object.assign(kbForm, { name: '', code: '', description: '' })
  kbDialogVisible.value = true
}

async function handleCreateKb() {
  if (!kbForm.name || !kbForm.code) {
    msgError('名称和编码为必填项')
    return
  }
  kbCreating.value = true
  try {
    await knowledgeAPI.createKnowledgeBase(kbForm)
    msgSuccess('知识库创建成功')
    kbDialogVisible.value = false
    await fetchKnowledgeBases()
  } catch (e) {
    msgError('创建失败')
    console.error(e)
  } finally {
    kbCreating.value = false
  }
}

// ── 笔记 ──
const notesLoading = ref(false)
const notes = ref<any[]>([])
const editingNote = ref(false)
const isNewNote = ref(false)
const saving = ref(false)
const noteForm = reactive({
  id: '',
  title: '',
  content: '',
  tags: [] as string[],
  is_published: false,
})

async function fetchNotes() {
  if (!currentKbId.value) return
  notesLoading.value = true
  try {
    const res: any = await knowledgeAPI.listNotes({ knowledge_base_id: parseInt(currentKbId.value) })
    notes.value = res?.items || []
  } catch (e) {
    console.error(e)
  } finally {
    notesLoading.value = false
  }
}

function createNewNote() {
  isNewNote.value = true
  editingNote.value = true
  Object.assign(noteForm, { id: '', title: '', content: '', tags: [], is_published: false })
}

function editNote(row: any) {
  isNewNote.value = false
  editingNote.value = true
  Object.assign(noteForm, {
    id: row.id,
    title: row.title,
    content: row.content,
    tags: row.tags || [],
    is_published: row.is_published || false,
  })
}

function cancelEdit() {
  editingNote.value = false
}

async function saveNote() {
  if (!noteForm.title) {
    msgError('标题不能为空')
    return
  }
  saving.value = true
  try {
    const data: any = {
      title: noteForm.title,
      content: noteForm.content,
      tags: noteForm.tags,
      is_published: noteForm.is_published,
      knowledge_base_id: parseInt(currentKbId.value!),
    }
    if (isNewNote.value) {
      await knowledgeAPI.createNote(data)
    } else {
      await knowledgeAPI.updateNote(parseInt(noteForm.id), data)
    }
    msgSuccess(isNewNote.value ? '创建成功' : '保存成功')
    editingNote.value = false
    await fetchNotes()
  } catch (e) {
    msgError('保存失败')
    console.error(e)
  } finally {
    saving.value = false
  }
}

async function handleDeleteNote(row: any) {
  const ok = await confirmDanger(`确认删除笔记「${row.title}」？此操作不可恢复。`)
  if (!ok) return
  try {
    await knowledgeAPI.deleteNote(parseInt(row.id))
    msgSuccess('删除成功')
    await fetchNotes()
  } catch (e) {
    msgError('删除失败')
    console.error(e)
  }
}


onMounted(() => {
  fetchKnowledgeBases()
})
</script>

<style scoped>
.knowledge-page {
  padding: 20px;
}
.view-switcher {
  margin-bottom: 0;
}
.kb-sidebar {
  min-height: 500px;
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.kb-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
}
.kb-item:hover {
  background: #f0f5ff;
}
.kb-item.active {
  background: #e6f0ff;
  color: #1a5276;
  font-weight: 600;
}
.kb-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.empty-hint {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.no-link {
  color: #999;
}
</style>
