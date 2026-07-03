<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <text class="title">抗遗忘卡片</text>
        <text class="subtitle">艾宾浩斯记忆曲线，科学对抗遗忘</text>
      </view>
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-num">{{ pendingCards.length }}</text>
          <text class="stat-label">待复习</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ cards.length }}</text>
          <text class="stat-label">总卡片</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ masteredCount }}</text>
          <text class="stat-label">已掌握</text>
        </view>
      </view>
    </view>

    <!-- Mode Toggle -->
    <view class="mode-toggle">
      <view class="mode-btn" :class="{ active: viewMode === 'pending' }" @click="switchMode('pending')">今日复习</view>
      <view class="mode-btn" :class="{ active: viewMode === 'all' }" @click="switchMode('all')">查看全部</view>
    </view>

    <!-- Tag Filter -->
    <view class="filter-section" v-if="allTags.length > 0">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view class="filter-item" :class="{ active: activeTag === '' }" @click="activeTag = ''">全部</view>
          <view class="filter-item" v-for="t in allTags" :key="t" :class="{ active: activeTag === t }" @click="activeTag = t">{{ t }}</view>
        </view>
      </scroll-view>
    </view>

    <view class="card-list">
      <!-- Review Mode -->
      <view class="review-card" v-if="reviewMode && reviewCards.length > 0">
        <view class="review-progress">
          <text class="review-counter">{{ reviewIndex + 1 }} / {{ reviewCards.length }}</text>
          <view class="review-progress-bar">
            <view class="review-progress-fill" :style="{ width: ((reviewIndex + 1) / reviewCards.length * 100) + '%' }"></view>
          </view>
        </view>

        <view class="review-card-body">
          <view class="review-subject">{{ reviewCards[reviewIndex].subject }}</view>
          <view class="review-question">
            <text class="question-label">Q</text>
            <text class="question-text">{{ reviewCards[reviewIndex].question }}</text>
          </view>
          <view class="image-gallery" v-if="reviewCards[reviewIndex].image_urls && reviewCards[reviewIndex].image_urls.length > 0">
            <image v-for="(url, idx) in reviewCards[reviewIndex].image_urls" :key="idx" :src="url" mode="widthFix" class="review-image" @click="previewImage(url, reviewCards[reviewIndex].image_urls)" />
          </view>

          <view class="review-answer" v-if="reviewShowAnswer">
            <view class="answer-divider"></view>
            <view class="answer-content">
              <text class="answer-label">A</text>
              <text class="answer-text">{{ reviewCards[reviewIndex].answer }}</text>
            </view>
          </view>
        </view>

        <view class="review-actions">
          <view class="show-answer-btn" v-if="!reviewShowAnswer" @click="reviewShowAnswer = true">
            <text>点击查看答案</text>
          </view>
          <view class="review-result-btns" v-else>
            <view class="result-btn fail" @click="reviewResult('unmastered')">
              <text class="result-icon">😣</text>
              <text class="result-text">未掌握</text>
            </view>
            <view class="result-btn ok" @click="reviewResult('familiar')">
              <text class="result-icon">🤔</text>
              <text class="result-text">较熟悉</text>
            </view>
            <view class="result-btn great" @click="reviewResult('mastered')">
              <text class="result-icon">😎</text>
              <text class="result-text">已掌握</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Review Empty -->
      <view class="review-complete" v-if="reviewMode && reviewCards.length === 0">
        <text class="complete-icon">🎉</text>
        <text class="complete-text">今天没有需要复习的卡片</text>
        <view class="back-btn" @click="exitReview">查看全部</view>
      </view>

      <!-- Review Complete -->
      <view class="review-complete" v-if="reviewComplete">
        <text class="complete-icon">🏆</text>
        <text class="complete-text">复习完成！</text>
        <view class="back-btn" @click="exitReview">返回卡片列表</view>
      </view>

      <!-- Normal List -->
      <view v-if="!reviewMode && !reviewComplete">
        <view class="section-header" v-if="viewMode === 'pending' && filteredCards.length > 0">
          <text class="section-title">今日待复习 · {{ filteredCards.length }} 张</text>
          <view class="start-review-btn" @click="startReview"><text>开始复习</text></view>
        </view>

        <view class="section-header" v-if="viewMode === 'all'">
          <text class="section-title">全部卡片</text>
          <text class="section-count">{{ filteredCards.length }}张</text>
        </view>

        <view class="empty" v-if="filteredCards.length === 0">
          <text class="empty-icon">📖</text>
          <text class="empty-text">{{ viewMode === 'pending' ? '今天没有需要复习的卡片' : '暂无卡片' }}</text>
          <text class="empty-hint">点击右下角按钮，手动添加知识卡片</text>
        </view>

        <view class="card-item" v-for="card in filteredCards" :key="card.id" :class="{ 'not-today': card.next_review_date > today }">
          <view class="card-item-header">
            <text class="card-item-subject">{{ card.subject }}</text>
            <view class="card-item-tags">
              <view class="card-tag" v-for="t in (card.tags || [])" :key="t">{{ t }}</view>
              <view class="mastery-badge" :class="getMasteryClass(card.mastery_level)">
                {{ getMasteryLabel(card.mastery_level) }}
              </view>
            </view>
          </view>

          <view class="card-item-question">
            <text class="section-label">问题</text>
            <text class="card-question-text">{{ card.question }}</text>
          </view>

          <view class="card-item-footer">
            <text class="review-count">第{{ card.review_count }}次复习</text>
            <text class="review-date" v-if="card.next_review_date && card.next_review_date > today">下次 {{ formatDate(card.next_review_date) }}</text>
            <view class="card-item-actions">
              <view class="action-btn" @click="removeCard(card)">删除</view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- FAB -->
    <view class="fab" @click="showForm = true">
      <text class="fab-icon">+</text>
    </view>

    <!-- Add Card Modal -->
    <view class="modal-overlay" v-if="showForm" @click="showForm = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">添加知识卡片</text>
          <view class="modal-close" @click="showForm = false">✕</view>
        </view>

        <scroll-view scroll-y class="modal-body">
          <view class="form-group">
            <text class="form-label">科目</text>
            <view class="subject-grid">
              <view class="subject-item" v-for="s in allSubjects" :key="s" :class="{ active: form.subject === s }" @click="form.subject = s">{{ s }}</view>
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">自定义标签（逗号分隔，如：重点,公式,必考）</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="tagInput" placeholder="输入标签，逗号分隔..." @blur="parseTags" />
            </view>
            <view class="tag-preview" v-if="form.tags.length > 0">
              <view class="tag-chip" v-for="(t, idx) in form.tags" :key="idx">
                {{ t }}
                <text class="tag-remove" @click="form.tags.splice(idx, 1)">✕</text>
              </view>
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">问题</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.question" placeholder="请输入复习问题..." maxlength="2000" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">答案</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.answer" placeholder="请输入答案..." maxlength="2000" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">相关图片（可选，最多3张）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in form.image_urls" :key="idx">
                <image :src="img" mode="aspectFill" class="uploaded-image" />
                <view class="image-remove" @click="removeImage(idx)">✕</view>
              </view>
              <view class="image-add-btn" v-if="form.image_urls.length < 3" @click="chooseImage">
                <text class="add-icon">+</text>
                <text class="add-text">图片</text>
              </view>
            </view>
          </view>
        </scroll-view>

        <view class="modal-footer">
          <view class="cancel-btn" @click="showForm = false">取消</view>
          <view class="submit-btn" @click="submitCard">提交</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'

