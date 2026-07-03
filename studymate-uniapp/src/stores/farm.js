import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/api/supabase'

export const useFarmStore = defineStore('farm', () => {
  const plants = ref([])
  const coins = ref(0)
  const experience = ref(0)
  const level = ref(1)
  const loading = ref(false)

  const totalProgress = computed(() => {
    if (plants.value.length === 0) return 0
    const sum = plants.value.reduce((acc, p) => acc + p.progress, 0)
    return Math.round(sum / plants.value.length)
  })

  const maturePlants = computed(() => {
    return plants.value.filter(p => p.type === 'mature' || p.type === 'harvested')
  })

  async function getPlantsByPlanId(planId) {
    loading.value = true
    try {
      const { data, error } = await supabase
        .from('plants')
        .select()
        .eq('plan_id', planId)
        .order('created_at', { ascending: true })
      if (error) throw error
      plants.value = data
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function plantSeed(subject, planId) {
    loading.value = true
    try {
      const { data: plant, error } = await supabase
        .from('plants')
        .insert([{
          plan_id: planId,
          type: 'seed',
          subject,
          progress: 0
        }])
        .select()
        .single()
      if (error) throw error
      plants.value.push(plant)
      return { success: true, data: plant }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function waterPlant(id) {
    loading.value = true
    try {
      const plant = plants.value.find(p => p.id === id)
      if (!plant) return { success: false, error: 'Plant not found' }

      let newProgress = plant.progress + 10
      let newType = plant.type

      if (newProgress >= 100) {
        newProgress = 100
        newType = 'mature'
      } else if (newProgress >= 50) {
        newType = 'growing'
      } else if (newProgress >= 20) {
        newType = 'sprout'
      }

      const { data: updatedPlant, error } = await supabase
        .from('plants')
        .update({
          progress: newProgress,
          type: newType,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single()
      if (error) throw error

      const index = plants.value.findIndex(p => p.id === id)
      if (index !== -1) plants.value[index] = updatedPlant

      coins.value += 5
      experience.value += 10
      checkLevelUp()

      return { success: true, data: updatedPlant }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function harvestPlant(id) {
    loading.value = true
    try {
      const plant = plants.value.find(p => p.id === id)
      if (!plant) return { success: false, error: 'Plant not found' }
      if (plant.type !== 'mature') return { success: false, error: 'Plant is not mature yet' }

      const { data: updatedPlant, error } = await supabase
        .from('plants')
        .update({
          type: 'harvested',
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single()
      if (error) throw error

      const index = plants.value.findIndex(p => p.id === id)
      if (index !== -1) plants.value[index] = updatedPlant

      coins.value += 50
      experience.value += 50
      checkLevelUp()

      return { success: true, data: updatedPlant }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  function checkLevelUp() {
    const expNeeded = level.value * 100
    if (experience.value >= expNeeded) {
      level.value++
      experience.value -= expNeeded
    }
  }

  async function updatePlantProgress(id, progress) {
    loading.value = true
    try {
      const { data: plant, error } = await supabase
        .from('plants')
        .update({
          progress,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single()
      if (error) throw error

      const index = plants.value.findIndex(p => p.id === id)
      if (index !== -1) plants.value[index] = plant

      return { success: true, data: plant }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  return {
    plants,
    coins,
    experience,
    level,
    loading,
    totalProgress,
    maturePlants,
    getPlantsByPlanId,
    plantSeed,
    waterPlant,
    harvestPlant,
    updatePlantProgress
  }
})