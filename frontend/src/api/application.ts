import request from './request'

/** 注册申请 API */
export const applicationAPI = {
  /** 提交注册申请（公开） */
  submit: (data: {
    username: string
    password: string
    nickname?: string
    email?: string
    phone?: string
    reason?: string
  }) => request.post('/auth/apply', data),

  /** 列出申请（管理员） */
  list: (statusFilter?: 'pending' | 'approved' | 'rejected') =>
    request.get('/auth/applications', { params: statusFilter ? { status_filter: statusFilter } : {} }),

  /** 通过申请（管理员） */
  approve: (
    id: number,
    data: {
      role: string
      company_id?: string
      department_id?: string
      team_id?: string
      comment?: string
    },
  ) => request.post(`/auth/applications/${id}/approve`, data),

  /** 拒绝申请（管理员） */
  reject: (id: number, data: { comment?: string }) =>
    request.post(`/auth/applications/${id}/reject`, data),
}

/** 演示/测试数据 API */
export const demoAPI = {
  /** 灌入演示数据 */
  seed: () => request.post('/demo/seed'),
  /** 清空演示数据 */
  clear: () => request.delete('/demo/seed'),
  /** 个人看板 */
  personalKanban: () => request.get('/demo/kanban/personal'),
  /** 团队看板 */
  teamKanban: (teamId: number | string) => request.get(`/demo/kanban/team/${teamId}`),
  /** 我的团队列表 */
  myTeams: () => request.get('/demo/kanban/teams'),
}
