import request from './request'

export const userAPI = {
  getProfile: () => request.get('/user/profile'),
  
  updateProfile: (data: any) => request.put('/user/profile', data),
  
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
