import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/api/supabase'
import { ai } from '@/api/ai'

export const useCardStore = defineStore('card', () => {
  const cards = ref([])
  const currentCardIndex = ref(0)
  const reviewMode = ref(false)
  const loading = ref(false)

  const currentCard = computed(() => {
    return cards.value[currentCardIndex.value] || null
  })

  const pendingCards = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return cards.value.filter(c => c.next_review_date <= today)
  })

  async function getCardsByPlanId(planId) {
    loading.value = true
    try {
      const { data, error } = await supabase
        .from('flash_cards')
        .select()
        .eq('plan_id', planId)
        .order('next_review_date', { ascending: true })
      if (error) throw error
      cards.value = data
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function createCard(data) {
    loading.value = true
    try {
      const { data: card, error } = await supabase
        .from('flash_cards')
        .insert([data])
        .select()
        .single()
      if (error) throw error
      cards.value.push(card)
      return { success: true, data: card }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function updateCard(id, data) {
    loading.value = true
    try {
      const { data: card, error } = await supabase
        .from('flash_cards')
        .update(data)
        .eq('id', id)
        .select()
        .single()
      if (error) throw error
      const index = cards.value.findIndex(c => c.id === id)
      if (index !== -1) cards.value[index] = card
      return { success: true, data: card }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function deleteCard(id) {
    loading.value = true
    try {
      const { error } = await supabase
        .from('flash_cards')
        .delete()
        .eq('id', id)
      if (error) throw error
      cards.value = cards.value.filter(c => c.id !== id)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  async function markMastery(id, level) {
    const card = cards.value.find(c => c.id === id)
    if (!card) return { success: false, error: 'Card not found' }

    const reviewInterval = getReviewInterval(level)
    const nextReviewDate = new Date()
    nextReviewDate.setDate(nextReviewDate.getDate() + reviewInterval)

    return updateCard(id, {
      mastery_level: level,
      next_review_date: nextReviewDate.toISOString().split('T')[0],
      review_count: card.review_count + 1,
      updated_at: new Date().toISOString()
    })
  }

  function getReviewInterval(masteryLevel) {
    const intervals = {
      unmastered: 1,
      familiar: 3,
      mastered: 7
    }
    return intervals[masteryLevel] || 1
  }

  async function generateCardsByAI(content) {
    try {
      const result = await ai.generateFlashCards(content)
      return result
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  function startReview() {
    reviewMode.value = true
    currentCardIndex.value = 0
  }

  function endReview() {
    reviewMode.value = false
    currentCardIndex.value = 0
  }

  function nextCard() {
    if (currentCardIndex.value < cards.value.length - 1) {
      currentCardIndex.value++
    }
  }

  function prevCard() {
    if (currentCardIndex.value > 0) {
      currentCardIndex.value--
    }
  }

  return {
    cards,
    currentCardIndex,
    reviewMode,
    loading,
    currentCard,
    pendingCards,
    getCardsByPlanId,
    createCard,
    updateCard,
    deleteCard,
    markMastery,
    generateCardsByAI,
    startReview,
    endReview,
    nextCard,
    prevCard
  }
})