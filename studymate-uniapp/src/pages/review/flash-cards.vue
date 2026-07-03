<template>
  <view class="page">
    <view class="header">
      <text class="page-title">复习卡片</text>
      <view class="card-count">
        <text class="count-value">{{ cardStore.pendingCards.length }}</text>
        <text class="count-label">待复习</text>
      </view>
    </view>

    <view class="mode-tabs">
      <view class="mode-tab" :class="{ active: reviewMode === 'review' }" @click="reviewMode = 'review'">
        <text class="tab-icon">📖</text>
        <text class="tab-text">复习模式</text>
      </view>
      <view class="mode-tab" :class="{ active: reviewMode === 'browse' }" @click="reviewMode = 'browse'">
        <text class="tab-icon">📋</text>
        <text class="tab-text">浏览模式</text>
      </view>
    </view>

    <view class="review-mode" v-if="reviewMode === 'review'">
      <view class="progress-info">
        <text class="progress-text">{{ currentIndex + 1 }} / {{ cardStore.pendingCards.length }}</text>
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
      </view>

      <view class="card-container" v-if="currentCard">
        <view class="flash-card" :class="{ flipped: isFlipped }" @click="flipCard">
          <view class="card-front">
            <text class="card-subject">{{ currentCard.subject }}</text>
            <text class="card-question">{{ currentCard.question }}</text>
            <text class="card-hint">点击查看答案</text>
          </view>
          <view class="card-back">
            <text class="card-subject">{{ currentCard.subject }}</text>
            <text class="card-answer">{{ currentCard.answer }}</text>
            <text class="card-hint">点击选择掌握程度</text>
          </view>
        </view>

        <view class="mastery-buttons" v-if="isFlipped">
          <view class="mastery-btn unmastered" @click="markMastery('unmastered')">
            <text class="mastery-icon">😅</text>
            <text class="mastery-text">未掌握</text>
            <text class="mastery-days">1天后复习</text>
          </view>
          <view class="mastery-btn familiar" @click="markMastery('familiar')">
            <text class="mastery-icon">🤔</text>
            <text class="mastery-text">较熟悉</text>
            <text class="mastery-days">3天后复习</text>
          </view>
          <view class="mastery-btn mastered" @click="markMastery('mastered')">
            <text class="mastery-icon">😎</text>
            <text class="mastery-text">已掌握</text>
            <text class="mastery-days">7天后复习</text>
          </view>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="empty-icon">🎉</text>
        <text class="empty-text">今日复习完成！</text>
        <text class="empty-hint">所有卡片都已复习完毕</text>
      </view>
    </view>

    <view class="browse-mode" v-if="reviewMode === 'browse'">
      <view class="filter-row">
        <scroll-view scroll-x class="filter-scroll">
          <view class="filter-list">
            <view class="filter-item" :class="{ active: activeFilter === 'all' }" @click="activeFilter = 'all'">
              全部
            </view>
            <view class="filter-item" :class="{ active: activeFilter === subject }" v-for="subject in subjects" :key="subject" @click="activeFilter = subject">
              {{ subject }}
            </view>
          </view>
        </scroll-view>
      </view>

      <view class="card-list">
        <view class="browse-card" v-for="card in filteredCards" :key="card.id">
          <view class="card-header">
            <text class="card-subject">{{ card.subject }}</text>
            <view class="mastery-badge" :class="card.mastery_level">
              {{ masteryText(card.mastery_level) }}
            </view>
          </view>
          <text class="card-question">{{ card.question }}</text>
          <text class="card-answer">{{ card.answer }}</text>
          <view class="card-footer">
            <text class="review-count">已复习 {{ card.review_count }} 次</text>
            <text class="next-review">下次复习：{{ card.next_review_date }}</text>
          </view>
          <view class="card-actions">
            <view class="action-btn" @click="editCard(card)">编辑</view>
            <view class="action-btn delete" @click="deleteCard(card)">删除</view>
          </view>
        </view>

        <view class="empty-state" v-if="filteredCards.length === 0">
          <text class="empty-icon">📚</text>
          <text class="empty-text">暂无卡片</text>
          <text class="empty-hint">点击下方按钮添加卡片</text>
        </view>
      </view>
    </view>

    <view class="fab-area">
      <view class="fab" @click="addCard">
        <text class="fab-icon">+</text>
        <text class="fab-text">添加卡片</text>
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

const cardStore = useCardStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const reviewMode = ref('review')
const activeFilter = ref('all')
const isFlipped = ref(false)
const currentIndex = ref(0)

