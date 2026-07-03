<template>
  <view class="page">
    <view class="header">
      <text class="title">错题本</text>
      <view class="header-actions">
        <view class="add-btn" @click="showForm = true; editingMistake = null">
          <text class="add-icon">+</text>
        </view>
      </view>
    </view>

    <view class="filters">
      <view class="filter-row">
        <text class="filter-label">科目:</text>
        <view class="filter-options">
          <view class="filter-option" :class="{ active: filterSubject === '' }" @click="filterSubject = ''">全部</view>
          <view class="filter-option" v-for="s in subjects" :key="s" :class="{ active: filterSubject === s }" @click="filterSubject = s">{{ s }}</view>
        </view>
      </view>
      <view class="filter-row">
        <text class="filter-label">掌握:</text>
        <view class="filter-options">
          <view class="filter-option" :class="{ active: filterMastered === '' }" @click="filterMastered = ''">全部</view>
          <view class="filter-option" :class="{ active: filterMastered === '0' }" @click="filterMastered = '0'">未掌握</view>
          <view class="filter-option" :class="{ active: filterMastered === '1' }" @click="filterMastered = '1'">已掌握</view>
        </view>
      </view>
    </view>

    <view class="mistake-list">
      <view class="mistake-card" v-for="m in filteredMistakes" :key="m.id">
        <view class="mistake-header">
          <text class="mistake-question">{{ m.question }}</text>
          <view class="mistake-tags">
            <text class="mistake-tag subject-tag">{{ m.subject }}</text>
            <text class="mistake-tag difficulty-tag">{{ m.difficulty }}</text>
            <text class="mistake-tag mastered-tag" :class="{ mastered: m.mastered === '1' }">{{ m.mastered === '1' ? '已掌握' : '未掌握' }}</text>
          </view>
        </view>
        <view class="mistake-body" v-if="expandedMistake === m.id">
          <view class="mistake-section">
            <text class="mistake-section-title">答案:</text>
            <text class="mistake-section-text">{{ m.answer }}</text>
          </view>
          <view class="mistake-section" v-if="m.analysis">
            <text class="mistake-section-title">分析:</text>
            <text class="mistake-section-text">{{ m.analysis }}</text>
          </view>
          <view class="mistake-stats">
            <text class="stat-item">错误次数: {{ m.error_count }}</text>
            <text class="stat-item">正确次数: {{ m.correct_count }}</text>
          </view>
        </view>
        <view class="mistake-actions">
          <view class="mistake-action" @click="toggleMistake(m.id)">
            <text>{{ expandedMistake === m.id ? '收起' : '展开' }}</text>
          </view>
          <view class="mistake-action" @click="editMistake(m)">
            <text>编辑</text>
          </view>
          <view class="mistake-action" @click="toggleMastered(m)">
            <text>{{ m.mastered === '1' ? '标记未掌握' : '标记已掌握' }}</text>
          </view>
          <view class="mistake-action delete" @click="deleteMistake(m)">
            <text>删除</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty" v-if="filteredMistakes.length === 0">
      <text class="empty-icon">📝</text>
      <text class="empty-text">暂无错题</text>
      <text class="empty-hint">点击 + 添加错题</text>
    </view>

    <!-- Export Button -->
    <view class="export-section">
      <view class="export-btn" @click="exportMistakes">
        <text>📥 导出CSV</text>
      </view>
    </view>

    <!-- Add/Edit Form Modal -->
    <view class="modal-overlay" v-if="showForm" @click="showForm = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingMistake ? '编辑错题' : '添加错题' }}</text>
          <view class="modal-close" @click="showForm = false">✕</view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="form-group">
            <text class="form-label">科目</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="form.subject" placeholder="如：高等数学" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">题目</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.question" placeholder="请输入题目..." />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">答案</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.answer" placeholder="请输入正确答案..." />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">错误分析</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.analysis" placeholder="分析错误原因..." />
            </view>
          </view>
          <view class="form-row">
            <view class="form-group half">
              <text class="form-label">难度</text>
              <view class="difficulty-row">
                <view class="diff-item" :class="{ active: form.difficulty === 'easy' }" @click="form.difficulty = 'easy'">简单</view>
                <view class="diff-item" :class="{ active: form.difficulty === 'medium' }" @click="form.difficulty = 'medium'">中等</view>
                <view class="diff-item" :class="{ active: form.difficulty === 'hard' }" @click="form.difficulty = 'hard'">困难</view>
              </view>
            </view>
            <view class="form-group half">
              <text class="form-label">错误次数</text>
              <view class="input-wrapper">
                <input class="input-field" v-model="form.error_count" type="number" placeholder="1" />
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">标签（逗号分隔）</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="form.tags" placeholder="如：积分, 不定积分" />
            </view>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showForm = false">取消</view>
          <view class="submit-btn" @click="submitForm">{{ editingMistake ? '保存' : '创建' }}</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMistakeStore } from '@/stores/mistake'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'

