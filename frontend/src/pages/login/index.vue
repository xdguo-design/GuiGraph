<template>
  <div class="login-page">
    <div class="login-box">
      <h1>GuiGraph</h1>
      <h2>版本变更管理系统</h2>
      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名/邮箱/手机"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
            <el-form-item>
          <el-button size="large" style="width: 100%" @click="handleWechatLogin">
            <el-icon><Position /></el-icon> 微信扫码登录
          </el-button>
        </el-form-item>
      </el-form>
      <p class="hint">还没有账号？联系管理员开通</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const data = await authAPI.login(form)
    authStore.setToken(data.access_token)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (e) {
    // 错误已在拦截器处理
  } finally {
    loading.value = false
  }
}

function handleWechatLogin() {
  ElMessage.info('微信登录功能待配置')
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%);
}
.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
.login-box h1 {
  text-align: center;
  color: #1a5276;
  margin-bottom: 8px;
}
.login-box h2 {
  text-align: center;
  color: #7f8c8d;
  font-weight: normal;
  font-size: 14px;
  margin-bottom: 32px;
}
.hint {
  text-align: center;
  color: #7f8c8d;
  font-size: 12px;
  margin-top: 16px;
}
</style>
