import request from './request'

export const authAPI = {
  login: (data: { username: string; password: string }) =>
    request.post('/auth/login', data),
  
  logout: () => request.post('/auth/logout'),
  
  refreshToken: (refreshToken: string) =>
    request.post('/auth/refresh', null, { params: { refresh_token: refreshToken } }),
}
