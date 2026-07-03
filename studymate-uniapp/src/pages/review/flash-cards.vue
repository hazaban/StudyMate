<template>
  <view class="page" :class="themeClass">
    <!-- Header -->
    <view class="header">
      <view class="header-top">
        <view class="header-text">
          <text class="title">{{ activeTab === 'cards' ? '抗遗忘卡片' : '错题本' }}</text>
          <text class="subtitle">{{ activeTab === 'cards' ? '艾宾浩斯记忆曲线，科学对抗遗忘' : '记录每一次错误，让知识不再溜走' }}</text>
        </view>
        <view class="export-btn" @click="openExport">
          <text class="emoji">📥</text>
          <text>导出</text>
        </view>
      </view>
      <view class="stats-row">
        <template v-if="activeTab === 'cards'">
          <view class="stat-item">
            <text class="stat-num">{{ pendingCardsCount }}</text>
            <text class="stat-label">待复习</text>
          </view>
          <view class="stat-item">
            <text class="stat-num">{{ cards.length }}</text>
            <text class="stat-label">总卡片</text>
          </view>
          <view class="stat-item">
            <text class="stat-num">{{ masteredCardsCount }}</text>
            <text class="stat-label">已掌握</text>
          </view>
        </template>
        <template v-else>
          <view class="stat-item">
            <text class="stat-num">{{ mistakes.length }}</text>
            <text class="stat-label">总错题</text>
          </view>
          <view class="stat-item">
            <text class="stat-num">{{ masteredMistakesCount }}</text>
            <text class="stat-label">已掌握</text>
          </view>
          <view class="stat-item">
            <text class="stat-num">{{ activeMistakesCount }}</text>
            <text class="stat-label">待攻克</text>
          </view>
        </template>
      </view>
    </view>

    <!-- Sub Navigation -->
    <view class="sub-nav">
      <view class="sub-nav-item" :class="{ active: activeTab === 'cards' }" @click="switchTab('cards')">知识卡片</view>
      <view class="sub-nav-item" :class="{ active: activeTab === 'mistakes' }" @click="switchTab('mistakes')">错题本</view>
    </view>

    <!-- Mode Toggle -->
    <view class="mode-toggle">
      <view class="mode-btn" :class="{ active: viewMode === 'pending' }" @click="switchMode('pending')">今日复习</view>
      <view class="mode-btn" :class="{ active: viewMode === 'all' }" @click="switchMode('all')">查看全部</view>
    </view>

    <!-- Filter Section -->
    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll" v-if="allTags.length > 0">
        <view class="filter-list">
          <view class="filter-item" :class="{ active: activeTag === '' }" @click="activeTag = ''">全部标签</view>
          <view class="filter-item" v-for="t in allTags" :key="t" :class="{ active: activeTag === t }" @click="activeTag = t">{{ t }}</view>
        </view>
      </scroll-view>
      <view class="dropdown-row">
        <picker mode="selector" :range="subjectFilterOptions" @change="onSubjectFilter">
          <view class="filter-dropdown">{{ activeSubject || '全部科目' }} ▾</view>
        </picker>
        <picker v-if="activeTab === 'cards'" mode="selector" :range="masteryFilterOptions" range-key="label" @change="onMasteryFilter">
          <view class="filter-dropdown">{{ currentMasteryFilterLabel }} ▾</view>
        </picker>
        <picker v-if="activeTab === 'mistakes'" mode="selector" :range="difficultyFilterOptions" range-key="label" @change="onDifficultyFilter">
          <view class="filter-dropdown">{{ currentDifficultyFilterLabel }} ▾</view>
        </picker>
        <view class="filter-dropdown filter-input-wrap" v-if="activeTab === 'mistakes'">
          <input class="min-error-input" type="number" v-model="minErrorCount" placeholder="最小错误次数" />
        </view>
      </view>
    </view>

    <!-- Content List -->
    <view class="content-list">
      <!-- Review Mode -->
      <view class="review-card" v-if="reviewMode && reviewCards.length > 0">
        <view class="review-progress">
          <text class="review-counter">{{ reviewIndex + 1 }} / {{ reviewCards.length }}</text>
          <view class="review-progress-bar">
            <view class="review-progress-fill" :style="{ width: ((reviewIndex + 1) / reviewCards.length * 100) + '%' }"></view>
          </view>
        </view>

        <view class="review-card-body">
          <view class="review-subject">{{ currentReviewItem.subject }}</view>
          <view class="review-question">
            <text class="question-label">Q</text>
            <text class="question-text">{{ currentReviewItem.question }}</text>
          </view>
          <view class="image-gallery" v-if="currentReviewItem.question_images && currentReviewItem.question_images.length > 0">
            <image v-for="(url, idx) in currentReviewItem.question_images" :key="'rq'+idx" :src="url" mode="widthFix" class="review-image no-dark" @click="previewImage(url, currentReviewItem.question_images)" />
          </view>

          <view class="review-answer" v-if="reviewShowAnswer">
            <view class="answer-divider"></view>
            <view class="answer-content">
              <text class="answer-label">A</text>
              <text class="answer-text">{{ currentReviewItem.answer }}</text>
            </view>
            <view class="image-gallery" v-if="currentReviewItem.answer_images && currentReviewItem.answer_images.length > 0" style="margin-top: 10px;">
              <image v-for="(url, idx) in currentReviewItem.answer_images" :key="'ra'+idx" :src="url" mode="widthFix" class="review-image no-dark" @click="previewImage(url, currentReviewItem.answer_images)" />
            </view>
            <view v-if="activeTab === 'mistakes' && currentReviewItem.analysis" class="analysis-content">
              <text class="analysis-label">分析</text>
              <text class="analysis-text">{{ currentReviewItem.analysis }}</text>
            </view>
          </view>
        </view>

        <view class="review-actions">
          <view class="show-answer-btn" v-if="!reviewShowAnswer" @click="reviewShowAnswer = true">
            <text>点击查看答案</text>
          </view>
          <view class="review-result-btns" v-else>
            <template v-if="activeTab === 'cards'">
              <view class="result-btn fail" @click="reviewResult('unmastered')">
                <text class="result-icon emoji">😣</text>
                <text class="result-text">未掌握</text>
              </view>
              <view class="result-btn ok" @click="reviewResult('familiar')">
                <text class="result-icon emoji">🤔</text>
                <text class="result-text">较熟悉</text>
              </view>
              <view class="result-btn great" @click="reviewResult('mastered')">
                <text class="result-icon emoji">😎</text>
                <text class="result-text">已掌握</text>
              </view>
            </template>
            <template v-else>
              <view class="result-btn wrong" @click="reviewResult(false)">
                <text class="result-icon emoji">❌</text>
                <text class="result-text">做错了</text>
              </view>
              <view class="result-btn correct" @click="reviewResult(true)">
                <text class="result-icon emoji">✅</text>
                <text class="result-text">做对了</text>
              </view>
            </template>
          </view>
        </view>
      </view>

      <!-- Review Empty -->
      <view class="review-complete" v-if="reviewMode && reviewCards.length === 0">
        <text class="complete-icon emoji">🎉</text>
        <text class="complete-text">{{ activeTab === 'cards' ? '今天没有需要复习的卡片' : '今天没有需要复习的错题' }}</text>
        <view class="back-btn" @click="exitReview">查看全部</view>
      </view>

      <!-- Review Complete -->
      <view class="review-complete" v-if="reviewComplete">
        <text class="complete-icon emoji">🏆</text>
        <text class="complete-text">复习完成！</text>
        <text class="complete-hint" v-if="activeTab === 'mistakes'">正确 {{ reviewCorrect }} / {{ reviewTotal }} 道</text>
        <view class="back-btn" @click="exitReview">返回{{ activeTab === 'cards' ? '卡片列表' : '错题列表' }}</view>
      </view>

      <!-- Normal List -->
      <view v-if="!reviewMode && !reviewComplete">
        <view class="section-header" v-if="currentList.length > 0">
          <text class="section-title">
            <template v-if="viewMode === 'pending'">今日待复习 · {{ currentList.length }}{{ unit }}</template>
            <template v-else>{{ activeTab === 'cards' ? '全部卡片' : '全部错题' }} · {{ currentList.length }}{{ unit }}</template>
          </text>
          <view class="start-review-btn" v-if="reviewCards.length > 0" @click="startReview">
            <text>开始复习</text>
          </view>
        </view>

        <view class="empty" v-if="currentList.length === 0">
          <text class="empty-icon emoji">{{ activeTab === 'cards' ? '📖' : '📝' }}</text>
          <text class="empty-text">{{ viewMode === 'pending' ? (activeTab === 'cards' ? '今天没有需要复习的卡片' : '今天没有需要复习的错题') : (activeTab === 'cards' ? '暂无卡片' : '暂无错题') }}</text>
          <text class="empty-hint">点击右下角按钮，{{ activeTab === 'cards' ? '手动添加知识卡片' : '手动录入错题' }}</text>
        </view>

        <!-- Card Items -->
        <template v-if="activeTab === 'cards'">
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
              <text class="review-count">第{{ card.review_count || 0 }}次复习</text>
              <text class="review-date" v-if="card.next_review_date && card.next_review_date > today">下次 {{ formatDate(card.next_review_date) }}</text>
              <view class="card-item-actions">
                <view class="action-btn edit-btn" @click="editCard(card)">编辑</view>
                <view class="action-btn delete-btn" @click="removeCard(card)">删除</view>
              </view>
            </view>
          </view>
        </template>

        <!-- Mistake Items -->
        <template v-else>
          <view class="mistake-card" v-for="mistake in filteredMistakes" :key="mistake.id" :class="{ mastered: mistake.mastered === '1' }">
            <view class="mistake-header">
              <text class="mistake-subject">{{ mistake.subject }}</text>
              <view class="mistake-tags">
                <view class="mistake-tag" v-for="t in (mistake.tags || [])" :key="t">{{ t }}</view>
                <view class="mistake-tag" :class="mistake.difficulty">{{ getDifficultyLabel(mistake.difficulty) }}</view>
                <view class="mistake-tag mastered-tag" v-if="mistake.mastered === '1'">已掌握</view>
              </view>
            </view>

            <view class="mistake-question-section">
              <text class="section-label">题目</text>
              <text class="mistake-question">{{ mistake.question }}</text>
              <view class="image-gallery" v-if="mistake.question_images && mistake.question_images.length > 0">
                <image v-for="(url, idx) in mistake.question_images" :key="idx" :src="url" mode="widthFix" class="mistake-image no-dark" @click="previewImage(url, mistake.question_images)" />
              </view>
            </view>

            <view class="mistake-answer-section">
              <text class="section-label">正确答案</text>
              <text class="mistake-answer">{{ mistake.answer }}</text>
              <view class="image-gallery" v-if="mistake.answer_images && mistake.answer_images.length > 0">
                <image v-for="(url, idx) in mistake.answer_images" :key="'a'+idx" :src="url" mode="widthFix" class="mistake-image no-dark" @click="previewImage(url, mistake.answer_images)" />
              </view>
            </view>

            <view class="mistake-analysis-section" v-if="mistake.analysis">
              <text class="section-label">错误分析</text>
              <text class="mistake-analysis">{{ mistake.analysis }}</text>
            </view>

            <view class="mistake-footer">
              <text class="mistake-date">{{ formatDate(mistake.created_at) }}</text>
              <text class="correct-progress" v-if="!mistake.mastered || mistake.mastered === '0'">正确 {{ mistake.correct_count || 0 }}/2 次</text>
              <text class="error-count">做错 {{ mistake.error_count || 0 }} 次</text>
              <text class="correct-rate" v-if="(mistake.error_count || 0) + (mistake.correct_count || 0) > 0">
                正确率 {{ Math.round((mistake.correct_count || 0) / ((mistake.error_count || 0) + (mistake.correct_count || 0)) * 100) }}%
              </text>
              <view class="mistake-actions">
                <view class="action-btn edit-btn" @click="editMistake(mistake)">编辑</view>
                <view class="action-btn toggle-btn" @click="toggleMastered(mistake)">
                  {{ mistake.mastered === '1' ? '重新攻克' : '已掌握' }}
                </view>
                <view class="action-btn delete-btn" @click="removeMistake(mistake)">删除</view>
              </view>
            </view>
          </view>
        </template>
      </view>
    </view>

    <!-- FAB -->
    <view class="fab" @click="openAddForm">
      <text class="fab-icon">+</text>
    </view>

    <!-- Add/Edit Form Modal -->
    <view class="modal-overlay" v-if="showForm" @click="closeForm">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ modalTitle }}</text>
          <view class="modal-close" @click="closeForm">✕</view>
        </view>

        <scroll-view scroll-y class="modal-body">
          <!-- Subject -->
          <view class="form-group">
            <text class="form-label">科目</text>
            <view class="subject-grid">
              <view class="subject-item" v-for="s in subjectOptions" :key="s" :class="{ active: form.subject === s }" @click="form.subject = s">{{ s }}</view>
              <view class="subject-item subject-add" @click="showSubjectInput = !showSubjectInput">
                <text v-if="!showSubjectInput">+ 自定义</text>
                <text v-else>收起</text>
              </view>
            </view>
            <view class="input-wrapper" v-if="showSubjectInput" style="margin-top: 10px;">
              <input class="input-field" v-model="customSubject" placeholder="输入自定义科目..." @confirm="addCustomSubject" />
            </view>
          </view>

          <!-- Tags -->
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

          <!-- Question -->
          <view class="form-group">
            <text class="form-label">{{ activeTab === 'cards' ? '问题' : '题目内容' }}</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.question" :placeholder="activeTab === 'cards' ? '请输入复习问题...' : '请输入错题题目...'" maxlength="2000" />
            </view>
          </view>

          <!-- Answer -->
          <view class="form-group">
            <text class="form-label">正确答案</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.answer" placeholder="请输入答案..." maxlength="2000" />
            </view>
          </view>

          <!-- Analysis (mistakes only) -->
          <view class="form-group" v-if="activeTab === 'mistakes'">
            <text class="form-label">错误分析（可选）</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.analysis" placeholder="分析错误原因..." maxlength="2000" />
            </view>
          </view>

          <!-- Difficulty (mistakes only) -->
          <view class="form-group" v-if="activeTab === 'mistakes'">
            <text class="form-label">难度</text>
            <view class="difficulty-row">
              <view class="diff-item" :class="{ active: form.difficulty === 'easy' }" @click="form.difficulty = 'easy'">简单</view>
              <view class="diff-item" :class="{ active: form.difficulty === 'medium' }" @click="form.difficulty = 'medium'">中等</view>
              <view class="diff-item" :class="{ active: form.difficulty === 'hard' }" @click="form.difficulty = 'hard'">困难</view>
            </view>
          </view>

          <!-- Question Images -->
          <view class="form-group">
            <text class="form-label">{{ activeTab === 'cards' ? '问题图片（可选）' : '题目图片（可选）' }}</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in form.question_images" :key="'q'+idx">
                <image :src="img" mode="aspectFill" class="uploaded-image no-dark" />
                <view class="image-remove" @click="form.question_images.splice(idx, 1)">✕</view>
              </view>
              <view class="image-add-btn" @click="chooseQuestionImage">
                <text class="add-icon">+</text>
                <text class="add-text">上传图片</text>
              </view>
            </view>
          </view>

          <!-- Answer Images -->
          <view class="form-group">
            <text class="form-label">答案图片（可选）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in form.answer_images" :key="'a'+idx">
                <image :src="img" mode="aspectFill" class="uploaded-image no-dark" />
                <view class="image-remove" @click="form.answer_images.splice(idx, 1)">✕</view>
              </view>
              <view class="image-add-btn" @click="chooseAnswerImage">
                <text class="add-icon">+</text>
                <text class="add-text">上传图片</text>
              </view>
            </view>
          </view>
        </scroll-view>

        <view class="modal-footer">
          <view class="cancel-btn" @click="closeForm">取消</view>
          <view class="submit-btn" @click="submitForm">{{ isEdit ? '保存' : '添加' }}</view>
        </view>
      </view>
    </view>

    <!-- Export Panel Modal -->
    <view class="modal-overlay" v-if="showExport" @click="showExport = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">导出{{ activeTab === 'cards' ? '知识卡片' : '错题' }}</text>
          <view class="modal-close" @click="showExport = false">✕</view>
        </view>

        <view class="modal-body">
          <!-- Format Selection -->
          <view class="form-group">
            <text class="form-label">导出格式</text>
            <view class="format-row">
              <view class="format-item" :class="{ active: exportFormat === 'excel' }" @click="exportFormat = 'excel'">
                <text class="emoji">📊</text>
                <text>Excel</text>
              </view>
              <view class="format-item" :class="{ active: exportFormat === 'pdf' }" @click="exportFormat = 'pdf'">
                <text class="emoji">📄</text>
                <text>PDF</text>
              </view>
              <view class="format-item" :class="{ active: exportFormat === 'csv' }" @click="exportFormat = 'csv'">
                <text class="emoji">📋</text>
                <text>CSV</text>
              </view>
            </view>
          </view>

          <!-- Subject Filter -->
          <view class="form-group">
            <text class="form-label">科目</text>
            <picker mode="selector" :range="exportSubjectOptions" @change="onExportSubject">
              <view class="dropdown-display">{{ exportSubjectLabel }} ▾</view>
            </picker>
          </view>

          <!-- Tag Filter -->
          <view class="form-group">
            <text class="form-label">标签</text>
            <picker mode="selector" :range="exportTagOptions" @change="onExportTag">
              <view class="dropdown-display">{{ exportTagLabel }} ▾</view>
            </picker>
          </view>

          <!-- Mastery/Difficulty Filter -->
          <view class="form-group" v-if="activeTab === 'cards'">
            <text class="form-label">掌握程度</text>
            <picker mode="selector" :range="masteryFilterOptions" range-key="label" @change="onExportMastery">
              <view class="dropdown-display">{{ exportMasteryLabel }} ▾</view>
            </picker>
          </view>
          <view class="form-group" v-else>
            <text class="form-label">难度</text>
            <picker mode="selector" :range="difficultyFilterOptions" range-key="label" @change="onExportDifficulty">
              <view class="dropdown-display">{{ exportDifficultyLabel }} ▾</view>
            </picker>
          </view>

          <!-- Min Error Count (mistakes only) -->
          <view class="form-group" v-if="activeTab === 'mistakes'">
            <text class="form-label">最小错误次数</text>
            <view class="input-wrapper">
              <input class="input-field" type="number" v-model="exportMinErrors" placeholder="留空则不限制" />
            </view>
          </view>
        </view>

        <view class="modal-footer">
          <view class="cancel-btn" @click="showExport = false">取消</view>
          <view class="submit-btn" @click="doExport">导出</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'

