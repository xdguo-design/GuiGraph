import request from './request'

/** 组织架构 API */
export const orgAPI = {
  /** 获取组织树（公司→部门→团队→成员） */
  tree: () => request.get('/org/tree'),
  /** 获取所有公司（含部门与团队） */
  companies: () => request.get('/org/companies'),
  /** 创建公司 */
  createCompany: (data: { name: string; code: string }) =>
    request.post('/org/companies', data),
  /** 更新公司 */
  updateCompany: (id: string, data: { name?: string; code?: string }) =>
    request.put(`/org/companies/${id}`, data),
  /** 删除公司 */
  deleteCompany: (id: string) => request.delete(`/org/companies/${id}`),

  /** 创建部门 */
  createDepartment: (data: { name: string; code: string; company_id: string; parent_id?: string }) =>
    request.post('/org/departments', data),
  /** 更新部门 */
  updateDepartment: (id: string, data: { name?: string; code?: string }) =>
    request.put(`/org/departments/${id}`, data),
  /** 删除部门 */
  deleteDepartment: (id: string) => request.delete(`/org/departments/${id}`),

  /** 团队列表（所有团队） */
  listTeams: () => request.get('/org/teams'),
  /** 当前用户可访问的团队（演示/真实场景均可用） */
  myTeams: () => request.get('/demo/kanban/teams'),
  /** 创建团队 */
  createTeam: (data: { name: string; code: string; department_id: string; description?: string }) =>
    request.post('/org/teams', data),
  /** 更新团队 */
  updateTeam: (id: string, data: { name?: string; code?: string; description?: string }) =>
    request.put(`/org/teams/${id}`, data),
  /** 删除团队 */
  deleteTeam: (id: string) => request.delete(`/org/teams/${id}`),

  /** 团队成员 */
  teamMembers: (teamId: string | number) => request.get(`/org/teams/${teamId}/members`),
  addTeamMember: (teamId: string | number, data: { user_id: string | number; role?: string }) =>
    request.post(`/org/teams/${teamId}/members`, data),
  updateTeamMember: (teamId: string | number, userId: string | number, data: { role: string }) =>
    request.put(`/org/teams/${teamId}/members/${userId}`, data),
  removeTeamMember: (teamId: string | number, userId: string | number) =>
    request.delete(`/org/teams/${teamId}/members/${userId}`),

  /** 上传组织结构（JSON） */
  upload: (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return request.post('/org/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

/** 用户管理 API（管理员） */
export const userAdminAPI = {
  list: () => request.get('/user-admin/list'),
  updateStatus: (userId: string | number, status: 'active' | 'pending' | 'disabled') =>
    request.put(`/user-admin/${userId}/status`, { status }),
  assignTeam: (userId: string | number, data: { team_id: string | number; role?: string }) =>
    request.post(`/user-admin/${userId}/teams`, data),
  removeFromTeam: (userId: string | number, teamId: string | number) =>
    request.delete(`/user-admin/${userId}/teams/${teamId}`),
}
