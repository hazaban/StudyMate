<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">计划总览</text>
      <view class="edit-btn" @click="editPlan">
        <text class="edit-icon">✎</text>
      </view>
    </view>

    <!-- Plan Switcher -->
    <view class="plan-switcher" v-if="planStore.plans.length > 1">
      <scroll-view scroll-x class="switcher-scroll">
        <view class="switcher-list">
          <view
            class="switcher-item"
            :class="{ active: planStore.currentPlan?.id === p.id }"
            v-for="p in planStore.plans"
            :key="p.id"
            @click="switchToPlan(p.id)"
          >
            <text class="switcher-name">{{ p.exam_name }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="plan-card" v-if="planStore.currentPlan">
      <view class="plan-header">
        <text class="plan-name">{{ planStore.currentPlan.exam_name }}</text>
        <text class="plan-status">进行中</text>
      </view>

      <view class="plan-info">
        <view class="info-item">
          <text class="info-icon">📅</text>
          <view class="info-content">
            <text class="info-label">考试日期</text>
            <text class="info-value">{{ planStore.currentPlan.exam_date }}</text>
          </view>
        </view>

        <view class="info-item">
          <text class="info-icon">⏱</text>
          <view class="info-content">
            <text class="info-label">每日学习</text>
            <text class="info-value">{{ planStore.currentPlan.daily_study_time }}分钟</text>
          </view>
        </view>

        <view class="info-item">
          <text class="info-icon">📊</text>
          <view class="info-content">
            <text class="info-label">剩余天数</text>
            <text class="info-value highlight">{{ daysRemaining }}天</text>
          </view>
        </view>
      </view>

      <!-- Subjects Section -->
      <view class="subjects-section" v-if="subjects.length > 0">
        <view class="section-header">
          <text class="section-title">科目列表</text>
          <view class="add-subject-btn" @click="startAddSubject">
            <text>+ 添加科目</text>
          </view>
        </view>
        <view class="subject-list">
          <view class="subject-card" v-for="(subj, idx) in subjects" :key="idx" @click="editSubjectPhase(idx)">
            <view class="subject-header">
              <text class="subject-name">{{ subj.name }}</text>
              <text class="subject-score" v-if="subj.target_score">目标: {{ subj.target_score }}分</text>
            </view>
            <view class="subject-chapters" v-if="subj.chapters && subj.chapters.length > 0">
              <text class="chapters-label">章节规划:</text>
              <view class="chapter-tags">
                <view class="chapter-tag" v-for="(ch, ci) in subj.chapters" :key="ci">
                  {{ ch.name }}({{ ch.duration || 30 }}分钟/天)
                </view>
              </view>
            </view>
            <view class="subject-actions">
              <text class="action-link" @click.stop="editSubjectPhase(idx)">编辑阶段规划</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Subject Phase Edit Modal -->
      <view class="modal-overlay" v-if="showSubjectModal" @click="showSubjectModal = false">
        <view class="modal-content" @click.stop>
          <view class="modal-header">
            <text class="modal-title">编辑「{{ editingSubject?.name }}」阶段规划</text>
            <view class="modal-close" @click="showSubjectModal = false">✕</view>
          </view>
          <scroll-view scroll-y class="modal-body">
            <!-- Text description → AI -->
            <view class="form-group">
              <text class="form-label">文字描述（AI 自动匹配规划）</text>
              <view class="input-wrapper">
                <textarea class="textarea-field" v-model="phaseDescription" placeholder="描述你的学习进度和计划，如：数据结构还有3章没学，每天想学2小时..." />
              </view>
              <view class="ai-btn" @click="aiAnalyzePhase" style="margin-top: 8px;">
                <text>🤖 AI 分析生成规划</text>
              </view>
            </view>

            <!-- Image upload -->
            <view class="form-group">
              <text class="form-label">上传科目大纲图片（AI 解析）</text>
              <view class="image-upload-area">
                <view class="image-item" v-if="syllabusImage">
                  <image :src="syllabusImage" mode="aspectFill" class="uploaded-image" />
                  <view class="image-remove" @click="syllabusImage = ''">✕</view>
                </view>
                <view class="image-add-btn" @click="chooseSyllabusImage" v-if="!syllabusImage">
                  <text class="add-icon">+</text>
                  <text class="add-text">上传大纲图片</text>
                </view>
              </view>
              <view class="ai-btn" @click="aiAnalyzeSyllabus" v-if="syllabusImage" style="margin-top: 8px;">
                <text>🤖 AI 解析图片</text>
              </view>
            </view>

            <!-- Manual chapter editing -->
            <view class="form-group">
              <text class="form-label">章节规划（可手动编辑）</text>
              <view class="chapter-list">
                <view class="chapter-item" v-for="(ch, ci) in editingChapters" :key="ci">
                  <view class="chapter-row">
                    <input class="chapter-input" v-model="ch.name" placeholder="章节名" />
                    <input class="chapter-input short" v-model="ch.duration" type="number" placeholder="分钟/天" />
                    <view class="chapter-remove" @click="editingChapters.splice(ci, 1)">✕</view>
                  </view>
                </view>
                <view class="add-chapter-btn" @click="editingChapters.push({ name: '', duration: 30 })">
                  <text>+ 添加章节</text>
                </view>
              </view>
            </view>
          </scroll-view>
          <view class="modal-footer">
            <view class="cancel-btn" @click="showSubjectModal = false">取消</view>
            <view class="submit-btn" @click="saveSubjectPhase">保存</view>
          </view>
        </view>
      </view>

      <!-- Add Subject Modal -->
      <view class="modal-overlay" v-if="showAddSubject" @click="showAddSubject = false">
        <view class="modal-content" @click.stop>
          <view class="modal-header">
            <text class="modal-title">添加科目</text>
            <view class="modal-close" @click="showAddSubject = false">✕</view>
          </view>
          <view class="modal-body">
            <view class="form-group">
              <text class="form-label">科目名称</text>
              <view class="input-wrapper">
                <input class="input-field" v-model="newSubject.name" placeholder="如：高等数学" />
              </view>
            </view>
            <view class="form-group">
              <text class="form-label">目标分数（选填）</text>
              <view class="input-wrapper">
                <input class="input-field" v-model="newSubject.target_score" type="number" placeholder="选填" />
              </view>
            </view>
          </view>
          <view class="modal-footer">
            <view class="cancel-btn" @click="showAddSubject = false">取消</view>
            <view class="submit-btn" @click="confirmAddSubject">确认添加</view>
          </view>
        </view>
      </view>

      <view class="phase-section">
        <text class="section-title">学习阶段</text>
        <view class="phase-badge">{{ planStore.currentPlan.study_phase }}</view>
      </view>

      <view class="action-buttons">
        <view class="action-btn primary" @click="goToTaskBoard">
          <text class="btn-icon">📋</text>
          <text class="btn-text">今日任务</text>
        </view>
        <view class="action-btn secondary" @click="deletePlan">
          <text class="btn-icon">🗑</text>
          <text class="btn-text">删除计划</text>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无学习计划</text>
      <text class="empty-hint">点击下方按钮创建新计划</text>
      <view class="empty-btn" @click="createPlan">
        <text class="empty-btn-text">创建计划</text>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import { dateUtil } from '@/utils/date'
import * as api from '@/api/client'

const planStore = usePlanStore()
const userStore = useUserStore()

const showSubjectModal = ref(false)
const showAddSubject = ref(false)
const editingSubjectIndex = ref(-1)
const editingChapters = ref([])
const phaseDescription = ref('')
const syllabusImage = ref('')
const syllabusImageBase64 = ref('')
const newSubject = ref({ name: '', target_score: '' })

const editingSubject = computed(() => {
  if (editingSubjectIndex.value >= 0) {
    return subjects.value[editingSubjectIndex.value]
  }
  return null
})

const subjects = computed(() => {
  return planStore.currentPlan?.subjects || []
})

const daysRemaining = computed(() => {
  if (!planStore.currentPlan) return 0
  return dateUtil.getDaysBetween(dateUtil.today(), planStore.currentPlan.exam_date)
})

function switchToPlan(planId) {
  planStore.switchPlan(planId)
}

function goBack() {
  uni.navigateBack()
}

function editPlan() {
  uni.navigateTo({ url: '/pages/plan/target-setup?edit=1' })
}

function goToTaskBoard() {
  uni.switchTab({ url: '/pages/daily/task-board' })
}

function createPlan() {
  uni.navigateTo({ url: '/pages/plan/target-setup' })
}

function startAddSubject() {
  newSubject.value = { name: '', target_score: '' }
  showAddSubject.value = true
}

async function confirmAddSubject() {
  if (!newSubject.value.name.trim()) return
  const updatedSubjects = [...subjects.value, { name: newSubject.value.name.trim(), target_score: newSubject.value.target_score || '', chapters: [] }]
  await planStore.updatePlan(planStore.currentPlan.id, { subjects: updatedSubjects })
  showAddSubject.value = false
}

function editSubjectPhase(idx) {
  editingSubjectIndex.value = idx
  const subj = subjects.value[idx]
  editingChapters.value = JSON.parse(JSON.stringify(subj.chapters || []))
  phaseDescription.value = ''
  syllabusImage.value = ''
  syllabusImageBase64.value = ''
  showSubjectModal.value = true
}

async function aiAnalyzePhase() {
  if (!phaseDescription.value.trim()) return
  uni.showLoading({ title: 'AI 分析中...' })
  try {
    const result = await api.aiAnalyzeSubjectPhase(phaseDescription.value, editingSubject.value?.name || '')
    if (result.chapters) {
      editingChapters.value = result.chapters.map(c => ({
        name: c.name,
        duration: c.daily_duration || 30
      }))
    }
    uni.showToast({ title: '分析完成', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '分析失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

function chooseSyllabusImage() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const tempPath = res.tempFilePaths[0]
      syllabusImage.value = tempPath
      // Convert image to base64 for AI analysis
      // #ifdef H5
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const maxSize = 1024
        let { width, height } = img
        if (width > maxSize || height > maxSize) {
          const ratio = Math.min(maxSize / width, maxSize / height)
          width = Math.round(width * ratio)
          height = Math.round(height * ratio)
        }
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        syllabusImageBase64.value = canvas.toDataURL('image/jpeg', 0.8)
      }
      img.src = tempPath
      // #endif
      // #ifndef H5
      uni.getFileSystemManager().readFile({
        filePath: tempPath,
        encoding: 'base64',
        success: (data) => {
          syllabusImageBase64.value = `data:image/jpeg;base64,${data.data}`
        }
      })
      // #endif
    }
  })
}