const planStore = usePlanStore()
const userStore = useUserStore()

// ==================== State ====================
const activeTab = ref('cards')          // 'cards' | 'mistakes'
const viewMode = ref('pending')          // 'pending' | 'all'
const activeTag = ref('')
const activeSubject = ref('')            // 科目筛选
const activeMastery = ref('')            // 掌握程度筛选（卡片）
const activeDifficulty = ref('')         // 难度筛选（错题）
const minErrorCount = ref('')            // 最小错误次数筛选（错题）

const showForm = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const showExport = ref(false)
const exportFormat = ref('excel')
const exportSubject = ref('')
const exportTag = ref('')
const exportMastery = ref('')
const exportDifficulty = ref('')
const exportMinErrors = ref('')

const reviewMode = ref(false)
const reviewShowAnswer = ref(false)
const reviewIndex = ref(0)
const reviewCorrect = ref(0)
const reviewTotal = ref(0)
const reviewComplete = ref(false)

const cards = ref([])
const mistakes = ref([])
const tagInput = ref('')

const today = new Date().toISOString().split('T')[0]

// ==================== Constants ====================
const allSubjects = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']
const subjectOptions = ref(JSON.parse(uni.getStorageSync('studymate_subjects') || JSON.stringify(allSubjects)))
const showSubjectInput = ref(false)
const customSubject = ref('')