const planStore = usePlanStore()
const userStore = useUserStore()

const viewMode = ref('pending')  // 'all' | 'pending'
const activeTag = ref('')
const showForm = ref(false)
const reviewMode = ref(false)
const reviewShowAnswer = ref(false)
const reviewIndex = ref(0)
const reviewComplete = ref(false)
const cards = ref([])
const tagInput = ref('')
const today = new Date().toISOString().split('T')[0]

const allSubjects = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']

const form = ref({
  subject: '数据结构',
  question: '',
  answer: '',
  image_urls: [],
  tags: []
})

const allTags = computed(() => {
  const set = new Set()
  cards.value.forEach(c => (c.tags || []).forEach(t => set.add(t)))
  return [...set]
})

const filteredCards = computed(() => {
  if (activeTag.value) {
    return cards.value.filter(c => (c.tags || []).includes(activeTag.value))
  }
  return cards.value
})

const pendingCards = computed(() => {
  return cards.value.filter(c => c.next_review_date && c.next_review_date <= today)
})

const reviewCards = computed(() => {
  return filteredCards.value.filter(c => c.next_review_date && c.next_review_date <= today)
})

const masteredCount = computed(() => cards.value.filter(c => c.mastery_level === 'mastered').length)

const getMasteryLabel = (level) => {
  const map = { unmastered: '未掌握', familiar: '较熟悉', mastered: '已掌握' }
  return map[level] || level
}

