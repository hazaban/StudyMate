<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <view class="header-left">
          <text class="title">今日任务</text>
          <text class="date">{{ currentDate }}</text>
        </view>
        <view class="ai-btn" @click="aiGenerateTasks">
          <text class="ai-icon">🤖</text>
          <text class="ai-text">AI 生成</text>
        </view>
      </view>
      <view class="progress-summary">
        <view class="progress-item">
          <text class="progress-num">{{ taskStore.completedCount }}</text>
          <text class="progress-label">已完成</text>
        </view>
        <view class="progress-divider"></view>
        <view class="progress-item">
          <text class="progress-num">{{ taskStore.pendingTasks.length }}</text>
          <text class="progress-label">待完成</text>
        </view>
        <view class="progress-divider"></view>
        <view class="progress-item">
          <text class="progress-num">{{ taskStore.totalCount }}</text>
          <text class="progress-label">总任务</text>
        </view>
      </view>
    </view>

    <view class="tabs">
      <view class="tab" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
        <text class="tab-text">全部</text>
      </view>
      <view class="tab" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">
        <text class="tab-text">待完成</text>
      </view>
      <view class="tab" :class="{ active: activeTab === 'completed' }" @click="activeTab = 'completed'">
        <text class="tab-text">已完成</text>
      </view>
    </view>

    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view class="filter-item" :class="{ active: activeFilter === 'all' }" @click="activeFilter = 'all'">
            全部科目
          </view>
          <view class="filter-item" :class="{ active: activeFilter === subject }" v-for="subject in subjects" :key="subject" @click="activeFilter = subject">
            {{ subject }}
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="task-list">
      <view class="task-item" v-for="task in filteredTasks" :key="task.id" :class="{ completed: task.status === 'completed' }">
        <view class="task-check" @click="toggleTask(task)">
          <view class="check-circle" :class="{ checked: task.status === 'completed' }">
            <text v-if="task.status === 'completed'" class="check-icon">✓</text>
          </view>
        </view>
        <view class="task-body" @click="goToPomodoro(task)">
          <view class="task-top">
            <text class="task-content">{{ task.content }}</text>
            <view class="task-type-tag" :class="getTypeClass(task.type)">
              {{ getTypeLabel(task.type) }}
            </view>
          </view>
          <view class="task-meta">
            <text class="task-subject">{{ task.subject }}</text>
            <text class="task-duration">⏱ {{ task.duration }}分钟</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty" v-if="filteredTasks.length === 0">
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无任务</text>
      <text class="empty-hint">点击 AI 生成按钮，让 AI 帮你规划今日任务</text>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useTaskStore } from '@/stores/task'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'

const taskStore = useTaskStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const activeTab = ref('all')
const activeFilter = ref('all')

