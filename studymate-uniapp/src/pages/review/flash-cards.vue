<template>
  <view class="page">
    <view class="header">
      <text class="title">知识卡片</text>
      <view class="header-actions">
        <view class="add-btn" @click="showForm = true; editingCard = null">
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
        <text class="filter-label">掌握度:</text>
        <view class="filter-options">
          <view class="filter-option" :class="{ active: filterMastery === '' }" @click="filterMastery = ''">全部</view>
          <view class="filter-option" :class="{ active: filterMastery === 'low' }" @click="filterMastery = 'low'">未掌握</view>
          <view class="filter-option" :class="{ active: filterMastery === 'medium' }" @click="filterMastery = 'medium'">一般</view>
          <view class="filter-option" :class="{ active: filterMastery === 'high' }" @click="filterMastery = 'high'">已掌握</view>
        </view>
      </view>
    </view>

    <view class="card-list">
      <view class="flash-card" v-for="card in filteredCards" :key="card.id">
        <view class="card-front">
          <text class="card-question">{{ card.question }}</text>
          <view class="card-tags">
            <text class="card-tag subject-tag">{{ card.subject }}</text>
            <text class="card-tag mastery-tag" :class="getMasteryClass(card.mastery_level)">{{ getMasteryLabel(card.mastery_level) }}</text>
          </view>
        </view>
        <view class="card-answer" v-if="expandedCard === card.id">
          <text class="answer-text">{{ card.answer }}</text>
        </view>
        <view class="card-actions">
          <view class="card-action" @click="toggleCard(card.id)">
            <text>{{ expandedCard === card.id ? '收起' : '展开答案' }}</text>
          </view>
          <view class="card-action" @click="editCard(card)">
            <text>编辑</text>
          </view>
          <view class="card-action delete" @click="deleteCard(card)">
            <text>删除</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty" v-if="filteredCards.length === 0">
      <text class="empty-icon">🃏</text>
      <text class="empty-text">暂无知识卡片</text>
      <text class="empty-hint">点击 + 创建新卡片</text>
    </view>

    <!-- Export Button -->
    <view class="export-section">
      <view class="export-btn" @click="exportCards">
        <text>📥 导出CSV</text>
      </view>
    </view>

    <!-- Add/Edit Form Modal -->
    <view class="modal-overlay" v-if="showForm" @click="showForm = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingCard ? '编辑卡片' : '新建卡片' }}</text>
          <view class="modal-close" @click="showForm = false">✕</view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="form-group">
            <text class="form-label">科目</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="form.subject" placeholder="如：数据结构" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">问题</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.question" placeholder="请输入问题..." />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">答案</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.answer" placeholder="请输入答案..." />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">掌握程度</text>
            <view class="mastery-row">
              <view class="mastery-item" :class="{ active: form.mastery_level === 'low' }" @click="form.mastery_level = 'low'">未掌握</view>
              <view class="mastery-item" :class="{ active: form.mastery_level === 'medium' }" @click="form.mastery_level = 'medium'">一般</view>
              <view class="mastery-item" :class="{ active: form.mastery_level === 'high' }" @click="form.mastery_level = 'high'">已掌握</view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">标签（逗号分隔）</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="form.tags" placeholder="如：二叉树, 遍历" />
            </view>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showForm = false">取消</view>
          <view class="submit-btn" @click="submitForm">{{ editingCard ? '保存' : '创建' }}</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCardStore } from '@/stores/card'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'

const cardStore = useCardStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const expandedCard = ref(null)
const showForm = ref(false)
const editingCard = ref(null)
const filterSubject = ref('')
const filterMastery = ref('')

const defaultForm = { subject: '', question: '', answer: '', mastery_level: 'medium', tags: '' }
const form = ref({ ...defaultForm })

const subjects = computed(() => {
  const set = new Set()
  cardStore.cards.forEach(c => set.add(c.subject))
  return [...set]
})

const filteredCards = computed(() => {
  let cards = cardStore.cards
  if (filterSubject.value) cards = cards.filter(c => c.subject === filterSubject.value)
  if (filterMastery.value) cards = cards.filter(c => c.mastery_level === filterMastery.value)
  return cards
})

const getMasteryLabel = (level) => {
  const map = { low: '未掌握', medium: '一般', high: '已掌握' }
  return map[level] || '未知'
}

const getMasteryClass = (level) => {
  const map = { low: 'mastery-low', medium: 'mastery-medium', high: 'mastery-high' }
  return map[level] || ''
}

