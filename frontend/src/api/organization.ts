import request from './request'

export const orgAPI = {
  getStructure: () => request.get('/org/structure'),
  
  createDepartment: (data: any) => request.post('/org/departments', data),
  
  updateDepartment: (id: string, data: any) => request.put(`/org/departments/${id}`, data),
  
  createTeam: (data: any) => request.post('/org/teams', data),
  
  addMember: (teamId: string, data: any) => request.post(`/org/teams/${teamId}/members`, data),
  
  removeMember: (teamId: string, userId: string) => 
    request.delete(`/org/teams/${teamId}/members/${userId}`),
}
