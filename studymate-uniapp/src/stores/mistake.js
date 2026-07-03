/** Mistake store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import * as api from '@/api/client'

export const useMistakeStore = defineStore('mistake', {
  state: () => ({
    mistakes: [],
    loading: false
  }),

  getters: {
    totalCount: (state) => state.mistakes.length,
    unmasteredCount: (state) => state.mistakes.filter(m => m.mastered === '0').length
  },

  actions: {
    async getMistakesByPlanId(planId) {
      try {
        const mistakes = await api.getMistakes(planId)
        this.mistakes = mistakes
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async createMistake(data) {
      try {
        const mistake = await api.createMistake(data)
        this.mistakes.unshift(mistake)
        return { success: true, mistake }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async updateMistake(id, data) {
      try {
        const mistake = await api.updateMistake(id, data)
        const idx = this.mistakes.findIndex(m => m.id === id)
        if (idx !== -1) this.mistakes[idx] = mistake
        return { success: true, mistake }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async deleteMistake(id) {
      try {
        await api.deleteMistake(id)
        this.mistakes = this.mistakes.filter(m => m.id !== id)
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    }
  }
})