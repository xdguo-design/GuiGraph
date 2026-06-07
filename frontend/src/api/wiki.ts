/** Wiki 文档 API */
import request from './request'

export const wikiAPI = {
  // ── 空间 ──
  listSpaces: () => request.get('/wiki/spaces'),
  createSpace: (data: any) => request.post('/wiki/spaces', data),

  // ── 文档 ──
  listDocs: (params?: { space_id?: number }) =>
    request.get('/wiki/docs', { params }),
  getDoc: (docId: number) => request.get(`/wiki/${docId}`),
  createDoc: (data: any) => request.post('/wiki/docs', data),
  updateDoc: (docId: number, data: any) =>
    request.put(`/wiki/docs/${docId}`, data),
  deleteDoc: (docId: number) => request.delete(`/wiki/docs/${docId}`),
}
