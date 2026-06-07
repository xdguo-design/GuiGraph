<template>
  <div class="apply-page">
    <div class="apply-box">
      <h1>GuiGraph</h1>
      <h2>注册申请</h2>
      <p class="hint">提交后请等待管理员审核，审核通过后您将获得登录权限。</p>

      <el-form
        v-if="!submitted"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="100px"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password clearable placeholder="4-50 位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" show-password clearable placeholder="再次输入密码" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="选填" clearable />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="选填，用于通知审核结果" clearable />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="选填" clearable />
        </el-form-item>
        <el-form-item label="申请原因" prop="reason">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="3"
            placeholder="请简要说明您的角色、所属团队/部门及使用场景"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleSubmit">
            提交申请
          </el-button>
        </el-form-item>
      </el-form>

      <el-result v-else icon="success" title="申请已提交" sub-title="请耐心等待管理员审核，审核通过后会通过邮箱/站内信通知您。">
        <template #extra>
          <el-button type="primary" @click="nav.to('/login')">返回登录</el-button>
        </template>
      </el-result>

      <p class="footer">
        <el-link type="primary" :underline="false" @click="nav.to('/login')">已有账号？返回登录</el-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { applicationAPI } from '@/api/application'
import { msgSuccess, msgError, usePageNav } from '@/utils/pageTools'

const nav = usePageNav()
const formRef = ref()
const loading = ref(false)
const submitted = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  nickname: '',
  email: '',
  phone: '',
  reason: '',
})

const validateConfirm = (_: any, value: string, cb: any) => {
  if (value !== form.password) cb(new Error('两次输入的密码不一致'))
  else cb()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2-50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_.-]+$/, message: '只能包含字母、数字、下划线、点、连字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, max: 50, message: '长度在 4-50 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
  email: [
    { type: 'email' as const, message: '请输入正确的邮箱', trigger: 'blur' },
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  reason: [
    { max: 500, message: '不能超过 500 个字符', trigger: 'blur' },
  ],
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await applicationAPI.submit({
      username: form.username,
      password: form.password,
      nickname: form.nickname,
      email: form.email,
      phone: form.phone,
      reason: form.reason,
    })
    submitted.value = true
    msgSuccess('申请已提交')
  } catch {
    // 错误由拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.apply-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%);
  padding: 24px;
}
.apply-box {
  width: 560px;
  max-width: 100%;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
.apply-box h1 {
  text-align: center;
  color: #1a5276;
  margin: 0 0 8px;
}
.apply-box h2 {
  text-align: center;
  color: #7f8c8d;
  font-weight: normal;
  font-size: 14px;
  margin: 0 0 16px;
}
.hint {
  background: #ecf5ff;
  border-left: 3px solid #409eff;
  color: #5a6e7a;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  margin: 0 0 24px;
}
.footer {
  text-align: center;
  margin: 16px 0 0;
  color: #7f8c8d;
  font-size: 13px;
}
</style>
