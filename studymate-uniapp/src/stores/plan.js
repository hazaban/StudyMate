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
    hasPlan: (state) => state.currentPlan !== null,
    activePlanId: (state) => state.currentPlan?.id || null
  },

  actions: {
    /** Switch to a different plan by ID */
    switchPlan(planId) {
      const plan = this.plans.find(p => p.id === planId)
      if (plan) {
        this.currentPlan = plan
        this.targetScores = plan.target_scores || {}
        this.dailyStudyTime = plan.daily_study_time || 0
        this.weakPoints = plan.weak_points || []
        uni.setStorageSync('studymate_current_plan_id', planId)
        return true
      }
      return false
    },

    async createPlan(data) {
      try {
        const plan = await api.createPlan(data)
        this.plans.unshift(plan)
        this.currentPlan = plan
        uni.setStorageSync('studymate_current_plan_id', plan.id)
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
        if (this.currentPlan?.id === id) {
          // Switch to the next plan or clear
          const remaining = this.plans.filter(p => p.id !== id)
          this.currentPlan = remaining.length > 0 ? remaining[0] : null
          uni.setStorageSync('studymate_current_plan_id', this.currentPlan?.id || null)
        }
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async getPlansByUserId() {
      try {
        const plans = await api.getPlans()
        this.plans = plans
        // Restore last selected plan
        const savedPlanId = uni.getStorageSync('studymate_current_plan_id')
        if (savedPlanId) {
          const saved = plans.find(p => p.id === savedPlanId)
          if (saved) {
            this.currentPlan = saved
          } else if (plans.length > 0) {
            this.currentPlan = plans[0]
          }
        } else if (plans.length > 0) {
          this.currentPlan = plans[0]
        }
        if (this.currentPlan) {
          this.targetScores = this.currentPlan.target_scores || {}
          this.dailyStudyTime = this.currentPlan.daily_study_time || 0
          this.weakPoints = this.currentPlan.weak_points || []
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