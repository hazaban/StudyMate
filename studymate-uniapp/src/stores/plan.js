import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/api/supabase'
import { ai } from '@/api/ai'

export const usePlanStore = defineStore('plan', () => {
  const currentPlan = ref(null)
  const plans = ref([])
  const loading = ref(false)

  const planSubjects = computed(() => {
    if (!currentPlan.value) return []
    return Object.keys(currentPlan.value.target_scores || {})
  })

  async function createPlan(data) {
    loading.value = true
    try {
      const { data: plan, error } = await supabase
        .from('study_plans')
        .insert([data])
        .select()
        .single()
      if (error) throw error
      currentPlan.value = plan
      plans.value.unshift(plan)
      return { success: true, data: plan }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function updatePlan(id, data) {
    loading.value = true
    try {
      const { data: plan, error } = await supabase
        .from('study_plans')
        .update(data)
        .eq('id', id)
        .select()
        .single()
      if (error) throw error
      currentPlan.value = plan
      const index = plans.value.findIndex(p => p.id === id)
      if (index !== -1) plans.value[index] = plan
      return { success: true, data: plan }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function deletePlan(id) {
    loading.value = true
    try {
      const { error } = await supabase
        .from('study_plans')
        .delete()
        .eq('id', id)
      if (error) throw error
      plans.value = plans.value.filter(p => p.id !== id)
      if (currentPlan.value?.id === id) {
        currentPlan.value = plans.value[0] || null
      }
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function getPlanById(id) {
    loading.value = true
    try {
      const { data: plan, error } = await supabase
        .from('study_plans')
        .select()
        .eq('id', id)
        .single()
      if (error) throw error
      currentPlan.value = plan
      return { success: true, data: plan }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function getPlansByUserId(userId) {
    loading.value = true
    try {
      const { data, error } = await supabase
        .from('study_plans')
        .select()
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
      if (error) throw error
      plans.value = data
      if (!currentPlan.value && data.length > 0) {
        currentPlan.value = data[0]
      }
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function generatePlanByAI(params) {
    try {
      const result = await ai.generateStudyPlan(params)
      return result
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  return {
    currentPlan,
    plans,
    loading,
    planSubjects,
    createPlan,
    updatePlan,
    deletePlan,
    getPlanById,
    getPlansByUserId,
    generatePlanByAI
  }
})