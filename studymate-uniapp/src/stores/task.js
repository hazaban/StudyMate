/** Task store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import * as api from '@/api/client'

export const useTaskStore = defineStore('task', {
  state: () => ({
    todayTasks: [],
    currentTask: null,
    completedCount: 0,
    totalCount: 0
  }),

  getters: {
    pendingTasks: (state) => state.todayTasks.filter(t => t.status === 'pending'),
    completedTasks: (state) => state.todayTasks.filter(t => t.status === 'completed')
  },

  actions: {
    async getTasksByDate(planId, date) {
      try {
        const tasks = await api.getTasks(planId, date)
        this.todayTasks = tasks
        this.totalCount = tasks.length
        this.completedCount = tasks.filter(t => t.status === 'completed').length
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async createTask(data) {
      try {
        const task = await api.createTask(data)
        this.todayTasks.push(task)
        this.totalCount++
        return { success: true, task }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async updateTask(id, data) {
      try {
        const task = await api.updateTask(id, data)
        const idx = this.todayTasks.findIndex(t => t.id === id)
        if (idx !== -1) this.todayTasks[idx] = task
        this._updateCounts()
        return { success: true, task }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async completeTask(id) {
      try {
        const task = await api.completeTask(id)
        const idx = this.todayTasks.findIndex(t => t.id === id)
        if (idx !== -1) this.todayTasks[idx] = task
        this._updateCounts()
        return { success: true, task }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async generateDailyTasks(params) {
      try {
        return await api.aiGenerateTasks(params)
      } catch (error) {
        console.error('AI task generation failed:', error)
        return { tasks: [] }
      }
    },

    _updateCounts() {
      this.totalCount = this.todayTasks.length
      this.completedCount = this.todayTasks.filter(t => t.status === 'completed').length
    }
  }
})