async function aiAnalyzeSyllabus() {
  if (!syllabusImage.value) return
  if (!syllabusImageBase64.value) {
    uni.showToast({ title: '图片正在处理中，请稍等', icon: 'none' })
    return
  }
  uni.showLoading({ title: '千问AI 解析图片中...' })
  try {
    const result = await api.aiAnalyzeSyllabus(syllabusImageBase64.value, editingSubject.value?.name || '')
    if (result.chapters) {
      editingChapters.value = result.chapters.map(c => ({
        name: c.name,
        duration: c.estimated_days ? Math.round(c.estimated_days * 30) : 30
      }))
    }
    uni.showToast({ title: '解析完成', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message || '解析失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

async function saveSubjectPhase() {
  const updatedSubjects = [...subjects.value]
  updatedSubjects[editingSubjectIndex.value] = {
    ...updatedSubjects[editingSubjectIndex.value],
    chapters: editingChapters.value
  }
  await planStore.updatePlan(planStore.currentPlan.id, { subjects: updatedSubjects })
  showSubjectModal.value = false
  uni.showToast({ title: '保存成功', icon: 'success' })
}

async function deletePlan() {
  if (!planStore.currentPlan) return

  uni.showModal({
    title: '删除计划',
    content: '确定要删除这个学习计划吗？',
    success: async (res) => {
      if (res.confirm) {
        const result = await planStore.deletePlan(planStore.currentPlan.id)
        if (result.success) {
          uni.showToast({ title: '删除成功', icon: 'success' })
          setTimeout(() => {
            uni.switchTab({ url: '/pages/index/index' })
          }, 1000)
        }
      }
    }
  })
}

onMounted(async () => {
  await userStore.getUserInfo()

  if (userStore.isLoggedIn && userStore.user) {
    await planStore.getPlansByUserId(userStore.user.id)
  }
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 20px 20px;

  .back-btn, .edit-btn {
    width: 40px;
    height: 40px;
    background: $bg2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;

    .back-icon, .edit-icon {
      font-size: 20px;
      color: $ink;
    }
  }

  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: $ink;
  }
}

.plan-switcher {
  margin-bottom: 16px;
  .switcher-scroll { white-space: nowrap; }
  .switcher-list { display: flex; gap: 8px; }
  .switcher-item {
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    background: $bg2;
    color: $muted;
    border: 1px solid $rule;
    white-space: nowrap;
    &.active { background: $accent; color: #fff; border-color: $accent; }
  }
}

.plan-card {
  background: $bg2;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid $rule;
}

.plan-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  .plan-name {
    font-size: 24px;
    font-weight: 700;
    color: $ink;
  }

  .plan-status {
    font-size: 12px;
    padding: 4px 12px;
    background: $soft;
    color: $accent;
    border-radius: 20px;
  }
}

.plan-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;

  .info-icon { font-size: 20px; }

  .info-content {
    flex: 1;
    .info-label { display: block; font-size: 12px; color: $muted; }
    .info-value { display: block; font-size: 16px; color: $ink; font-weight: 500; &.highlight { color: $accent; font-size: 18px; font-weight: 700; } }
  }
}

.subjects-section {
  margin-bottom: 20px;
  .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
  .section-title { font-size: 14px; color: $muted; }
  .add-subject-btn { font-size: 13px; color: $accent; }
}

.subject-list { display: flex; flex-direction: column; gap: 10px; }
.subject-card {
  background: $soft;
  border-radius: 12px;
  padding: 14px;
  .subject-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
  .subject-name { font-size: 15px; font-weight: 600; color: $ink; }
  .subject-score { font-size: 12px; color: $accent; }
  .chapters-label { font-size: 12px; color: $muted; display: block; margin-bottom: 6px; }
  .chapter-tags { display: flex; flex-wrap: wrap; gap: 6px; }
  .chapter-tag { font-size: 11px; padding: 3px 8px; background: $bg2; border-radius: 8px; color: $ink; }
  .subject-actions { margin-top: 8px; }
  .action-link { font-size: 12px; color: $accent; }
}

.section-title { display: block; font-size: 14px; color: $muted; margin-bottom: 12px; }

.phase-section { margin-bottom: 24px; }
.phase-badge { display: inline-block; padding: 10px 20px; background: $accent; color: #fff; border-radius: 20px; font-size: 14px; font-weight: 500; }

.action-buttons { display: flex; gap: 12px; }
.action-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 14px; border-radius: 12px;
  &.primary { background: $accent; .btn-icon, .btn-text { color: #fff; } }
  &.secondary { background: #ffebee; .btn-icon, .btn-text { color: #c62828; } }
  .btn-icon { font-size: 16px; }
  .btn-text { font-size: 15px; font-weight: 500; }
}

.empty-state {
  display: flex; flex-direction: column; align-items: center; padding: 80px 20px;
  .empty-icon { font-size: 64px; margin-bottom: 20px; }
  .empty-text { font-size: 20px; color: $ink; margin-bottom: 8px; font-weight: 600; }
  .empty-hint { font-size: 14px; color: $muted; margin-bottom: 24px; }
  .empty-btn { padding: 14px 32px; background: $accent; border-radius: 50px; .empty-btn-text { font-size: 16px; color: #fff; font-weight: 500; } }
}

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; }
.modal-content { background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: $accent; font-weight: 600; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 80px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.ai-btn { padding: 10px 16px; background: #f3f0ff; border-radius: 10px; text-align: center; font-size: 14px; color: #6b4ce6; }
.chapter-list { display: flex; flex-direction: column; gap: 8px; }
.chapter-item { background: #f5f7f5; border-radius: 10px; padding: 10px; }
.chapter-row { display: flex; align-items: center; gap: 8px; }
.chapter-input { flex: 1; padding: 8px 12px; border: 1px solid #e8ece9; border-radius: 8px; font-size: 14px; background: #fff; &.short { flex: 0 0 80px; } }
.chapter-remove { font-size: 16px; color: #ef5350; padding: 4px; }
.add-chapter-btn { padding: 10px; text-align: center; border: 1.5px dashed #d0d5d2; border-radius: 10px; font-size: 14px; color: $accent; }
.image-upload-area { display: flex; gap: 10px; flex-wrap: wrap; }
.image-item { position: relative; width: 80px; height: 80px; }
.uploaded-image { width: 80px; height: 80px; border-radius: 10px; }
.image-remove { position: absolute; top: -6px; right: -6px; width: 22px; height: 22px; border-radius: 50%; background: #ef5350; color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; }
.image-add-btn { width: 80px; height: 80px; border-radius: 10px; border: 2px dashed #d0d5d2; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; background: #fafafa; }
.add-icon { font-size: 24px; color: #999; }
.add-text { font-size: 11px; color: #999; }

.bottom-space { height: 60px; }
</style>