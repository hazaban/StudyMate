<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <view class="header-left">
          <text class="title">错题本</text>
          <text class="subtitle">记录每一次错误，让知识不再溜走</text>
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

    <!-- Sub Navigation -->
    <view class="sub-nav">
      <view class="sub-nav-item" @click="goToCards">知识卡片</view>
      <view class="sub-nav-item active">错题本</view>
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

    <!-- Error Count Filter -->
    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view class="filter-item err-item" :class="{ active: activeErrorCount === '' }" @click="activeErrorCount = ''">全部次数</view>
          <view class="filter-item err-item err-1" :class="{ active: activeErrorCount === '1' }" @click="activeErrorCount = '1'">做错1次</view>
          <view class="filter-item err-item err-2" :class="{ active: activeErrorCount === '2' }" @click="activeErrorCount = '2'">做错2次</view>
          <view class="filter-item err-item err-3" :class="{ active: activeErrorCount === '3+' }" @click="activeErrorCount = '3+'">做错3次+</view>
        </view>
      </scroll-view>
    </view>

    <view class="mistake-list">
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

      <!-- Review Empty -->
      <view class="review-complete" v-if="reviewMode && reviewCards.length === 0">
        <text class="complete-icon">🎉</text>
        <text class="complete-text">今天没有需要复习的错题</text>
        <view class="back-btn" @click="exitReview">查看全部</view>
      </view>

      <!-- Review Complete -->
      <view class="review-complete" v-if="reviewComplete">
        <text class="complete-icon">🏆</text>
        <text class="complete-text">复习完成！</text>
        <text class="complete-hint">正确 {{ reviewCorrect }} / {{ reviewTotal }} 道</text>
        <view class="back-btn" @click="exitReview">返回错题列表</view>
      </view>

      <!-- Normal List -->
      <view v-if="!reviewMode && !reviewComplete">
        <view class="section-header" v-if="viewMode === 'pending' && filteredMistakes.length > 0">
          <text class="section-title">今日待复习 · {{ filteredMistakes.length }} 道</text>
          <view class="start-review-btn" @click="startReview"><text>开始复习</text></view>
        </view>

        <view class="empty" v-if="filteredMistakes.length === 0">
          <text class="empty-icon">📝</text>
          <text class="empty-text">{{ viewMode === 'pending' ? '今天没有需要复习的错题' : '暂无错题' }}</text>
          <text class="empty-hint">点击右下角按钮，手动录入错题</text>
        </view>

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
              <image v-for="(url, idx) in mistake.question_images" :key="idx" :src="url" mode="widthFix" class="mistake-image" @click="previewImage(url, mistake.question_images)" />
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
            <text class="correct-progress" v-if="!mistake.mastered || mistake.mastered === '0'">正确 {{ mistake.correct_count }}/2 次</text>
            <text class="error-count">做错 {{ mistake.error_count }} 次</text>
            <view class="mistake-actions">
              <view class="action-btn edit-btn" @click="openEditMistake(mistake)">编辑</view>
              <view class="action-btn master-btn" @click="toggleMastered(mistake)">
                {{ mistake.mastered === '1' ? '重新攻克' : '已掌握' }}
              </view>
              <view class="action-btn del-btn" @click="removeMistake(mistake)">删除</view>
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
            <text class="form-label">自定义标签（逗号分隔）</text>
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
              <textarea class="textarea-field" v-model="form.analysis" placeholder="分析错误原因..." maxlength="2000" />
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
            <text class="form-label">题目图片（可选）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in form.question_images" :key="'q'+idx">
                <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, form.question_images)" />
                <view class="image-remove" @click="form.question_images.splice(idx, 1)">✕</view>
              </view>
              <view class="upload-actions">
                <view class="upload-action-btn" @click="takeQuestionPhoto">
                  <text class="action-icon">📷</text>
                  <text class="action-text">拍照</text>
                </view>
                <view class="upload-action-btn" @click="chooseQuestionImage">
                  <text class="action-icon">🖼️</text>
                  <text class="action-text">相册</text>
                </view>
                <view
                  class="upload-action-btn paste-btn"
                  :class="{ active: activePasteTarget === 'add_question' }"
                  @click="setPasteTarget('add_question')"
                >
                  <text class="action-icon">📋</text>
                  <text class="action-text">粘贴</text>
                </view>
              </view>
            </view>
            <text class="paste-hint">💡 手机端可拍照或从相册选择，电脑端点击「粘贴」后按 Ctrl+V</text>
          </view>
          <view class="form-group">
            <text class="form-label">答案图片（可选）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in form.answer_images" :key="'a'+idx">
                <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, form.answer_images)" />
                <view class="image-remove" @click="form.answer_images.splice(idx, 1)">✕</view>
              </view>
              <view class="upload-actions">
                <view class="upload-action-btn" @click="takeAnswerPhoto">
                  <text class="action-icon">📷</text>
                  <text class="action-text">拍照</text>
                </view>
                <view class="upload-action-btn" @click="chooseAnswerImage">
                  <text class="action-icon">🖼️</text>
                  <text class="action-text">相册</text>
                </view>
                <view
                  class="upload-action-btn paste-btn"
                  :class="{ active: activePasteTarget === 'add_answer' }"
                  @click="setPasteTarget('add_answer')"
                >
                  <text class="action-icon">📋</text>
                  <text class="action-text">粘贴</text>
                </view>
              </view>
            </view>
            <text class="paste-hint">💡 手机端可拍照或从相册选择，电脑端点击「粘贴」后按 Ctrl+V</text>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showForm = false">取消</view>
          <view class="submit-btn" @click="submitMistake">提交</view>
        </view>
      </view>
    </view>

    <!-- Edit Mistake Modal -->
    <view class="modal-overlay" v-if="showEditMistake" @click="showEditMistake = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑错题</text>
          <view class="modal-close" @click="showEditMistake = false">✕</view>
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
            <text class="form-label">题目内容</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="editForm.question" placeholder="请输入错题题目..." maxlength="2000" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">正确答案</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="editForm.answer" placeholder="请输入正确答案..." maxlength="2000" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">错误分析（可选）</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="editForm.analysis" placeholder="分析错误原因..." maxlength="2000" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">难度</text>
            <view class="difficulty-row">
              <view class="diff-item" :class="{ active: editForm.difficulty === 'easy' }" @click="editForm.difficulty = 'easy'">简单</view>
              <view class="diff-item" :class="{ active: editForm.difficulty === 'medium' }" @click="editForm.difficulty = 'medium'">中等</view>
              <view class="diff-item" :class="{ active: editForm.difficulty === 'hard' }" @click="editForm.difficulty = 'hard'">困难</view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">题目图片（可选）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in editForm.question_images" :key="'eq'+idx">
                <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, editForm.question_images)" />
                <view class="image-remove" @click="editForm.question_images.splice(idx, 1)">✕</view>
              </view>
              <view class="upload-actions">
                <view class="upload-action-btn" @click="takeEditQuestionPhoto">
                  <text class="action-icon">📷</text>
                  <text class="action-text">拍照</text>
                </view>
                <view class="upload-action-btn" @click="chooseEditQuestionImage">
                  <text class="action-icon">🖼️</text>
                  <text class="action-text">相册</text>
                </view>
                <view
                  class="upload-action-btn paste-btn"
                  :class="{ active: activePasteTarget === 'edit_question' }"
                  @click="setPasteTarget('edit_question')"
                >
                  <text class="action-icon">📋</text>
                  <text class="action-text">粘贴</text>
                </view>
              </view>
            </view>
            <text class="paste-hint">💡 手机端可拍照或从相册选择，电脑端点击「粘贴」后按 Ctrl+V</text>
          </view>
          <view class="form-group">
            <text class="form-label">答案图片（可选）</text>
            <view class="image-upload-area">
              <view class="image-item" v-for="(img, idx) in editForm.answer_images" :key="'ea'+idx">
                <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, editForm.answer_images)" />
                <view class="image-remove" @click="editForm.answer_images.splice(idx, 1)">✕</view>
              </view>
              <view class="upload-actions">
                <view class="upload-action-btn" @click="takeEditAnswerPhoto">
                  <text class="action-icon">📷</text>
                  <text class="action-text">拍照</text>
                </view>
                <view class="upload-action-btn" @click="chooseEditAnswerImage">
                  <text class="action-icon">🖼️</text>
                  <text class="action-text">相册</text>
                </view>
                <view
                  class="upload-action-btn paste-btn"
                  :class="{ active: activePasteTarget === 'edit_answer' }"
                  @click="setPasteTarget('edit_answer')"
                >
                  <text class="action-icon">📋</text>
                  <text class="action-text">粘贴</text>
                </view>
              </view>
            </view>
            <text class="paste-hint">💡 手机端可拍照或从相册选择，电脑端点击「粘贴」后按 Ctrl+V</text>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showEditMistake = false">取消</view>
          <view class="submit-btn" @click="saveEditMistake">保存</view>
        </view>
      </view>
    </view>

    <!-- Export Modal -->
    <view class="export-overlay" v-if="showExportModal" @click="showExportModal = false">
      <view class="export-dialog" @click.stop>
        <view class="export-dialog-top">
          <text class="export-dialog-title">导出错题本</text>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'
