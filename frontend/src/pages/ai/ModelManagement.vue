<template>
  <div class="ai-model-page">
    <el-row :gutter="20">
      <!-- 左侧：模型配置 -->
      <el-col :span="14">
        <!-- Complex 档 -->
        <el-card class="tier-card">
          <template #header>
            <div class="card-header">
              <span>🧠 高算力档 (complex)</span>
              <span class="tier-desc">复杂推理 · 长文本生成 · 变更分析</span>
            </div>
          </template>
          <el-table :data="complexModels" size="small" v-loading="loading">
            <el-table-column prop="name" label="模型名称" min-width="120" show-overflow-tooltip />
            <el-table-column prop="model_id" label="模型 ID" width="110" />
            <el-table-column prop="provider" label="提供商" width="80" />
            <el-table-column prop="rate_limit_rpm" label="RPM" width="60" />
            <el-table-column prop="cost_per_1m" label="¥/M" width="70">
              <template #default="{ row }">{{ row.cost_per_1m ?? '-' }}</template>
            </el-table-column>
            <el-table-column label="默认" width="60">
              <template #default="{ row }">
                <el-tag v-if="row.is_default" type="success" size="small">✓</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="60">
              <template #default="{ row }">
                <el-tag :type="row.active ? 'success' : 'info'" size="small">{{ row.active ? '启用' : '禁用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editModel(row)">编辑</el-button>
                <el-button link type="danger" size="small" @click="deleteModel(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && complexModels.length === 0" description="暂无模型" />
        </el-card>

        <!-- Fast 档 -->
        <el-card class="tier-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>⚡ 低算力档 (fast)</span>
              <span class="tier-desc">快速响应 · 简单任务 · 检索诊断</span>
            </div>
          </template>
          <el-table :data="fastModels" size="small" v-loading="loading">
            <el-table-column prop="name" label="模型名称" min-width="120" show-overflow-tooltip />
            <el-table-column prop="model_id" label="模型 ID" width="110" />
            <el-table-column prop="provider" label="提供商" width="80" />
            <el-table-column prop="rate_limit_rpm" label="RPM" width="60" />
            <el-table-column prop="cost_per_1m" label="¥/M" width="70">
              <template #default="{ row }">{{ row.cost_per_1m ?? '-' }}</template>
            </el-table-column>
            <el-table-column label="默认" width="60">
              <template #default="{ row }">
                <el-tag v-if="row.is_default" type="success" size="small">✓</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="60">
              <template #default="{ row }">
                <el-tag :type="row.active ? 'success' : 'info'" size="small">{{ row.active ? '启用' : '禁用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editModel(row)">编辑</el-button>
                <el-button link type="danger" size="small" @click="deleteModel(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && fastModels.length === 0" description="暂无模型" />
        </el-card>
      </el-col>

      <!-- 右侧：场景绑定 + 用量 -->
      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🔗 场景-模型绑定</span>
            </div>
          </template>
          <el-table :data="bindings" size="small" v-loading="loadingBindings">
            <el-table-column prop="scenario_name" label="场景" min-width="140" show-overflow-tooltip />
            <el-table-column prop="tier" label="档位" width="80">
              <template #default="{ row }">
                <el-tag :type="row.tier === 'complex' ? 'warning' : 'success'" size="small">{{ row.tier }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="model_name" label="模型" min-width="120" show-overflow-tooltip />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editBinding(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- AI 用量统计 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>📊 AI 用量统计</span>
              <el-button link type="primary" size="small" @click="refreshUsage">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div v-loading="loadingUsage">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="总调用次数">{{ usage.total_calls || 0 }}</el-descriptions-item>
              <el-descriptions-item label="输入 Tokens">{{ usage.total_input_tokens || 0 }}</el-descriptions-item>
              <el-descriptions-item label="输出 Tokens">{{ usage.total_output_tokens || 0 }}</el-descriptions-item>
              <el-descriptions-item label="场景数">{{ Object.keys(usage.by_scenario || {}).length }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑模型对话框 -->
    <el-dialog v-model="modelDialogVisible" :title="editingModel.id ? '编辑模型' : '添加模型'" width="600px">
      <el-form :model="editingModel" label-width="110px">
        <el-form-item label="模型名称" required>
          <el-input v-model="editingModel.name" placeholder="如：智谱 GLM-5.1" />
        </el-form-item>
        <el-form-item label="提供商" required>
          <el-select v-model="editingModel.provider">
            <el-option label="智谱 (Zhipu)" value="zhipu" />
            <el-option label="通义千问 (Aliyun)" value="aliyun" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="本地模型" value="local" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型 ID" required>
          <el-input v-model="editingModel.model_id" placeholder="如：glm-5.1" />
        </el-form-item>
        <el-form-item label="算力档位" required>
          <el-select v-model="editingModel.tier">
            <el-option label="🧠 Complex（高算力）" value="complex" />
            <el-option label="⚡ Fast（低算力）" value="fast" />
          </el-select>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="editingModel.api_key" type="password" show-password placeholder="sk-xxx" />
        </el-form-item>
        <el-form-item label="API Base URL">
          <el-input v-model="editingModel.base_url" placeholder="https://open.bigmodel.cn/api/paas/v4" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最大 Tokens">
              <el-input-number v-model="editingModel.max_output_tokens" :min="256" :max="32768" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="温度">
              <el-input-number v-model="editingModel.temperature" :min="0" :max="2" :step="0.1" :precision="1" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="RPM 限制">
              <el-input-number v-model="editingModel.rate_limit_rpm" :min="1" :max="1000" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="¥/百万 Tokens">
              <el-input-number v-model="editingModel.cost_per_1m" :min="0" :precision="2" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="设为默认">
          <el-switch v-model="editingModel.is_default" active-text="该档位默认模型" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="modelDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveModel">保存</el-button>
      </template>
    </el-dialog>

    <!-- 底部操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="addModel">➕ 添加模型</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { aiAPI } from '@/api/ai'

const loading = ref(false)
const loadingBindings = ref(false)
const loadingUsage = ref(false)
const saving = ref(false)
const models = ref<any[]>([])
const bindings = ref<any[]>([])
const usage = ref<any>({})
const modelDialogVisible = ref(false)
const editingModel = ref<any>({})

const complexModels = computed(() => models.value.filter((m: any) => m.tier === 'complex'))
const fastModels = computed(() => models.value.filter((m: any) => m.tier === 'fast'))

async function refreshModels() {
  loading.value = true
  try {
    const res: any = await aiAPI.listModels()
    models.value = res?.items || res || []
  } catch (e) {
    console.error('Failed to load models:', e)
  } finally {
    loading.value = false
  }
}

async function refreshBindings() {
  loadingBindings.value = true
  try {
    const res: any = await aiAPI.listScenarios()
    bindings.value = res?.items || res || []
  } catch (e) {
    console.error('Failed to load bindings:', e)
  } finally {
    loadingBindings.value = false
  }
}

async function refreshUsage() {
  loadingUsage.value = true
  try {
    usage.value = await aiAPI.getUsage() || {}
  } catch (e) {
    console.error('Failed to load usage:', e)
  } finally {
    loadingUsage.value = false
  }
}

function addModel() {
  editingModel.value = {
    name: '', provider: 'zhipu', model_id: '', tier: 'fast',
    api_key: '', base_url: '', max_output_tokens: 4096,
    temperature: 0.7, rate_limit_rpm: 60, cost_per_1m: null,
    is_default: false,
  }
  modelDialogVisible.value = true
}

function editModel(row: any) {
  editingModel.value = { ...row, api_key: '' }
  modelDialogVisible.value = true
}

async function saveModel() {
  if (!editingModel.value.name || !editingModel.value.model_id) {
    ElMessage.warning('请填写模型名称和模型 ID')
    return
  }
  saving.value = true
  try {
    if (editingModel.value.id) {
      await aiAPI.updateModel(editingModel.value.id, editingModel.value)
      ElMessage.success('模型已更新')
    } else {
      await aiAPI.createModel(editingModel.value)
      ElMessage.success('模型已添加')
    }
    modelDialogVisible.value = false
    await refreshModels()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteModel(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除模型 ${row.name}？`, '提示', { type: 'warning' })
  } catch { return }
  try {
    await aiAPI.deleteModel(row.id)
    ElMessage.success('已删除')
    await refreshModels()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

function editBinding(row: any) {
  ElMessage.info('场景绑定编辑功能开发中')
}

onMounted(() => {
  refreshModels()
  refreshBindings()
  refreshUsage()
})
</script>

<style scoped>
.ai-model-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tier-desc {
  font-size: 12px;
  color: #909399;
}
.action-bar {
  margin-top: 20px;
  text-align: right;
}
</style>
