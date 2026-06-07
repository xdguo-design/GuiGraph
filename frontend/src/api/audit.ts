/** 审计日志 API */
import request from './request'

export const auditAPI = {
  listLogs: (params?: {
    page?: number
    page_size?: number
    user_id?: string
    operation?: string
    start_time?: string
    end_time?: string
  }) => request.get('/audit', { params }),
}
