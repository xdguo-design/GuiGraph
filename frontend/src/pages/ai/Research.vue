<template>
  <div class="ai-research-page">
    <el-row :gutter="20">
      <!-- 左侧：搜索区 -->
      <el-col :span="14">
        <el-card class="search-card">
          <template #header>
            <div class="card-header">
              <span>🧠 AI 智能检索</span>
              <el-tag type="info" size="small">RAG</el-tag>
            </div>
          </template>

          <!-- 搜索框 -->
          <div class="search-section">
            <el-input
              v-model="searchQuery"
              type="textarea"
              :rows="3"
              placeholder="输入你的问题或搜索关键词..."
              @keydown.ctrl.enter="handleSearch"
              :maxlength="500"
              show-word-limit
            />
            <div class="search-actions">
              <el-button type="primary" @click="handleSearch" :loading="searching" :icon="Search">
                搜索 (Ctrl+Enter)
              </el-button>
              <el-button @click="searchQuery = ''" :icon="Refresh">清空</el-button>
            </div>
          </div>

          <!-- 搜索结果 -->
          <div v-if="searchResults.length > 0 || searching" class="results-section">
            <el-divider>{{ searching ? '搜索中...' : `找到 ${searchResults.length} 条结果` }}</el-divider>
            <div v-loading="searching">
              <div v-for="(result, index) in searchResults" :key="index" class="result-item">
                <div class="result-header">
                  <el-icon class="result-icon"><Document /></el-icon>
                  <span class="result-title">{{ result.title || '未命名文档' }}</span>
                  <el-tag size="small" type="success">相关度 {{ result.score || 0.85 }}</el-tag>
                </div>
                <div class="result-content">{{ result.content || result.snippet }}</div>
                <div v-if="result.metadata" class="result-meta">
                  <el-tag size="small" type="info">{{ result.metadata.source || '知识库' }}</el-tag>
                  <span class="meta-text">{{ result.metadata.date || '' }}</span>
                </div>
              </div>
              <el-empty v-if="!searching && searchResults.length === 0" description="未找到相关内容" />
            </div>
          </div>
        </el-card>

        <!-- 文档分析卡片 -->
        <el-card class="analyze-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>📄 文档分析</span>
              <el-tag type="warning" size="small">AI</el-tag>
            </div>
          </template>

          <div class="analyze-section">
            <el-input
              v-model="analyzeDocument"
              type="textarea"
              :rows="6"
              placeholder="粘贴文档内容，AI 将自动分析提取关键信息..."
              :maxlength="5000"
              show-word-limit
            />
            <div class="analyze-actions">
              <el-button type="primary" @click="handleAnalyze" :loading="analyzing" :icon="MagicStick">
                开始分析
              </el-button>
              <el-upload
                :auto-upload="false"
                :on-change="handleFileUpload"
                :show-file-list="false"
                accept=".txt,.md,.doc,.docx,.pdf"
                style="display: inline-block; margin-left: 10px;"
              >
                <el-button :icon="Upload">上传文档</el-button>
              </el-upload>
            </div>
          </div>

          <!-- 分析结果 -->
          <div v-if="analysisResult" class="analysis-result">
            <el-divider>分析结果</el-divider>
            <div class="analysis-sections">
              <div v-if="analysisResult.summary" class="analysis-item">
                <strong>摘要：</strong>
                <p>{{ analysisResult.summary }}</p>
              </div>
              <div v-if="analysisResult.entities?.length" class="analysis-item">
                <strong>实体识别：</strong>
                <el-tag
                  v-for="(entity, idx) in analysisResult.entities"
                  :key="idx"
                  size="small"
                  style="margin: 4px;"
                  type="primary"
                >
                  {{ entity }}
                </el-tag>
              </div>
              <div v-if="analysisResult.keywords?.length" class="analysis-item">
                <strong>关键词：</strong>
                <el-tag
                  v-for="(keyword, idx) in analysisResult.keywords"
                  :key="idx"
                  size="small"
                  style="margin: 4px;"
                  type="warning"
                >
                  {{ keyword }}
                </el-tag>
              </div>
              <div v-if="analysisResult.analysis" class="analysis-item">
                <strong>详细分析：</strong>
                <p>{{ analysisResult.analysis }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：AI 模型 & Skill 管理 -->
      <el-col :span="10">
        <el-card class="models-card">
          <template #header>
            <div class="card-header">
              <span>🤖 AI 模型</span>
              <el-button link type="primary" size="small" @click="refreshModels">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="models" size="small" v-loading="loadingModels">
            <el-table-column prop="name" label="模型名称" min-width="120" show-overflow-tooltip />
            <el-table-column prop="provider" label="提供商" width="100" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '可用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingModels && models.length === 0" description="暂无模型配置" />
        </el-card>

        <el-card class="skills-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>⚡ AI Skills</span>
              <el-button link type="primary" size="small" @click="refreshSkills">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="skills" size="small" v-loading="loadingSkills">
            <el-table-column prop="name" label="Skill 名称" min-width="120" show-overflow-tooltip />
            <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
            <el-table-column prop="is_enabled" label="状态" width="80">
              <template #default="{ row }">
                <el-switch
                  v-model="row.is_enabled"
                  size="small"
                  @change="toggleSkill(row)"
                  :loading="row.toggling"
                />
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingSkills && skills.length === 0" description="暂无 Skill" />
        </el-card>

        <!-- MCP 服务器 -->
        <el-card class="mcp-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>🔌 MCP 服务器</span>
              <el-button link type="primary" size="small" @click="refreshMcpServers">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="mcpServers" size="small" v-loading="loadingMcp">
            <el-table-column prop="name" label="名称" min-width="100" show-overflow-tooltip />
            <el-table-column prop="transport" label="协议" width="80" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'connected' ? 'success' : 'danger'" size="small">
                  {{ row.status === 'connected' ? '已连接' : '未连接' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button
                  link
                  type="primary"
                  size="small"
                  @click="testMcpConnection(row)"
                  :loading="row.testing"
                >
                  测试
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingMcp && mcpServers.length === 0" description="暂无 MCP" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search, Refresh, MagicStick, Upload, Document,
} from '@element-plus/icons-vue'
import { aiAPI } from '@/api/ai'

// ── 搜索 ──
const searchQuery = ref('')
const searching = ref(false)
const searchResults = ref<any[]>([])

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  searching.value = true
  try {
    const res: any = await aiAPI.ragSearch(searchQuery.value, 5)
    searchResults.value = res?.results || []
    ElMessage.success(`找到 ${searchResults.value.length} 条结果`)
  } catch (error: any) {
    ElMessage.error(error?.message || '搜索失败')
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

// ── 文档分析 ──
const analyzeDocument = ref('')
const analyzing = ref(false)
const analysisResult = ref<any>(null)

async function handleAnalyze() {
  if (!analyzeDocument.value.trim()) {
    ElMessage.warning('请输入文档内容')
    return
  }
  analyzing.value = true
  try {
    const res: any = await aiAPI.ragAnalyze(analyzeDocument.value)
    analysisResult.value = res
    ElMessage.success('分析完成')
  } catch (error: any) {
    ElMessage.error(error?.message || '分析失败')
    analysisResult.value = null
  } finally {
    analyzing.value = false
  }
}

function handleFileUpload(file: any) {
  const reader = new FileReader()
  reader.onload = (e) => {
    analyzeDocument.value = e.target?.result as string || ''
    ElMessage.success('文件已加载')
  }
  reader.readAsText(file.raw)
}

// ── AI 模型 ──
const loadingModels = ref(false)
const models = ref<any[]>([])

async function refreshModels() {
  loadingModels.value = true
  try {
    const res: any = await aiAPI.listModels()
    models.value = res?.items || res || []
  } catch (error) {
    console.error('Failed to load models:', error)
  } finally {
    loadingModels.value = false
  }
}

// ── AI Skills ──
const loadingSkills = ref(false)
const skills = ref<any[]>([])

async function refreshSkills() {
  loadingSkills.value = true
  try {
    const res: any = await aiAPI.listSkills()
    skills.value = res?.items || res || []
  } catch (error) {
    console.error('Failed to load skills:', error)
  } finally {
    loadingSkills.value = false
  }
}

async function toggleSkill(skill: any) {
  skill.toggling = true
  try {
    if (skill.is_enabled) {
      await aiAPI.enableSkill(skill.id)
      ElMessage.success('Skill 已启用')
    } else {
      await aiAPI.disableSkill(skill.id)
      ElMessage.info('Skill 已禁用')
    }
  } catch (error: any) {
    ElMessage.error(error?.message || '操作失败')
    skill.is_enabled = !skill.is_enabled
  } finally {
    skill.toggling = false
  }
}

// ── MCP 服务器 ──
const loadingMcp = ref(false)
const mcpServers = ref<any[]>([])

async function refreshMcpServers() {
  loadingMcp.value = true
  try {
    const res: any = await aiAPI.listMcpServers()
    mcpServers.value = res?.items || res || []
  } catch (error) {
    console.error('Failed to load MCP servers:', error)
  } finally {
    loadingMcp.value = false
  }
}

async function testMcpConnection(server: any) {
  server.testing = true
  try {
    await aiAPI.testMcpConnection(server.id)
    server.status = 'connected'
    ElMessage.success('连接成功')
  } catch (error: any) {
    server.status = 'disconnected'
    ElMessage.error(error?.message || '连接失败')
  } finally {
    server.testing = false
  }
}

// ── 初始化 ──
onMounted(() => {
  refreshModels()
  refreshSkills()
  refreshMcpServers()
})
</script>

<style scoped>
.ai-research-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-card,
.analyze-card,
.models-card,
.skills-card,
.mcp-card {
  min-height: 300px;
}

.search-section {
  margin-bottom: 20px;
}
.search-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  justify-content: flex-end;
}

.results-section {
  margin-top: 20px;
}
.result-item {
  padding: 12px;
  margin-bottom: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  background: var(--el-fill-color-light);
  transition: all 0.2s;
}
.result-item:hover {
  background: var(--el-fill-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.result-icon {
  color: #1a5276;
  font-size: 18px;
}
.result-title {
  font-weight: 600;
  flex: 1;
  color: var(--el-text-color-primary);
}
.result-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  margin-bottom: 8px;
  padding-left: 26px;
}
.result-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 26px;
}
.meta-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.analyze-section {
  margin-bottom: 20px;
}
.analyze-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  justify-content: flex-end;
  align-items: center;
}
.analysis-result {
  margin-top: 16px;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
}
.analysis-sections {
  font-size: 14px;
}
.analysis-item {
  margin-bottom: 16px;
}
.analysis-item:last-child {
  margin-bottom: 0;
}
.analysis-item strong {
  display: block;
  margin-bottom: 6px;
  color: var(--el-text-color-primary);
}
.analysis-item p {
  color: var(--el-text-color-regular);
  line-height: 1.6;
  margin: 0;
}

/* 暗色模式适配 */
:deep(html.dark) .result-item {
  background: var(--el-fill-color);
}
:deep(html.dark) .result-item:hover {
  background: var(--el-fill-color-dark);
}
:deep(html.dark) .analysis-result {
  background: var(--el-fill-color);
}
</style>
