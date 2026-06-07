import request from './request'

export interface GitRepo {
  id?: string
  name: string
  url: string
  default_branch: string
  description?: string
  auth_type?: 'none' | 'ssh' | 'token'
  credentials?: string
  created_at?: string
  updated_at?: string
}

export const gitAPI = {
  list: () => request.get<GitRepo[]>('/git/repos'),
  
  get: (id: string) => request.get<GitRepo>(`/git/repos/${id}`),
  
  create: (data: Omit<GitRepo, 'id'>) => request.post<GitRepo>('/git/repos', data),
  
  update: (id: string, data: Partial<GitRepo>) => request.put<GitRepo>(`/git/repos/${id}`, data),
  
  delete: (id: string) => request.delete(`/git/repos/${id}`),
  
  test: (data: Omit<GitRepo, 'id'>) => request.post<{ success: boolean; message: string }>('/git/repos/test', data),
}
