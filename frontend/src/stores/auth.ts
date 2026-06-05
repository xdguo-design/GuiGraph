import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const userInfo = ref<any>(null)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }

  function setUserInfo(info: any) {
    userInfo.value = info
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
  }

  function getToken() {
    return token.value
  }

  return { token, userInfo, setToken, setUserInfo, logout, getToken }
})
