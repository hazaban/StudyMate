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
      try {
        const plans = await api.getPlans()
        this.plans = plans
        if (plans.length > 0) {
          this.currentPlan = plans[0]
          this.targetScores = plans[0].target_scores || {}
          this.dailyStudyTime = plans[0].daily_study_time || 0
          this.weakPoints = plans[0].weak_points || []
        }
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
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