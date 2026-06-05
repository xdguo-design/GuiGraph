import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/login/index.vue'),
    meta: { title: '登录', layout: 'blank' },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/DefaultLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/dashboard/index.vue'),
        meta: { title: '仪表盘', requiresAuth: true },
      },
      {
        path: 'changes',
        name: 'ChangeList',
        component: () => import('@/pages/change/ChangeList.vue'),
        meta: { title: '变更管理', requiresAuth: true },
      },
      {
        path: 'changes/create',
        name: 'ChangeCreate',
        component: () => import('@/pages/change/ChangeCreate.vue'),
        meta: { title: '新建变更', requiresAuth: true },
      },
      {
        path: 'changes/:id',
        name: 'ChangeDetail',
        component: () => import('@/pages/change/ChangeDetail.vue'),
        meta: { title: '变更详情', requiresAuth: true },
      },
      {
        path: 'org',
        name: 'Organization',
        component: () => import('@/pages/organization/index.vue'),
        meta: { title: '组织架构', requiresAuth: true },
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
        meta: { title: 'Jenkins', requiresAuth: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'GuiGraph'} - 版本变更管理系统`
  
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
