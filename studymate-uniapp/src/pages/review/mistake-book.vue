<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <text class="title">错题本</text>
        <text class="subtitle">记录每一次错误，让知识不再溜走</text>
      </view>
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-num">{{ mistakes.length }}</text>
          <text class="stat-label">总错题</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ masteredCount }}</text>
          <text class="stat-label">已掌握</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ activeCount }}</text>
          <text class="stat-label">待攻克</text>
        </view>
      </view>
    </view>

    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view class="filter-item" :class="{ active: activeFilter === 'all' }" @click="activeFilter = 'all'">全部</view>
          <view class="filter-item" :class="{ active: activeFilter === subject }" v-for="subject in subjects" :key="subject" @click="activeFilter = subject">{{ subject }}</view>
        </view>
      </scroll-view>
    </view>

    <view class="mistake-list">
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
            <view v-if="reviewCards[reviewIndex].analysis" class="analysis-content">
              <text class="analysis-label">分析</text>
              <text class="analysis-text">{{ reviewCards[reviewIndex].analysis }}</text>
            </view>
          </view>
        </view>

        <view class="review-actions">
          <view class="show-answer-btn" v-if="!reviewShowAnswer" @click="reviewShowAnswer = true">
            <text>点击查看答案</text>
          </view>
          <view class="review-result-btns" v-else>
            <view class="result-btn wrong" @click="reviewResult(false)">
              <text class="result-icon">❌</text>
              <text class="result-text">做错了</text>
            </view>
            <view class="result-btn correct" @click="reviewResult(true)">
              <text class="result-icon">✅</text>
              <text class="result-text">做对了</text>
            </view>
          </view>
        </view>
      </view>

      <view class="review-complete" v-if="reviewMode && reviewCards.length === 0">
        <text class="complete-icon">🎉</text>
        <text class="complete-text">暂无待复习错题</text>
      </view>

      <view class="review-complete" v-if="reviewComplete">
        <text class="complete-icon">🏆</text>
        <text class="complete-text">复习完成！</text>
        <text class="complete-hint">正确 {{ reviewCorrect }} / {{ reviewTotal }} 道</text>
        <view class="back-btn" @click="exitReview">返回错题列表</view>
      </view>

      <!-- Normal List View -->
      <view v-if="!reviewMode && !reviewComplete">
        <view class="section-header">
          <text class="section-title">错题列表</text>
          <view class="start-review-btn" v-if="filteredMistakes.length > 0" @click="startReview">
            <text>开始复习</text>
          </view>
        </view>

        <view class="empty" v-if="filteredMistakes.length === 0">
          <text class="empty-icon">📝</text>
          <text class="empty-text">暂无错题</text>
          <text class="empty-hint">点击右下角按钮，手动录入错题</text>
        </view>

        <view class="mistake-card" v-for="mistake in filteredMistakes" :key="mistake.id" :class="{ mastered: mistake.mastered === '1' }">
          <view class="mistake-header">
            <text class="mistake-subject">{{ mistake.subject }}</text>
            <view class="mistake-tags">
              <view class="mistake-tag" :class="mistake.difficulty">
                {{ getDifficultyLabel(mistake.difficulty) }}
              </view>
              <view class="mistake-tag mastered-tag" v-if="mistake.mastered === '1'">已掌握</view>
            </view>
          </view>

          <view class="mistake-question-section">
            <text class="section-label">题目</text>
            <text class="mistake-question">{{ mistake.question }}</text>
            <view class="image-gallery" v-if="mistake.image_urls && mistake.image_urls.length > 0">
              <image v-for="(url, idx) in mistake.image_urls" :key="idx" :src="url" mode="widthFix" class="mistake-image" @click="previewImage(url, mistake.image_urls)" />
            </view>
          </view>

          <view class="mistake-answer-section">
            <text class="section-label">正确答案</text>
            <text class="mistake-answer">{{ mistake.answer }}</text>
          </view>

          <view class="mistake-analysis-section" v-if="mistake.analysis">
            <text class="section-label">错误分析</text>
            <text class="mistake-analysis">{{ mistake.analysis }}</text>
          </view>

          <view class="mistake-footer">
            <text class="mistake-date">{{ formatDate(mistake.created_at) }}</text>
            <text class="error-count">做错 {{ mistake.error_count }} 次</text>
            <view class="mistake-actions">
              <view class="action-btn" @click="toggleMastered(mistake)">
                {{ mistake.mastered === '1' ? '重新攻克' : '已掌握' }}
              </view>
              <view class="action-btn delete-btn" @click="removeMistake(mistake)">删除</view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- FAB -->
    <view class="fab" @click="showForm = true">
      <text class="fab-icon">+</text>
    </view>

    <!-- Add Form Modal -->
    <view class="modal-overlay" v-if="showForm" @click="showForm = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">添加错题</text>
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
            <text class="form-label">题目内容</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.question" placeholder="请输入错题题目..." maxlength="2000" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">正确答案</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.answer" placeholder="请输入正确答案..." maxlength="2000" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">错误分析（可选）</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.analysis" placeholder="分析错误原因，帮助加深理解..." maxlength="2000" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">难度</text>
            <view class="difficulty-row">
              <view class="diff-item" :class="{ active: form.difficulty === 'easy' }" @click="form.difficulty = 'easy'">简单</view>
              <view class="diff-item" :class="{ active: form.difficulty === 'medium' }" @click="form.difficulty = 'medium'">中等</view>
              <view class="diff-item" :class="{ active: form.difficulty === 'hard' }" @click="form.difficulty = 'hard'">困难</view>
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
          <view class="submit-btn" @click="submitMistake">提交</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'

