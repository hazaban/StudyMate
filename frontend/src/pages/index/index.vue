<template>
  <view class="page">
    <view class="header">
      <view class="header-content">
        <view class="welcome">
          <text class="greeting">早安，{{ userStore.user?.nickname || '学习者' }}！</text>
          <text class="date">{{ currentDate }}</text>
        </view>
        <view class="header-right">
          <view class="notification-btn" @click="goToProfile">
            <text class="notif-icon">🔔</text>
          </view>
          <view class="avatar" @click="goToProfile">
            <text class="avatar-text">{{ userStore.user?.nickname?.charAt(0) || '学' }}</text>
          </view>
        </view>
      </view>
      <view class="motivation-card">
        <text class="motivation-text">"让知识进脑子，而不是走过场"</text>
        <view class="streak-badge">
          <text class="streak-icon">🔥</text>
          <text class="streak-days">连续学习 {{ streakDays }} 天</text>
        </view>
      </view>
    </view>

    <view class="stats-section">
      <view class="stat-card">
        <text class="stat-value">{{ taskStore.completedCount }}</text>
        <text class="stat-label">今日完成</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ daysRemaining }}</text>
        <text class="stat-label">剩余天数</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ farmStore.level }}</text>
        <text class="stat-label">农场等级</text>
      </view>
    </view>

    <view class="plan-section" v-if="planStore.currentPlan">
      <view class="section-header">
        <text class="section-title">当前计划</text>
        <text class="section-link" @click="goToPlan">查看详情</text>
      </view>
      <view class="plan-card" @click="goToPlan">
        <text class="plan-name">{{ planStore.currentPlan.exam_name }}</text>
        <text class="plan-date">{{ planStore.currentPlan.exam_date }}</text>
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
        <text class="progress-text">已完成 {{ progressPercent }}%</text>
      </view>
    </view>

    <view class="quick-actions">
      <view class="action-card" @click="startPomodoro">
        <view class="action-icon">🍅</view>
        <text class="action-text">开始学习</text>
      </view>
      <view class="action-card" @click="goToReview">
        <view class="action-icon">📚</view>
        <text class="action-text">今日复习</text>
      </view>
      <view class="action-card" @click="goToFarm">
        <view class="action-icon">🌱</view>
        <text class="action-text">照顾农场</text>
      </view>
      <view class="action-card" @click="goToStats">
        <view class="action-icon">📊</view>
        <text class="action-text">学习统计</text>
      </view>
    </view>

    <view class="task-preview">
      <view class="section-header">
        <text class="section-title">今日任务</text>
        <text class="section-link" @click="goToTaskBoard">全部任务</text>
      </view>
      <view class="task-list">
        <view class="task-item" v-for="task in previewTasks" :key="task.id">
          <view class="task-checkbox" :class="{ checked: task.status === 'completed' }" @click="toggleTaskComplete(task)">
            <text v-if="task.status === 'completed'">✓</text>
          </view>
          <view class="task-content" @click="editTask(task)">
            <text class="task-title">{{ task.content }}</text>
            <view class="task-meta">
              <text class="task-subject">{{ task.subject }}</text>
              <text class="task-duration">{{ task.duration }}分钟</text>
              <text class="task-actual" v-if="task.actual_duration">实际{{ task.actual_duration }}分钟</text>
            </view>
          </view>
          <view class="task-actions">
            <view class="task-action-btn" @click="startPomodoroFromTask(task)">🍅</view>
            <view class="task-action-btn" @click="editTask(task)">✎</view>
          </view>
          <view class="task-type" :class="task.type">
            {{ taskTypeText(task.type) }}
          </view>
        </view>
      </view>
    </view>

    <!-- Task Edit Modal -->
    <view class="modal-overlay" v-if="showTaskForm" @click="showTaskForm = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑任务</text>
          <view class="modal-close" @click="showTaskForm = false">✕</view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="form-group">
            <text class="form-label">科目</text>
            <view class="subject-grid">
              <view class="subject-tag" :class="{ active: editingForm.subject === s }" v-for="s in subjectOptions" :key="s" @click="editingForm.subject = s">{{ s }}</view>
              <view class="subject-tag subject-add" @click="showSubjectInput = !showSubjectInput">
                <text v-if="!showSubjectInput">+ 自定义</text>
                <text v-else>收起</text>
              </view>
            </view>
            <view class="subject-empty-hint" v-if="subjectOptions.length === 0 && !showSubjectInput">
              <text class="subject-empty-text">还没有科目，点击「+ 自定义」添加你的科目</text>
            </view>
            <view class="input-wrap" v-if="showSubjectInput" style="margin-top: 10px;">
              <input class="input-inner" v-model="customSubject" placeholder="输入自定义科目..." @confirm="addCustomSubject" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">章节</text>
            <view class="input-wrap">
              <input class="input-inner" v-model="editingForm.chapter" placeholder="如：第3章 二叉树" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">任务内容</text>
            <textarea class="modal-textarea" v-model="editingForm.content" placeholder="今天要完成的内容..." />
          </view>
          <view class="form-group">
            <text class="form-label">类型</text>
            <view class="type-row">
              <view class="type-tag" :class="{ active: editingForm.type === 'new_study' }" @click="editingForm.type = 'new_study'">新学</view>
              <view class="type-tag" :class="{ active: editingForm.type === 'review' }" @click="editingForm.type = 'review'">复习</view>
              <view class="type-tag" :class="{ active: editingForm.type === 'mistake' }" @click="editingForm.type = 'mistake'">错题</view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">预计时间（分钟）</text>
            <view class="input-wrap">
              <input class="input-inner" type="number" v-model="editingForm.duration" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">循环</text>
            <view class="type-row repeat-row">
              <view class="type-tag" :class="{ active: (editingForm.repeat_type || 'none') === 'none' }" @click="editingForm.repeat_type = 'none'">不循环</view>
              <view class="type-tag" :class="{ active: editingForm.repeat_type === 'daily' }" @click="editingForm.repeat_type = 'daily'">每天</view>
              <view class="type-tag" :class="{ active: editingForm.repeat_type === 'weekday' }" @click="editingForm.repeat_type = 'weekday'">工作日</view>
              <view class="type-tag" :class="{ active: editingForm.repeat_type === 'holiday' }" @click="editingForm.repeat_type = 'holiday'">节假日</view>
            </view>
          </view>
          <view class="form-group" v-if="editingForm.actual_duration !== undefined">
            <text class="form-label">实际用时（分钟，系统自动记录）</text>
            <view class="input-wrap">
              <input class="input-inner" type="number" v-model="editingForm.actual_duration" disabled />
            </view>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="delete-btn" @click="deleteTask">删除</view>
          <view class="cancel-btn" @click="showTaskForm = false">取消</view>
          <view class="submit-btn" @click="saveTask">保存</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { usePlanStore } from '@/stores/plan'