const masteryFilterOptions = [
  { label: '全部掌握程度', value: '' },
  { label: '未掌握', value: 'unmastered' },
  { label: '较熟悉', value: 'familiar' },
  { label: '已掌握', value: 'mastered' }
]

const difficultyFilterOptions = [
  { label: '全部难度', value: '' },
  { label: '简单', value: 'easy' },
  { label: '中等', value: 'medium' },
  { label: '困难', value: 'hard' }
]

const form = ref({
  subject: '数据结构',
  question: '',
  answer: '',
  analysis: '',
  difficulty: 'medium',
  question_images: [],
  answer_images: [],
  tags: []
})

// ==================== Computed ====================
const themeClass = computed(() => activeTab.value === 'cards' ? 'theme-cards' : 'theme-mistakes')

const unit = computed(() => activeTab.value === 'cards' ? '张' : '道')

const allTags = computed(() => {
  const set = new Set()
  const source = activeTab.value === 'cards' ? cards.value : mistakes.value
  source.forEach(item => (item.tags || []).forEach(t => set.add(t)))
  return [...set]
})

const subjectFilterOptions = computed(() => ['全部科目', ...subjectOptions.value])

const exportSubjectOptions = computed(() => ['全部科目', ...subjectOptions.value])
const exportTagOptions = computed(() => ['全部标签', ...allTags.value])

