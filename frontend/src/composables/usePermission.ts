import { useAuthStore } from '@/stores/auth'

/**
 * 权限矩阵（与后端 permissions.py 保持一致）
 * 6 角色 × 9 资源的细粒度操作权限
 */
export const PERMISSION_MATRIX: Record<string, Record<string, string[]>> = {
  system_admin: {
    org: ['create', 'read', 'update', 'delete', 'manage_members'],
    change: ['create', 'read', 'update', 'delete', 'approve'],
    git: ['add_repo', 'auth_user', 'view_branches', 'merge', 'create_branch', 'delete_branch'],
    jenkins: ['configure', 'trigger', 'stop', 'view_log'],
    ai: ['search', 'generate', 'analyze', 'manage_model', 'manage_skill', 'manage_mcp'],
    audit: ['view'],
    upgrade: ['view', 'rollback', 'export'],
    minio: ['manage'],
    mcp: ['register', 'configure', 'test', 'delete', 'view_stats'],
  },
  dept_admin: {
    org: ['create', 'read', 'update', 'manage_members'],
    change: ['create', 'read', 'update', 'approve'],
    git: ['add_repo', 'auth_user', 'view_branches', 'merge'],
    jenkins: ['trigger', 'stop', 'view_log'],
    ai: ['search', 'generate', 'analyze'],
    audit: ['view'],
    upgrade: ['view', 'export'],
    mcp: ['view_stats'],
  },
  team_admin: {
    org: ['create', 'read', 'update', 'manage_members'],
    change: ['create', 'read', 'update', 'approve'],
    git: ['add_repo', 'auth_user', 'view_branches', 'merge'],
    jenkins: ['trigger', 'stop', 'view_log'],
    ai: ['search', 'generate', 'analyze'],
    upgrade: ['view'],
  },
  editor: {
    change: ['create', 'read', 'update'],
    git: ['view_branches', 'merge'],
    jenkins: ['trigger', 'view_log'],
    ai: ['search', 'generate', 'analyze'],
    upgrade: ['view'],
  },
  viewer: {
    change: ['read'],
    git: ['view_branches'],
    jenkins: ['view_log'],
    ai: ['search', 'generate'],
    upgrade: ['view'],
  },
  auditor: {
    change: ['read'],
    git: ['view_branches'],
    jenkins: ['view_log'],
    ai: ['search'],
    audit: ['view', 'export'],
    upgrade: ['view', 'export'],
    mcp: ['view_stats'],
  },
}

/** 角色显示名称 */
export const ROLE_LABELS: Record<string, string> = {
  system_admin: '系统管理员',
  dept_admin: '部门管理员',
  team_admin: '团队管理员',
  editor: '编辑者',
  viewer: '查看者',
  auditor: '审计员',
}

/** 所有资源列表（从矩阵中提取） */
export const ALL_RESOURCES = Array.from(
  new Set(Object.values(PERMISSION_MATRIX).flatMap((perms) => Object.keys(perms)))
).sort()

/** 系统管理员角色标识列表 */
const ADMIN_ROLES = ['system_admin', 'dept_admin', 'team_admin']

/**
 * 检查角色对某资源是否有任一操作权限（资源级）
 * @param role 用户角色
 * @param resource 权限资源名（如 'change', 'git', 'org'）
 */
export function checkResourceAccess(role: string, resource: string): boolean {
  if (role === 'system_admin') return true
  const perms = PERMISSION_MATRIX[role]?.[resource]
  return !!perms && perms.length > 0
}

/**
 * 检查角色是否在允许的角色列表中（角色级）
 * @param role 用户角色
 * @param allowedRoles 允许的角色数组
 */
export function checkRoleAccess(role: string, allowedRoles: string[]): boolean {
  if (role === 'system_admin') return true
  return allowedRoles.includes(role)
}

/**
 * Vue composable：权限检查
 * 从 auth store 自动获取当前用户角色
 */
export function usePermission() {
  const authStore = useAuthStore()

  const role = authStore.role

  /** 当前角色对某资源是否有访问权限 */
  function hasResourceAccess(resource: string): boolean {
    return checkResourceAccess(role, resource)
  }

  /** 当前角色是否在允许列表中 */
  function hasRoleAccess(allowedRoles: string[]): boolean {
    return checkRoleAccess(role, allowedRoles)
  }

  /** 是否是管理员角色 */
  const isAdmin = ADMIN_ROLES.includes(role)

  return {
    role,
    isAdmin,
    hasResourceAccess,
    hasRoleAccess,
  }
}