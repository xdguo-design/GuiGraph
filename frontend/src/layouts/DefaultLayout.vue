<template>
  <div class="app-layout">
    <el-container>
      <!-- 侧边栏：与登录页品牌区同款渐变 -->
      <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="brand-aside">
        <div class="sidebar-header">
          <div class="logo-box">
            <el-icon :size="22" color="#fff"><Histogram /></el-icon>
          </div>
          <span v-if="!sidebarCollapsed" class="brand-name">GuiGraph</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          :collapse="sidebarCollapsed"
          class="brand-menu"
          router
        >
          <el-menu-item index="/kanban">
            <el-icon><DataLine /></el-icon>
            <template #title>个人/团队看板</template>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <template #title>仪表盘</template>
          </el-menu-item>
          <el-menu-item index="/changes">
            <el-icon><Document /></el-icon>
            <template #title>变更管理</template>
          </el-menu-item>
          <el-menu-item index="/org">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>组织架构</template>
          </el-menu-item>
          <el-menu-item index="/git">
            <el-icon><Link /></el-icon>
            <template #title>Git 仓库</template>
          </el-menu-item>
          <el-menu-item index="/jenkins">
            <el-icon><Cpu /></el-icon>
            <template #title>Jenkins</template>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="/applications">
            <el-icon><UserFilled /></el-icon>
            <template #title>账号审核</template>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="/demo-data">
            <el-icon><MagicStick /></el-icon>
            <template #title>演示数据</template>
          </el-menu-item>
        </el-menu>
        <div v-if="!sidebarCollapsed" class="sidebar-footer">© {{ year }} GuiGraph</div>
      </el-aside>

      <el-container>
        <!-- 顶栏 -->
        <el-header class="brand-header">
          <div class="header-content">
            <el-button
              :icon="sidebarCollapsed ? 'Expand' : 'Fold'"
              class="collapse-btn"
              @click="toggleSidebar"
            />
            <div class="header-right">
              <el-dropdown trigger="click" @command="handleCommand">
                <span class="user-info">
                  <el-avatar
                    :size="34"
                    :src="userInfo?.avatar_url || ''"
                    class="user-avatar"
                  >
                    {{ avatarInitial }}
                  </el-avatar>
                  <span class="username-text">{{ userInfo?.nickname || userInfo?.username || '用户' }}</span>
                  <el-icon class="arrow"><CaretBottom /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon> 用户中心
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon> 退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>

        <el-main class="brand-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { userAPI } from '@/api/user'
