/** Farm store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import * as api from '@/api/client'

export const useFarmStore = defineStore('farm', {
  state: () => ({
    plants: [],
    coins: 0,
    experience: 0,
    level: 1
  }),

  getters: {
    totalProgress: (state) => {
      if (state.plants.length === 0) return 0
      const total = state.plants.reduce((sum, p) => sum + p.progress, 0)
      return Math.round(total / state.plants.length)
    },
    maturePlants: (state) => state.plants.filter(p => p.type === 'harvested'),
    activePlants: (state) => state.plants.filter(p => p.type !== 'harvested')
  },

  actions: {
    async getPlantsByPlanId(planId) {
      try {
        const data = await api.getFarm(planId)
        this.plants = data.plants || []
        this.coins = data.coins || 0
        this.experience = data.experience || 0
        this.level = data.level || 1
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async plantSeed(subject, planId) {
      try {
        const plant = await api.plantSeed({
          plan_id: planId,
          subject,
          type: 'seed',
          progress: 0
        })
        this.plants.push(plant)
        this.coins = Math.max(0, this.coins - 10)
        return { success: true, plant }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async waterPlant(plantId) {
      try {
        const plant = await api.waterPlant(plantId)
        const idx = this.plants.findIndex(p => p.id === plantId)
        if (idx !== -1) this.plants[idx] = plant
        return { success: true, plant }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async harvestPlant(plantId) {
      try {
        const plant = await api.harvestPlant(plantId)
        const idx = this.plants.findIndex(p => p.id === plantId)
        if (idx !== -1) this.plants[idx] = plant
        this.coins += 50
        return { success: true, plant }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async fertilizePlant(plantId) {
      try {
        const plant = await api.fertilizePlant(plantId)
        const idx = this.plants.findIndex(p => p.id === plantId)
        if (idx !== -1) this.plants[idx] = plant
        return { success: true, plant }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async ensureCrop(planId, subject) {
      try {
        const plant = await api.ensureCrop(planId, subject)
        const idx = this.plants.findIndex(p => p.id === plant.id)
        if (idx !== -1) {
          this.plants[idx] = plant
        } else {
          this.plants.push(plant)
        }
        return { success: true, plant }
      } catch (error) {
        return { success: false, error: error.message }
      }
    }
  }
})