const planStore = usePlanStore()
const userStore = useUserStore()

const activeFilter = ref('all')
const showForm = ref(false)
const reviewMode = ref(false)
const reviewShowAnswer = ref(false)
const reviewIndex = ref(0)
const reviewCorrect = ref(0)
const reviewTotal = ref(0)
const reviewComplete = ref(false)
const mistakes = ref([])

const allSubjects = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']

const form = ref({
  subject: '数据结构',
  question: '',
  answer: '',
  analysis: '',
  difficulty: 'medium',
  image_urls: []
})

const subjects = computed(() => {
  const set = new Set()
  mistakes.value.forEach(m => set.add(m.subject))
  return [...set]
})

const filteredMistakes = computed(() => {
  if (activeFilter.value === 'all') return mistakes.value
  return mistakes.value.filter(m => m.subject === activeFilter.value)
})

const reviewCards = computed(() => {
  return mistakes.value.filter(m => m.mastered === '0')
})

const masteredCount = computed(() => mistakes.value.filter(m => m.mastered === '1').length)
const activeCount = computed(() => mistakes.value.filter(m => m.mastered === '0').length)

const getDifficultyLabel = (d) => {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[d] || d
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

function chooseImage() {
  uni.chooseImage({
    count: 3 - form.value.image_urls.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      res.tempFilePaths.forEach(path => {
        form.value.image_urls.push(path)
      })
    }
  })
}

function removeImage(idx) {
  form.value.image_urls.splice(idx, 1)
}

function previewImage(current, urls) {
  uni.previewImage({ current, urls })
}