import { exportMistakesCSV, exportMistakesExcel, exportMistakesPDF, getDefaultTags, SUBJECT_TAGS } from '@/utils/export'
import { uploadUtil } from '@/utils/upload'

const planStore = usePlanStore()
const userStore = useUserStore()

const viewMode = ref('pending')
const activeSubject = ref('')
const activeTag = ref('')
const activeErrorCount = ref('')
const showForm = ref(false)
const reviewMode = ref(false)
const reviewShowAnswer = ref(false)
const reviewIndex = ref(0)
const reviewCorrect = ref(0)
const reviewTotal = ref(0)
const reviewComplete = ref(false)
const mistakes = ref([])
const tagInput = ref('')

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
  analysis: '',
  difficulty: 'medium',
  question_images: [],
  answer_images: [],
  tags: []
})

// Edit mistake
const showEditMistake = ref(false)
const editingMistakeId = ref(null)
const editTagInput = ref('')
const editForm = ref({
  subject: '',
  question: '',
  answer: '',
  analysis: '',
  difficulty: 'medium',
  question_images: [],
  answer_images: [],
  tags: []
})

// Paste target tracking
const activePasteTarget = ref('')

function setPasteTarget(target) {
  activePasteTarget.value = target
  // #ifdef H5
  uni.showToast({ title: '请按 Ctrl+V 粘贴图片', icon: 'none', duration: 1500 })
  // #endif
}