const currentDate = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 ${['日','一','二','三','四','五','六'][d.getDay()]}`
})

const subjects = computed(() => {
  const set = new Set()
  taskStore.todayTasks.forEach(t => set.add(t.subject))
  return [...set]
})

const filteredTasks = computed(() => {
  let tasks = taskStore.todayTasks
  if (activeTab.value === 'pending') tasks = tasks.filter(t => t.status === 'pending')
  if (activeTab.value === 'completed') tasks = tasks.filter(t => t.status === 'completed')
  if (activeFilter.value !== 'all') tasks = tasks.filter(t => t.subject === activeFilter.value)
  return tasks
})

const getTypeLabel = (type) => {
  const map = { new_study: '新学', review: '复习', mistake: '错题' }
  return map[type] || type
}

const getTypeClass = (type) => {
  const map = { new_study: 'tag-green', review: 'tag-orange', mistake: 'tag-red' }
  return map[type] || ''
}

async function toggleTask(task) {
  if (task.status === 'completed') {
    await taskStore.updateTask(task.id, { status: 'pending' })
  } else {
    await taskStore.completeTask(task.id)
  }
}

function goToPomodoro(task) {
  taskStore.currentTask = task
  uni.navigateTo({ url: '/pages/daily/pomodoro' })
}

async function aiGenerateTasks() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先创建学习计划', icon: 'none' })
    return
  }
  uni.showLoading({ title: 'AI 生成中...' })
  try {
    const result = await taskStore.generateDailyTasks({
      exam_name: planStore.currentPlan.exam_name,
      date: new Date().toISOString().split('T')[0],
      subjects: Object.keys(planStore.currentPlan.target_scores || {}),
      days_remaining: 0,
      available_time: planStore.currentPlan.daily_study_time || 480
    })
    if (result.tasks) {
      for (const t of result.tasks) {
        await taskStore.createTask({
          plan_id: planStore.currentPlan.id,
          date: new Date().toISOString().split('T')[0],
          type: t.type,
          subject: t.subject,
          content: t.content,
          duration: t.duration || 25
        })
      }
      uni.showToast({ title: '任务已生成', icon: 'success' })
    }
  } catch (e) {
    uni.showToast({ title: '生成失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    if (planStore.currentPlan) {
      const today = new Date().toISOString().split('T')[0]
      await taskStore.getTasksByDate(planStore.currentPlan.id, today)
    }
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, #2f7d4f 0%, #3d9a62 100%);
  border-radius: 0 0 32px 32px;
  margin-bottom: 24px;
  margin-left: -20px;
  margin-right: -20px;
  padding-left: 20px;
  padding-right: 20px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.header-left {
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

.ai-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.2);
  padding: 10px 18px;
  border-radius: 25px;
  transition: all 0.2s;
  
  &:active {
    background: rgba(255,255,255,0.3);
    transform: scale(0.96);
  }
  
  .ai-icon { font-size: 18px; }
  .ai-text { font-size: 14px; color: #fff; font-weight: 500; }
}

.progress-summary {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(255,255,255,0.15);
}

.progress-item {
  flex: 1;
  text-align: center;
  
  .progress-num {
    display: block;
    font-size: 22px;
    font-weight: 700;
    color: #fff;
  }
  .progress-label {
    font-size: 12px;
    color: rgba(255,255,255,0.7);
    margin-top: 2px;
  }
}

.progress-divider {
  width: 1px;
  height: 32px;
  background: rgba(255,255,255,0.2);
}

.tabs {
  display: flex;
  margin-bottom: 16px;
  background: #f5f7f5;
  border-radius: 12px;
  padding: 4px;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 10px;
  border-radius: 10px;
  transition: all 0.2s;
  
  &.active {
    background: #fff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    
    .tab-text {
      color: #2f7d4f;
      font-weight: 600;
    }
  }
  
  .tab-text {
    font-size: 14px;
    color: #65746d;
  }
}

.filter-section {
  margin-bottom: 16px;
}

.filter-scroll {
  white-space: nowrap;
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
  transition: all 0.2s;
  white-space: nowrap;
  
  &.active {
    background: #2f7d4f;
    color: #fff;
  }
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border-radius: 14px;
  padding: 14px 16px;
  border: 1px solid #e8ece9;
  transition: all 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  
  &:active {
    transform: scale(0.99);
  }
  
  &.completed {
    opacity: 0.7;
    .task-content {
      text-decoration: line-through;
    }
  }
}

.task-check {
  flex-shrink: 0;
}

.check-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid #d0d5d2;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  
  &.checked {
    background: #2f7d4f;
    border-color: #2f7d4f;
  }
  
  .check-icon {
    color: #fff;
    font-size: 14px;
    font-weight: 700;
  }
}

.task-body {
  flex: 1;
  min-width: 0;
}

.task-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 6px;
}

.task-content {
  font-size: 15px;
  color: #1a1a2e;
  line-height: 1.5;
  flex: 1;
}

.task-type-tag {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
  
  &.tag-green { background: #e8f5e9; color: #2e7d32; }
  &.tag-orange { background: #fff3e0; color: #e65100; }
  &.tag-red { background: #ffebee; color: #c62828; }
}

.task-meta {
  display: flex;
  gap: 16px;
  
  .task-subject {
    font-size: 12px;
    color: #2f7d4f;
    background: #e8f5e9;
    padding: 2px 8px;
    border-radius: 8px;
  }
  
  .task-duration {
    font-size: 12px;
    color: #999;
  }
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  
  .empty-icon { font-size: 48px; margin-bottom: 12px; }
  .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; }
  .empty-hint { font-size: 13px; color: #999; text-align: center; }
}

.bottom-space { height: 100px; }
</style>