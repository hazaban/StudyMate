/** User-defined subjects store - each user has their own independent subjects. */
import { defineStore } from 'pinia'
import * as api from '@/api/client'

export const useSubjectsStore = defineStore('subjects', {
  state: () => ({
    subjects: [],
    loaded: false,
    loading: false
  }),

  getters: {
    hasSubjects: (state) => state.subjects.length > 0
  },

  actions: {
    async load(force = false) {
      if (this.loading) return
      if (this.loaded && !force) return
      this.loading = true
      try {
        const res = await api.getUserSubjects()
        this.subjects = res.subjects || []
        this.loaded = true
      } catch (e) {
        // offline / not logged in: keep empty
        this.subjects = []
      } finally {
        this.loading = false
      }
    },

    async add(name) {
      const trimmed = (name || '').trim()
      if (!trimmed) return
      if (!this.subjects.includes(trimmed)) {
        this.subjects.push(trimmed)
      }
      try {
        await api.addUserSubject(trimmed)
      } catch (e) { /* ignore */ }
    },

    async remove(name) {
      this.subjects = this.subjects.filter(s => s !== name)
      try {
        await api.removeUserSubject(name)
      } catch (e) { /* ignore */ }
    },

    clear() {
      this.subjects = []
      this.loaded = false
    }
  }
})