const getMasteryClass = (level) => {
  const map = { unmastered: 'badge-red', familiar: 'badge-orange', mastered: 'badge-green' }
  return map[level] || ''
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

function parseTags() {
  if (!tagInput.value.trim()) return
  const tags = tagInput.value.split(/[,，]/).map(t => t.trim()).filter(Boolean)
  form.value.tags = [...new Set([...form.value.tags, ...tags])]
  tagInput.value = ''
}

function switchMode(mode) {
  viewMode.value = mode
  loadCards()
}

function chooseImage() {
  uni.chooseImage({
    count: 3 - form.value.image_urls.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.image_urls.push(path))
  })
}

function removeImage(idx) { form.value.image_urls.splice(idx, 1) }
function previewImage(current, urls) { uni.previewImage({ current, urls }) }

async function submitCard() {
  if (!form.value.question.trim()) { uni.showToast({ title: '请输入问题', icon: 'none' }); return }
  if (!form.value.answer.trim()) { uni.showToast({ title: '请输入答案', icon: 'none' }); return }
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }

  uni.showLoading({ title: '保存中...' })
  try {
    await api.createCard({
      plan_id: planStore.currentPlan.id,
      question: form.value.question,
      answer: form.value.answer,
      subject: form.value.subject,
      mastery_level: 'unmastered',
      next_review_date: today,
      image_urls: form.value.image_urls,
      tags: form.value.tags
    })
    resetForm()
    uni.showToast({ title: '添加成功', icon: 'success' })
    await loadCards()
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

function resetForm() {
  showForm.value = false
  form.value = { subject: '数据结构', question: '', answer: '', image_urls: [], tags: [] }
  tagInput.value = ''
}

function startReview() {
  reviewMode.value = true
  reviewShowAnswer.value = false
  reviewIndex.value = 0
  reviewComplete.value = false
}

async function reviewResult(level) {
  const currentCard = reviewCards.value[reviewIndex.value]
  await api.reviewCard(currentCard.id, level)

  if (reviewIndex.value < reviewCards.value.length - 1) {
    reviewIndex.value++
    reviewShowAnswer.value = false
  } else {
    reviewMode.value = false
    reviewComplete.value = true
    await loadCards()
  }
}

function exitReview() {
  reviewMode.value = false
  reviewComplete.value = false
  reviewIndex.value = 0
  viewMode.value = 'all'
  activeTag.value = ''
  loadCards()
}

async function removeCard(card) {
  const res = await new Promise(r => uni.showModal({ title: '删除确认', content: '确定删除吗？', success: r }))
  if (res.confirm) {
    try {
      await api.deleteCard(card.id)
      cards.value = cards.value.filter(c => c.id !== card.id)
      uni.showToast({ title: '已删除', icon: 'success' })
    } catch (e) {
      uni.showToast({ title: '删除失败', icon: 'none' })
    }
  }
}

async function loadCards() {
  if (!planStore.currentPlan) return
  try {
    const pending = viewMode.value === 'pending'
    const result = await api.getCards(planStore.currentPlan.id, null, activeTag.value || null, pending)
    cards.value = result.cards || []
  } catch (e) {
    console.error('Failed to load cards:', e)
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    await loadCards()
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, #6b4ce6 0%, #8b6ef5 100%);
  border-radius: 0 0 32px 32px;
  margin-bottom: 20px;
  margin-left: -20px;
  margin-right: -20px;
  padding-left: 20px;
  padding-right: 20px;
}

.header-top {
  margin-bottom: 16px;
  .title { display: block; font-size: 26px; font-weight: 700; color: #fff; margin-bottom: 4px; }
  .subtitle { font-size: 14px; color: rgba(255,255,255,0.8); }
}

.stats-row {
  display: flex; background: rgba(255,255,255,0.12); border-radius: 16px; padding: 16px; border: 1px solid rgba(255,255,255,0.15);
}
.stat-item {
  flex: 1; text-align: center;
  .stat-num { display: block; font-size: 22px; font-weight: 700; color: #fff; }
  .stat-label { font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 2px; }
}

/* Mode Toggle */
.mode-toggle {
  display: flex; margin-bottom: 16px; background: #f5f7f5; border-radius: 12px; padding: 4px;
}
.mode-btn {
  flex: 1; text-align: center; padding: 10px; border-radius: 10px; font-size: 14px; color: #65746d; transition: all 0.2s;
  &.active { background: #fff; color: #6b4ce6; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
}

/* Tag Filter */
.filter-section { margin-bottom: 14px; }
.filter-scroll { white-space: nowrap; }
.filter-list { display: flex; gap: 8px; }
.filter-item {
  padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; white-space: nowrap; transition: all 0.2s;
  &.active { background: #6b4ce6; color: #fff; }
}

/* Section Header */
.section-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;
  .section-title { font-size: 18px; font-weight: 600; color: #1a1a2e; }
  .section-count { font-size: 13px; color: #999; }
}
.start-review-btn {
  background: #6b4ce6; color: #fff; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 500; transition: all 0.2s;
  &:active { transform: scale(0.96); }
}

/* Card Item */
.card-item {
  background: #fff; border-radius: 16px; padding: 18px; margin-bottom: 12px; border: 1px solid #e8ece9; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  &.not-today { opacity: 0.6; }
}
.card-item-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
  .card-item-subject { font-size: 12px; padding: 4px 12px; background: #f3f0ff; border-radius: 20px; color: #6b4ce6; }
}
.card-item-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.card-tag {
  font-size: 11px; padding: 3px 8px; border-radius: 8px; background: #f5f5f5; color: #65746d;
}
.mastery-badge {
  font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 500;
  &.badge-red { background: #ffebee; color: #c62828; }
  &.badge-orange { background: #fff3e0; color: #e65100; }
  &.badge-green { background: #e8f5e9; color: #2e7d32; }
}

.section-label { display: block; font-size: 12px; color: #6b4ce6; margin-bottom: 6px; font-weight: 500; }
.card-question-text { font-size: 15px; color: #1a1a2e; line-height: 1.6; display: block; }

.card-item-footer {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-top: 12px;
  .review-count { font-size: 12px; color: #999; }
  .review-date { font-size: 12px; color: #6b4ce6; }
  .card-item-actions { display: flex; gap: 8px; margin-left: auto; }
}
.action-btn {
  padding: 6px 14px; border-radius: 8px; font-size: 13px; background: #f5f5f5; color: #999;
}

/* Review Card */
.review-card {
  background: #fff; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); margin-bottom: 20px;
}
.review-progress {
  margin-bottom: 20px;
  .review-counter { display: block; font-size: 14px; color: #6b4ce6; font-weight: 600; margin-bottom: 8px; }
  .review-progress-bar { height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden; }
  .review-progress-fill { height: 100%; background: #6b4ce6; border-radius: 3px; transition: width 0.3s; }
}
.review-card-body { min-height: 160px; }
.review-subject {
  font-size: 13px; color: #6b4ce6; background: #f3f0ff; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 16px;
}
.review-question { display: flex; gap: 12px; margin-bottom: 16px; }
.question-label { font-size: 32px; font-weight: 800; color: #6b4ce6; line-height: 1; flex-shrink: 0; }
.question-text { font-size: 18px; color: #1a1a2e; line-height: 1.6; font-weight: 500; }
.image-gallery { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.review-image { width: 120px; border-radius: 8px; border: 1px solid #e8ece9; }
.answer-divider { height: 1px; background: #e8ece9; margin: 16px 0; }
.answer-content { display: flex; gap: 12px; }
.answer-label { font-size: 32px; font-weight: 800; color: #2e7d32; line-height: 1; flex-shrink: 0; }
.answer-text { font-size: 16px; color: #1a1a2e; line-height: 1.7; }

.review-actions { margin-top: 20px; }
.show-answer-btn {
  text-align: center; padding: 16px; background: #f3f0ff; border-radius: 14px; transition: all 0.2s;
  &:active { transform: scale(0.98); background: #e8e0ff; }
  text { font-size: 16px; color: #6b4ce6; font-weight: 600; }
}
.review-result-btns { display: flex; gap: 12px; }
.result-btn {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 8px; border-radius: 14px; transition: all 0.2s;
  &:active { transform: scale(0.96); }
  &.fail { background: #fff0f0; .result-text { color: #c62828; } }
  &.ok { background: #fff8f0; .result-text { color: #e65100; } }
  &.great { background: #f0fff4; .result-text { color: #2e7d32; } }
  .result-icon { font-size: 24px; }
  .result-text { font-size: 13px; font-weight: 500; }
}
.review-complete {
  display: flex; flex-direction: column; align-items: center; padding: 60px 20px;
  .complete-icon { font-size: 56px; margin-bottom: 12px; }
  .complete-text { font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; }
  .back-btn { padding: 12px 28px; background: #6b4ce6; color: #fff; border-radius: 25px; font-size: 15px; font-weight: 500; }
}

/* FAB */
.fab {
  position: fixed; right: 20px; bottom: 60px; z-index: 50; width: 56px; height: 56px; border-radius: 50%;
  background: #6b4ce6; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(107,76,230,0.35);
  &:active { transform: scale(0.92); }
  .fab-icon { font-size: 28px; color: #fff; font-weight: 300; }
}

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end;
}
.modal-content {
  background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh; display: flex; flex-direction: column;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0;
  .modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
  .modal-close { font-size: 20px; color: #999; padding: 4px; }
}
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer {
  display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0;
  .cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
  .submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #6b4ce6; font-weight: 600; }
}

.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-item {
  padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; transition: all 0.2s;
  &.active { background: #6b4ce6; color: #fff; }
}
.tag-preview { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.tag-chip {
  padding: 4px 10px; border-radius: 12px; font-size: 12px; background: #f3f0ff; color: #6b4ce6; display: flex; align-items: center; gap: 4px;
}
.tag-remove { font-size: 14px; color: #6b4ce6; }
.input-wrapper {
  border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; transition: border-color 0.2s;
  &:focus-within { border-color: #6b4ce6; }
}
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field {
  width: 100%; min-height: 80px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none;
}
.image-upload-area { display: flex; gap: 10px; flex-wrap: wrap; }
.image-item { position: relative; width: 80px; height: 80px; }
.uploaded-image { width: 80px; height: 80px; border-radius: 10px; }
.image-remove {
  position: absolute; top: -6px; right: -6px; width: 22px; height: 22px; border-radius: 50%; background: #ef5350; color: #fff; font-size: 12px;
  display: flex; align-items: center; justify-content: center;
}
.image-add-btn {
  width: 80px; height: 80px; border-radius: 10px; border: 2px dashed #d0d5d2; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 4px; background: #fafafa;
  .add-icon { font-size: 24px; color: #999; }
  .add-text { font-size: 11px; color: #999; }
}

.empty {
  display: flex; flex-direction: column; align-items: center; padding: 60px 20px;
  .empty-icon { font-size: 48px; margin-bottom: 12px; }
  .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; }
  .empty-hint { font-size: 13px; color: #999; text-align: center; }
}
.bottom-space { height: 100px; }
</style>