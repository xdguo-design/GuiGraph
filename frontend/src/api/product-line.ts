/** 产品线 API */
import request from './request'

export const productLineAPI = {
  listLines: (params?: { business_line_id?: number; status?: string }) =>
    request.get('/product-line', { params }),
  getLine: (lineId: number) =>
    request.get(`/product-line/${lineId}`),
  createLine: (data: any) =>
    request.post('/product-line', data),
  updateLine: (lineId: number, data: any) =>
    request.put(`/product-line/${lineId}`, data),
  deleteLine: (lineId: number) =>
    request.delete(`/product-line/${lineId}`),
}
