import request from './request'

export interface JenkinsInstance {
  id?: string
  name: string
  url: string
  username?: string
  token?: string
  description?: string
  status?: 'online' | 'offline'
  created_at?: string
  updated_at?: string
}

export const jenkinsAPI = {
  list: () => request.get<JenkinsInstance[]>('/jenkins/instances'),
  
  get: (id: string) => request.get<JenkinsInstance>(`/jenkins/instances/${id}`),
  
  create: (data: Omit<JenkinsInstance, 'id'>) => request.post<JenkinsInstance>('/jenkins/instances', data),
  
  update: (id: string, data: Partial<JenkinsInstance>) => request.put<JenkinsInstance>(`/jenkins/instances/${id}`, data),
  
  delete: (id: string) => request.delete(`/jenkins/instances/${id}`),
  
  test: (data: Omit<JenkinsInstance, 'id'>) => request.post<{ success: boolean; message: string }>('/jenkins/instances/test', data),
}