const currentCard = computed(() => {
  return cardStore.pendingCards[currentIndex.value] || null
})

const progressPercent = computed(() => {
  if (cardStore.pendingCards.length === 0) return 100
  return Math.round((currentIndex.value / cardStore.pendingCards.length) * 100)
})

const subjects = computed(() => {
  return [...new Set(cardStore.cards.map(c => c.subject))]
})

const filteredCards = computed(() => {
  let cards = cardStore.cards
  if (activeFilter.value !== 'all') {
    cards = cards.filter(c => c.subject === activeFilter.value)
  }
  return cards
})

function masteryText(level) {
  const map = {
    unmastered: '未掌握',
    familiar: '较熟悉',
    mastered: '已掌握'
  }
  return map[level] || level
}

function flipCard() {
  isFlipped.value = !isFlipped.value
}

async function markMastery(level) {
  if (!currentCard.value) return

  const result = await cardStore.markMastery(currentCard.value.id, level)
  
  if (result.success) {
    uni.showToast({ title: '已更新掌握程度', icon: 'success' })
    isFlipped.value = false
    
    if (currentIndex.value < cardStore.pendingCards.length - 1) {
      currentIndex.value++
    } else {
      currentIndex.value = 0
      await loadCards()
    }
  }
}

function editCard(card) {
  uni.showModal({
    title: '编辑卡片',
    editable: true,
    placeholderText: '请输入卡片内容',
    success: async (res) => {
      if (res.confirm && res.content) {
        await cardStore.updateCard(card.id, { content: res.content })
      }
    }
  })
}

async function deleteCard(card) {
  uni.showModal({
    title: '删除卡片',
    content: '确定要删除这张卡片吗？',
    success: async (res) => {
      if (res.confirm) {
        await cardStore.deleteCard(card.id)
        uni.showToast({ title: '删除成功', icon: 'success' })
      }
    }
  })
}

async function addCard() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先设置学习计划', icon: 'none' })
    return
  }

  uni.showModal({
    title: '添加卡片',
    editable: true,
    placeholderText: '请输入学习内容，AI将自动生成问答卡片',
    success: async (res) => {
      if (res.confirm && res.content) {
        uni.showLoading({ title: 'AI生成卡片中...' })
        
        try {
          const result = await cardStore.generateCardsByAI(res.content)
          
          if (result.cards && result.cards.length > 0) {
            for (const card of result.cards) {
              await cardStore.createCard({
                plan_id: planStore.currentPlan.id,
                question: card.question,
                answer: card.answer,
                subject: card.subject,
                mastery_level: 'unmastered',
                next_review_date: new Date().toISOString().split('T')[0]
              })
            }
            uni.showToast({ title: `生成了${result.cards.length}张卡片`, icon: 'success' })
          } else {
            uni.showToast({ title: '生成失败', icon: 'none' })
          }
        } catch (error) {
          uni.showToast({ title: '生成失败', icon: 'none' })
          console.error(error)
        } finally {
          uni.hideLoading()
        }
      }
    }
  })
}

async function loadCards() {
  if (planStore.currentPlan) {
    await cardStore.getCardsByPlanId(planStore.currentPlan.id)
    currentIndex.value = 0
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  
  if (userStore.isLoggedIn && userStore.user) {
    await planStore.getPlansByUserId(userStore.user.id)
    await loadCards()
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, #5c6bc0 0%, #3949ab 100%);
  border-radius: 0 0 30px 30px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  
  .page-title {
    font-size: 28px;
    font-weight: 700;
    color: #fff;
  }
  
  .card-count {
    display: flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.2);
    padding: 6px 12px;
    border-radius: 20px;
    
    .count-value {
      font-size: 18px;
      font-weight: 700;
      color: #fff;
    }
    
    .count-label {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.8);
    }
  }
}

.mode-tabs {
  display: flex;
  background: $bg2;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 20px;
  border: 1px solid $rule;
}

.mode-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.2s;
  
  &.active {
    background: #5c6bc0;
    
    .tab-icon, .tab-text {
      color: #fff;
    }
  }
  
  .tab-icon {
    font-size: 16px;
  }
  
  .tab-text {
    font-size: 14px;
    color: $muted;
  }
}

.progress-info {
  margin-bottom: 20px;
  
  .progress-text {
    display: block;
    text-align: center;
    font-size: 14px;
    color: $muted;
    margin-bottom: 8px;
  }
  
  .progress-bar {
    height: 6px;
    background: $soft;
    border-radius: 3px;
    overflow: hidden;
    
    .progress-fill {
      height: 100%;
      background: #5c6bc0;
      border-radius: 3px;
    }
  }
}