const mistakeStore = useMistakeStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const expandedMistake = ref(null)
const showForm = ref(false)
const editingMistake = ref(null)
const filterSubject = ref('')
const filterMastered = ref('')

const defaultForm = { subject: '', question: '', answer: '', analysis: '', difficulty: 'medium', error_count: 1, tags: '' }
const form = ref({ ...defaultForm })

const subjects = computed(() => {
  const set = new Set()
  mistakeStore.mistakes.forEach(m => set.add(m.subject))
  return [...set]
})

const filteredMistakes = computed(() => {
  let mistakes = mistakeStore.mistakes
  if (filterSubject.value) mistakes = mistakes.filter(m => m.subject === filterSubject.value)
  if (filterMastered.value !== '') mistakes = mistakes.filter(m => m.mastered === filterMastered.value)
  return mistakes
})

function toggleMistake(id) {
  expandedMistake.value = expandedMistake.value === id ? null : id
}

function editMistake(m) {
  editingMistake.value = m
  form.value = {
    subject: m.subject,
    question: m.question,
    answer: m.answer,
    analysis: m.analysis || '',
    difficulty: m.difficulty,
    error_count: m.error_count,
    tags: (m.tags || []).join(', ')
  }
  showForm.value = true
}

async function toggleMastered(m) {
  await mistakeStore.updateMistake(m.id, { mastered: m.mastered === '1' ? '0' : '1' })
  uni.showToast({ title: '已更新', icon: 'success' })
}

async function deleteMistake(m) {
  uni.showModal({
    title: '删除确认',
    content: '确定要删除这条错题吗？',
    success: async (res) => {
      if (res.confirm) {
        await mistakeStore.deleteMistake(m.id)
        uni.showToast({ title: '已删除', icon: 'success' })
      }
    }
  })
}

async function submitForm() {
  if (!form.value.subject || !form.value.question || !form.value.answer) {
    uni.showToast({ title: '请填写完整', icon: 'none' })
    return
  }

  uni.showLoading({ title: '保存中...' })
  try {
    const data = {
      subject: form.value.subject,
      question: form.value.question,
      answer: form.value.answer,
      analysis: form.value.analysis,
      difficulty: form.value.difficulty,
      error_count: parseInt(form.value.error_count) || 1,
      tags: form.value.tags ? form.value.tags.split(',').map(t => t.trim()).filter(Boolean) : []
    }

    if (editingMistake.value) {
      await mistakeStore.updateMistake(editingMistake.value.id, data)
    } else {
      if (!planStore.currentPlan) {
        uni.showToast({ title: '请先创建学习计划', icon: 'none' })
        return
      }
      await mistakeStore.createMistake({ ...data, plan_id: planStore.currentPlan.id })
    }

    showForm.value = false
    editingMistake.value = null
    form.value = { ...defaultForm }
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

function exportMistakes() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先创建计划', icon: 'none' })
    return
  }
  const url = api.getExportMistakesUrl(planStore.currentPlan.id, filterSubject.value || undefined, null, null, filterMastered.value || undefined)
  uni.downloadFile({
    url,
    success: (res) => {
      uni.saveFile({
        tempFilePath: res.tempFilePath,
        success: () => uni.showToast({ title: '导出成功', icon: 'success' }),
        fail: () => uni.showToast({ title: '保存失败', icon: 'none' })
      })
    },
    fail: () => uni.showToast({ title: '导出失败', icon: 'none' })
  })
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    if (planStore.currentPlan) {
      await mistakeStore.getMistakesByPlanId(planStore.currentPlan.id)
    }
  }
})
</script>