function handleGlobalPaste(e) {
  if (!activePasteTarget.value) return
  const items = e.clipboardData?.items
  if (!items) return
  const files = []
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) {
        const url = URL.createObjectURL(file)
        files.push(url)
      }
    }
  }
  if (files.length === 0) return
  e.preventDefault()
  const target = activePasteTarget.value
  let targetArray = null
  if (target === 'add_question') targetArray = form.value.question_images
  else if (target === 'add_answer') targetArray = form.value.answer_images
  else if (target === 'edit_question') targetArray = editForm.value.question_images
  else if (target === 'edit_answer') targetArray = editForm.value.answer_images
  if (targetArray) {
    files.forEach(f => targetArray.push(f))
    uni.showToast({ title: `已粘贴 ${files.length} 张图片`, icon: 'success' })
  }
}

// Available tags based on selected subject (二级联动)
const availableTags = computed(() => {
  if (activeSubject.value) {
    return getDefaultTags(activeSubject.value)
  }
  const set = new Set()
  mistakes.value.forEach(m => (m.tags || []).forEach(t => set.add(t)))
  return [...set]
})

const filteredMistakes = computed(() => {
  let result = mistakes.value
  if (activeSubject.value) {
    result = result.filter(m => m.subject === activeSubject.value)
  }
  if (activeTag.value) {
    result = result.filter(m => (m.tags || []).includes(activeTag.value))
  }
  if (activeErrorCount.value === '1') {
    result = result.filter(m => m.error_count === 1)
  } else if (activeErrorCount.value === '2') {
    result = result.filter(m => m.error_count === 2)
  } else if (activeErrorCount.value === '3+') {
    result = result.filter(m => m.error_count >= 3)
  }
  return result
})