.card-container {
  margin-bottom: 20px;
}

.flash-card {
  width: 100%;
  height: 300px;
  perspective: 1000px;
  
  &.flipped {
    .card-front {
      transform: rotateY(180deg);
    }
    
    .card-back {
      transform: rotateY(0);
    }
  }
  
  > div {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
    transition: transform 0.6s;
  }
}

.card-front {
  background: linear-gradient(135deg, #5c6bc0 0%, #3949ab 100%);
  color: #fff;
  
  .card-subject {
    font-size: 12px;
    padding: 4px 12px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    margin-bottom: 16px;
  }
  
  .card-question {
    font-size: 20px;
    font-weight: 600;
    text-align: center;
    line-height: 1.6;
    margin-bottom: 20px;
  }
  
  .card-hint {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
  }
}

.card-back {
  background: $bg2;
  border: 2px solid #5c6bc0;
  transform: rotateY(180deg);
  
  .card-subject {
    font-size: 12px;
    padding: 4px 12px;
    background: #e3e8f7;
    border-radius: 20px;
    color: #5c6bc0;
    margin-bottom: 16px;
  }
  
  .card-answer {
    font-size: 18px;
    color: $ink;
    text-align: center;
    line-height: 1.6;
    margin-bottom: 20px;
  }
  
  .card-hint {
    font-size: 12px;
    color: $muted;
  }
}

.mastery-buttons {
  display: flex;
  gap: 12px;
}

.mastery-btn {
  flex: 1;
  background: $bg2;
  border-radius: 12px;
  padding: 16px 12px;
  text-align: center;
  border: 1px solid $rule;
  
  &.unmastered {
    border-color: #ef5350;
    background: #ffebee;
    
    .mastery-text { color: #c62828; }
  }
  
  &.familiar {
    border-color: #ffb74d;
    background: #fff3e0;
    
    .mastery-text { color: #e65100; }
  }
  
  &.mastered {
    border-color: #66bb6a;
    background: #e8f5e9;
    
    .mastery-text { color: #2e7d32; }
  }
  
  .mastery-icon {
    display: block;
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  .mastery-text {
    display: block;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
  }
  
  .mastery-days {
    font-size: 11px;
    color: $muted;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .empty-text {
    font-size: 18px;
    color: $ink;
    margin-bottom: 8px;
  }
  
  .empty-hint {
    font-size: 14px;
    color: $muted;
  }
}

.filter-scroll {
  white-space: nowrap;
}

.filter-list {
  display: inline-flex;
  gap: 8px;
}

.filter-item {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  background: $bg2;
  color: $muted;
  border: 1px solid $rule;
  
  &.active {
    background: #5c6bc0;
    color: #fff;
    border-color: #5c6bc0;
  }
}

.card-list {
  padding-bottom: 20px;
}

.browse-card {
  background: $bg2;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
  border: 1px solid $rule;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  .card-subject {
    font-size: 12px;
    padding: 4px 12px;
    background: $soft;
    border-radius: 20px;
    color: $accent;
  }
}

.mastery-badge {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 8px;
  
  &.unmastered {
    background: #ffebee;
    color: #c62828;
  }
  
  &.familiar {
    background: #fff3e0;
    color: #e65100;
  }
  
  &.mastered {
    background: #e8f5e9;
    color: #2e7d32;
  }
}

.card-question {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: $ink;
  margin-bottom: 8px;
}

.card-answer {
  display: block;
  font-size: 14px;
  color: $muted;
  line-height: 1.6;
  margin-bottom: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  
  .review-count, .next-review {
    font-size: 12px;
    color: $muted;
  }
}

.card-actions {
  display: flex;
  gap: 8px;
  
  .action-btn {
    flex: 1;
    padding: 8px;
    text-align: center;
    border-radius: 8px;
    font-size: 13px;
    background: $soft;
    color: $accent;
    
    &.delete {
      background: #ffebee;
      color: #c62828;
    }
  }
}

.fab-area {
  position: fixed;
  right: 20px;
  bottom: 120px;
}

.fab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  background: #5c6bc0;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(92, 107, 192, 0.3);
  
  .fab-icon {
    font-size: 20px;
    color: #fff;
  }
  
  .fab-text {
    font-size: 15px;
    color: #fff;
    font-weight: 500;
  }
}

.bottom-space {
  height: 100px;
}
</style>