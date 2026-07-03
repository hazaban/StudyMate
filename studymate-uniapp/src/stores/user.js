import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/api/supabase'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)

  async function login(email, password) {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error
      user.value = data.user
      isLoggedIn.value = true
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  async function register(email, password, nickname) {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { nickname }
        }
      })
      if (error) throw error
      user.value = data.user
      isLoggedIn.value = true
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  async function logout() {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      user.value = null
      isLoggedIn.value = false
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  async function getUserInfo() {
    const { data } = await supabase.auth.getUser()
    if (data.user) {
      user.value = data.user
      isLoggedIn.value = true
    }
    return data.user
  }

  return {
    user,
    isLoggedIn,
    login,
    register,
    logout,
    getUserInfo
  }
})