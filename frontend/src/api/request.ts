import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 刷新 Token 状态标记
let isRefreshing = false
// 重试队列
let retryRequests: Array<(token: string) => void> = []

// 请求拦截器 — 自动携带 token
request.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
      config.headers['X-Access-Token'] = authStore.token
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data
    if (code === 'OK' || code === 200) {
      return data
    } else if (code === 401) {
      handleUnauthorized()
      return Promise.reject(new Error(message || '未授权'))
    } else {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message || '请求失败'))
    }
  },
  async (error: AxiosError) => {
    const authStore = useAuthStore()
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // 401 未授权：尝试刷新 Token
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 正在刷新中，加入队列等待
        return new Promise((resolve) => {
          retryRequests.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            originalRequest.headers['X-Access-Token'] = token
            resolve(request(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const res = await axios.post('/api/v1/auth/refresh', null, {
            params: { refresh_token: refreshToken },
          })
          if (res.data?.code === 'OK') {
            const { access_token } = res.data.data
            authStore.setToken(access_token)
            // 重试队列中的请求
            retryRequests.forEach((cb) => cb(access_token))
            retryRequests = []
            // 重试当前请求
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            originalRequest.headers['X-Access-Token'] = access_token
            return request(originalRequest)
          }
        }
        handleUnauthorized()
      } catch (refreshErr) {
        handleUnauthorized()
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }

    // 网络错误或服务器错误
    const errorMsg = (error.response?.data as any)?.message || error.message || '网络错误'
    ElMessage.error(errorMsg)
    return Promise.reject(error)
  }
)

// 统一处理未授权
function handleUnauthorized() {
  const authStore = useAuthStore()
  authStore.logout()
  // 避免在登录页重复跳转
  if (!window.location.pathname.includes('/login')) {
    ElMessage.warning('登录已过期，请重新登录')
    window.location.href = '/login'
  }
}

export default request
