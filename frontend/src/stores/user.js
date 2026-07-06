/** User store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, getMe, logout as apiLogout } from '@/api/client'
import { usePlanStore } from '@/stores/plan'
import { useTaskStore } from '@/stores/task'

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
        // 登录成功后立即预加载计划和任务，无需等用户点击
        await this._preloadData()
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
        await this._preloadData()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    /** 登录后立即同步核心数据 */
    async _preloadData() {
      try {
        const planStore = usePlanStore()
        await planStore.getPlansByUserId()
        if (planStore.currentPlan) {
          const taskStore = useTaskStore()
          const today = new Date().toISOString().split('T')[0]
          await taskStore.getTasksByDate(planStore.currentPlan.id, today)
          await taskStore.getAllTasks(planStore.currentPlan.id)
        }
      } catch (e) { /* 静默，预加载失败不影响登录流程 */ }
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