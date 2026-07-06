/** Task store - connects to FastAPI backend */
import { defineStore } from 'pinia'
import * as api from '@/api/client'

export const useTaskStore = defineStore('task', {
  state: () => ({
    todayTasks: [],
    weekTasks: [],
    currentTask: null,
    completedCount: 0,
    totalCount: 0,
    _currentPlanId: null,
    _todayFetchedAt: 0,
    _weekFetchedAt: 0
  }),

  getters: {
    pendingTasks: (state) => state.todayTasks.filter(t => t.status === 'pending'),
    completedTasks: (state) => state.todayTasks.filter(t => t.status === 'completed')
  },

  actions: {
    _refreshAll(planId) {
      if (!planId) planId = this._currentPlanId
      if (!planId) return
      return this.getAllTasks(planId)
    },

    async getTasksByDate(planId, date) {
      // 缓存: 1秒内同日同计划不重复请求
      const cacheKey = planId + '|' + date
      if (this._todayCacheKey === cacheKey && Date.now() - this._todayFetchedAt < 1000) {
        return { success: true, cached: true }
      }
      try {
        const tasks = await api.getTasks(planId, date)
        this.todayTasks = tasks
        this.totalCount = tasks.length
        this.completedCount = tasks.filter(t => t.status === 'completed').length
        this._currentPlanId = planId
        this._todayCacheKey = cacheKey
        this._todayFetchedAt = Date.now()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async getAllTasks(planId) {
      try {
        const tasks = await api.getTasks(planId)
        this.weekTasks = tasks
        this._currentPlanId = planId
        return { success: true, tasks }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async createTask(data) {
      try {
        const task = await api.createTask(data)
        if (task.date === data.date) {
          this.todayTasks.push(task)
          this.totalCount = this.todayTasks.length
          this.completedCount = this.todayTasks.filter(t => t.status === 'completed').length
        }
        this.weekTasks.push(task)
        return { success: true, task }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async updateTask(id, data) {
      try {
        const task = await api.updateTask(id, data)
        const todayIdx = this.todayTasks.findIndex(t => t.id === id)
        if (todayIdx !== -1) this.todayTasks[todayIdx] = task
        const weekIdx = this.weekTasks.findIndex(t => t.id === id)
        if (weekIdx !== -1) this.weekTasks[weekIdx] = task
        this._updateCounts()
        return { success: true, task }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async completeTask(id, taskDate) {
      try {
        const task = await api.completeTask(id, taskDate)
        const todayIdx = this.todayTasks.findIndex(t => t.id === id)
        if (todayIdx !== -1) this.todayTasks[todayIdx] = task
        const weekIdx = this.weekTasks.findIndex(t => t.id === id)
        if (weekIdx !== -1) this.weekTasks[weekIdx] = task
        this._updateCounts()
        return { success: true, task }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async uncompleteTask(id, taskDate) {
      try {
        const task = await api.uncompleteTask(id, taskDate)
        const todayIdx = this.todayTasks.findIndex(t => t.id === id)
        if (todayIdx !== -1) this.todayTasks[todayIdx] = task
        const weekIdx = this.weekTasks.findIndex(t => t.id === id)
        if (weekIdx !== -1) this.weekTasks[weekIdx] = task
        this._updateCounts()
        return { success: true, task }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async deleteTask(id) {
      try {
        await api.deleteTask(id)
        this.todayTasks = this.todayTasks.filter(t => t.id !== id)
        this.weekTasks = this.weekTasks.filter(t => t.id !== id)
        this._updateCounts()
        return { success: true }
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