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
        <view class="task-item" v-for="task in previewTasks" :key="task.id" @contextmenu.prevent="editTask(task)" @touchstart="onTaskTouchStart(task)" @touchend="onTaskTouchEnd" @touchmove="onTaskTouchEnd">
          <view class="task-checkbox" :class="{ checked: task.status === 'completed' }" @click="toggleTaskComplete(task)">
            <text v-if="task.status === 'completed'">✓</text>
          </view>
          <view class="task-content">
            <text class="task-title">{{ task.content }}</text>
            <view class="task-meta">
              <text class="task-subject">{{ task.subject }}</text>
              <text class="task-time">{{ formatTaskTime(task) }}</text>
              <text class="task-duration">{{ task.duration }}分钟</text>
              <text class="task-actual" v-if="task.actual_duration">实际{{ task.actual_duration }}分钟</text>
            </view>
          </view>
          <view class="task-actions">
            <view class="task-action-btn" @click="startPomodoroFromTask(task)">🍅</view>
          </view>
          <view class="task-type" :class="task.type">
            {{ taskTypeText(task.type) }}
          </view>
        </view>
      </view>
    </view>

    <!-- Shared Task Form Modal -->
    <TaskFormModal
      v-model:visible="showTaskForm"
      :task="editingTask"
      :date="todayStr"
      :enable-quadrant="false"
      :show-a-i-mode="false"
      @saved="onTaskSaved"
      @deleted="onTaskDeleted"
    />

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
import TaskFormModal from '@/components/TaskFormModal.vue'
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
const editingTask = ref(null)
const todayStr = computed(() => dateUtil.today())

async function loadSubjects() {
  await subjectsStore.load()
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

function formatTaskTime(task) {
  const h = task.start_hour || 9
  const m = task.start_minute || 0
  return `${h}:${String(m).padStart(2, '0')}`
}

function editTask(task) {
  editingTask.value = task
  showTaskForm.value = true
}

// Long-press to edit task
let taskLongPressTimer = null
function onTaskTouchStart(task) {
  taskLongPressTimer = setTimeout(() => {
    taskLongPressTimer = null
    editTask(task)
  }, 600)
}
function onTaskTouchEnd() {
  if (taskLongPressTimer) { clearTimeout(taskLongPressTimer); taskLongPressTimer = null }
}

function confirmDeleteTask(task) {
  uni.showModal({
    title: '删除任务',
    content: `确定要删除「${task.content}」吗？`,
    success: async (res) => {
      if (!res.confirm) return
      try {
        await api.deleteTask(task.id)
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

async function onTaskSaved() {
  const today = dateUtil.today()
  if (planStore.currentPlan) {
    await taskStore.getTasksByDate(planStore.currentPlan.id, today)
  }
  await computeStreak()
  editingTask.value = null
}

async function onTaskDeleted() {
  const today = dateUtil.today()
  if (planStore.currentPlan) {
    await taskStore.getTasksByDate(planStore.currentPlan.id, today)
  }
  await computeStreak()
  editingTask.value = null
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

    .task-subject, .task-duration, .task-actual, .task-time {
      font-size: 12px;
      color: $muted;
    }
    .task-time { color: $accent; font-weight: 500; }
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
</style>