const filteredCards = computed(() => {
  let result = cards.value
  if (activeTag.value) {
    result = result.filter(c => (c.tags || []).includes(activeTag.value))
  }
  if (activeSubject.value) {
    result = result.filter(c => c.subject === activeSubject.value)
  }
  if (activeMastery.value) {
    result = result.filter(c => c.mastery_level === activeMastery.value)
  }
  return result
})

const filteredMistakes = computed(() => {
  let result = mistakes.value
  if (activeTag.value) {
    result = result.filter(m => (m.tags || []).includes(activeTag.value))
  }
  if (activeSubject.value) {
    result = result.filter(m => m.subject === activeSubject.value)
  }
  if (activeDifficulty.value) {
    result = result.filter(m => m.difficulty === activeDifficulty.value)
  }
  if (minErrorCount.value !== '' && minErrorCount.value !== null) {
    const min = parseInt(minErrorCount.value) || 0
    result = result.filter(m => (m.error_count || 0) >= min)
  }
  return result
})

const currentList = computed(() => {
  return activeTab.value === 'cards' ? filteredCards.value : filteredMistakes.value
})

// Card stats
const pendingCardsCount = computed(() => cards.value.filter(c => c.next_review_date && c.next_review_date <= today).length)
const masteredCardsCount = computed(() => cards.value.filter(c => c.mastery_level === 'mastered').length)

// Mistake stats
const masteredMistakesCount = computed(() => mistakes.value.filter(m => m.mastered === '1').length)
const activeMistakesCount = computed(() => mistakes.value.filter(m => m.mastered === '0').length)

// Review cards
const reviewCards = computed(() => {
  if (activeTab.value === 'cards') {
    return filteredCards.value.filter(c => c.next_review_date && c.next_review_date <= today)
  } else {
    return filteredMistakes.value.filter(m => m.mastered === '0')
  }
})

const currentReviewItem = computed(() => reviewCards.value[reviewIndex.value] || {})

// Filter labels
const currentMasteryFilterLabel = computed(() => {
  const opt = masteryFilterOptions.find(o => o.value === activeMastery.value)
  return opt ? opt.label : '掌握程度'
})

const currentDifficultyFilterLabel = computed(() => {
  const opt = difficultyFilterOptions.find(o => o.value === activeDifficulty.value)
  return opt ? opt.label : '难度'
})

// Export labels
const exportSubjectLabel = computed(() => exportSubject.value || '全部科目')
const exportTagLabel = computed(() => exportTag.value || '全部标签')
const exportMasteryLabel = computed(() => {
  const opt = masteryFilterOptions.find(o => o.value === exportMastery.value)
  return opt ? opt.label : '全部掌握程度'
})
const exportDifficultyLabel = computed(() => {
  const opt = difficultyFilterOptions.find(o => o.value === exportDifficulty.value)
  return opt ? opt.label : '全部难度'
})

// Modal title
const modalTitle = computed(() => {
  const action = isEdit.value ? '编辑' : '添加'
  const type = activeTab.value === 'cards' ? '知识卡片' : '错题'
  return `${action}${type}`
})

// ==================== Watch ====================
watch(activeTab, (newTab) => {
  // Reset filters
  activeTag.value = ''
  activeSubject.value = ''
  activeMastery.value = ''
  activeDifficulty.value = ''
  minErrorCount.value = ''
  // Exit review mode
  reviewMode.value = false
  reviewComplete.value = false
  reviewIndex.value = 0
  reviewShowAnswer.value = false
  reviewCorrect.value = 0
  // Close form if open
  if (showForm.value) {
    closeForm()
  }
  // Load data for the new tab
  if (newTab === 'cards') {
    loadCards()
  } else {
    loadMistakes()
  }
})

// ==================== Label Helpers ====================
const getMasteryLabel = (level) => {
  const map = { unmastered: '未掌握', familiar: '较熟悉', mastered: '已掌握' }
  return map[level] || level
}

const getMasteryClass = (level) => {
  const map = { unmastered: 'badge-red', familiar: 'badge-orange', mastered: 'badge-green' }
  return map[level] || ''
}