<style lang="scss" scoped>
.header { display: flex; justify-content: space-between; align-items: center; padding: 40px 0 20px; .title { font-size: 22px; font-weight: 700; color: #1a1a2e; } .add-btn { width: 40px; height: 40px; background: #e65100; border-radius: 50%; display: flex; align-items: center; justify-content: center; } .add-icon { font-size: 24px; color: #fff; } }
.filters { margin-bottom: 16px; }
.filter-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.filter-label { font-size: 13px; color: #65746d; white-space: nowrap; }
.filter-options { display: flex; gap: 6px; flex-wrap: wrap; }
.filter-option { padding: 4px 12px; border-radius: 12px; font-size: 12px; color: #65746d; background: #f5f7f5; &.active { background: #e65100; color: #fff; } }
.mistake-list { display: flex; flex-direction: column; gap: 12px; }
.mistake-card { background: #fff; border-radius: 14px; padding: 16px; border: 1px solid #e8ece9; }
.mistake-header { margin-bottom: 8px; }
.mistake-question { font-size: 15px; color: #1a1a2e; line-height: 1.5; display: block; margin-bottom: 8px; }
.mistake-tags { display: flex; gap: 6px; }
.mistake-tag { font-size: 11px; padding: 3px 8px; border-radius: 8px; &.subject-tag { background: #e8f5e9; color: #2e7d32; } &.difficulty-tag { background: #fff3e0; color: #e65100; } &.mastered-tag { background: #ffebee; color: #c62828; &.mastered { background: #e8f5e9; color: #2e7d32; } } }
.mistake-body { background: #f5f7f5; border-radius: 10px; padding: 12px; margin-bottom: 8px; }
.mistake-section { margin-bottom: 8px; &:last-child { margin-bottom: 0; } }
.mistake-section-title { font-size: 13px; font-weight: 600; color: #65746d; display: block; margin-bottom: 4px; }
.mistake-section-text { font-size: 14px; color: #1a1a2e; line-height: 1.5; }
.mistake-stats { display: flex; gap: 16px; margin-top: 8px; }
.stat-item { font-size: 12px; color: #999; }
.mistake-actions { display: flex; gap: 12px; justify-content: flex-end; }
.mistake-action { font-size: 13px; color: #e65100; &.delete { color: #ef5350; } }
.empty { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .empty-icon { font-size: 48px; margin-bottom: 12px; } .empty-text { font-size: 16px; color: #65746d; } .empty-hint { font-size: 13px; color: #999; margin-top: 4px; } }
.export-section { padding: 16px 0; }
.export-btn { text-align: center; padding: 14px; background: #f5f7f5; border-radius: 12px; font-size: 15px; color: #e65100; font-weight: 500; border: 1px solid #e8ece9; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; }
.modal-content { background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #e65100; font-weight: 600; }
.form-group { margin-bottom: 16px; &.half { flex: 1; } }
.form-row { display: flex; gap: 12px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 60px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.difficulty-row { display: flex; gap: 8px; }
.diff-item { flex: 1; padding: 10px; text-align: center; border-radius: 10px; font-size: 13px; color: #65746d; background: #f5f7f5; &.active { background: #e65100; color: #fff; } }

.bottom-space { height: 100px; }
</style>