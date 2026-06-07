<template>
  <div class="login-page">
    <!-- 左侧品牌展示区 -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="logo">
          <el-icon :size="48" color="#fff"><Histogram /></el-icon>
        </div>
        <h1 class="brand-name">GuiGraph</h1>
        <p class="brand-subtitle">版本变更管理系统</p>
        <ul class="brand-features">
          <li><el-icon><Check /></el-icon> 统一管理版本变更与升级</li>
          <li><el-icon><Check /></el-icon> 可视化依赖拓扑，洞察影响范围</li>
          <li><el-icon><Check /></el-icon> 自动化流程跟踪与发布回滚</li>
          <li><el-icon><Check /></el-icon> 多角色协作，权限精细可控</li>
        </ul>
      </div>
      <div class="brand-footer">© {{ year }} GuiGraph Team</div>
    </div>

    <!-- 右侧登录表单区 -->
    <div class="form-panel">
      <div class="form-box">
        <h2 class="form-title">欢迎回来</h2>
        <p class="form-tip">请选择登录方式继续</p>

        <el-tabs v-model="activeTab" class="login-tabs" stretch>
          <!-- 账号密码登录 -->
          <el-tab-pane name="password">
            <template #label>
              <span class="tab-label">
                <el-icon><UserFilled /></el-icon> 账号密码
              </span>
            </template>
            <el-form
              :model="form"
              :rules="rules"
              ref="formRef"
              size="large"
              @submit.prevent="handleLogin"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="form.username"
                  placeholder="用户名 / 邮箱 / 手机号"
                  prefix-icon="User"
                  clearable
                  autocomplete="username"
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="密码"
                  prefix-icon="Lock"
                  show-password
                  clearable
                  autocomplete="current-password"
                  @keyup.enter="handleLogin"
                />
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  :loading="loading"
                  class="submit-btn"
                  @click="handleLogin"
                >
                  登 录
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 微信扫码登录 -->
          <el-tab-pane name="wechat">
            <template #label>
              <span class="tab-label">
                <el-icon><ChatDotRound /></el-icon> 微信扫码
              </span>
            </template>
            <div class="qrcode-wrapper">
              <div v-if="qrLoading" class="qrcode-loading">
                <el-icon class="rotating" :size="32"><Loading /></el-icon>
                <p>正在生成二维码...</p>
              </div>
              <div v-else-if="qrDataUrl" class="qrcode-box">
                <div class="qrcode-frame">
                  <img :src="qrDataUrl" alt="微信登录二维码" />
                  <div class="qrcode-corners">
                    <span class="corner tl"></span>
                    <span class="corner tr"></span>
                    <span class="corner bl"></span>
                    <span class="corner br"></span>
                  </div>
                </div>
                <p class="qrcode-tip">
                  <el-icon><ChatDotRound /></el-icon>
                  打开 <b>微信</b> 扫一扫
                </p>
                <p class="qrcode-sub">扫描上方二维码即可登录</p>
                <el-button
                  link
                  type="primary"
                  :loading="qrLoading"
                  @click="loadWechatQRCode"
                >
                  二维码已失效？点击刷新
                </el-button>
              </div>
              <el-empty
                v-else
                description="微信登录尚未配置，请联系管理员或使用账号密码登录"
                :image-size="120"
              >
                <el-button type="primary" @click="loadWechatQRCode">重试</el-button>
              </el-empty>
            </div>
          </el-tab-pane>
        </el-tabs>

        <div class="form-footer">
          还没有账号？
          <el-link type="primary" :underline="false" @click="nav.to('/apply')">
            申请注册
          </el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import QRCode from 'qrcode'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'
import { userAPI } from '@/api/user'
import { msgSuccess, msgWarning, usePageNav } from '@/utils/pageTools'

const route = useRoute()
const authStore = useAuthStore()
const nav = usePageNav()

const activeTab = ref<'password' | 'wechat'>('password')
const formRef = ref()
const loading = ref(false)
const year = computed(() => new Date().getFullYear())

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2-50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, max: 50, message: '长度在 4-50 个字符', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (loading.value) return
  loading.value = true
  try {
    const data = await authAPI.login(form)
    authStore.setTokens(data.access_token, data.refresh_token)
    try {
      const payload = JSON.parse(atob(data.access_token.split('.')[1]))
      authStore.setUserInfo({
        id: payload.sub,
        username: payload.username,
        role: payload.role || 'editor',
      })
    } catch (e) {
      console.warn('解析 token 失败', e)
    }
    // 异步拉取用户资料（头像、昵称）以填充右上角
    userAPI.getProfile()
      .then((profile: any) => {
        authStore.setUserInfo({
          ...(authStore.userInfo || {}),
          nickname: profile?.nickname || authStore.userInfo?.nickname,
          avatar_url: profile?.avatar_url || authStore.userInfo?.avatar_url,
        })
      })
      .catch((e) => console.warn('拉取用户资料失败', e))
    msgSuccess('登录成功')
    const redirect = route.query.redirect as string | undefined
    nav.to(redirect || '/kanban')
  } catch (e) {
    console.error('登录失败', e)
  } finally {
    loading.value = false
  }
}