const getDifficultyLabel = (d) => {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[d] || d
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

// ==================== Tab / Mode Switching ====================
function switchTab(tab) {
  if (activeTab.value === tab) return
  activeTab.value = tab
}

function switchMode(mode) {
  viewMode.value = mode
  if (activeTab.value === 'cards') {
    loadCards()
  } else {
    loadMistakes()
  }
}

// ==================== Filter Handlers ====================
function onSubjectFilter(e) {
  const idx = parseInt(e.detail.value)
  activeSubject.value = idx === 0 ? '' : subjectFilterOptions.value[idx]
}

function onMasteryFilter(e) {
  const idx = parseInt(e.detail.value)
  activeMastery.value = masteryFilterOptions[idx].value
}

function onDifficultyFilter(e) {
  const idx = parseInt(e.detail.value)
  activeDifficulty.value = difficultyFilterOptions[idx].value
}

function onExportSubject(e) {
  const idx = parseInt(e.detail.value)
  exportSubject.value = idx === 0 ? '' : exportSubjectOptions.value[idx]
}

function onExportTag(e) {
  const idx = parseInt(e.detail.value)
  exportTag.value = idx === 0 ? '' : exportTagOptions.value[idx]
}

function onExportMastery(e) {
  const idx = parseInt(e.detail.value)
  exportMastery.value = masteryFilterOptions[idx].value
}

function onExportDifficulty(e) {
  const idx = parseInt(e.detail.value)
  exportDifficulty.value = difficultyFilterOptions[idx].value
}

// ==================== Subject Management ====================
function addCustomSubject() {
  const name = customSubject.value.trim()
  if (!name) return
  if (!subjectOptions.value.includes(name)) {
    subjectOptions.value.push(name)
    uni.setStorageSync('studymate_subjects', JSON.stringify(subjectOptions.value))
  }
  form.value.subject = name
  customSubject.value = ''
  showSubjectInput.value = false
}

function parseTags() {
  if (!tagInput.value.trim()) return
  const tags = tagInput.value.split(/[,，]/).map(t => t.trim()).filter(Boolean)
  form.value.tags = [...new Set([...form.value.tags, ...tags])]
  tagInput.value = ''
}

// ==================== Image Management ====================
function chooseQuestionImage() {
  uni.chooseImage({
    count: 9,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.question_images.push(path))
  })
}

function chooseAnswerImage() {
  uni.chooseImage({
    count: 9,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.answer_images.push(path))
  })
}

function previewImage(current, urls) {
  uni.previewImage({ current, urls })
}

// ==================== Form Management ====================
function openAddForm() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  showForm.value = true
}

function editCard(card) {
  isEdit.value = true
  editingId.value = card.id
  form.value = {
    subject: card.subject || '数据结构',
    question: card.question || '',
    answer: card.answer || '',
    analysis: '',
    difficulty: 'medium',
    question_images: card.question_images || [],
    answer_images: card.answer_images || [],
    tags: card.tags || []
  }
  tagInput.value = ''
  showSubjectInput.value = false
  customSubject.value = ''
  showForm.value = true
}

function editMistake(mistake) {
  isEdit.value = true
  editingId.value = mistake.id
  form.value = {
    subject: mistake.subject || '数据结构',
    question: mistake.question || '',
    answer: mistake.answer || '',
    analysis: mistake.analysis || '',
    difficulty: mistake.difficulty || 'medium',
    question_images: mistake.question_images || [],
    answer_images: mistake.answer_images || [],
    tags: mistake.tags || []
  }
  tagInput.value = ''
  showSubjectInput.value = false
  customSubject.value = ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  isEdit.value = false
  editingId.value = null
}

function resetForm() {
  form.value = {
    subject: subjectOptions.value[0] || '数据结构',
    question: '',
    answer: '',
    analysis: '',
    difficulty: 'medium',
    question_images: [],
    answer_images: [],
    tags: []
  }
  tagInput.value = ''
  showSubjectInput.value = false
  customSubject.value = ''
}

async function submitForm() {
  if (activeTab.value === 'cards') {
    await submitCard()
  } else {
    await submitMistake()
  }
}

