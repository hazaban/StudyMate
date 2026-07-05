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

    <!-- Switch Plan Button -->
    <view class="switch-section" v-if="planStore.plans.length > 1">
      <view class="switch-trigger" @click="showPlanSwitcher = !showPlanSwitcher">
        <text class="switch-label">📋 切换计划</text>
        <view class="switch-current">
          <text class="switch-current-name">{{ planStore.currentPlan?.exam_name }}</text>
          <text class="switch-arrow" :class="{ open: showPlanSwitcher }">▾</text>
        </view>
      </view>

      <!-- Plan List Panel -->
      <view class="switch-panel" v-if="showPlanSwitcher">
        <view
          class="switch-plan-item"
          :class="{ active: planStore.currentPlan?.id === p.id }"
          v-for="p in planStore.plans"
          :key="p.id"
          @click="switchToPlan(p)"
        >
          <view class="switch-plan-info">
            <text class="switch-plan-name">{{ p.exam_name }}</text>
            <text class="switch-plan-meta">{{ p.study_phase }} · {{ p.exam_date }}</text>
          </view>
          <view class="switch-plan-check" v-if="planStore.currentPlan?.id === p.id">✓</view>
        </view>
      </view>
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
              <text
                class="action-link apply-link"
                @click.stop="applyChaptersToTasks(idx)"
                v-if="subj.chapters && subj.chapters.length > 0"
              >应用到今日任务</text>
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
            <!-- Manual chapter editing -->
            <view class="form-group">
              <text class="form-label">章节规划</text>
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
const showPlanSwitcher = ref(false)
const editingSubjectIndex = ref(-1)
const editingChapters = ref([])
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

function switchToPlan(plan) {
  planStore.switchPlan(plan.id)
  showPlanSwitcher.value = false
}

function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) { uni.navigateBack() } else { uni.switchTab({ url: '/pages/profile/profile' }) }
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
  showSubjectModal.value = true
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

async function applyChaptersToTasks(subjIdx) {
  const subj = subjects.value[subjIdx]
  if (!subj || !subj.chapters || subj.chapters.length === 0) {
    uni.showToast({ title: '该科目没有章节', icon: 'none' })
    return
  }
  uni.showModal({
    title: '添加到今日任务',
    content: `将「${subj.name}」的 ${subj.chapters.length} 个章节添加到今日任务？`,
    success: async (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '添加中...' })
        const today = new Date().toISOString().split('T')[0]
        let added = 0
        for (const ch of subj.chapters) {
          try {
            await api.createTask({
              plan_id: planStore.currentPlan.id,
              date: today,
              type: 'new_study',
              subject: subj.name,
              content: `${ch.name}`,
              duration: ch.duration || 30,
              status: 'pending'
            })
            added++
          } catch (e) { /* skip */ }
        }
        uni.hideLoading()
        uni.showToast({ title: `已添加 ${added} 个任务`, icon: 'success' })
      }
    }
  })
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

.switch-section {
  margin-bottom: 16px;
}
.switch-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: $bg2;
  border-radius: 16px;
  padding: 14px 18px;
  border: 1px solid $rule;
  &:active { background: $soft; }
}
.switch-label {
  font-size: 13px;
  color: $muted;
  font-weight: 500;
}
.switch-current {
  display: flex;
  align-items: center;
  gap: 6px;
}
.switch-current-name {
  font-size: 14px;
  color: $accent;
  font-weight: 600;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.switch-arrow {
  font-size: 16px;
  color: $muted;
  transition: transform 0.2s;
  &.open { transform: rotate(180deg); }
}

.switch-panel {
  background: $bg2;
  border-radius: 0 0 16px 16px;
  border: 1px solid $rule;
  border-top: none;
  overflow: hidden;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
.switch-plan-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-top: 1px solid $rule;
  transition: background 0.15s;
  &:active { background: $soft; }
  &.active { background: rgba(47,125,79,0.06); }
}
.switch-plan-info {
  flex: 1;
  min-width: 0;
}
.switch-plan-name {
  display: block;
  font-size: 14px;
  color: $ink;
  font-weight: 500;
}
.switch-plan-meta {
  display: block;
  font-size: 11px;
  color: $muted;
  margin-top: 2px;
}
.switch-plan-check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: $accent;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
  margin-left: 10px;
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
  .chapter-tag { font-size: 12px; padding: 6px 10px; background: $bg2; border-radius: 8px; color: $ink; line-height: 1.4; }
  .subject-actions { margin-top: 8px; display: flex; gap: 12px; }
  .action-link { font-size: 12px; color: $accent; }
  .apply-link { color: #ef5350; font-weight: 500; }
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

.bottom-space { height: 60px; }
</style>