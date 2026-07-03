<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <text class="title">抗遗忘卡片</text>
        <text class="date">{{ formattedDate }}</text>
      </view>
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-num">{{ pendingCards.length }}</text>
          <text class="stat-label">待复习</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ cardStore.cards.length }}</text>
          <text class="stat-label">总卡片</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ masteredCount }}</text>
          <text class="stat-label">已掌握</text>
        </view>
      </view>
    </view>

    <!-- Review Mode -->
    <view class="review-card" v-if="reviewMode && currentCard">
      <view class="card-face">
        <view class="card-subject">{{ currentCard.subject }}</view>
        <view class="card-question">
          <text class="question-label">Q</text>
          <text class="question-text">{{ currentCard.question }}</text>
        </view>
        <view class="card-answer" v-if="showAnswer">
          <view class="answer-divider"></view>
          <view class="answer-content">
            <text class="answer-label">A</text>
            <text class="answer-text">{{ currentCard.answer }}</text>
          </view>
        </view>
      </view>
      
      <view class="review-actions" v-if="showAnswer">
        <text class="actions-title">掌握程度如何？</text>
        <view class="action-buttons">
          <view class="action-btn fail" @click="markMastery('unmastered')">
            <text class="btn-icon">😣</text>
            <text class="btn-text">未掌握</text>
          </view>
          <view class="action-btn ok" @click="markMastery('familiar')">
            <text class="btn-icon">🤔</text>
            <text class="btn-text">较熟悉</text>
          </view>
          <view class="action-btn great" @click="markMastery('mastered')">
            <text class="btn-icon">😎</text>
            <text class="btn-text">已掌握</text>
          </view>
        </view>
      </view>
      
      <view class="show-answer-btn" v-else @click="showAnswer = true">
        <text>点击查看答案</text>
      </view>
    </view>

    <!-- Card List -->
    <view class="card-list" v-if="!reviewMode">
      <view class="section-header">
        <text class="section-title">今日待复习</text>
        <view class="start-review-btn" v-if="pendingCards.length > 0" @click="startReview">
          <text>开始复习</text>
        </view>
      </view>

      <view class="empty" v-if="pendingCards.length === 0">
        <text class="empty-icon">🎉</text>
        <text class="empty-text">今天没有需要复习的卡片</text>
        <text class="empty-hint">完成学习后，AI 会自动生成复习卡片</text>
      </view>

      <view class="card-item" v-for="card in pendingCards" :key="card.id">
        <view class="card-item-left">
          <text class="card-item-subject">{{ card.subject }}</text>
          <text class="card-item-question">{{ card.question }}</text>
        </view>
        <view class="card-item-right">
          <view class="mastery-badge" :class="getMasteryClass(card.mastery_level)">
            {{ getMasteryLabel(card.mastery_level) }}
          </view>
          <text class="review-count">第{{ card.review_count }}次</text>
        </view>
      </view>

      <view class="section-header mt-24">
        <text class="section-title">全部卡片</text>
        <text class="section-count">{{ cardStore.cards.length }}张</text>
      </view>

      <view class="card-item" v-for="card in cardStore.cards" :key="card.id" :class="{ 'not-today': card.next_review_date > today }">
        <view class="card-item-left">
          <text class="card-item-subject">{{ card.subject }}</text>
          <text class="card-item-question">{{ card.question }}</text>
        </view>
        <view class="card-item-right">
          <view class="mastery-badge" :class="getMasteryClass(card.mastery_level)">
            {{ getMasteryLabel(card.mastery_level) }}
          </view>
          <text class="review-date" v-if="card.next_review_date > today">{{ formatDate(card.next_review_date) }}</text>
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
              <view class="subject-item" v-for="s in allSubjects" :key="s" :class="{ active: cardForm.subject === s }" @click="cardForm.subject = s">{{ s }}</view>
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">问题</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="cardForm.question" placeholder="请输入复习问题..." maxlength="2000" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">答案</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="cardForm.answer" placeholder="请输入答案..." maxlength="2000" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">相关图片（可选，最多3张）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in cardForm.image_urls" :key="idx">
                <image :src="img" mode="aspectFill" class="uploaded-image" />
                <view class="image-remove" @click="removeCardImage(idx)">✕</view>
              </view>
              <view class="image-add-btn" v-if="cardForm.image_urls.length < 3" @click="chooseCardImage">
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
import { ref, computed } from 'vue'
import { useCardStore } from '@/stores/card'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'