async function submitCard() {
  const hasQ = form.value.question.trim() || form.value.question_images.length > 0
  const hasA = form.value.answer.trim() || form.value.answer_images.length > 0
  if (!hasQ) { uni.showToast({ title: '请输入问题或上传问题图片', icon: 'none' }); return }
  if (!hasA) { uni.showToast({ title: '请输入答案或上传答案图片', icon: 'none' }); return }
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }

  uni.showLoading({ title: '保存中...' })
  try {
    if (isEdit.value) {
      await api.updateCard(editingId.value, {
        subject: form.value.subject,
        question: form.value.question,
        answer: form.value.answer,
        question_images: form.value.question_images,
        answer_images: form.value.answer_images,
        tags: form.value.tags
      })
      uni.showToast({ title: '更新成功', icon: 'success' })
    } else {
      await api.createCard({
        plan_id: planStore.currentPlan.id,
        subject: form.value.subject,
        question: form.value.question,
        answer: form.value.answer,
        mastery_level: 'unmastered',
        next_review_date: today,
        question_images: form.value.question_images,
        answer_images: form.value.answer_images,
        tags: form.value.tags
      })
      uni.showToast({ title: '添加成功', icon: 'success' })
    }
    closeForm()
    await loadCards()
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

async function submitMistake() {
  const hasQ = form.value.question.trim() || form.value.question_images.length > 0
  const hasA = form.value.answer.trim() || form.value.answer_images.length > 0
  if (!hasQ) { uni.showToast({ title: '请输入题目或上传题目图片', icon: 'none' }); return }
  if (!hasA) { uni.showToast({ title: '请输入答案或上传答案图片', icon: 'none' }); return }
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }

  uni.showLoading({ title: '保存中...' })
  try {
    if (isEdit.value) {
      await api.updateMistake(editingId.value, {
        subject: form.value.subject,
        question: form.value.question,
        answer: form.value.answer,
        analysis: form.value.analysis,
        difficulty: form.value.difficulty,
        question_images: form.value.question_images,
        answer_images: form.value.answer_images,
        tags: form.value.tags
      })
      uni.showToast({ title: '更新成功', icon: 'success' })
    } else {
      await api.createMistake({
        plan_id: planStore.currentPlan.id,
        subject: form.value.subject,
        question: form.value.question,
        answer: form.value.answer,
        analysis: form.value.analysis,
        difficulty: form.value.difficulty,
        question_images: form.value.question_images,
        answer_images: form.value.answer_images,
        tags: form.value.tags
      })
      uni.showToast({ title: '添加成功', icon: 'success' })
    }
    closeForm()
    await loadMistakes()
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

// ==================== Review ====================
function startReview() {
  if (reviewCards.value.length === 0) {
    uni.showToast({ title: '没有可复习的内容', icon: 'none' })
    return
  }
  reviewMode.value = true
  reviewShowAnswer.value = false
  reviewIndex.value = 0
  reviewCorrect.value = 0
  reviewTotal.value = reviewCards.value.length
  reviewComplete.value = false
}

async function reviewResult(payload) {
  if (activeTab.value === 'cards') {
    const currentCard = reviewCards.value[reviewIndex.value]
    await api.reviewCard(currentCard.id, payload)
  } else {
    if (payload) reviewCorrect.value++
    const currentMistake = reviewCards.value[reviewIndex.value]
    await api.reviewMistake(currentMistake.id, payload)
  }

  if (reviewIndex.value < reviewCards.value.length - 1) {
    reviewIndex.value++
    reviewShowAnswer.value = false
  } else {
    reviewMode.value = false
    reviewComplete.value = true
    if (activeTab.value === 'cards') {
      await loadCards()
    } else {
      await loadMistakes()
    }
  }
}

function exitReview() {
  reviewMode.value = false
  reviewComplete.value = false
  reviewIndex.value = 0
  reviewCorrect.value = 0
  reviewShowAnswer.value = false
  viewMode.value = 'all'
  activeTag.value = ''
  activeSubject.value = ''
  activeMastery.value = ''
  activeDifficulty.value = ''
  minErrorCount.value = ''
  if (activeTab.value === 'cards') {
    loadCards()
  } else {
    loadMistakes()
  }
}

// ==================== Delete ====================
async function removeCard(card) {
  const res = await new Promise(r => uni.showModal({ title: '删除确认', content: '确定删除这张卡片吗？', success: r }))
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

async function removeMistake(mistake) {
  const res = await new Promise(r => uni.showModal({ title: '删除确认', content: '确定删除这道错题吗？', success: r }))
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

// ==================== Mistake Mastered Toggle ====================
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

// ==================== Export ====================
function openExport() {
  // Initialize export filters from current filters
  exportSubject.value = activeSubject.value
  exportTag.value = activeTag.value
  exportMastery.value = activeMastery.value
  exportDifficulty.value = activeDifficulty.value
  exportMinErrors.value = minErrorCount.value
  showExport.value = true
}

async function doExport() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先创建学习计划', icon: 'none' })
    return
  }

  const params = {
    planId: planStore.currentPlan.id,
    subject: exportSubject.value,
    tag: exportTag.value
  }

  if (activeTab.value === 'cards') {
    params.mastery_level = exportMastery.value
  } else {
    params.difficulty = exportDifficulty.value
    if (exportMinErrors.value !== '' && exportMinErrors.value !== null) {
      params.min_errors = exportMinErrors.value
    }
  }

  uni.showLoading({ title: '导出中...' })
  try {
    await api.downloadExport(activeTab.value, exportFormat.value, params)
    showExport.value = false
    uni.showToast({ title: '导出成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message || '导出失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

// ==================== Data Loading ====================
async function loadCards() {
  if (!planStore.currentPlan) return
  try {
    const pending = viewMode.value === 'pending'
    const result = await api.getCards(planStore.currentPlan.id, null, null, pending)
    cards.value = result.cards || []
  } catch (e) {
    console.error('Failed to load cards:', e)
  }
}

async function loadMistakes() {
  if (!planStore.currentPlan) return
  try {
    const pending = viewMode.value === 'pending'
    const result = await api.getMistakes(planStore.currentPlan.id, null, null, pending)
    mistakes.value = result.mistakes || []
  } catch (e) {
    console.error('Failed to load mistakes:', e)
  }
}

// ==================== Lifecycle ====================
onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    await loadCards()
  }
})
</script>

<style lang="scss" scoped>
/* ==================== Header ==================== */
.header {
  padding: 60px 0 20px;
  border-radius: 0 0 32px 32px;
  margin-bottom: 20px;
  margin-left: -20px;
  margin-right: -20px;
  padding-left: 20px;
  padding-right: 20px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.header-text {
  flex: 1;
}

.title {
  display: block;
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  font-size: 13px;
  color: #fff;
  flex-shrink: 0;
  transition: all 0.2s;

  &:active {
    transform: scale(0.96);
    background: rgba(255, 255, 255, 0.3);
  }
}

.stats-row {
  display: flex;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
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
    color: rgba(255, 255, 255, 0.7);
    margin-top: 2px;
  }
}

/* ==================== Sub Navigation ==================== */
.sub-nav {
  display: flex;
  margin-bottom: 16px;
  background: #f5f7f5;
  border-radius: 12px;
  padding: 4px;
}

.sub-nav-item {
  flex: 1;
  text-align: center;
  padding: 10px;
  border-radius: 10px;
  font-size: 14px;
  color: #65746d;
  transition: all 0.2s;

  &.active {
    background: #fff;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
}

/* ==================== Mode Toggle ==================== */
.mode-toggle {
  display: flex;
  margin-bottom: 16px;
  background: #f5f7f5;
  border-radius: 12px;
  padding: 4px;
}

.mode-btn {
  flex: 1;
  text-align: center;
  padding: 10px;
  border-radius: 10px;
  font-size: 14px;
  color: #65746d;
  transition: all 0.2s;

  &.active {
    background: #fff;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
}

/* ==================== Filter Section ==================== */
.filter-section {
  margin-bottom: 14px;
}

.filter-scroll {
  white-space: nowrap;
  margin-bottom: 10px;
}

.filter-list {
  display: flex;
  gap: 8px;
}

.filter-item {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  color: #65746d;
  background: #f5f7f5;
  white-space: nowrap;
  transition: all 0.2s;

  &.active {
    color: #fff;
  }
}

.dropdown-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-dropdown {
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 13px;
  color: #65746d;
  background: #f5f7f5;
  white-space: nowrap;
  transition: all 0.2s;
}

.filter-input-wrap {
  padding: 0 14px;
  display: flex;
  align-items: center;
}

.min-error-input {
  width: 110px;
  font-size: 13px;
  color: #65746d;
  border: none;
  outline: none;
  background: transparent;
}

/* ==================== Section Header ==================== */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a2e;
  }
}

.start-review-btn {
  color: #fff;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;

  &:active {
    transform: scale(0.96);
  }
}

/* ==================== Card Item ==================== */
.card-item {
  background: #fff;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
  border: 1px solid #e8ece9;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);

  &.not-today {
    opacity: 0.6;
  }
}

.card-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;

  .card-item-subject {
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 20px;
  }
}

.card-item-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.card-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 8px;
  background: #f5f5f5;
  color: #65746d;
}

.mastery-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;

  &.badge-red {
    background: #ffebee;
    color: #c62828;
  }

  &.badge-orange {
    background: #fff3e0;
    color: #e65100;
  }

  &.badge-green {
    background: #e8f5e9;
    color: #2e7d32;
  }
}

