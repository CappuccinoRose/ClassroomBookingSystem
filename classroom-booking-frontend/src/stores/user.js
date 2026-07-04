import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getUserInfo } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value.role === 1)

  function setAuth(authToken, user) {
    token.value = authToken
    userInfo.value = user
    localStorage.setItem('token', authToken)
    localStorage.setItem('userInfo', JSON.stringify(user))
  }

  function clearAuth() {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  async function initializeAuth() {
    if (token.value && !userInfo.value.user_id) {
      try {
        const res = await getUserInfo()
        if (res.code === 200) {
          userInfo.value = res.data
          localStorage.setItem('userInfo', JSON.stringify(res.data))
        }
      } catch (error) {
        clearAuth()
      }
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    setAuth,
    clearAuth,
    initializeAuth
  }
})
