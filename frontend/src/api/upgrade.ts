import request from './request'

export const upgradeAPI = {
  list: (params: any) => request.get('/upgrades', { params }),
  
  get: (id: string) => request.get(`/upgrades/${id}`),
  
  rollback: (id: string) => request.post(`/upgrades/${id}/rollback`),
}