.section-label {
  display: block;
  font-size: 12px;
  margin-bottom: 6px;
  font-weight: 500;
}

.card-question-text {
  font-size: 15px;
  color: #1a1a2e;
  line-height: 1.6;
  display: block;
}

.card-item-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 12px;

  .review-count {
    font-size: 12px;
    color: #999;
  }

  .review-date {
    font-size: 12px;
  }

  .card-item-actions {
    display: flex;
    gap: 8px;
    margin-left: auto;
  }
}

.action-btn {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  transition: all 0.2s;

  &:active {
    transform: scale(0.96);
  }
}

.edit-btn {
  background: #f3f0ff;
  color: #6b4ce6;
}

.delete-btn {
  background: #f5f5f5;
  color: #999;
}

.toggle-btn {
  background: #e8f5e9;
  color: #2e7d32;
}

/* ==================== Mistake Card ==================== */
.mistake-card {
  background: #fff;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
  border: 1px solid #e8ece9;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);

  &.mastered {
    opacity: 0.6;
  }
}

.mistake-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;

  .mistake-subject {
    font-size: 12px;
    padding: 4px 12px;
    background: #ffebee;
    border-radius: 20px;
    color: #ef5350;
  }
}

.mistake-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.mistake-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 8px;
  background: #f5f5f5;
  color: #65746d;

  &.easy {
    background: #e8f5e9;
    color: #2e7d32;
  }

  &.medium {
    background: #fff3e0;
    color: #e65100;
  }

  &.hard {
    background: #ffebee;
    color: #c62828;
  }

  &.mastered-tag {
    background: #e8f5e9;
    color: #2e7d32;
  }
}

.mistake-question-section,
.mistake-answer-section,
.mistake-analysis-section {
  margin-bottom: 12px;
}

.mistake-question {
  font-size: 15px;
  color: #1a1a2e;
  line-height: 1.6;
  display: block;
}

.image-gallery {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.mistake-image {
  width: 120px;
  border-radius: 8px;
  border: 1px solid #e8ece9;
}

.mistake-answer {
  font-size: 14px;
  color: #2e7d32;
  line-height: 1.6;
  display: block;
  font-weight: 500;
}

.mistake-analysis {
  font-size: 14px;
  color: #65746d;
  line-height: 1.6;
  display: block;
}

.mistake-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;

  .mistake-date {
    font-size: 12px;
    color: #999;
  }

  .correct-progress {
    font-size: 12px;
    color: #2e7d32;
    font-weight: 500;
  }

  .error-count {
    font-size: 12px;
    color: #ef5350;
  }

  .correct-rate {
    font-size: 12px;
    color: #1565c0;
    font-weight: 500;
  }

  .mistake-actions {
    display: flex;
    gap: 8px;
    margin-left: auto;
  }
}

/* ==================== Review Card ==================== */
.review-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
}

.review-progress {
  margin-bottom: 20px;

  .review-counter {
    display: block;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .review-progress-bar {
    height: 6px;
    background: #f0f0f0;
    border-radius: 3px;
    overflow: hidden;
  }

  .review-progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s;
  }
}

.review-card-body {
  min-height: 160px;
}

.review-subject {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
  margin-bottom: 16px;
}