// ── 微信二维码 ──
const qrLoading = ref(false)
const qrDataUrl = ref<string>('')

async function loadWechatQRCode() {
  qrLoading.value = true
  qrDataUrl.value = ''
  try {
    const res = await authAPI.getWechatQRCode()
    const qrUrl: string = (res as any)?.qr_url || ''
    if (!qrUrl) {
      msgWarning('微信登录尚未配置，请联系管理员')
      return
    }
    qrDataUrl.value = await QRCode.toDataURL(qrUrl, {
      width: 220,
      margin: 1,
      color: { dark: '#1a5276', light: '#ffffff' },
    })
  } catch (e) {
    console.error('获取微信二维码失败', e)
  } finally {
    qrLoading.value = false
  }
}

// 切换到微信 tab 时按需加载
watch(activeTab, (val) => {
  if (val === 'wechat' && !qrDataUrl.value && !qrLoading.value) {
    loadWechatQRCode()
  }
})

onMounted(() => {
  // 已登录用户自动跳转
  if (authStore.isLoggedIn) {
    const redirect = route.query.redirect as string | undefined
    nav.to(redirect || '/kanban')
  }
})
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  background: #f5f7fa;
  overflow: hidden;
}

/* ── 左侧品牌区 ── */
.brand-panel {
  flex: 1;
  position: relative;
  background: linear-gradient(135deg, #1a5276 0%, #2980b9 50%, #6dd5fa 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 60px 80px;
  overflow: hidden;
}
.brand-panel::before,
.brand-panel::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  pointer-events: none;
}
.brand-panel::before {
  width: 420px;
  height: 420px;
  top: -120px;
  right: -120px;
}
.brand-panel::after {
  width: 260px;
  height: 260px;
  bottom: -80px;
  left: -60px;
  background: rgba(255, 255, 255, 0.05);
}
.brand-content {
  position: relative;
  z-index: 1;
  max-width: 460px;
}
.logo {
  width: 80px;
  height: 80px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}
.brand-name {
  font-size: 40px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: 1px;
}
.brand-subtitle {
  font-size: 16px;
  opacity: 0.85;
  margin: 0 0 48px;
}
.brand-features {
  list-style: none;
  padding: 0;
  margin: 0;
}
.brand-features li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  line-height: 1.8;
  opacity: 0.92;
}
.brand-features .el-icon {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  padding: 4px;
}
.brand-footer {
  position: relative;
  z-index: 1;
  font-size: 13px;
  opacity: 0.7;
}

/* ── 右侧表单区 ── */
.form-panel {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}
.form-box {
  width: 100%;
  max-width: 380px;
}
.form-title {
  font-size: 26px;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0 0 8px;
}
.form-tip {
  font-size: 14px;
  color: #909399;
  margin: 0 0 28px;
}

.login-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  padding: 0 16px;
}
.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  letter-spacing: 4px;
  background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(26, 82, 118, 0.25);
}
.submit-btn:hover {
  background: linear-gradient(135deg, #154360 0%, #21618c 100%);
}

/* ── 微信二维码 ── */
.qrcode-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0 4px;
  min-height: 280px;
  justify-content: center;
}
.qrcode-loading {
  text-align: center;
  color: #909399;
}
.qrcode-loading p {
  margin-top: 12px;
  font-size: 14px;
}
.rotating {
  animation: spin 1.2s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.qrcode-box {
  text-align: center;
  width: 100%;
}
.qrcode-frame {
  position: relative;
  display: inline-block;
  padding: 12px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}
.qrcode-frame img {
  display: block;
  width: 220px;
  height: 220px;
}
.qrcode-corners .corner {
  position: absolute;
  width: 18px;
  height: 18px;
  border: 3px solid #1a5276;
}
.qrcode-corners .tl {
  top: 4px;
  left: 4px;
  border-right: none;
  border-bottom: none;
}
.qrcode-corners .tr {
  top: 4px;
  right: 4px;
  border-left: none;
  border-bottom: none;
}
.qrcode-corners .bl {
  bottom: 4px;
  left: 4px;
  border-right: none;
  border-top: none;
}
.qrcode-corners .br {
  bottom: 4px;
  right: 4px;
  border-left: none;
  border-top: none;
}
.qrcode-tip {
  margin: 20px 0 4px;
  font-size: 15px;
  color: #303133;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.qrcode-tip .el-icon {
  color: #07c160;
  font-size: 18px;
}
.qrcode-sub {
  font-size: 13px;
  color: #909399;
  margin: 0 0 8px;
}

.form-footer {
  text-align: center;
  font-size: 14px;
  color: #606266;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* ── 响应式 ── */
@media (max-width: 960px) {
  .brand-panel {
    display: none;
  }
  .form-panel {
    width: 100%;
  }
}
</style>