const cardStore = useCardStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const reviewMode = ref(false)
const showAnswer = ref(false)
const currentCardIndex = ref(0)
const showForm = ref(false)
const today = new Date().toISOString().split('T')[0]

const allSubjects = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']

const cardForm = ref({
  subject: '数据结构',
  question: '',
  answer: '',
  image_urls: []
})

const formattedDate = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})

const pendingCards = computed(() => {
  return cardStore.cards.filter(c => c.next_review_date <= today)
})

const currentCard = computed(() => {
  return pendingCards.value[currentCardIndex.value] || null
})

const masteredCount = computed(() => {
  return cardStore.cards.filter(c => c.mastery_level === 'mastered').length
})

const getMasteryLabel = (level) => {
  const map = { unmastered: '未掌握', familiar: '较熟悉', mastered: '已掌握' }
  return map[level] || level
}

const getMasteryClass = (level) => {
  const map = { unmastered: 'badge-red', familiar: 'badge-orange', mastered: 'badge-green' }
  return map[level] || ''
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function startReview() {
  currentCardIndex.value = 0
  showAnswer.value = false
  reviewMode.value = true
}

async function markMastery(level) {
  if (!currentCard.value) return
  await cardStore.markMastery(currentCard.value.id, level)
  showAnswer.value = false

  if (currentCardIndex.value < pendingCards.value.length - 1) {
    currentCardIndex.value++
  } else {
    reviewMode.value = false
    uni.showToast({ title: '🎉 复习完成！', icon: 'none' })
  }
}

function chooseCardImage() {
  uni.chooseImage({
    count: 3 - cardForm.value.image_urls.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      res.tempFilePaths.forEach(path => {
        cardForm.value.image_urls.push(path)
      })
    }
  })
}

function removeCardImage(idx) {
  cardForm.value.image_urls.splice(idx, 1)
}

