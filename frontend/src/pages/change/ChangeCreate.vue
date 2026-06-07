<template>
  <div class="change-create-page" v-loading="loading">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑变更申请' : '新建变更申请' }}</span>
          <el-tag v-if="reportDate" type="info" effect="plain">
            <el-icon><Calendar /></el-icon>
            为 {{ reportDate }} 上报
          </el-tag>
        </div>
      </template>
      <el-alert
        v-if="isEdit && change && change.status !== 'draft'"
        title="提示"
        type="warning"
        :description="`当前变更状态为「${statusTextMap[change.status]}」，不允许编辑`"
        show-icon
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" :disabled="isEdit && change && change.status !== 'draft'">
        <el-form-item label="变更类型" required>
          <el-select v-model="form.change_type" placeholder="请选择">
            <el-option label="DB 变更" value="db" />
            <el-option label="API 变更" value="api" />
            <el-option label="配置变更" value="config" />
            <el-option label="代码变更" value="code" />
            <el-option label="基础设施" value="infra" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="请输入变更内容描述（至少 10 字符）"
          />
        </el-form-item>
        <el-form-item label="变更原因" required>
          <el-select v-model="form.change_reason" placeholder="请选择">
            <el-option label="需求变更" value="requirement" />
            <el-option label="BUG 修复" value="bug_fix" />
            <el-option label="性能优化" value="performance" />
            <el-option label="合规要求" value="compliance" />
            <el-option label="技术债务" value="tech_debt" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更原因补充">
          <el-input
            v-model="form.change_reason_detail"
            type="textarea"
            :rows="3"
            placeholder="补充描述"
          />
        </el-form-item>
        <el-form-item label="影响范围">
          <el-input
            v-model="form.effect_scope"
            type="textarea"
            :rows="3"
            placeholder="影响范围描述"
          />
        </el-form-item>
        <el-form-item label="关联需求号">
          <el-input v-model="form.related_requirement_no" placeholder="如 REQ-2026-03-001" />
        </el-form-item>
        <el-form-item label="关联功能点">
          <el-select v-model="form.func_point_ids" multiple placeholder="选择功能点">
            <el-option label="医保结算模块" value="func_001" />
            <el-option label="支付对账模块" value="func_002" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更图片">
          <el-upload
            v-model:file-list="imageList"
            list-type="picture-card"
            :http-request="handleCustomUpload"
            :before-upload="beforeImageUpload"
            :on-preview="handlePicturePreview"
            :on-remove="handleImageRemove"
            multiple
            :limit="9"
            accept="image/*"
            :disabled="uploading"
          >
            <el-icon v-if="!uploading"><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">
                支持 JPG/PNG/GIF/WebP，单张不超过 20MB，最多 9 张
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="附件文档">
          <el-upload
            v-model:file-list="fileList"
            :http-request="handleCustomUpload"
            :before-upload="beforeDocUpload"
            :on-remove="handleFileRemove"
            multiple
            :limit="5"
          >
            <el-button :icon="Upload" :disabled="uploading">点击上传文档</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF/Word/Excel/压缩包/TXT，单个不超过 20MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :disabled="isEdit && change && change.status !== 'draft'">
            {{ isEdit ? '保存修改' : '提交申请' }}
          </el-button>
          <el-button @click="handleDraft" v-if="!isEdit">保存草稿</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="previewVisible" width="60%" :show-close="true" align-center>
      <img :src="previewImageUrl" alt="预览" class="preview-img" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type UploadFile, type UploadRequestOptions, type UploadRawFile, type UploadUserFile } from 'element-plus'
import { Calendar, Plus, Upload } from '@element-plus/icons-vue'
import { changeAPI } from '@/api/change'
import { attachmentAPI } from '@/api/attachment'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const change = ref<any>(null)

// 判断是创建还是编辑模式
const isEdit = computed(() => !!route.params.id)
const changeId = computed(() => route.params.id as string)
// 从看板带过来的日期（仅作视觉提示，实际 created_at 由后端生成）
const reportDate = computed(() => (route.query.date as string) || '')

const form = reactive({
  change_type: '',
  content: '',
  change_reason: '',
  change_reason_detail: '',
  effect_scope: '',
  related_requirement_no: '',
  func_point_ids: [],
})

const rules = {
  change_type: [{ required: true, message: '请选择变更类型', trigger: 'change' }],
  content: [
    { required: true, message: '请输入变更内容', trigger: 'blur' },
    { min: 10, message: '变更内容至少 10 字符', trigger: 'blur' },
  ],
  change_reason: [{ required: true, message: '请选择变更原因', trigger: 'change' }],
}

