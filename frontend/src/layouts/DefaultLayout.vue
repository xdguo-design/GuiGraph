<template>
  <div class="app-layout">
    <el-container>
      <el-aside :width="sidebarCollapsed ? '64px' : '220px'">
        <div class="sidebar-header">
          <el-icon v-if="!sidebarCollapsed"><Monitor /></el-icon>
          <span v-if="!sidebarCollapsed">GuiGraph</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          :collapse="sidebarCollapsed"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/changes">
            <el-icon><Document /></el-icon>
            <span>变更管理</span>
          </el-menu-item>
          <el-menu-item index="/org">
            <el-icon><OfficeBuilding /></el-icon>
            <span>组织架构</span>
          </el-menu-item>
          <el-menu-item index="/git">
            <el-icon><GitBranch /></el-icon>
            <span>Git 仓库</span>
          </el-menu-item>
          <el-menu-item index="/jenkins">
            <el-icon><Cpu /></el-icon>
            <span>Jenkins</span>
          </el-menu-item>
          <el-menu-item index="/user">
            <el-icon><User /></el-icon>
            <span>用户中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-content">
            <el-button icon="Fold" @click="toggleSidebar" />
            <div class="header-right">
              <el-dropdown>
                <span class="user-info">
                  <el-avatar :size="32" />
                  {{ userInfo?.username || '用户' }}
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const { sidebarCollapsed, toggleSidebar } = appStore
const { userInfo, logout } = authStore

const activeMenu = computed(() => route.path)

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.el-container {
  height: 100%;
}
.el-aside {
  background: #001529;
  transition: width 0.3s;
}
.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: bold;
  font-size: 16px;
}
.el-header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.el-main {
  background: #f0f2f5;
}
</style>
