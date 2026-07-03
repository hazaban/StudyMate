<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <view class="header-left">
          <text class="title">抗遗忘卡片</text>
          <text class="subtitle">艾宾浩斯记忆曲线，科学对抗遗忘</text>
        </view>
        <view class="header-right">
          <view class="export-btn" @click="showExportModal = true">
            <text class="export-icon">📤</text>
            <text class="export-text">导出</text>
          </view>
        </view>
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

    <!-- Sub Navigation -->
    <view class="sub-nav">
      <view class="sub-nav-item active">知识卡片</view>
      <view class="sub-nav-item" @click="goToMistakes">错题本</view>
    </view>

    <!-- Mode Toggle -->
    <view class="mode-toggle">
      <view class="mode-btn" :class="{ active: viewMode === 'pending' }" @click="switchMode('pending')">今日复习</view>
      <view class="mode-btn" :class="{ active: viewMode === 'all' }" @click="switchMode('all')">查看全部</view>
    </view>

    <!-- Subject Filter (一级) -->
    <view class="filter-section">
      <view class="filter-row">
        <scroll-view scroll-x class="filter-scroll">
          <view class="filter-list">
            <view class="filter-item" :class="{ active: activeSubject === '' }" @click="onSubjectChange('')">全部科目</view>
            <view
              class="filter-item"
              v-for="s in allSubjects"
              :key="s"
              :class="{ active: activeSubject === s }"
              @click="onSubjectChange(s)"
            >{{ s }}</view>
          </view>
        </scroll-view>
        <view class="filter-manage-btn" @click="showManageSubjects = true">⚙</view>
      </view>
    </view>

    <!-- Tag Filter (二级，联动科目) -->
    <view class="filter-section" v-if="availableTags.length > 0">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view class="filter-item tag-item" :class="{ active: activeTag === '' }" @click="activeTag = ''">全部标签</view>
          <view class="filter-item tag-item" v-for="t in availableTags" :key="t" :class="{ active: activeTag === t }" @click="activeTag = t">{{ t }}</view>
        </view>
      </scroll-view>
    </view>

    <!-- Mastery Level Filter (三级) -->
    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view class="filter-item mastery-item" :class="{ active: activeMastery === '' }" @click="activeMastery = ''">全部掌握</view>
          <view class="filter-item mastery-item unmastered" :class="{ active: activeMastery === 'unmastered' }" @click="activeMastery = 'unmastered'">未掌握</view>
          <view class="filter-item mastery-item familiar" :class="{ active: activeMastery === 'familiar' }" @click="activeMastery = 'familiar'">较熟悉</view>
          <view class="filter-item mastery-item mastered" :class="{ active: activeMastery === 'mastered' }" @click="activeMastery = 'mastered'">已掌握</view>
        </view>
      </scroll-view>
    </view>

    <view class="card-list">
      <!-- Review Mode -->
      <view class="review-card" v-if="reviewMode && reviewCards.length > 0">
        <text class="review-counter">{{ reviewIndex + 1 }} / {{ reviewCards.length }}</text>

        <view class="review-card-body">
          <view class="review-subject">{{ reviewCards[reviewIndex].subject }}</view>
          <view class="review-question">
            <text class="question-label">Q</text>
            <text class="question-text">{{ reviewCards[reviewIndex].question }}</text>
          </view>
          <view class="image-gallery" v-if="reviewCards[reviewIndex].question_images && reviewCards[reviewIndex].question_images.length > 0">
            <image v-for="(url, idx) in reviewCards[reviewIndex].question_images" :key="'rq'+idx" :src="url" mode="widthFix" class="review-image" @click="previewImage(url, reviewCards[reviewIndex].question_images)" />
          </view>

          <view class="review-answer" v-if="reviewShowAnswer">
            <view class="answer-divider"></view>
            <view class="answer-content">
              <text class="answer-label">A</text>
              <text class="answer-text">{{ reviewCards[reviewIndex].answer }}</text>
            </view>
            <view class="image-gallery" v-if="reviewCards[reviewIndex].answer_images && reviewCards[reviewIndex].answer_images.length > 0" style="margin-top: 10px;">
              <image v-for="(url, idx) in reviewCards[reviewIndex].answer_images" :key="'ra'+idx" :src="url" mode="widthFix" class="review-image" @click="previewImage(url, reviewCards[reviewIndex].answer_images)" />
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
              <view class="action-btn edit-btn" @click="openEditCard(card)">编辑</view>
              <view class="action-btn del-btn" @click="removeCard(card)">删除</view>
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
              <view class="subject-item subject-add" @click="showSubjectInput = !showSubjectInput">
                <text v-if="!showSubjectInput">+ 自定义</text>
                <text v-else>收起</text>
              </view>
            </view>
            <view class="input-wrapper" v-if="showSubjectInput" style="margin-top: 10px;">
              <input class="input-field" v-model="customSubject" placeholder="输入自定义科目..." @confirm="addCustomSubject" />
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
            <text class="form-label">问题图片（可选）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in form.question_images" :key="'q'+idx">
                <image :src="img" mode="aspectFill" class="uploaded-image" />
                <view class="image-remove" @click="form.question_images.splice(idx, 1)">✕</view>
              </view>
              <view class="image-add-btn" tabindex="0" @click="chooseQuestionImage" @paste="onPasteQuestionImage">
                <text class="add-icon">+</text>
                <text class="add-text">上传/粘贴</text>
              </view>
            </view>
            <text class="paste-hint">💡 电脑端：点击上传框后按 Ctrl+V 直接粘贴图片</text>
          </view>
          <view class="form-group">
            <text class="form-label">答案图片（可选）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in form.answer_images" :key="'a'+idx">
                <image :src="img" mode="aspectFill" class="uploaded-image" />
                <view class="image-remove" @click="form.answer_images.splice(idx, 1)">✕</view>
              </view>
              <view class="image-add-btn" tabindex="0" @click="chooseAnswerImage" @paste="onPasteAnswerImage">
                <text class="add-icon">+</text>
                <text class="add-text">上传/粘贴</text>
              </view>
            </view>
            <text class="paste-hint">💡 电脑端：点击上传框后按 Ctrl+V 直接粘贴图片</text>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showForm = false">取消</view>
          <view class="submit-btn" @click="submitCard">提交</view>
        </view>
      </view>
    </view>

    <!-- Edit Card Modal -->
    <view class="modal-overlay" v-if="showEditCard" @click="showEditCard = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑知识卡片</text>
          <view class="modal-close" @click="showEditCard = false">✕</view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="form-group">
            <text class="form-label">科目</text>
            <view class="subject-grid">
              <view class="subject-item" v-for="s in allSubjects" :key="s" :class="{ active: editForm.subject === s }" @click="editForm.subject = s">{{ s }}</view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">标签（逗号分隔）</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="editTagInput" placeholder="输入标签，逗号分隔..." @blur="parseEditTags" />
            </view>
            <view class="tag-preview" v-if="editForm.tags.length > 0">
              <view class="tag-chip" v-for="(t, idx) in editForm.tags" :key="idx">
                {{ t }}
                <text class="tag-remove" @click="editForm.tags.splice(idx, 1)">✕</text>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">问题</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="editForm.question" placeholder="请输入复习问题..." maxlength="2000" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">答案</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="editForm.answer" placeholder="请输入答案..." maxlength="2000" />
            </view>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showEditCard = false">取消</view>
          <view class="submit-btn" @click="saveEditCard">保存</view>
        </view>
      </view>
    </view>

    <!-- Export Modal -->
    <view class="export-overlay" v-if="showExportModal" @click="showExportModal = false">
      <view class="export-dialog" @click.stop>
        <view class="export-dialog-top">
          <text class="export-dialog-title">导出知识卡片</text>
          <view class="export-dialog-close" @click="showExportModal = false">✕</view>
        </view>
        <view class="export-dialog-body">
          <view class="export-option" @click="doExport('csv')">
            <text class="export-opt-icon">📄</text>
            <view class="export-opt-right">
              <text class="export-opt-label">导出 CSV</text>
              <text class="export-opt-desc">表格数据，可用 Excel 打开</text>
            </view>
          </view>
          <view class="export-option" @click="doExport('excel')">
            <text class="export-opt-icon">📊</text>
            <view class="export-opt-right">
              <text class="export-opt-label">导出 Excel</text>
              <text class="export-opt-desc">HTML 表格格式，兼容 Excel</text>
            </view>
          </view>
          <view class="export-option" @click="doExport('pdf')">
            <text class="export-opt-icon">🖨</text>
            <view class="export-opt-right">
              <text class="export-opt-label">导出 PDF</text>
              <text class="export-opt-desc">调用浏览器打印，保存为 PDF</text>
            </view>
          </view>
          <view class="export-answer-toggle">
            <text class="export-toggle-label">导出内容包含答案</text>
            <view class="export-switch" :class="{ on: exportIncludeAnswer }" @click.stop="exportIncludeAnswer = !exportIncludeAnswer">
              <view class="export-switch-dot"></view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Manage Subjects Modal -->
    <view class="export-overlay" v-if="showManageSubjects" @click="showManageSubjects = false">
      <view class="export-dialog" @click.stop>
        <view class="export-dialog-top">
          <text class="export-dialog-title">管理科目</text>
          <view class="export-dialog-close" @click="showManageSubjects = false">✕</view>
        </view>
        <view class="export-dialog-body">
          <view class="manage-item" v-for="s in allSubjects" :key="s">
            <view class="manage-left">
              <text class="manage-name">{{ s }}</text>
              <text class="manage-badge" v-if="!customSubjects.includes(s)">预设</text>
              <text class="manage-badge custom-badge" v-else>自定义</text>
            </view>
            <view
              class="manage-del-btn"
              v-if="customSubjects.includes(s)"
              @click="removeSubject(s)"
            >删除</view>
          </view>
          <view class="manage-add-row">
            <input
              class="manage-add-input"
              v-model="manageNewSubject"
              placeholder="输入新科目名称"
              @confirm="addManageSubject"
            />
            <view class="manage-add-btn" @click="addManageSubject">添加</view>
          </view>
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
import { exportCardsCSV, exportCardsExcel, exportCardsPDF, getDefaultTags, SUBJECT_TAGS } from '@/utils/export'
import { uploadUtil } from '@/utils/upload'

