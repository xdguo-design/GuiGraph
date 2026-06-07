import request from './request'

export const userAPI = {
  getProfile: () => request.get('/user/profile'),
  updateProfile: (data: any) => request.put('/user/profile', data),

  /** 上传头像：传入 File 对象 */
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /** 解绑微信 */
  unbindWechat: () => request.post('/user/unbind-wechat'),

  /** 绑定微信 */
  bindWechat: (code: string) => request.post('/user/bind-wechat', { code }),

  /** 获取微信二维码（dev 模式下返回说明） */
  getWechatQrCode: () => request.get('/user/wechat-qrcode'),
}
