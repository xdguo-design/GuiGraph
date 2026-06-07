/** 字典管理 API */
import request from './request'

export const dictionaryAPI = {
  listDomains: () => request.get('/dictionary/domains'),
  createDomain: (data: any) => request.post('/dictionary/domains', data),
  listApplications: () => request.get('/dictionary/applications'),
  createApplication: (data: any) =>
    request.post('/dictionary/applications', data),
  listComponents: () => request.get('/dictionary/components'),
  createComponent: (data: any) =>
    request.post('/dictionary/components', data),
}
