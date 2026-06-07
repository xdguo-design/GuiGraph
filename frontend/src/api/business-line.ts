/** 业务线 API */
import request from './request'

export const businessLineAPI = {
  listLines: (params?: { status?: string }) =>
    request.get('/business-line', { params }),
  getLine: (lineId: number) =>
    request.get(`/business-line/${lineId}`),
  createLine: (data: any) =>
    request.post('/business-line', data),
  updateLine: (lineId: number, data: any) =>
    request.put(`/business-line/${lineId}`, data),
  deleteLine: (lineId: number) =>
    request.delete(`/business-line/${lineId}`),
}
