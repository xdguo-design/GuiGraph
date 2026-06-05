<template>
  <div class="change-create-page">
    <el-card>
      <template #header>新建变更申请</template>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
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
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">提交申请</el-button>
          <el-button @click="handleDraft">保存草稿</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { changeAPI } from '@/api/change'

const router = useRouter()
const formRef = ref()

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
  content: [{ required: true, message: '请输入变更内容', trigger: 'blur' }],
  change_reason: [{ required: true, message: '请选择变更原因', trigger: 'change' }],
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    // TODO: 实际调用 API
    // await changeAPI.create(form)
    ElMessage.success('提交成功')
    router.push('/changes')
  } catch (e) {
    // 错误已在拦截器处理
  }
}

function handleDraft() {
  ElMessage.info('草稿保存功能待实现')
}

function handleCancel() {
  router.back()
}
</script>

<style scoped>
.change-create-page {
  padding: 20px;
}
</style>
