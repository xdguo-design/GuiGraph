import request from './request'

/** 看板/仪表盘 API */
export const dashboardAPI = {
  /** 看板日历数据（按月聚合变更+团队色） */
  kanban: (params: { month: string; team_id?: string }) =>
    request.get('/dashboard/kanban', { params }),

  /** Gantt 图数据（任务起止时间+依赖关系） */
  gantt: (params: { start_date: string; end_date: string; team_id?: string }) =>
    request.get('/dashboard/gantt', { params }),
}