async function submitCard() {
  if (!cardForm.value.question.trim()) {
    uni.showToast({ title: '请输入问题', icon: 'none' })
    return
  }
  if (!cardForm.value.answer.trim()) {
    uni.showToast({ title: '请输入答案', icon: 'none' })
    return
  }
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先创建学习计划', icon: 'none' })
    return
  }

  uni.showLoading({ title: '保存中...' })
  try {
    const data = {
      plan_id: planStore.currentPlan.id,
      question: cardForm.value.question,
      answer: cardForm.value.answer,
      subject: cardForm.value.subject,
      mastery_level: 'unmastered',
      next_review_date: today,
      image_urls: cardForm.value.image_urls
    }
    await cardStore.createCard(data)
    showForm.value = false
    cardForm.value = { subject: '数据结构', question: '', answer: '', image_urls: [] }
    // Reload cards
    await cardStore.getCardsByPlanId(planStore.currentPlan.id)
    uni.showToast({ title: '添加成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
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
  padding: 60px 0 20px;
  background: linear-gradient(135deg, #6b4ce6 0%, #8b6ef5 100%);
  border-radius: 0 0 32px 32px;
  margin-bottom: 24px;
  margin-left: -20px;
  margin-right: -20px;
  padding-left: 20px;
  padding-right: 20px;
}

.header-top {
  margin-bottom: 16px;
  
  .title {
    display: block;
    font-size: 26px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 4px;
  }
  .date {
    font-size: 14px;
    color: rgba(255,255,255,0.8);
  }
}

.stats-row {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(255,255,255,0.15);
}

.stat-item {
  flex: 1;
  text-align: center;
  
  .stat-num {
    display: block;
    font-size: 22px;
    font-weight: 700;
    color: #fff;
  }
  .stat-label {
    font-size: 12px;
    color: rgba(255,255,255,0.7);
    margin-top: 2px;
  }
}

/* Review Card */
.review-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  margin-bottom: 20px;
}

.card-face {
  min-height: 200px;
}

.card-subject {
  font-size: 13px;
  color: #6b4ce6;
  background: #f3f0ff;
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
  margin-bottom: 16px;
}

.card-question {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.question-label {
  font-size: 32px;
  font-weight: 800;
  color: #6b4ce6;
  line-height: 1;
  flex-shrink: 0;
}

.question-text {
  font-size: 18px;
  color: #1a1a2e;
  line-height: 1.6;
  font-weight: 500;
}

.answer-divider {
  height: 1px;
  background: #e8ece9;
  margin-bottom: 16px;
}

.answer-content {
  display: flex;
  gap: 12px;
}

.answer-label {
  font-size: 32px;
  font-weight: 800;
  color: #2f7d4f;
  line-height: 1;
  flex-shrink: 0;
}

.answer-text {
  font-size: 16px;
  color: #1a1a2e;
  line-height: 1.7;
}

.show-answer-btn {
  text-align: center;
  padding: 16px;
  background: #f3f0ff;
  border-radius: 14px;
  margin-top: 20px;
  transition: all 0.2s;
  
  &:active {
    transform: scale(0.98);
    background: #e8e0ff;
  }
  
  text {
    font-size: 16px;
    color: #6b4ce6;
    font-weight: 600;
  }
}

.review-actions {
  margin-top: 20px;
  
  .actions-title {
    display: block;
    text-align: center;
    font-size: 14px;
    color: #999;
    margin-bottom: 14px;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border-radius: 14px;
  transition: all 0.2s;
  
  &:active { transform: scale(0.96); }
  
  &.fail { background: #fff0f0; }
  &.ok { background: #fff8f0; }
  &.great { background: #f0fff4; }
  
  .btn-icon { font-size: 24px; }
  .btn-text { font-size: 13px; font-weight: 500; }
}

/* Card List */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
}

.section-count {
  font-size: 13px;
  color: #999;
}

.start-review-btn {
  background: #6b4ce6;
  color: #fff;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  
  &:active { transform: scale(0.96); }
}

.card-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 14px;
  padding: 14px 16px;
  margin-bottom: 10px;
  border: 1px solid #e8ece9;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  
  &.not-today {
    opacity: 0.6;
  }
}

.card-item-left {
  flex: 1;
  min-width: 0;
  
  .card-item-subject {
    font-size: 12px;
    color: #6b4ce6;
    background: #f3f0ff;
    padding: 2px 8px;
    border-radius: 8px;
    margin-bottom: 6px;
    display: inline-block;
  }
  
  .card-item-question {
    display: block;
    font-size: 14px;
    color: #1a1a2e;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.5;
  }
}

.card-item-right {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  margin-left: 12px;
}

.mastery-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;
  
  &.badge-red { background: #ffebee; color: #c62828; }
  &.badge-orange { background: #fff3e0; color: #e65100; }
  &.badge-green { background: #e8f5e9; color: #2e7d32; }
}

.review-count, .review-date {
  font-size: 11px;
  color: #999;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  
  .empty-icon { font-size: 48px; margin-bottom: 12px; }
  .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; }
  .empty-hint { font-size: 13px; color: #999; text-align: center; }
}

.mt-24 { margin-top: 24px; }
.bottom-space { height: 100px; }

/* FAB */
.fab {
  position: fixed; right: 20px; bottom: 60px; z-index: 50;
  width: 56px; height: 56px; border-radius: 50%; background: #6b4ce6;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 16px rgba(107,76,230,0.35);
  transition: all 0.2s;
  &:active { transform: scale(0.92); }
  .fab-icon { font-size: 28px; color: #fff; font-weight: 300; }
}

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100;
  display: flex; align-items: flex-end;
}
.modal-content {
  background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh;
  display: flex; flex-direction: column;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px; border-bottom: 1px solid #f0f0f0;
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
  padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d;
  background: #f5f7f5; transition: all 0.2s;
  &.active { background: #6b4ce6; color: #fff; }
}

.input-wrapper {
  border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa;
  transition: border-color 0.2s;
  &:focus-within { border-color: #6b4ce6; }
}
.textarea-field {
  width: 100%; min-height: 80px; font-size: 15px; color: #1a1a2e; line-height: 1.6;
  border: none; outline: none; background: transparent; resize: none;
}

.image-upload-area { display: flex; gap: 10px; flex-wrap: wrap; }
.image-item { position: relative; width: 80px; height: 80px; }
.uploaded-image { width: 80px; height: 80px; border-radius: 10px; }
.image-remove {
  position: absolute; top: -6px; right: -6px; width: 22px; height: 22px;
  border-radius: 50%; background: #ef5350; color: #fff; font-size: 12px;
  display: flex; align-items: center; justify-content: center;
}
.image-add-btn {
  width: 80px; height: 80px; border-radius: 10px; border: 2px dashed #d0d5d2;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 4px; background: #fafafa;
  .add-icon { font-size: 24px; color: #999; }
  .add-text { font-size: 11px; color: #999; }
}
</style>