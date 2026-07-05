/** User store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, getMe, logout as apiLogout } from '@/api/client'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: null,
    isLoggedIn: false
  }),

  actions: {
    async login(email, password) {
      try {
        const data = await apiLogin(email, password)
        this.user = data.user
        this.token = data.access_token
        this.isLoggedIn = true
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async register(email, password, nickname) {
      try {
        const data = await apiRegister(email, password, nickname)
        this.user = data.user
        this.token = data.access_token
        this.isLoggedIn = true
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async getUserInfo() {
      try {
        const user = await getMe()
        this.user = user
        this.isLoggedIn = true
        return { success: true }
      } catch (error) {
        this.isLoggedIn = false
        this.user = null
        return { success: false, error: error.message }
      }
    },

    logout() {
      apiLogout()
      this.user = null
      this.token = null
      this.isLoggedIn = false
    }
  }
})