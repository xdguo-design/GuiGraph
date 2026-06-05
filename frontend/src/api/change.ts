import request from './request'

export const changeAPI = {
  list: (params: any) => request.get('/changes', { params }),
  
  get: (id: string) => request.get(`/changes/${id}`),
  
  create: (data: any) => request.post('/changes', data),
  
  update: (id: string, data: any) => request.put(`/changes/${id}`, data),
  
  approve: (id: string, data: any) => request.post(`/changes/${id}/approve`, data),
}