import { useTaskStore } from '@/stores/task'
import { useFarmStore } from '@/stores/farm'
import { useSubjectsStore } from '@/stores/subjects'
import { dateUtil } from '@/utils/date'
import * as api from '@/api/client'

const userStore = useUserStore()
const planStore = usePlanStore()
const taskStore = useTaskStore()
const farmStore = useFarmStore()
const subjectsStore = useSubjectsStore()

const currentDate = ref('')
const daysRemaining = ref(0)
const progressPercent = ref(0)
const streakDays = ref(0)

async function computeStreak() {
  try {
    // Collect active days from backend FocusRecords across ALL plans
    const activeDays = new Set()
    for (const p of planStore.plans) {
      try {
        const res = await api.getFocusRecords(p.id, null, null, null)
        const records = Array.isArray(res) ? res : (res.records || res.data || [])
        records.forEach(r => { if (r.date) activeDays.add(r.date) })
      } catch (e) { /* skip */ }
    }

    // Also count today if there's any completed task
    if (taskStore.completedCount > 0) {
      activeDays.add(dateUtil.today())
    }

    // Walk backwards from today, count consecutive active days
    let count = 0
    const today = new Date()
    for (let i = 0; i < 365; i++) {
      const d = new Date(today)
      d.setDate(d.getDate() - i)
      const ds = d.toISOString().split('T')[0]
      if (activeDays.has(ds)) {
        count++
      } else {
        break
      }
    }
    streakDays.value = count
  } catch (e) {
    streakDays.value = 0
  }
}

const showTaskForm = ref(false)
const editingForm = ref({})
const subjectOptions = computed(() => subjectsStore.subjects)
const showSubjectInput = ref(false)
const customSubject = ref('')

async function loadSubjects() {
  await subjectsStore.load()
}

function addCustomSubject() {
  const name = customSubject.value.trim()
  if (!name) return
  subjectsStore.add(name)
  editingForm.value.subject = name
  customSubject.value = ''
  showSubjectInput.value = false
}

const previewTasks = computed(() => {
  return taskStore.todayTasks.slice(0, 3)
})

function taskTypeText(type) {
  const map = {
    new_study: '新学',
    review: '复习',
    mistake: '错题'
  }
  return map[type] || type
}

function editTask(task) {
  editingForm.value = {
    id: task.id,
    subject: task.subject,
    chapter: task.chapter || '',
    content: task.content,
    type: task.type,
    duration: task.duration,
    actual_duration: task.actual_duration,
    repeat_type: task.repeat_type || 'none'
  }
  showTaskForm.value = true
}