const planStore = usePlanStore()
const userStore = useUserStore()

const viewMode = ref('pending')
const activeSubject = ref('')
const activeTag = ref('')
const activeMastery = ref('')
const showForm = ref(false)
const reviewMode = ref(false)
const reviewShowAnswer = ref(false)
const reviewIndex = ref(0)
const reviewComplete = ref(false)
const cards = ref([])
const tagInput = ref('')
const today = new Date().toISOString().split('T')[0]

// Export
const showExportModal = ref(false)
const exportIncludeAnswer = ref(true)

// Subject options
const defaultSubjects = Object.keys(SUBJECT_TAGS)
const allSubjects = ref([...defaultSubjects])
const customSubjects = ref([])
const showSubjectInput = ref(false)
const customSubject = ref('')
const showManageSubjects = ref(false)
const manageNewSubject = ref('')

function addCustomSubject() {
  const name = customSubject.value.trim()
  if (!name) return
  if (!allSubjects.value.includes(name)) {
    allSubjects.value.push(name)
  }
  form.value.subject = name
  customSubject.value = ''
  showSubjectInput.value = false
}

function addManageSubject() {
  const name = manageNewSubject.value.trim()
  if (!name) return
  if (!allSubjects.value.includes(name)) {
    allSubjects.value.push(name)
    customSubjects.value.push(name)
  }
  manageNewSubject.value = ''
}

