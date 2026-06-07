import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_INFO_KEY = 'user_info'

export interface UserInfo {
  id: string
  username: string
  nickname?: string
  avatar_url?: string
  role?: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const refreshToken = ref<string>(localStorage.getItem(REFRESH_TOKEN_KEY) || '')

  // 初始化用户信息
  const initUserInfo = (): UserInfo | null => {
    try {
      const stored = localStorage.getItem(USER_INFO_KEY)
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  }
  const userInfo = ref<UserInfo | null>(initUserInfo())

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => userInfo.value?.username || '')
  const role = computed(() => userInfo.value?.role || 'editor')

  /**
   * 设置 access token
   */
  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  }

  /**
   * 设置 refresh token
   */
  function setRefreshToken(newRefreshToken: string) {
    refreshToken.value = newRefreshToken
    localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken)
  }

  /**
   * 同时设置 access 和 refresh token
   */
  function setTokens(access: string, refresh: string) {
    setToken(access)
    setRefreshToken(refresh)
  }

  /**
   * 设置用户信息
   */
  function setUserInfo(info: UserInfo | null) {
    userInfo.value = info
    if (info) {
      localStorage.setItem(USER_INFO_KEY, JSON.stringify(info))
    } else {
      localStorage.removeItem(USER_INFO_KEY)
    }
  }

  /**
   * 退出登录
   */
  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_INFO_KEY)
  }

  /**
   * 获取 access token
   */
  function getToken() {
    return token.value
  }

  /**
   * 获取 refresh token
   */
  function getRefreshToken() {
    return refreshToken.value
  }

  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    username,
    role,
    setToken,
    setRefreshToken,
    setTokens,
    setUserInfo,
    logout,
    getToken,
    getRefreshToken,
  }
})