const statusTextMap: Record<string, string> = {
  draft: '草稿',
  approved: '已批准',
  rejected: '已驳回',
  released: '已发布',
  rolled_back: '已回滚',
}

// ── 上传（图片 + 文档） ──
const MAX_SIZE = 20 * 1024 * 1024
const ALLOWED_IMAGE_MIME = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
const ALLOWED_DOC_EXT = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'md', 'zip', 'rar']

const uploading = ref(false)
const imageList = ref<UploadUserFile[]>([])
const fileList = ref<UploadUserFile[]>([])

// 图片预览
const previewVisible = ref(false)
const previewImageUrl = ref('')

function beforeImageUpload(file: UploadRawFile): boolean {
  if (!ALLOWED_IMAGE_MIME.includes(file.type)) {
    ElMessage.error('仅支持 JPG/PNG/GIF/WebP 格式')
    return false
  }
  if (file.size > MAX_SIZE) {
    ElMessage.error('单张图片不能超过 20MB')
    return false
  }
  return true
}

function beforeDocUpload(file: UploadRawFile): boolean {
  if (file.size > MAX_SIZE) {
    ElMessage.error('单个文档不能超过 20MB')
    return false
  }
  const ext = (file.name.split('.').pop() || '').toLowerCase()
  if (!ALLOWED_DOC_EXT.includes(ext)) {
    ElMessage.error(`不支持的文档格式: .${ext}`)
    return false
  }
  return true
}

async function handleCustomUpload(options: UploadRequestOptions) {
  uploading.value = true
  try {
    const res: any = await attachmentAPI.upload(options.file as File)
    // 把返回的 url/file_id 写回到 file 对象的 url 属性（el-upload 列表展示需要）
    if (options.file && (options.file as any).uid) {
      const item = [...imageList.value, ...fileList.value].find(
        (f) => f.uid === (options.file as any).uid,
      )
      if (item) {
        item.url = res.file_url
        ;(item as any).fileId = res.file_id
      }
    }
    ElMessage.success(`${options.file.name} 上传成功`)
  } catch (err: any) {
    // 业务错误已由拦截器提示；从列表中移除
    const item = [...imageList.value, ...fileList.value].find(
      (f) => f.uid === (options.file as any).uid,
    )
    if (item) {
      if (imageList.value.includes(item)) imageList.value.splice(imageList.value.indexOf(item), 1)
      if (fileList.value.includes(item)) fileList.value.splice(fileList.value.indexOf(item), 1)
    }
  } finally {
    uploading.value = false
  }
}

async function handleImageRemove(file: UploadFile) {
  const fileId = (file as any).fileId
  if (fileId) {
    try {
      await attachmentAPI.delete(fileId)
    } catch (e) {
      // 忽略：文件可能已被清理
    }
  }
}

async function handleFileRemove(file: UploadFile) {
  const fileId = (file as any).fileId
  if (fileId) {
    try {
      await attachmentAPI.delete(fileId)
    } catch (e) {
      // 忽略
    }
  }
}

function handlePicturePreview(file: UploadFile) {
  previewImageUrl.value = file.url || ''
  previewVisible.value = true
}

// 加载变更详情（编辑模式）
async function loadChange() {
  if (!isEdit.value) return

  loading.value = true
  try {
    const response = await changeAPI.get(changeId.value)
    change.value = response.data

    // 填充表单
    Object.assign(form, {
      change_type: change.value.type,
      content: change.value.content,
      change_reason: change.value.reason,
      change_reason_detail: change.value.change_reason_detail || '',
      effect_scope: change.value.impact || '',
      related_requirement_no: change.value.requirement_id || '',
      func_point_ids: change.value.func_point_ids || [],
    })
  } catch (error) {
    ElMessage.error('加载变更详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    // 收集已上传的图片 URL
    const img_list = imageList.value
      .filter((f) => f.url)
      .map((f) => f.url as string)
    // 收集已上传的文档 URL
    const file_ref = fileList.value
      .filter((f) => f.url)
      .map((f) => f.url as string)
    const payload = { ...form, img_list, file_ref }

    if (isEdit.value) {
      await changeAPI.update(changeId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await changeAPI.create(payload)
      ElMessage.success('提交成功')
    }
    router.push('/changes')
  } catch (e) {
    // 错误已在拦截器处理
  } finally {
    loading.value = false
  }
}

function handleDraft() {
  ElMessage.info('草稿保存功能待实现')
}

function handleCancel() {
  router.back()
}

onMounted(() => {
  loadChange()
})
</script>

<style scoped>
.change-create-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header .el-icon {
  vertical-align: -2px;
  margin-right: 4px;
}
.preview-img {
  width: 100%;
  display: block;
}
:deep(.el-upload__tip) {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 92px;
  height: 92px;
}
</style>