function toggleCard(id) {
  expandedCard.value = expandedCard.value === id ? null : id
}

function editCard(card) {
  editingCard.value = card
  form.value = {
    subject: card.subject,
    question: card.question,
    answer: card.answer,
    mastery_level: card.mastery_level,
    tags: (card.tags || []).join(', ')
  }
  showForm.value = true
}

async function deleteCard(card) {
  uni.showModal({
    title: '删除确认',
    content: '确定要删除这张卡片吗？',
    success: async (res) => {
      if (res.confirm) {
        await cardStore.deleteCard(card.id)
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
      mastery_level: form.value.mastery_level,
      tags: form.value.tags ? form.value.tags.split(',').map(t => t.trim()).filter(Boolean) : []
    }

    if (editingCard.value) {
      await cardStore.updateCard(editingCard.value.id, data)
    } else {
      if (!planStore.currentPlan) {
        uni.showToast({ title: '请先创建学习计划', icon: 'none' })
        return
      }
      await cardStore.createCard({ ...data, plan_id: planStore.currentPlan.id })
    }

    showForm.value = false
    editingCard.value = null
    form.value = { ...defaultForm }
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

function exportCards() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先创建计划', icon: 'none' })
    return
  }
  const url = api.getExportCardsUrl(planStore.currentPlan.id, filterSubject.value || undefined, null, filterMastery.value || undefined)
  // Open in browser or download
  uni.downloadFile({
    url,
    success: (res) => {
      uni.saveFile({
        tempFilePath: res.tempFilePath,
        success: () => {
          uni.showToast({ title: '导出成功', icon: 'success' })
        },
        fail: () => {
          uni.showToast({ title: '保存失败', icon: 'none' })
        }
      })
    },
    fail: () => {
      uni.showToast({ title: '导出失败', icon: 'none' })
    }
  })
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    if (planStore.currentPlan) {
      await cardStore.getCardsByPlanId(planStore.currentPlan.id)
    }
  }
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40px 0 20px;
  .title { font-size: 22px; font-weight: 700; color: #1a1a2e; }
  .add-btn { width: 40px; height: 40px; background: #2f7d4f; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
  .add-icon { font-size: 24px; color: #fff; }
}

.filters { margin-bottom: 16px; }
.filter-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.filter-label { font-size: 13px; color: #65746d; white-space: nowrap; }
.filter-options { display: flex; gap: 6px; flex-wrap: wrap; }
.filter-option { padding: 4px 12px; border-radius: 12px; font-size: 12px; color: #65746d; background: #f5f7f5; &.active { background: #2f7d4f; color: #fff; } }

.card-list { display: flex; flex-direction: column; gap: 12px; }
.flash-card { background: #fff; border-radius: 14px; padding: 16px; border: 1px solid #e8ece9; }
.card-front { margin-bottom: 8px; }
.card-question { font-size: 15px; color: #1a1a2e; line-height: 1.5; display: block; margin-bottom: 8px; }
.card-tags { display: flex; gap: 6px; }
.card-tag { font-size: 11px; padding: 3px 8px; border-radius: 8px; &.subject-tag { background: #e8f5e9; color: #2e7d32; } &.mastery-low { background: #ffebee; color: #c62828; } &.mastery-medium { background: #fff3e0; color: #e65100; } &.mastery-high { background: #e8f5e9; color: #2e7d32; } }
.card-answer { background: #f5f7f5; border-radius: 10px; padding: 12px; margin-bottom: 8px; }
.answer-text { font-size: 14px; color: #65746d; line-height: 1.5; }
.card-actions { display: flex; gap: 12px; justify-content: flex-end; }
.card-action { font-size: 13px; color: #2f7d4f; &.delete { color: #ef5350; } }

.empty { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .empty-icon { font-size: 48px; margin-bottom: 12px; } .empty-text { font-size: 16px; color: #65746d; } .empty-hint { font-size: 13px; color: #999; margin-top: 4px; } }

.export-section { padding: 16px 0; }
.export-btn { text-align: center; padding: 14px; background: #f5f7f5; border-radius: 12px; font-size: 15px; color: #2f7d4f; font-weight: 500; border: 1px solid #e8ece9; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; }
.modal-content { background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #2f7d4f; font-weight: 600; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 60px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.mastery-row { display: flex; gap: 8px; }
.mastery-item { flex: 1; padding: 10px; text-align: center; border-radius: 10px; font-size: 13px; color: #65746d; background: #f5f7f5; &.active { background: #2f7d4f; color: #fff; } }

.bottom-space { height: 100px; }
</style>