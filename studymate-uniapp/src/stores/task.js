import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/api/supabase'
import { ai } from '@/api/ai'

export const useTaskStore = defineStore('task', () => {
  const todayTasks = ref([])
  const currentTask = ref(null)
  const loading = ref(false)

  const completedCount = computed(() => {
    return todayTasks.value.filter(t => t.status === 'completed').length
  })

  const totalCount = computed(() => {
    return todayTasks.value.length
  })

  const pendingTasks = computed(() => {
    return todayTasks.value.filter(t => t.status === 'pending')
  })

  const inProgressTasks = computed(() => {
    return todayTasks.value.filter(t => t.status === 'doing')
  })

  async function getTasksByDate(planId, date) {
    loading.value = true
    try {
      const { data, error } = await supabase
        .from('daily_tasks')
        .select()
        .eq('plan_id', planId)
        .eq('date', date)
        .order('created_at', { ascending: true })
      if (error) throw error
      todayTasks.value = data
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function createTask(data) {
    loading.value = true
    try {
      const { data: task, error } = await supabase
        .from('daily_tasks')
        .insert([data])
        .select()
        .single()
      if (error) throw error
      todayTasks.value.push(task)
      return { success: true, data: task }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function updateTask(id, data) {
    loading.value = true
    try {
      const { data: task, error } = await supabase
        .from('daily_tasks')
        .update(data)
        .eq('id', id)
        .select()
        .single()
      if (error) throw error
      const index = todayTasks.value.findIndex(t => t.id === id)
      if (index !== -1) todayTasks.value[index] = task
      return { success: true, data: task }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function completeTask(id) {
    return updateTask(id, {
      status: 'completed',
      completed_at: new Date().toISOString()
    })
  }

  async function generateDailyTasks(params) {
    try {
      const result = await ai.generateDailyTasks(params)
      return result
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  return {
    todayTasks,
    currentTask,
    loading,
    completedCount,
    totalCount,
    pendingTasks,
    inProgressTasks,
    getTasksByDate,
    createTask,
    updateTask,
    completeTask,
    generateDailyTasks
  }
})