async function saveTask() {
  if (!editingForm.value.content || !editingForm.value.subject) {
    uni.showToast({ title: '请填写科目和内容', icon: 'none' })
    return
  }
  try {
    await api.updateTask(editingForm.value.id, {
      subject: editingForm.value.subject,
      chapter: editingForm.value.chapter,
      content: editingForm.value.content,
      type: editingForm.value.type,
      duration: parseInt(editingForm.value.duration) || 25,
      repeat_type: editingForm.value.repeat_type || 'none'
    })
    showTaskForm.value = false
    uni.showToast({ title: '保存成功', icon: 'success' })
    const today = dateUtil.today()
    if (planStore.currentPlan) {
      await taskStore.getTasksByDate(planStore.currentPlan.id, today)
    }
    await computeStreak()
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

async function deleteTask() {
  uni.showModal({
    title: '删除任务',
    content: '确定删除这个任务吗？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await api.deleteTask(editingForm.value.id)
        showTaskForm.value = false
        uni.showToast({ title: '删除成功', icon: 'success' })
        const today = dateUtil.today()
        if (planStore.currentPlan) {
          await taskStore.getTasksByDate(planStore.currentPlan.id, today)
        }
        await computeStreak()
      } catch (e) {
        uni.showToast({ title: '删除失败', icon: 'none' })
      }
    }
  })
}