// 显式导入图标，避免 Vue 组件解析警告
import {
  Histogram,
  House,
  Document,
  DataLine,
  OfficeBuilding,
  Link,
  Cpu,
  User,
  UserFilled,
  MagicStick,
  CaretBottom,
  SwitchButton,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const { sidebarCollapsed, toggleSidebar, theme, setTheme } = appStore
const { userInfo, logout, role, setUserInfo } = authStore

const isAdmin = computed(() => role.value === 'admin' || role.value === 'system_admin')
const activeMenu = computed(() => route.path)
const year = computed(() => new Date().getFullYear())

// 主题显示
const THEME_LABELS: Record<string, string> = {
  business: '商务蓝',
  tech: '科技黑',
  minimal: '极简白',
}
const themeLabel = computed(() => THEME_LABELS[theme.value] || '商务蓝')

function handleThemeChange(name: string) {
  if (name === 'business' || name === 'tech' || name === 'minimal') {
    setTheme(name)
  }
}

// 头像文字回退：取昵称/用户名的首字符
const avatarInitial = computed(() => {
  const src = userInfo.value?.nickname || userInfo.value?.username || 'U'
  return src.charAt(0).toUpperCase()
})

// 进入页面时若缺少头像/昵称，主动拉取一次资料
onMounted(async () => {
  if (!authStore.token) return
  if (userInfo.value?.avatar_url && userInfo.value?.nickname) return
  try {
    const profile: any = await userAPI.getProfile()
    setUserInfo({
      ...(userInfo.value || {}),
      id: profile.id,
      username: profile.username,
      nickname: profile.nickname,
      avatar_url: profile.avatar_url,
      role: userInfo.value?.role,
    })
  } catch (e) {
    console.warn('拉取用户资料失败', e)
  }
})

function handleCommand(command: string) {
  if (command === 'profile') {
    router.push('/user')
  } else if (command === 'logout') {
    logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.el-container {
  height: 100%;
}

/* ── 侧边栏：与登录页同款渐变 ── */
.brand-aside {
  position: relative;
  background: linear-gradient(180deg, #1a5276 0%, #2980b9 60%, #6dd5fa 130%);
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.brand-aside::before,
.brand-aside::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  pointer-events: none;
}
.brand-aside::before {
  width: 260px;
  height: 260px;
  top: -80px;
  right: -100px;
}
.brand-aside::after {
  width: 180px;
  height: 180px;
  bottom: -60px;
  left: -50px;
  background: rgba(255, 255, 255, 0.05);
}
.sidebar-header {
  position: relative;
  z-index: 1;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  color: #fff;
  font-weight: 600;
  font-size: 17px;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.logo-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(6px);
}
.brand-name {
  white-space: nowrap;
}
.brand-menu {
  position: relative;
  z-index: 1;
  flex: 1;
  background: transparent;
  border-right: none;
}
.brand-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.85) !important;
  background: transparent !important;
  margin: 4px 10px;
  border-radius: 8px;
  height: 44px;
  line-height: 44px;
}
.brand-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #fff !important;
}
.brand-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.22) !important;
  color: #fff !important;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.brand-menu :deep(.el-menu-item .el-icon) {
  color: inherit !important;
}
.sidebar-footer {
  position: relative;
  z-index: 1;
  padding: 12px 20px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* ── 顶栏 ── */
.brand-header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 1px 0 rgba(26, 82, 118, 0.04);
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}
.collapse-btn {
  border: none;
  background: transparent;
}
.collapse-btn:hover {
  background: #f5f7fa;
  color: #1a5276;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ── 主题切换器 ── */
.theme-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 18px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 13px;
  color: #303133;
}
.theme-switcher:hover {
  background: #f5f7fa;
}
.theme-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.08);
}
.theme-dot.business {
  background: linear-gradient(135deg, #1a5276, #2980b9);
}
.theme-dot.tech {
  background: linear-gradient(135deg, #0a0a0f, #00d4ff);
}
.theme-dot.minimal {
  background: linear-gradient(135deg, #ffffff, #dfe6e9);
}
.theme-name {
  font-weight: 500;
  color: #303133;
}
.theme-switcher .arrow {
  font-size: 11px;
  color: #909399;
}
/* 主题色点（下拉项用） */
:deep(.el-dropdown-menu .dot) {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
}
:deep(.el-dropdown-menu .dot.business) {
  background: linear-gradient(135deg, #1a5276, #2980b9);
}
:deep(.el-dropdown-menu .dot.tech) {
  background: linear-gradient(135deg, #0a0a0f, #00d4ff);
}
:deep(.el-dropdown-menu .dot.minimal) {
  background: linear-gradient(135deg, #ffffff, #dfe6e9);
  border: 1px solid #dfe6e9;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 4px;
  border-radius: 24px;
  cursor: pointer;
  transition: background 0.2s;
}
.user-info:hover {
  background: #f5f7fa;
}
.user-avatar {
  background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%);
  color: #fff;
  font-weight: 600;
}
.username-text {
  font-size: 14px;
  color: #303133;
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.arrow {
  font-size: 12px;
  color: #909399;
}

/* ── 主内容区 ── */
.brand-main {
  background: #f5f7fa;
  padding: 0 20px 20px;
  overflow: auto;
  /* 隐藏滚动条但保留滚动能力，避免外侧出现明显的滚动条 */
  scrollbar-width: thin;
  scrollbar-color: rgba(144, 147, 153, 0.3) transparent;
}
.brand-main::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.brand-main::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 3px;
  transition: background 0.2s;
}
.brand-main:hover::-webkit-scrollbar-thumb,
.brand-main:focus-within::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.4);
}
.brand-main::-webkit-scrollbar-track {
  background: transparent;
}
</style>