.review-question {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.question-label {
  font-size: 32px;
  font-weight: 800;
  line-height: 1;
  flex-shrink: 0;
}

.question-text {
  font-size: 18px;
  color: #1a1a2e;
  line-height: 1.6;
  font-weight: 500;
}

.review-image {
  width: 120px;
  border-radius: 8px;
  border: 1px solid #e8ece9;
}

.answer-divider {
  height: 1px;
  background: #e8ece9;
  margin: 16px 0;
}

.answer-content {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.answer-label {
  font-size: 32px;
  font-weight: 800;
  color: #2e7d32;
  line-height: 1;
  flex-shrink: 0;
}

.answer-text {
  font-size: 16px;
  color: #1a1a2e;
  line-height: 1.7;
}

.analysis-content {
  margin-top: 12px;
}

.analysis-label {
  display: block;
  font-size: 12px;
  margin-bottom: 4px;
  font-weight: 500;
}

.analysis-text {
  font-size: 14px;
  color: #65746d;
  line-height: 1.6;
}

.review-actions {
  margin-top: 20px;
}

.show-answer-btn {
  text-align: center;
  padding: 16px;
  border-radius: 14px;
  transition: all 0.2s;

  &:active {
    transform: scale(0.98);
  }

  text {
    font-size: 16px;
    font-weight: 600;
  }
}

.review-result-btns {
  display: flex;
  gap: 12px;
}

.result-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border-radius: 14px;
  transition: all 0.2s;

  &:active {
    transform: scale(0.96);
  }

  &.fail {
    background: #fff0f0;
    .result-text { color: #c62828; }
  }

  &.ok {
    background: #fff8f0;
    .result-text { color: #e65100; }
  }

  &.great {
    background: #f0fff4;
    .result-text { color: #2e7d32; }
  }

  &.wrong {
    background: #fff0f0;
    .result-text { color: #c62828; }
  }

  &.correct {
    background: #f0fff4;
    .result-text { color: #2e7d32; }
  }

  .result-icon {
    font-size: 24px;
  }

  .result-text {
    font-size: 13px;
    font-weight: 500;
  }
}

.review-complete {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;

  .complete-icon {
    font-size: 56px;
    margin-bottom: 12px;
  }

  .complete-text {
    font-size: 20px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 8px;
  }

  .complete-hint {
    font-size: 14px;
    color: #65746d;
    margin-bottom: 20px;
  }

  .back-btn {
    padding: 12px 28px;
    color: #fff;
    border-radius: 25px;
    font-size: 15px;
    font-weight: 500;
  }
}

/* ==================== FAB ==================== */
.fab {
  position: fixed;
  right: 20px;
  bottom: 60px;
  z-index: 50;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:active {
    transform: scale(0.92);
  }

  .fab-icon {
    font-size: 28px;
    color: #fff;
    font-weight: 300;
  }
}

/* ==================== Modal ==================== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}

.modal-content {
  background: #fff;
  border-radius: 24px 24px 0 0;
  width: 100%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;

  .modal-title {
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
  }

  .modal-close {
    font-size: 20px;
    color: #999;
    padding: 4px;
  }
}

.modal-body {
  padding: 20px 24px;
  flex: 1;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;

  .cancel-btn {
    flex: 1;
    padding: 14px;
    text-align: center;
    border-radius: 14px;
    font-size: 16px;
    color: #65746d;
    background: #f5f7f5;
    font-weight: 500;
  }

  .submit-btn {
    flex: 2;
    padding: 14px;
    text-align: center;
    border-radius: 14px;
    font-size: 16px;
    color: #fff;
    font-weight: 600;
  }
}

/* ==================== Form ==================== */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.subject-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.subject-item {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  color: #65746d;
  background: #f5f7f5;
  transition: all 0.2s;

  &.active {
    color: #fff;
  }

  &.subject-add {
    background: #fff;
    border: 1.5px dashed #d0d5d2;
  }
}

.tag-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.tag-chip {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-remove {
  font-size: 14px;
}

.input-wrapper {
  border: 1.5px solid #e8ece9;
  border-radius: 14px;
  padding: 12px 16px;
  background: #fafafa;
  transition: border-color 0.2s;
}

.input-field {
  width: 100%;
  font-size: 15px;
  color: #1a1a2e;
  border: none;
  outline: none;
  background: transparent;
}

.textarea-field {
  width: 100%;
  min-height: 80px;
  font-size: 15px;
  color: #1a1a2e;
  line-height: 1.6;
  border: none;
  outline: none;
  background: transparent;
  resize: none;
}

.difficulty-row {
  display: flex;
  gap: 10px;
}

.diff-item {
  flex: 1;
  padding: 10px;
  text-align: center;
  border-radius: 12px;
  font-size: 14px;
  color: #65746d;
  background: #f5f7f5;
  transition: all 0.2s;

  &.active {
    color: #fff;
  }
}

.image-upload-area {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.image-item {
  position: relative;
  width: 80px;
  height: 80px;
}

.uploaded-image {
  width: 80px;
  height: 80px;
  border-radius: 10px;
}

.image-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #ef5350;
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-add-btn {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  border: 2px dashed #d0d5d2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: #fafafa;

  .add-icon {
    font-size: 24px;
    color: #999;
  }

  .add-text {
    font-size: 11px;
    color: #999;
  }
}

/* ==================== Export Panel ==================== */
.format-row {
  display: flex;
  gap: 10px;
}

.format-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border-radius: 14px;
  background: #f5f7f5;
  font-size: 13px;
  color: #65746d;
  transition: all 0.2s;

  &.active {
    color: #fff;
  }

  &:active {
    transform: scale(0.96);
  }
}

.dropdown-display {
  padding: 12px 16px;
  border: 1.5px solid #e8ece9;
  border-radius: 14px;
  font-size: 15px;
  color: #1a1a2e;
  background: #fafafa;
}

/* ==================== Empty State ==================== */
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;

  .empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
  }

  .empty-text {
    font-size: 16px;
    color: #65746d;
    margin-bottom: 8px;
  }

  .empty-hint {
    font-size: 13px;
    color: #999;
    text-align: center;
  }
}

.bottom-space {
  height: 100px;
}

/* ==================== Theme: Cards (Purple) ==================== */
.theme-cards {
  .header {
    background: linear-gradient(135deg, #6b4ce6 0%, #8b6ef5 100%);
  }

  .sub-nav-item.active {
    color: #6b4ce6;
  }

  .mode-btn.active {
    color: #6b4ce6;
  }

  .filter-item.active {
    background: #6b4ce6;
  }

  .start-review-btn {
    background: #6b4ce6;
  }

  .fab {
    background: #6b4ce6;
    box-shadow: 0 4px 16px rgba(107, 76, 230, 0.35);
  }

  .submit-btn {
    background: #6b4ce6;
  }

  .card-item-subject {
    background: #f3f0ff;
    color: #6b4ce6;
  }

  .section-label {
    color: #6b4ce6;
  }

  .card-item-footer .review-date {
    color: #6b4ce6;
  }

  .edit-btn {
    background: #f3f0ff;
    color: #6b4ce6;
  }

  .review-counter {
    color: #6b4ce6;
  }

  .review-progress-fill {
    background: #6b4ce6;
  }

  .review-subject {
    color: #6b4ce6;
    background: #f3f0ff;
  }

  .question-label {
    color: #6b4ce6;
  }

  .show-answer-btn {
    background: #f3f0ff;

    text {
      color: #6b4ce6;
    }
  }

  .back-btn {
    background: #6b4ce6;
  }

  .subject-item.active {
    background: #6b4ce6;
  }

  .tag-chip {
    background: #f3f0ff;
    color: #6b4ce6;
  }

  .tag-remove {
    color: #6b4ce6;
  }

  .input-wrapper {
    &:focus-within {
      border-color: #6b4ce6;
    }
  }

  .diff-item.active {
    background: #6b4ce6;
  }

  .format-item.active {
    background: #6b4ce6;
  }
}

/* ==================== Theme: Mistakes (Red) ==================== */
.theme-mistakes {
  .header {
    background: linear-gradient(135deg, #ef5350 0%, #f27573 100%);
  }

  .sub-nav-item.active {
    color: #ef5350;
  }

  .mode-btn.active {
    color: #ef5350;
  }

  .filter-item.active {
    background: #ef5350;
  }

  .start-review-btn {
    background: #ef5350;
  }

  .fab {
    background: #ef5350;
    box-shadow: 0 4px 16px rgba(239, 83, 80, 0.35);
  }

  .submit-btn {
    background: #ef5350;
  }

  .section-label {
    color: #ef5350;
  }

  .edit-btn {
    background: #ffebee;
    color: #ef5350;
  }

  .review-counter {
    color: #ef5350;
  }

  .review-progress-fill {
    background: #ef5350;
  }

  .review-subject {
    color: #ef5350;
    background: #ffebee;
  }

  .question-label {
    color: #ef5350;
  }

  .show-answer-btn {
    background: #ffebee;

    text {
      color: #ef5350;
    }
  }

  .back-btn {
    background: #ef5350;
  }

  .subject-item.active {
    background: #ef5350;
  }

  .tag-chip {
    background: #ffebee;
    color: #ef5350;
  }

  .tag-remove {
    color: #ef5350;
  }

  .input-wrapper {
    &:focus-within {
      border-color: #ef5350;
    }
  }

  .diff-item.active {
    background: #ef5350;
  }

  .format-item.active {
    background: #ef5350;
  }

  .analysis-label {
    color: #ef5350;
  }
}
</style>