async function submitMistake() {
  if (!form.value.question.trim()) {
    uni.showToast({ title: '请输入题目', icon: 'none' })
    return
  }
  if (!form.value.answer.trim()) {
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
      question: form.value.question,
      answer: form.value.answer,
      subject: form.value.subject,
      analysis: form.value.analysis,
      difficulty: form.value.difficulty,
      image_urls: form.value.image_urls
    }
    const mistake = await api.createMistake(data)
    mistakes.value.unshift(mistake)
    resetForm()
    uni.showToast({ title: '添加成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

function resetForm() {
  showForm.value = false
  form.value = {
    subject: '数据结构',
    question: '',
    answer: '',
    analysis: '',
    difficulty: 'medium',
    image_urls: []
  }
}

async function toggleMastered(mistake) {
  try {
    if (mistake.mastered === '1') {
      await api.updateMistake(mistake.id, { mastered: '0' })
    } else {
      await api.markMistakeMastered(mistake.id)
    }
    await loadMistakes()
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

async function removeMistake(mistake) {
  const res = await new Promise(r => uni.showModal({
    title: '删除确认',
    content: '确定删除这道错题吗？',
    success: r
  }))
  if (res.confirm) {
    try {
      await api.deleteMistake(mistake.id)
      mistakes.value = mistakes.value.filter(m => m.id !== mistake.id)
      uni.showToast({ title: '已删除', icon: 'success' })
    } catch (e) {
      uni.showToast({ title: '删除失败', icon: 'none' })
    }
  }
}

function startReview() {
  reviewMode.value = true
  reviewShowAnswer.value = false
  reviewIndex.value = 0
  reviewCorrect.value = 0
  reviewTotal.value = reviewCards.value.length
  reviewComplete.value = false
}

async function reviewResult(correct) {
  if (correct) reviewCorrect.value++
  const currentMistake = reviewCards.value[reviewIndex.value]

  if (correct) {
    await api.markMistakeMastered(currentMistake.id)
  } else {
    await api.retryMistake(currentMistake.id)
  }

  if (reviewIndex.value < reviewCards.value.length - 1) {
    reviewIndex.value++
    reviewShowAnswer.value = false
  } else {
    reviewMode.value = false
    reviewComplete.value = true
    await loadMistakes()
  }
}

function exitReview() {
  reviewMode.value = false
  reviewComplete.value = false
  reviewIndex.value = 0
  activeFilter.value = 'all'
}

async function loadMistakes() {
  if (!planStore.currentPlan) return
  try {
    const result = await api.getMistakes(planStore.currentPlan.id)
    mistakes.value = result.mistakes || []
  } catch (e) {
    console.error('Failed to load mistakes:', e)
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    await loadMistakes()
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, #ef5350 0%, #f27573 100%);
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
  display: flex;
  background: rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(255,255,255,0.15);
}

.stat-item {
  flex: 1; text-align: center;
  .stat-num { display: block; font-size: 22px; font-weight: 700; color: #fff; }
  .stat-label { font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 2px; }
}

.filter-section { margin-bottom: 16px; }
.filter-scroll { white-space: nowrap; }
.filter-list { display: flex; gap: 8px; }
.filter-item {
  padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; white-space: nowrap;
  transition: all 0.2s;
  &.active { background: #ef5350; color: #fff; }
}

.mistake-card {
  background: #fff; border-radius: 16px; padding: 18px; margin-bottom: 12px;
  border: 1px solid #e8ece9; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  transition: opacity 0.3s;
  &.mastered { opacity: 0.6; }
}

.mistake-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
  .mistake-subject {
    font-size: 12px; padding: 4px 12px; background: #ffebee; border-radius: 20px; color: #ef5350;
  }
}

.mistake-tags { display: flex; gap: 6px; }
.mistake-tag {
  font-size: 11px; padding: 3px 8px; border-radius: 8px;
  &.easy { background: #e8f5e9; color: #2e7d32; }
  &.medium { background: #fff3e0; color: #e65100; }
  &.hard { background: #ffebee; color: #c62828; }
  &.mastered-tag { background: #e8f5e9; color: #2e7d32; }
}

.section-label { display: block; font-size: 12px; color: #ef5350; margin-bottom: 6px; font-weight: 500; }
.mistake-question { font-size: 15px; color: #1a1a2e; line-height: 1.6; display: block; margin-bottom: 12px; }

.image-gallery { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.mistake-image { width: 120px; border-radius: 8px; border: 1px solid #e8ece9; }

.mistake-answer-section, .mistake-analysis-section { margin-bottom: 12px; }
.mistake-answer { font-size: 14px; color: #2e7d32; line-height: 1.6; display: block; font-weight: 500; }
.mistake-analysis { font-size: 14px; color: #65746d; line-height: 1.6; display: block; }

.mistake-footer {
  display: flex; align-items: center; gap: 12px;
  .mistake-date { font-size: 12px; color: #999; }
  .error-count { font-size: 12px; color: #ef5350; }
  .mistake-actions { display: flex; gap: 8px; margin-left: auto; }
}

.action-btn {
  padding: 6px 14px; border-radius: 8px; font-size: 13px; background: #ef5350; color: #fff;
  &.delete-btn { background: #f5f5f5; color: #999; }
}

/* FAB */
.fab {
  position: fixed; right: 20px; bottom: 60px; z-index: 50;
  width: 56px; height: 56px; border-radius: 50%; background: #ef5350;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 16px rgba(239,83,80,0.35);
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
  .cancel-btn {
    flex: 1; padding: 14px; text-align: center; border-radius: 14px;
    font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500;
  }
  .submit-btn {
    flex: 2; padding: 14px; text-align: center; border-radius: 14px;
    font-size: 16px; color: #fff; background: #ef5350; font-weight: 600;
  }
}

.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }

.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-item {
  padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d;
  background: #f5f7f5; transition: all 0.2s;
  &.active { background: #ef5350; color: #fff; }
}

.input-wrapper {
  border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa;
  transition: border-color 0.2s;
  &:focus-within { border-color: #ef5350; }
}
.textarea-field {
  width: 100%; min-height: 80px; font-size: 15px; color: #1a1a2e; line-height: 1.6;
  border: none; outline: none; background: transparent; resize: none;
}

.difficulty-row { display: flex; gap: 10px; }
.diff-item {
  flex: 1; padding: 10px; text-align: center; border-radius: 12px; font-size: 14px;
  color: #65746d; background: #f5f7f5; transition: all 0.2s;
  &.active { background: #ef5350; color: #fff; }
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

.empty {
  display: flex; flex-direction: column; align-items: center; padding: 60px 20px;
  .empty-icon { font-size: 48px; margin-bottom: 12px; }
  .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; }
  .empty-hint { font-size: 13px; color: #999; text-align: center; }
}

.bottom-space { height: 100px; }

/* Review Mode */
.section-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;
  .section-title { font-size: 18px; font-weight: 600; color: #1a1a2e; }
}
.start-review-btn {
  background: #ef5350; color: #fff; padding: 8px 20px; border-radius: 20px;
  font-size: 14px; font-weight: 500; transition: all 0.2s;
  &:active { transform: scale(0.96); }
}

.review-card {
  background: #fff; border-radius: 20px; padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06); margin-bottom: 20px;
}

.review-progress {
  margin-bottom: 20px;
  .review-counter { display: block; font-size: 14px; color: #ef5350; font-weight: 600; margin-bottom: 8px; }
  .review-progress-bar { height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden; }
  .review-progress-fill { height: 100%; background: #ef5350; border-radius: 3px; transition: width 0.3s; }
}

.review-card-body { min-height: 160px; }

.review-subject {
  font-size: 13px; color: #ef5350; background: #ffebee;
  padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 16px;
}

.review-question { display: flex; gap: 12px; margin-bottom: 16px; }
.question-label { font-size: 32px; font-weight: 800; color: #ef5350; line-height: 1; flex-shrink: 0; }
.question-text { font-size: 18px; color: #1a1a2e; line-height: 1.6; font-weight: 500; }

.review-image { width: 120px; border-radius: 8px; border: 1px solid #e8ece9; }

.answer-divider { height: 1px; background: #e8ece9; margin: 16px 0; }

.answer-content { display: flex; gap: 12px; margin-bottom: 12px; }
.answer-label { font-size: 32px; font-weight: 800; color: #2e7d32; line-height: 1; flex-shrink: 0; }
.answer-text { font-size: 16px; color: #1a1a2e; line-height: 1.7; }

.analysis-content { margin-top: 12px; }
.analysis-label { display: block; font-size: 12px; color: #ef5350; margin-bottom: 4px; font-weight: 500; }
.analysis-text { font-size: 14px; color: #65746d; line-height: 1.6; }

.review-actions { margin-top: 20px; }

.show-answer-btn {
  text-align: center; padding: 16px; background: #ffebee; border-radius: 14px; transition: all 0.2s;
  &:active { transform: scale(0.98); background: #ffcdd2; }
  text { font-size: 16px; color: #ef5350; font-weight: 600; }
}

.review-result-btns { display: flex; gap: 12px; }
.result-btn {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 14px 8px; border-radius: 14px; transition: all 0.2s;
  &:active { transform: scale(0.96); }
  &.wrong { background: #fff0f0; .result-text { color: #c62828; } }
  &.correct { background: #f0fff4; .result-text { color: #2e7d32; } }
  .result-icon { font-size: 24px; }
  .result-text { font-size: 13px; font-weight: 500; }
}

.review-complete {
  display: flex; flex-direction: column; align-items: center; padding: 60px 20px;
  .complete-icon { font-size: 56px; margin-bottom: 12px; }
  .complete-text { font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; }
  .complete-hint { font-size: 14px; color: #65746d; margin-bottom: 20px; }
  .back-btn {
    padding: 12px 28px; background: #ef5350; color: #fff; border-radius: 25px;
    font-size: 15px; font-weight: 500;
  }
}
</style>