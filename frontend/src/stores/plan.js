/** Plan store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import * as api from '@/api/client'

export const usePlanStore = defineStore('plan', {
  state: () => ({
    currentPlan: null,
    plans: [],
    targetScores: {},
    dailyStudyTime: 0,
    weakPoints: []
  }),

  getters: {
    hasPlan: (state) => state.currentPlan !== null
  },

  actions: {
    async createPlan(data) {
      try {
        const plan = await api.createPlan(data)
        this.plans.unshift(plan)
        this.currentPlan = plan
        return { success: true, plan }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async updatePlan(id, data) {
      try {
        const plan = await api.updatePlan(id, data)
        const idx = this.plans.findIndex(p => p.id === id)
        if (idx !== -1) this.plans[idx] = plan
        if (this.currentPlan?.id === id) this.currentPlan = plan
        return { success: true, plan }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async deletePlan(id) {
      try {
        await api.deletePlan(id)
        this.plans = this.plans.filter(p => p.id !== id)
        if (this.currentPlan?.id === id) this.currentPlan = null
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async getPlansByUserId() {
      // 缓存: 如果2秒内已加载过，跳过重复请求
      if (this.plans.length > 0 && this._plansFetchedAt && Date.now() - this._plansFetchedAt < 2000) {
        return { success: true, cached: true }
      }
      try {
        const plans = await api.getPlans()
        this.plans = plans
        if (plans.length > 0) {
          const savedPlanId = uni.getStorageSync('studymate_current_plan_id')
          const target = savedPlanId
            ? (plans.find(p => p.id === savedPlanId) || plans[0])
            : plans[0]
          this.currentPlan = target
          this.targetScores = target.target_scores || {}
          this.dailyStudyTime = target.daily_study_time || 0
          this.weakPoints = target.weak_points || []
        }
        this._plansFetchedAt = Date.now()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    switchPlan(planId) {
      const plan = this.plans.find(p => p.id === planId)
      if (plan) {
        this.currentPlan = plan
        this.targetScores = plan.target_scores || {}
        this.dailyStudyTime = plan.daily_study_time || 0
        this.weakPoints = plan.weak_points || []
        uni.setStorageSync('studymate_current_plan_id', planId)
      }
    },

    async generatePlanByAI(params) {
      try {
        const result = await api.aiGeneratePlan(params)
        return result.plan || result
      } catch (error) {
        console.error('AI plan generation failed:', error)
        return null
      }
    }
  }
})