function removeSubject(name) {
  uni.showModal({
    title: '删除科目',
    content: `确定要删除「${name}」吗？`,
    success: (res) => {
      if (res.confirm) {
        customSubjects.value = customSubjects.value.filter(s => s !== name)
        allSubjects.value = allSubjects.value.filter(s => s !== name)
        if (activeSubject.value === name) {
          activeSubject.value = ''
          activeTag.value = ''
        }
      }
    }
  })
}

const form = ref({
  subject: '数据结构',
  question: '',
  answer: '',
  question_images: [],
  answer_images: [],
  tags: []
})

// Edit card
const showEditCard = ref(false)
const editingCardId = ref(null)
const editTagInput = ref('')
const editForm = ref({
  subject: '',
  question: '',
  answer: '',
  tags: []
})

// Available tags based on selected subject (二级联动)
const availableTags = computed(() => {
  if (activeSubject.value) {
    return getDefaultTags(activeSubject.value)
  }
  // When "全部科目" selected, collect all tags across all records
  const set = new Set()
  cards.value.forEach(c => (c.tags || []).forEach(t => set.add(t)))
  return [...set]
})

// Filter cards by subject AND tag AND mastery
const filteredCards = computed(() => {
  let result = cards.value
  if (activeSubject.value) {
    result = result.filter(c => c.subject === activeSubject.value)
  }
  if (activeTag.value) {
    result = result.filter(c => (c.tags || []).includes(activeTag.value))
  }
  if (activeMastery.value) {
    result = result.filter(c => c.mastery_level === activeMastery.value)
  }
  return result
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

function parseEditTags() {
  if (!editTagInput.value.trim()) return
  const tags = editTagInput.value.split(/[,，]/).map(t => t.trim()).filter(Boolean)
  editForm.value.tags = [...new Set([...editForm.value.tags, ...tags])]
  editTagInput.value = ''
}

// ── Subject change → reset tag ──
function onSubjectChange(subject) {
  activeSubject.value = subject
  activeTag.value = ''
  activeMastery.value = ''
}

function switchMode(mode) {
  viewMode.value = mode
  loadCards()
}

function goToMistakes() {
  uni.navigateTo({ url: '/pages/review/mistake-book' })
}

function chooseQuestionImage() {
  uni.chooseImage({
    count: 9, sizeType: ['compressed'], sourceType: ['album', 'camera'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.question_images.push(path))
  })
}
function chooseAnswerImage() {
  uni.chooseImage({
    count: 9, sizeType: ['compressed'], sourceType: ['album', 'camera'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.answer_images.push(path))
  })
}
async function onPasteQuestionImage(e) {
  const files = await uploadUtil.pasteToFiles(e)
  files.forEach(f => form.value.question_images.push(f))
  if (files.length > 0) {
    uni.showToast({ title: `已粘贴 ${files.length} 张图片`, icon: 'success' })
  }
}
async function onPasteAnswerImage(e) {
  const files = await uploadUtil.pasteToFiles(e)
  files.forEach(f => form.value.answer_images.push(f))
  if (files.length > 0) {
    uni.showToast({ title: `已粘贴 ${files.length} 张图片`, icon: 'success' })
  }
}
function previewImage(current, urls) { uni.previewImage({ current, urls }) }

// ── Add ──
async function submitCard() {
  const hasQ = form.value.question.trim() || form.value.question_images.length > 0
  const hasA = form.value.answer.trim() || form.value.answer_images.length > 0
  if (!hasQ) { uni.showToast({ title: '请输入问题或上传问题图片', icon: 'none' }); return }
  if (!hasA) { uni.showToast({ title: '请输入答案或上传答案图片', icon: 'none' }); return }
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }

  uni.showLoading({ title: '上传图片中...' })
  try {
    const userId = userStore.userInfo?.id || 'guest'

    const qImages = []
    for (const path of form.value.question_images) {
      if (path.startsWith('http')) { qImages.push(path); continue }
      const url = await uploadUtil.uploadCardQuestion(path, userId)
      qImages.push(url)
    }

    const aImages = []
    for (const path of form.value.answer_images) {
      if (path.startsWith('http')) { aImages.push(path); continue }
      const url = await uploadUtil.uploadCardAnswer(path, userId)
      aImages.push(url)
    }

    uni.showLoading({ title: '保存中...' })

    await api.createCard({
      plan_id: planStore.currentPlan.id,
      question: form.value.question,
      answer: form.value.answer,
      subject: form.value.subject,
      mastery_level: 'unmastered',
      next_review_date: today,
      question_images: qImages,
      answer_images: aImages,
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
  form.value = { subject: '数据结构', question: '', answer: '', question_images: [], answer_images: [], tags: [] }
  tagInput.value = ''
}

// ── Edit ──
function openEditCard(card) {
  editingCardId.value = card.id
  editForm.value = {
    subject: card.subject,
    question: card.question,
    answer: card.answer,
    tags: [...(card.tags || [])]
  }
  editTagInput.value = ''
  showEditCard.value = true
}

async function saveEditCard() {
  if (!editForm.value.question.trim()) { uni.showToast({ title: '请输入问题', icon: 'none' }); return }
  if (!editForm.value.answer.trim()) { uni.showToast({ title: '请输入答案', icon: 'none' }); return }

  uni.showLoading({ title: '保存中...' })
  try {
    await api.updateCard(editingCardId.value, {
      question: editForm.value.question,
      answer: editForm.value.answer,
      subject: editForm.value.subject,
      tags: editForm.value.tags
    })
    showEditCard.value = false
    uni.showToast({ title: '编辑成功', icon: 'success' })
    await loadCards()
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

// ── Review ──
function startReview() {
  reviewMode.value = true; reviewShowAnswer.value = false; reviewIndex.value = 0; reviewComplete.value = false
}

async function reviewResult(level) {
  const currentCard = reviewCards.value[reviewIndex.value]
  await api.reviewCard(currentCard.id, level)
  if (reviewIndex.value < reviewCards.value.length - 1) {
    reviewIndex.value++; reviewShowAnswer.value = false
  } else {
    reviewMode.value = false; reviewComplete.value = true; await loadCards()
  }
}

function exitReview() {
  reviewMode.value = false; reviewComplete.value = false; reviewIndex.value = 0
  viewMode.value = 'all'; activeSubject.value = ''; activeTag.value = ''; loadCards()
}

async function removeCard(card) {
  const res = await new Promise(r => uni.showModal({ title: '删除确认', content: '确定删除吗？', success: r }))
  if (res.confirm) {
    try {
      await api.deleteCard(card.id)
      cards.value = cards.value.filter(c => c.id !== card.id)
      uni.showToast({ title: '已删除', icon: 'success' })
    } catch (e) { uni.showToast({ title: '删除失败', icon: 'none' }) }
  }
}

// ── Export ──
async function doExport(format) {
  showExportModal.value = false
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }
  uni.showLoading({ title: '加载数据...' })
  try {
    // Use the existing getCards endpoint with no pagination
    const result = await api.getCards(
      planStore.currentPlan.id,
      activeSubject.value || null,
      activeTag.value || null,
      false  // not pending only, get ALL
    )
    let data = result.cards || []
    // Client-side mastery filter for export
    if (activeMastery.value) {
      data = data.filter(c => c.mastery_level === activeMastery.value)
    }
    if (data.length === 0) { uni.showToast({ title: '没有可导出的数据', icon: 'none' }); return }
    const opts = { includeAnswer: exportIncludeAnswer.value }
    if (format === 'csv') exportCardsCSV(data, opts)
    else if (format === 'excel') exportCardsExcel(data, opts)
    else if (format === 'pdf') exportCardsPDF(data, opts)
  } catch (e) {
    console.error('Export error:', e)
    uni.showToast({ title: e.message || '导出失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

// ── Load ──
async function loadCards() {
  if (!planStore.currentPlan) return
  try {
    const pending = viewMode.value === 'pending'
    // Apply subject filter if selected (pass as subject param for backend filtering)
    const subj = activeSubject.value || null
    const tag = activeTag.value || null
    const result = await api.getCards(planStore.currentPlan.id, subj, tag, pending)
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

watch(() => planStore.currentPlan?.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
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
  display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;
}
.header-left {
  .title { display: block; font-size: 26px; font-weight: 700; color: #fff; margin-bottom: 4px; }
  .subtitle { font-size: 14px; color: rgba(255,255,255,0.8); }
}
.header-right { position: relative; }
.export-btn {
  display: flex; align-items: center; gap: 4px;
  padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.3);
  &:active { background: rgba(255,255,255,0.35); }
  .export-icon { font-size: 14px; }
  .export-text { font-size: 13px; color: #fff; font-weight: 500; }
}

.stats-row {
  display: flex; background: rgba(255,255,255,0.12); border-radius: 16px; padding: 16px; border: 1px solid rgba(255,255,255,0.15);
}
.stat-item { flex: 1; text-align: center; .stat-num { display: block; font-size: 22px; font-weight: 700; color: #fff; } .stat-label { font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 2px; } }

.sub-nav { display: flex; margin-bottom: 16px; background: #f5f7f5; border-radius: 12px; padding: 4px; }
.sub-nav-item { flex: 1; text-align: center; padding: 10px; border-radius: 10px; font-size: 14px; color: #65746d; transition: all 0.2s; &.active { background: #fff; color: #6b4ce6; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); } }

.mode-toggle { display: flex; margin-bottom: 14px; background: #f5f7f5; border-radius: 12px; padding: 4px; }
.mode-btn { flex: 1; text-align: center; padding: 10px; border-radius: 10px; font-size: 14px; color: #65746d; transition: all 0.2s; &.active { background: #fff; color: #6b4ce6; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); } }

.filter-section { margin-bottom: 10px; }
.filter-scroll { white-space: nowrap; width: 100%; }
.filter-list { display: inline-flex; gap: 8px; padding: 2px 0; }
.filter-item { display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; white-space: nowrap; transition: all 0.2s; &.active { background: #6b4ce6; color: #fff; } }
.filter-row { display: flex; align-items: center; gap: 6px; }
.filter-scroll { flex: 1; min-width: 0; }
.mastery-item {
  &.active { background: #6b4ce6; color: #fff; }
  &.unmastered.active { background: #ef5350; }
  &.familiar.active { background: #ffb74d; }
  &.mastered.active { background: #66bb6a; }
}
.filter-manage-btn {
  width: 32px; height: 32px; border-radius: 50%; background: #f5f7f5;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0; border: 1px solid #e0e0e0;
  &:active { background: #e8e0ff; }
}
.tag-item { &.active { background: #8b6ef5; } }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; .section-title { font-size: 18px; font-weight: 600; color: #1a1a2e; } .section-count { font-size: 13px; color: #999; } }
.start-review-btn { background: #6b4ce6; color: #fff; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 500; &:active { transform: scale(0.96); } }

.card-item { background: #fff; border-radius: 16px; padding: 18px; margin-bottom: 12px; border: 1px solid #e8ece9; box-shadow: 0 1px 4px rgba(0,0,0,0.03); &.not-today { opacity: 0.6; } }
.card-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; .card-item-subject { font-size: 12px; padding: 4px 12px; background: #f3f0ff; border-radius: 20px; color: #6b4ce6; } }
.card-item-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.card-tag { font-size: 11px; padding: 3px 8px; border-radius: 8px; background: #f5f5f5; color: #65746d; }
.mastery-badge { font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 500; &.badge-red { background: #ffebee; color: #c62828; } &.badge-orange { background: #fff3e0; color: #e65100; } &.badge-green { background: #e8f5e9; color: #2e7d32; } }

.section-label { display: block; font-size: 12px; color: #6b4ce6; margin-bottom: 6px; font-weight: 500; }
.card-question-text { font-size: 15px; color: #1a1a2e; line-height: 1.6; display: block; }

.card-item-footer { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-top: 12px; .review-count { font-size: 12px; color: #999; } .review-date { font-size: 12px; color: #6b4ce6; } .card-item-actions { display: flex; gap: 8px; margin-left: auto; } }
.action-btn { padding: 6px 14px; border-radius: 8px; font-size: 13px; background: #f5f5f5; color: #999; }
.edit-btn { background: #f3f0ff; color: #6b4ce6; &:active { background: #e8e0ff; } }
.del-btn { &:active { background: #ffebee; color: #c62828; } }

/* Review */
.review-card { background: #fff; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); margin-bottom: 20px; }
.review-counter { display: block; font-size: 14px; color: #6b4ce6; font-weight: 600; margin-bottom: 16px; }
.review-card-body { min-height: 160px; }
.review-subject { font-size: 13px; color: #6b4ce6; background: #f3f0ff; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 16px; }
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
.show-answer-btn { text-align: center; padding: 16px; background: #f3f0ff; border-radius: 14px; &:active { transform: scale(0.98); background: #e8e0ff; } text { font-size: 16px; color: #6b4ce6; font-weight: 600; } }
.review-result-btns { display: flex; gap: 12px; }
.result-btn { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 8px; border-radius: 14px; &:active { transform: scale(0.96); } &.fail { background: #fff0f0; .result-text { color: #c62828; } } &.ok { background: #fff8f0; .result-text { color: #e65100; } } &.great { background: #f0fff4; .result-text { color: #2e7d32; } } .result-icon { font-size: 24px; } .result-text { font-size: 13px; font-weight: 500; } }
.review-complete { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .complete-icon { font-size: 56px; margin-bottom: 12px; } .complete-text { font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; } .back-btn { padding: 12px 28px; background: #6b4ce6; color: #fff; border-radius: 25px; font-size: 15px; font-weight: 500; } }

.fab { position: fixed; right: 20px; bottom: 60px; z-index: 50; width: 56px; height: 56px; border-radius: 50%; background: #6b4ce6; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(107,76,230,0.35); &:active { transform: scale(0.92); } .fab-icon { font-size: 28px; color: #fff; font-weight: 300; } }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; }
.modal-content { background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; .modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; } .modal-close { font-size: 20px; color: #999; padding: 4px; } }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; .cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; } .submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #6b4ce6; font-weight: 600; } }

.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-item { padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; transition: all 0.2s; &.active { background: #6b4ce6; color: #fff; } &.subject-add { background: #fff; border: 1.5px dashed #d0d5d2; color: #6b4ce6; } }
.tag-preview { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.tag-chip { padding: 4px 10px; border-radius: 12px; font-size: 12px; background: #f3f0ff; color: #6b4ce6; display: flex; align-items: center; gap: 4px; }
.tag-remove { font-size: 14px; color: #6b4ce6; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; &:focus-within { border-color: #6b4ce6; } }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 80px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.image-upload-area { display: flex; gap: 10px; flex-wrap: wrap; }
.image-item { position: relative; width: 80px; height: 80px; }
.uploaded-image { width: 80px; height: 80px; border-radius: 10px; }
.image-remove { position: absolute; top: -6px; right: -6px; width: 22px; height: 22px; border-radius: 50%; background: #ef5350; color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; }
.image-add-btn { width: 80px; height: 80px; border-radius: 10px; border: 2px dashed #d0d5d2; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; background: #fafafa; cursor: pointer; outline: none;
  &:focus { border-color: $accent; background: #f0f7f4; }
  .add-icon { font-size: 24px; color: #999; } .add-text { font-size: 11px; color: #999; } }
.paste-hint { display: block; font-size: 11px; color: $muted; margin-top: 6px; }

/* Export Modal - centered dialog */
.export-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 200;
  display: flex; align-items: center; justify-content: center; padding: 30px;
}
.export-dialog {
  background: #fff; border-radius: 20px; width: 100%; max-width: 360px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.15); overflow: hidden;
}
.export-dialog-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 20px 14px;
}
.export-dialog-title { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.export-dialog-close {
  width: 28px; height: 28px; border-radius: 50%; background: #f5f5f5;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; color: #999;
  &:active { background: #e0e0e0; }
}
.export-dialog-body { padding: 0 20px 20px; }
.export-option {
  display: flex; align-items: center; gap: 12px; padding: 12px 14px; margin-bottom: 8px;
  background: #f5f7f5; border-radius: 12px; border: 1.5px solid transparent;
  &:active { border-color: #6b4ce6; background: #f3f0ff; }
}
.export-opt-icon { font-size: 28px; flex-shrink: 0; }
.export-opt-right { flex: 1; }
.export-opt-label { font-size: 15px; font-weight: 600; color: #1a1a2e; display: block; }
.export-opt-desc { font-size: 12px; color: #999; margin-top: 2px; display: block; }

.export-answer-toggle {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 4px 0; margin-top: 6px; border-top: 1px solid #e0e0e0;
}
.export-toggle-label { font-size: 14px; color: #65746d; font-weight: 500; }

.export-switch {
  width: 48px; height: 28px; border-radius: 14px; background: #d0d5d2;
  padding: 2px; display: flex; align-items: center; transition: background 0.25s;
  flex-shrink: 0;
}
.export-switch.on { background: #6b4ce6; justify-content: flex-end; }
.export-switch-dot {
  width: 24px; height: 24px; border-radius: 50%; background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2); transition: none;
}

/* Manage Subjects */
.manage-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-radius: 10px; margin-bottom: 6px;
  background: #f5f7f5;
}
.manage-left { display: flex; align-items: center; gap: 8px; }
.manage-name { font-size: 14px; color: #1a1a2e; font-weight: 500; }
.manage-badge {
  font-size: 10px; padding: 2px 8px; border-radius: 10px;
  background: #e8e0ff; color: #6b4ce6;
}
.custom-badge { background: #fff3e0; color: #e65100; }
.manage-del-btn {
  font-size: 12px; padding: 5px 12px; border-radius: 8px;
  background: #ffebee; color: #c62828; font-weight: 500;
  &:active { background: #ffcdd2; }
}
.manage-add-row {
  display: flex; gap: 8px; margin-top: 12px; padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}
.manage-add-input {
  flex: 1; padding: 10px 12px; border: 1.5px solid #e0e0e0; border-radius: 10px;
  font-size: 14px; color: #1a1a2e; background: #f5f7f5;
  height: 44px; line-height: 24px;
}
.manage-add-input:focus { border-color: #6b4ce6; }
.manage-add-btn {
  padding: 10px 20px; border-radius: 10px; background: #6b4ce6; color: #fff;
  font-size: 14px; font-weight: 600; white-space: nowrap;
  &:active { opacity: 0.85; }
}

.empty { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .empty-icon { font-size: 48px; margin-bottom: 12px; } .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; } .empty-hint { font-size: 13px; color: #999; text-align: center; } }
.bottom-space { height: 100px; }
</style>
