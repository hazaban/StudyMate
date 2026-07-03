/** Card store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import * as api from '@/api/client'

export const useCardStore = defineStore('card', {
  state: () => ({
    cards: [],
    currentCardIndex: 0,
    reviewMode: false,
    masteryLevel: 'unmastered'
  }),

  getters: {
    pendingCards: (state) => state.cards.filter(c => {
      const today = new Date().toISOString().split('T')[0]
      return c.next_review_date <= today
    })
  },

  actions: {
    async getCardsByPlanId(planId) {
      try {
        const result = await api.getCards(planId)
        this.cards = result.cards || []
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async createCard(data) {
      try {
        const card = await api.createCard(data)
        this.cards.push(card)
        return { success: true, card }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async updateCard(id, data) {
      try {
        const card = await api.updateCard(id, data)
        const idx = this.cards.findIndex(c => c.id === id)
        if (idx !== -1) this.cards[idx] = card
        return { success: true, card }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async deleteCard(id) {
      try {
        await api.deleteCard(id)
        this.cards = this.cards.filter(c => c.id !== id)
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async markMastery(id, level) {
      try {
        const card = await api.reviewCard(id, level)
        const idx = this.cards.findIndex(c => c.id === id)
        if (idx !== -1) this.cards[idx] = card
        return { success: true, card }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async generateCardsByAI(content, subject = '通用') {
      try {
        return await api.aiGenerateCards(content, subject)
      } catch (error) {
        console.error('AI card generation failed:', error)
        return { cards: [] }
      }
    }
  }
})