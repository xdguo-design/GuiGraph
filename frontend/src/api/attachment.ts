import request from './request'

/** 附件（图片/文档）API */
export const attachmentAPI = {
  /** 上传单个文件，返回 { file_id, file_url, file_name, file_size, ... } */
  upload: (file: File, bizType = 'change', bizId = '0') => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/attachment/upload', formData, {
      params: { biz_type: bizType, biz_id: bizId },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /** 删除附件 */
  delete: (fileId: string) => request.delete(`/attachment/delete/${fileId}`),

  /** 列出附件 */
  list: (params?: { biz_type?: string; biz_id?: string }) =>
    request.get('/attachment/list', { params }),
}