const reviewCards = computed(() => {
  return filteredMistakes.value.filter(m => m.mastered === '0')
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
  activeErrorCount.value = ''
}

function switchMode(mode) {
  viewMode.value = mode
  loadMistakes()
}

function goBack() {
  uni.switchTab({ url: '/pages/review/flash-cards' })
}

function goToCards() {
  uni.switchTab({ url: '/pages/review/flash-cards' })
}

function chooseQuestionImage() {
  uni.chooseImage({
    count: 9, sizeType: ['compressed'], sourceType: ['album'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.question_images.push(path))
  })
}
function chooseAnswerImage() {
  uni.chooseImage({
    count: 9, sizeType: ['compressed'], sourceType: ['album'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.answer_images.push(path))
  })
}
function takeQuestionPhoto() {
  uni.chooseImage({
    count: 1, sizeType: ['compressed'], sourceType: ['camera'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.question_images.push(path))
  })
}
function takeAnswerPhoto() {
  uni.chooseImage({
    count: 1, sizeType: ['compressed'], sourceType: ['camera'],
    success: (res) => res.tempFilePaths.forEach(path => form.value.answer_images.push(path))
  })
}
function chooseEditQuestionImage() {
  uni.chooseImage({
    count: 9, sizeType: ['compressed'], sourceType: ['album'],
    success: (res) => res.tempFilePaths.forEach(path => editForm.value.question_images.push(path))
  })
}
function chooseEditAnswerImage() {
  uni.chooseImage({
    count: 9, sizeType: ['compressed'], sourceType: ['album'],
    success: (res) => res.tempFilePaths.forEach(path => editForm.value.answer_images.push(path))
  })
}
function takeEditQuestionPhoto() {
  uni.chooseImage({
    count: 1, sizeType: ['compressed'], sourceType: ['camera'],
    success: (res) => res.tempFilePaths.forEach(path => editForm.value.question_images.push(path))
  })
}
function takeEditAnswerPhoto() {
  uni.chooseImage({
    count: 1, sizeType: ['compressed'], sourceType: ['camera'],
    success: (res) => res.tempFilePaths.forEach(path => editForm.value.answer_images.push(path))
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
async function submitMistake() {
  const hasQ = form.value.question.trim() || form.value.question_images.length > 0
  const hasA = form.value.answer.trim() || form.value.answer_images.length > 0
  if (!hasQ) { uni.showToast({ title: '请输入题目或上传题目图片', icon: 'none' }); return }
  if (!hasA) { uni.showToast({ title: '请输入答案或上传答案图片', icon: 'none' }); return }
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }

  uni.showLoading({ title: '上传图片中...' })
  try {
    const userId = userStore.userInfo?.id || 'guest'

    const qImages = []
    for (const path of form.value.question_images) {
      if (path.startsWith('http')) { qImages.push(path); continue }
      const url = await uploadUtil.uploadMistakeQuestion(path, userId)
      qImages.push(url)
    }

    const aImages = []
    for (const path of form.value.answer_images) {
      if (path.startsWith('http')) { aImages.push(path); continue }
      const url = await uploadUtil.uploadMistakeAnswer(path, userId)
      aImages.push(url)
    }

    uni.showLoading({ title: '保存中...' })

    await api.createMistake({
      plan_id: planStore.currentPlan.id,
      question: form.value.question,
      answer: form.value.answer,
      analysis: form.value.analysis,
      subject: form.value.subject,
      difficulty: form.value.difficulty,
      question_images: qImages,
      answer_images: aImages,
      tags: form.value.tags
    })
    resetForm()
    uni.showToast({ title: '添加成功', icon: 'success' })
    await loadMistakes()
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

function resetForm() {
  showForm.value = false
  form.value = { subject: '数据结构', question: '', answer: '', analysis: '', difficulty: 'medium', question_images: [], answer_images: [], tags: [] }
  tagInput.value = ''
}

// ── Edit ──
function openEditMistake(mistake) {
  editingMistakeId.value = mistake.id
  editForm.value = {
    subject: mistake.subject,
    question: mistake.question,
    answer: mistake.answer,
    analysis: mistake.analysis || '',
    difficulty: mistake.difficulty,
    question_images: [...(mistake.question_images || [])],
    answer_images: [...(mistake.answer_images || [])],
    tags: [...(mistake.tags || [])]
  }
  editTagInput.value = ''
  activePasteTarget.value = ''
  showEditMistake.value = true
}

async function saveEditMistake() {
  const hasQ = editForm.value.question.trim() || editForm.value.question_images.length > 0
  const hasA = editForm.value.answer.trim() || editForm.value.answer_images.length > 0
  if (!hasQ) { uni.showToast({ title: '请输入题目或上传题目图片', icon: 'none' }); return }
  if (!hasA) { uni.showToast({ title: '请输入答案或上传答案图片', icon: 'none' }); return }

  uni.showLoading({ title: '上传图片中...' })
  try {
    const userId = userStore.userInfo?.id || 'guest'

    const qImages = []
    for (const path of editForm.value.question_images) {
      if (path.startsWith('http')) { qImages.push(path); continue }
      const url = await uploadUtil.uploadMistakeQuestion(path, userId)
      qImages.push(url)
    }

    const aImages = []
    for (const path of editForm.value.answer_images) {
      if (path.startsWith('http')) { aImages.push(path); continue }
      const url = await uploadUtil.uploadMistakeAnswer(path, userId)
      aImages.push(url)
    }

    uni.showLoading({ title: '保存中...' })

    await api.updateMistake(editingMistakeId.value, {
      question: editForm.value.question,
      answer: editForm.value.answer,
      analysis: editForm.value.analysis,
      subject: editForm.value.subject,
      difficulty: editForm.value.difficulty,
      question_images: qImages,
      answer_images: aImages,
      tags: editForm.value.tags
    })
    showEditMistake.value = false
    uni.showToast({ title: '编辑成功', icon: 'success' })
    await loadMistakes()
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

// ── Review ──
function startReview() {
  reviewMode.value = true; reviewShowAnswer.value = false; reviewIndex.value = 0
  reviewCorrect.value = 0; reviewTotal.value = reviewCards.value.length; reviewComplete.value = false
}

async function reviewResult(correct) {
  if (correct) reviewCorrect.value++
  const currentMistake = reviewCards.value[reviewIndex.value]
  await api.reviewMistake(currentMistake.id, correct)
  if (reviewIndex.value < reviewCards.value.length - 1) {
    reviewIndex.value++; reviewShowAnswer.value = false
  } else {
    reviewMode.value = false; reviewComplete.value = true; await loadMistakes()
  }
}

function exitReview() {
  reviewMode.value = false; reviewComplete.value = false; reviewIndex.value = 0
  viewMode.value = 'all'; activeSubject.value = ''; activeTag.value = ''; loadMistakes()
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
  const res = await new Promise(r => uni.showModal({ title: '删除确认', content: '确定删除吗？', success: r }))
  if (res.confirm) {
    try {
      await api.deleteMistake(mistake.id)
      mistakes.value = mistakes.value.filter(m => m.id !== mistake.id)
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
    // Use the existing getMistakes endpoint with no pagination
    const result = await api.getMistakes(
      planStore.currentPlan.id,
      activeSubject.value || null,
      activeTag.value || null,
      false  // not pending only, get ALL
    )
    let data = result.mistakes || []
    // Client-side error count filter for export
    if (activeErrorCount.value === '1') {
      data = data.filter(m => m.error_count === 1)
    } else if (activeErrorCount.value === '2') {
      data = data.filter(m => m.error_count === 2)
    } else if (activeErrorCount.value === '3+') {
      data = data.filter(m => m.error_count >= 3)
    }
    if (data.length === 0) { uni.showToast({ title: '没有可导出的数据', icon: 'none' }); return }
    const opts = { includeAnswer: exportIncludeAnswer.value }
    if (format === 'csv') exportMistakesCSV(data, opts)
    else if (format === 'excel') exportMistakesExcel(data, opts)
    else if (format === 'pdf') exportMistakesPDF(data, opts)
  } catch (e) {
    console.error('Export error:', e)
    uni.showToast({ title: e.message || '导出失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

// ── Load ──
async function loadMistakes() {
  if (!planStore.currentPlan) return
  try {
    const pending = viewMode.value === 'pending'
    const result = await api.getMistakes(planStore.currentPlan.id, activeSubject.value || null, activeTag.value || null, pending)
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
  // #ifdef H5
  document.addEventListener('paste', handleGlobalPaste)
  // #endif
})

onUnmounted(() => {
  // #ifdef H5
  document.removeEventListener('paste', handleGlobalPaste)
  // #endif
})

watch(() => planStore.currentPlan?.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
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
.sub-nav-item { flex: 1; text-align: center; padding: 10px; border-radius: 10px; font-size: 14px; color: #65746d; transition: all 0.2s; &.active { background: #fff; color: #ef5350; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); } }

.mode-toggle { display: flex; margin-bottom: 14px; background: #f5f7f5; border-radius: 12px; padding: 4px; }
.mode-btn { flex: 1; text-align: center; padding: 10px; border-radius: 10px; font-size: 14px; color: #65746d; transition: all 0.2s; &.active { background: #fff; color: #ef5350; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); } }

.filter-section { margin-bottom: 10px; }
.filter-scroll { white-space: nowrap; width: 100%; }
.filter-list { display: inline-flex; gap: 8px; padding: 2px 0; }
.filter-item { display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; white-space: nowrap; transition: all 0.2s; &.active { background: #ef5350; color: #fff; } }
.filter-row { display: flex; align-items: center; gap: 6px; }
.filter-scroll { flex: 1; min-width: 0; }
.err-item {
  &.active { background: #ef5350; color: #fff; }
  &.err-1.active { background: #ffb74d; }
  &.err-2.active { background: #ef5350; }
  &.err-3.active { background: #c62828; }
}
.filter-manage-btn {
  width: 32px; height: 32px; border-radius: 50%; background: #f5f7f5;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0; border: 1px solid #e0e0e0;
  &:active { background: #ffebee; }
}
.tag-item { &.active { background: #f27573; } }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; .section-title { font-size: 18px; font-weight: 600; color: #1a1a2e; } }
.start-review-btn { background: #ef5350; color: #fff; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 500; &:active { transform: scale(0.96); } }

.mistake-card { background: #fff; border-radius: 16px; padding: 18px; margin-bottom: 12px; border: 1px solid #e8ece9; box-shadow: 0 1px 4px rgba(0,0,0,0.03); &.mastered { opacity: 0.6; } }
.mistake-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; .mistake-subject { font-size: 12px; padding: 4px 12px; background: #ffebee; border-radius: 20px; color: #ef5350; } }
.mistake-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.mistake-tag { font-size: 11px; padding: 3px 8px; border-radius: 8px; background: #f5f5f5; color: #65746d; &.easy { background: #e8f5e9; color: #2e7d32; } &.medium { background: #fff3e0; color: #e65100; } &.hard { background: #ffebee; color: #c62828; } &.mastered-tag { background: #e8f5e9; color: #2e7d32; } }

.section-label { display: block; font-size: 12px; color: #ef5350; margin-bottom: 6px; font-weight: 500; }
.mistake-question { font-size: 15px; color: #1a1a2e; line-height: 1.6; display: block; margin-bottom: 12px; }
.image-gallery { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.mistake-image { width: 120px; border-radius: 8px; border: 1px solid #e8ece9; }
.mistake-answer-section, .mistake-analysis-section { margin-bottom: 12px; }
.mistake-answer { font-size: 14px; color: #2e7d32; line-height: 1.6; display: block; font-weight: 500; }
.mistake-analysis { font-size: 14px; color: #65746d; line-height: 1.6; display: block; }

.mistake-footer { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; .mistake-date { font-size: 12px; color: #999; } .correct-progress { font-size: 12px; color: #2e7d32; font-weight: 500; } .error-count { font-size: 12px; color: #ef5350; } .mistake-actions { display: flex; gap: 6px; margin-left: auto; } }
.action-btn { padding: 6px 12px; border-radius: 8px; font-size: 12px; }
.edit-btn { background: #fff0f0; color: #ef5350; &:active { background: #ffcdd2; } }
.master-btn { background: #e8f5e9; color: #2e7d32; }
.del-btn { background: #f5f5f5; color: #999; &:active { background: #ffebee; color: #c62828; } }

.review-card { background: #fff; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); margin-bottom: 20px; }
.review-counter { display: block; font-size: 14px; color: #ef5350; font-weight: 600; margin-bottom: 16px; }
.review-card-body { min-height: 160px; }
.review-subject { font-size: 13px; color: #ef5350; background: #ffebee; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 16px; }
.review-question { display: flex; gap: 12px; margin-bottom: 16px; }
.question-label { font-size: 32px; font-weight: 800; color: #ef5350; line-height: 1; flex-shrink: 0; }
.question-text { font-size: 18px; color: #1a1a2e; line-height: 1.6; font-weight: 500; }
.review-image { width: 120px; border-radius: 8px; border: 1px solid #e8ece9; }
.answer-divider { height: 1px; background: #e8ece9; margin: 16px 0; }
.answer-content { display: flex; gap: 12px; margin-bottom: 12px; }
.answer-label { font-size: 32px; font-weight: 800; color: #2e7d32; line-height: 1; flex-shrink: 0; }
.answer-text { font-size: 16px; color: #1a1a2e; line-height: 1.7; }
.analysis-content { margin-top: 12px; }
.analysis-text { font-size: 14px; color: #65746d; line-height: 1.6; }
.review-actions { margin-top: 20px; }
.show-answer-btn { text-align: center; padding: 16px; background: #ffebee; border-radius: 14px; &:active { transform: scale(0.98); background: #ffcdd2; } text { font-size: 16px; color: #ef5350; font-weight: 600; } }
.review-result-btns { display: flex; gap: 12px; }
.result-btn { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 8px; border-radius: 14px; &:active { transform: scale(0.96); } &.wrong { background: #fff0f0; .result-text { color: #c62828; } } &.correct { background: #f0fff4; .result-text { color: #2e7d32; } } .result-icon { font-size: 24px; } .result-text { font-size: 13px; font-weight: 500; } }
.review-complete { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .complete-icon { font-size: 56px; margin-bottom: 12px; } .complete-text { font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; } .complete-hint { font-size: 14px; color: #65746d; margin-bottom: 20px; } .back-btn { padding: 12px 28px; background: #ef5350; color: #fff; border-radius: 25px; font-size: 15px; font-weight: 500; } }

.fab { position: fixed; right: 20px; bottom: 60px; z-index: 50; width: 56px; height: 56px; border-radius: 50%; background: #ef5350; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(239,83,80,0.35); &:active { transform: scale(0.92); } .fab-icon { font-size: 28px; color: #fff; font-weight: 300; } }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; }
.modal-content { background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #ef5350; font-weight: 600; }

.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-item { padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; transition: all 0.2s; &.active { background: #6b4ce6; color: #fff; } &.subject-add { background: #fff; border: 1.5px dashed #d0d5d2; color: #6b4ce6; } }
.tag-preview { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.tag-chip { padding: 4px 10px; border-radius: 12px; font-size: 12px; background: #ffebee; color: #ef5350; display: flex; align-items: center; gap: 4px; }
.tag-remove { font-size: 14px; color: #ef5350; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; &:focus-within { border-color: #ef5350; } }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 80px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.difficulty-row { display: flex; gap: 10px; }
.diff-item { flex: 1; padding: 10px; text-align: center; border-radius: 12px; font-size: 14px; color: #65746d; background: #f5f7f5; transition: all 0.2s; &.active { background: #ef5350; color: #fff; } }
.image-upload-area { display: flex; gap: 10px; flex-wrap: wrap; }
.image-item { position: relative; width: 80px; height: 80px; }
.uploaded-image { width: 80px; height: 80px; border-radius: 10px; }
.image-remove { position: absolute; top: -6px; right: -6px; width: 22px; height: 22px; border-radius: 50%; background: #ef5350; color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; }
.upload-actions { display: flex; gap: 8px; }
.upload-action-btn {
  width: 80px; height: 80px; border-radius: 10px;
  border: 2px dashed #d0d5d2; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 4px; background: #fafafa;
  cursor: pointer; transition: all 0.2s;
  &:active { background: #f0f0f0; border-color: #ef5350; }
  .action-icon { font-size: 20px; }
  .action-text { font-size: 11px; color: #999; }
  &.paste-btn.active {
    border-color: #ef5350;
    background: #fff0f0;
    .action-text { color: #ef5350; font-weight: 500; }
  }
}
.paste-hint { display: block; font-size: 11px; color: #999; margin-top: 6px; }

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
  &:active { border-color: #ef5350; background: #ffebee; }
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
.export-switch.on { background: #ef5350; justify-content: flex-end; }
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
  background: #ffebee; color: #c62828;
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
.manage-add-input:focus { border-color: #ef5350; }
.manage-add-btn {
  padding: 10px 20px; border-radius: 10px; background: #ef5350; color: #fff;
  font-size: 14px; font-weight: 600; white-space: nowrap;
  &:active { opacity: 0.85; }
}

.empty { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .empty-icon { font-size: 48px; margin-bottom: 12px; } .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; } .empty-hint { font-size: 13px; color: #999; text-align: center; } }
.bottom-space { height: 100px; }
</style>