async function toggleTaskComplete(task) {
  try {
    if (task.status === 'completed') {
      await api.updateTask(task.id, { status: 'pending' })
    } else {
      await api.completeTask(task.id)
    }
    const today = dateUtil.today()
    if (planStore.currentPlan) {
      await taskStore.getTasksByDate(planStore.currentPlan.id, today)
    }
    await computeStreak()
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function startPomodoroFromTask(task) {
  const taskContent = `${task.subject}${task.chapter ? ' - ' + task.chapter : ''}: ${task.content}`
  uni.navigateTo({ url: `/pages/daily/pomodoro?taskContent=${encodeURIComponent(taskContent)}&taskId=${task.id}` })
}

function goToProfile() {
  uni.switchTab({ url: '/pages/profile/profile' })
}

function goToPlan() {
  uni.navigateTo({ url: '/pages/plan/plan-overview' })
}

function goToTaskBoard() {
  uni.switchTab({ url: '/pages/daily/task-board' })
}

function goToReview() {
  uni.switchTab({ url: '/pages/review/index' })
}

function goToFarm() {
  uni.navigateTo({ url: '/pages/farm/farm' })
}

function startPomodoro() {
  uni.navigateTo({ url: '/pages/daily/pomodoro' })
}

function goToStats() {
  uni.navigateTo({ url: '/pages/statistics/stats' })
}

onMounted(async () => {
  currentDate.value = `${dateUtil.format(new Date(), 'YYYY年MM月DD日')} ${dateUtil.getWeekDay(new Date())}`

  await userStore.getUserInfo()

  if (userStore.isLoggedIn && userStore.user) {
    await planStore.getPlansByUserId()
    await loadSubjects()

    if (planStore.currentPlan) {
      const today = dateUtil.today()
      await taskStore.getTasksByDate(planStore.currentPlan.id, today)
      await farmStore.getPlantsByPlanId(planStore.currentPlan.id)

      daysRemaining.value = dateUtil.getDaysBetween(today, planStore.currentPlan.exam_date)
      await computeStreak()
    }
  }
})

// Refresh streak when returning from other pages (e.g. after pomodoro)
onShow(async () => {
  if (planStore.currentPlan) {
    await computeStreak()
  }
})

watch(() => planStore.currentPlan?.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    const today = dateUtil.today()
    await taskStore.getTasksByDate(planStore.currentPlan.id, today)
    await farmStore.getPlantsByPlanId(planStore.currentPlan.id)
    daysRemaining.value = dateUtil.getDaysBetween(today, planStore.currentPlan.exam_date)
    await computeStreak()
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 24px;
  background: linear-gradient(135deg, var(--color-header-green-start, #2f7d4f) 0%, var(--color-header-green-end, #4a9d6a) 100%);
  border-radius: 0 0 32px 32px;
  margin-bottom: 24px;
  margin-left: -20px;
  margin-right: -20px;
  padding-left: 20px;
  padding-right: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.welcome {
  .greeting {
    display: block;
    font-size: 26px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 6px;
  }
  
  .date {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  
  .notif-icon {
    font-size: 18px;
  }
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.3);
  
  .avatar-text {
    font-size: 20px;
    font-weight: 700;
    color: #fff;
  }
}

.motivation-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.15);
  
  .motivation-text {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
    font-style: italic;
  }
  
  .streak-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.2);
    padding: 6px 12px;
    border-radius: 20px;
    
    .streak-icon {
      font-size: 14px;
    }
    
    .streak-days {
      font-size: 12px;
      color: #fff;
      font-weight: 500;
      white-space: nowrap;
    }
  }
}

.stats-section {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  background: $bg2;
  border-radius: 16px;
  padding: 16px 14px;
  text-align: center;
  border: 1px solid $rule;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s;
  
  &:active {
    transform: scale(0.97);
  }
  
  .stat-icon {
    font-size: 24px;
    display: block;
    margin-bottom: 4px;
  }
  
  .stat-value {
    display: block;
    font-size: 22px;
    font-weight: 700;
    color: $ink;
    margin-bottom: 2px;
  }
  
  .stat-label {
    font-size: 12px;
    color: $muted;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: $ink;
  }
  
  .section-link {
    font-size: 14px;
    color: $accent;
  }
}

.plan-card {
  background: linear-gradient(135deg, #f0f7f4 0%, $bg2 100%);
  border-radius: 18px;
  padding: 20px;
  border: 1px solid $rule;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 20px;
  
  .plan-name {
    display: block;
    font-size: 20px;
    font-weight: 700;
    color: $ink;
    margin-bottom: 4px;
  }
  
  .plan-date {
    display: block;
    font-size: 14px;
    color: $muted;
    margin-bottom: 14px;
  }
  
}

.quick-actions {
  display: flex;
  gap: 12px;
  margin: 20px 0;
}

.action-card {
  flex: 1;
  background: $bg2;
  border-radius: 16px;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border: 1px solid $rule;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:active {
    transform: scale(0.96);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  }
  
  .action-icon {
    font-size: 32px;
  }
  
  .action-text {
    font-size: 14px;
    color: $ink;
    font-weight: 500;
  }
}

.task-preview {
  margin-bottom: 20px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: $bg2;
  border-radius: 14px;
  padding: 14px 16px;
  border: 1px solid $rule;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
  transition: all 0.2s;
  
  &:active {
    transform: scale(0.99);
  }
}

.task-checkbox {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid $rule;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.checked {
    background: $accent;
    border-color: $accent;
    color: #fff;
  }
}

.task-content {
  flex: 1;

  .task-title {
    display: block;
    font-size: 15px;
    color: $ink;
    margin-bottom: 4px;
  }

  .task-meta {
    display: flex;
    gap: 8px;

    .task-subject, .task-duration, .task-actual {
      font-size: 12px;
      color: $muted;
    }
  }
}

.task-actions {
  display: flex;
  gap: 6px;
}

.task-action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: $soft;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.task-type {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 10px;
  
  &.new_study {
    background: #e8f5e9;
    color: #2e7d32;
  }
  
  &.review {
    background: #fff3e0;
    color: #e65100;
  }
  
  &.mistake {
    background: #ffebee;
    color: #c62828;
  }
}

.bottom-space {
  height: 100px;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}
.modal-content {
  width: 100%;
  max-height: 85vh;
  background: #fff;
  border-radius: 24px 24px 0 0;
  display: flex;
  flex-direction: column;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  .modal-title { font-size: 18px; font-weight: 600; color: #1a1a2e; }
  .modal-close { font-size: 20px; color: #999; padding: 4px 8px; }
}
.modal-body { padding: 20px; max-height: 60vh; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrap {
  width: 100%; padding: 10px 14px; border: 1px solid #e8ece9; border-radius: 10px; background: #fafafa;
}
.input-inner {
  width: 100%; font-size: 14px; color: #1a1a2e; border: none; outline: none; background: transparent;
}
.modal-textarea {
  width: 100%; min-height: 80px; padding: 10px 14px; border: 1px solid #e8ece9;
  border-radius: 10px; font-size: 14px; color: #1a1a2e; background: #fafafa;
}
.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-tag { padding: 6px 14px; border-radius: 16px; font-size: 13px; color: #65746d; background: #f5f7f5; &.active { background: #2f7d4f; color: #fff; } &.subject-add { background: #fff; border: 1.5px dashed #d0d5d2; color: #2f7d4f; } }
.subject-empty-hint { margin-top: 10px; padding: 10px 12px; background: #fff8e1; border-radius: 10px; }
.subject-empty-text { font-size: 12px; color: #9a7b00; }
.type-row { display: flex; gap: 8px; }
.type-tag { flex: 1; text-align: center; padding: 10px; border-radius: 10px; font-size: 14px; color: #65746d; background: #f5f7f5; &.active { background: #2f7d4f; color: #fff; } }
.modal-footer { display: flex; gap: 12px; padding: 20px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; text-align: center; padding: 14px; border-radius: 12px; background: #f5f7f5; font-size: 16px; color: #65746d; }
.delete-btn { flex: 1; text-align: center; padding: 14px; border-radius: 12px; background: #ffebee; font-size: 16px; color: #c62828; }
.submit-btn { flex: 1; text-align: center; padding: 14px; border-radius: 12px; background: #2f7d4f; font-size: 16px; color: #fff; font-weight: 500; }
</style>