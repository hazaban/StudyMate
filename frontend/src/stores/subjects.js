/** Subjects store — merges user-defined subjects + plan subjects into one list. */
import { defineStore } from 'pinia'
import * as api from '@/api/client'
import { usePlanStore } from '@/stores/plan'

export const useSubjectsStore = defineStore('subjects', {
  state: () => ({
    subjects: [],       // deduped flat list returned by the getter
    planSubjects: [],   // names extracted from currentPlan.subjects
    userSubjects: [],   // names from UserSubject table (backend)
    loaded: false,
    loading: false
  }),

  getters: {
    // 合并去重：用户自定义科目 + 当前计划中的科目
    mergedSubjects: (state) => {
      const planNames = (state.planSubjects || []).filter(Boolean)
      const userNames = (state.userSubjects || []).filter(Boolean)
      const merged = [...new Set([...planNames, ...userNames])]
      // 把计划科目排前面，用户自定义排后面
      return merged
    }
  },

  actions: {
    async load(force = false) {
      if (this.loading) return
      if (this.loaded && !force) return
      this.loading = true
      try {
        // 1) 加载用户自定义科目
        const res = await api.getUserSubjects()
        this.userSubjects = res.subjects || []
        // 2) 从所有计划中提取科目名
        const planStore = usePlanStore()
        const planNames = []
        for (const plan of (planStore.plans || [])) {
          const subjects = plan.subjects || []
          for (const s of subjects) {
            const name = (s.name || '').trim()
            if (name) planNames.push(name)
          }
        }
        this.planSubjects = [...new Set(planNames)]
        this.subjects = this.mergedSubjects
        this.loaded = true
      } catch (e) {
        this.subjects = []
      } finally {
        this.loading = false
      }
    },

    async add(name) {
      const trimmed = (name || '').trim()
      if (!trimmed) return
      if (!this.userSubjects.includes(trimmed)) {
        this.userSubjects.push(trimmed)
      }
      this.subjects = this.mergedSubjects
      try { await api.addUserSubject(trimmed) } catch (e) { /* ignore */ }
    },

    async remove(name) {
      this.userSubjects = this.userSubjects.filter(s => s !== name)
      this.subjects = this.mergedSubjects
      try { await api.removeUserSubject(name) } catch (e) { /* ignore */ }
    },

    clear() {
      this.userSubjects = []
      this.planSubjects = []
      this.subjects = []
      this.loaded = false
    }
  }
})
