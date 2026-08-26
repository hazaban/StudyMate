/** User store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, getMe, logout as apiLogout, createFocusRecord } from '@/api/client'
import { usePlanStore } from '@/stores/plan'
import { useTaskStore } from '@/stores/task'
import { useSubjectsStore } from '@/stores/subjects'

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
        // 补传之前因登录态过期而暂存的番茄钟记录
        await this._syncPendingFocusRecords()
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
        await this._syncPendingFocusRecords()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    /**
     * 补传因 token 过期 / 网络异常等原因未能同步到后端的番茄钟记录。
     * 队列由 pomodoro.vue 写入 localStorage(studymate_pomodoro_pending_sync)。
     * 成功同步的记录会从队列移除；仍失败的保留，等待下次重试。
     */
    async _syncPendingFocusRecords() {
      let pending = []
      try {
        pending = JSON.parse(uni.getStorageSync('studymate_pomodoro_pending_sync') || '[]')
      } catch (e) { pending = [] }
      if (!pending.length) return
      const remaining = []
      for (const rec of pending) {
        try {
          await createFocusRecord(rec)
        } catch (e) {
          // 同步仍失败：保留记录，等下次再试（不弹 toast，避免打扰登录流程）
          remaining.push(rec)
        }
      }
      uni.setStorageSync('studymate_pomodoro_pending_sync', JSON.stringify(remaining))
      if (remaining.length < pending.length) {
        const synced = pending.length - remaining.length
        uni.showToast({ title: `已补传 ${synced} 条番茄钟记录`, icon: 'success' })
      }
    },

    /** 登录后立即同步核心数据 */
    async _preloadData() {
      try {
        const planStore = usePlanStore()
        const subjectsStore = useSubjectsStore()
        await planStore.getPlansByUserId()
        await subjectsStore.load(true)
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
        // 登录态过期时，若内存中已有用户信息，不要立即清空——避免在番茄钟等
        // 页面出现"莫名断开登录"的体验。保留 UI 可用，提示用户重新登录即可。
        // 数据会通过番茄钟的"待同步队列"在重新登录后补传。
        if (error?.isAuthError && this.user) {
          return { success: false, error: error.message, authExpired: true }
        }
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
      // Clear cached subjects so a different user logging in starts fresh
      useSubjectsStore().clear()
    }
  }
})