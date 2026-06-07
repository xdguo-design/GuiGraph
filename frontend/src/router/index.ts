import { createRouter, createWebHistory, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/login/index.vue'),
    meta: { title: '登录', layout: 'blank' },
  },
  {
    path: '/apply',
    name: 'Apply',
    component: () => import('@/pages/apply/index.vue'),
    meta: { title: '注册申请', layout: 'blank' },
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/pages/error/NotFound.vue'),
    meta: { title: '页面未找到' },
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/pages/error/Forbidden.vue'),
    meta: { title: '无权访问' },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/DefaultLayout.vue'),
    redirect: '/kanban',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/dashboard/index.vue'),
        meta: { title: '仪表盘', requiresAuth: true, icon: 'Odometer' },
      },
      {
        path: 'changes',
        name: 'ChangeList',
        component: () => import('@/pages/change/ChangeList.vue'),
        meta: { title: '变更管理', requiresAuth: true, icon: 'Document' },
      },
      {
        path: 'changes/create',
        name: 'ChangeCreate',
        component: () => import('@/pages/change/ChangeCreate.vue'),
        meta: { title: '新建变更', requiresAuth: true, requiresRole: ['admin', 'editor'] },
      },
      {
        path: 'changes/:id',
        name: 'ChangeDetail',
        component: () => import('@/pages/change/ChangeDetail.vue'),
        meta: { title: '变更详情', requiresAuth: true },
      },
      {
        path: 'changes/:id/edit',
        name: 'ChangeEdit',
        component: () => import('@/pages/change/ChangeCreate.vue'),
        meta: { title: '编辑变更', requiresAuth: true, requiresRole: ['admin', 'editor'] },
      },
      {
        path: 'org',
        name: 'Organization',
        component: () => import('@/pages/organization/index.vue'),
        meta: { title: '组织架构', requiresAuth: true, requiresRole: ['admin'] },
      },
      {
        path: 'user',
        name: 'UserCenter',
        component: () => import('@/pages/user/UserCenter.vue'),
        meta: { title: '用户中心', requiresAuth: true },
      },
      {
        path: 'git',
        name: 'GitList',
        component: () => import('@/pages/git/RepoList.vue'),
        meta: { title: 'Git 仓库', requiresAuth: true },
      },
      {
        path: 'jenkins',
        name: 'JenkinsList',
        component: () => import('@/pages/jenkins/InstanceList.vue'),
        meta: { title: 'Jenkins', requiresAuth: true, requiresRole: ['admin'] },
      },
      {
        path: 'version-merge',
        name: 'VersionMerge',
        component: () => import('@/pages/version/VersionMerge.vue'),
        meta: { title: '版本合并', requiresAuth: true },
      },
      {
        path: 'upgrades',
        name: 'UpgradeList',
        component: () => import('@/pages/upgrade/UpgradeList.vue'),
        meta: { title: '升级日志', requiresAuth: true },
      },
      {
        path: 'upgrades/:id',
        name: 'UpgradeDetail',
        component: () => import('@/pages/upgrade/UpgradeDetail.vue'),
        meta: { title: '升级详情', requiresAuth: true },
      },
      {
        path: 'applications',
        name: 'Applications',
        component: () => import('@/pages/admin/Applications.vue'),
        meta: { title: '账号审核', requiresAuth: true, requiresRole: ['admin'] },
      },
      {
        path: 'demo-data',
        name: 'DemoData',
        component: () => import('@/pages/admin/DemoData.vue'),
        meta: { title: '演示数据', requiresAuth: true, requiresRole: ['admin'] },
      },
      {
        path: 'kanban',
        name: 'Kanban',
        component: () => import('@/pages/kanban/index.vue'),
        meta: { title: '看板', requiresAuth: true },
      },
    ],
  },
  // 兜底路由
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由白名单（无需登录）
const WHITE_LIST = ['/login', '/apply', '/404', '/403']

// 默认首页
const HOME_PATH = '/kanban'

/**
 * 路由守卫
 * 1. 设置页面标题
 * 2. 检查登录状态
 * 3. 检查角色权限
 * 4. 已登录用户访问登录页时跳转首页
 */
router.beforeEach((to: RouteLocationNormalized, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || 'GuiGraph'} - 版本变更管理系统`

  const authStore = useAuthStore()
  const token = authStore.token

  // 1. 白名单直接放行
  if (WHITE_LIST.includes(to.path)) {
    // 已登录用户访问登录页：跳转到首页
    if (to.path === '/login' && token) {
      return next({ path: HOME_PATH })
    }
    return next()
  }

  // 2. 需要登录的页面：检查 token
  if (to.meta.requiresAuth && !token) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // 3. 检查角色权限
  const requiredRoles = to.meta.requiresRole as string[] | undefined
  if (requiredRoles && requiredRoles.length > 0) {
    const userRole = authStore.role
    // 把 system_admin 视为超集，匹配 requiresRole: ['admin'] 也能通过
    const effectiveRole = userRole === 'system_admin' ? 'admin' : userRole
    if (!requiredRoles.includes(effectiveRole) && userRole !== 'system_admin') {
      return next({ path: '/403' })
    }
  }

  next()
})

export default router
