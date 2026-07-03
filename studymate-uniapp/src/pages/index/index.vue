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
          <text class="streak-days">连续学习 3 天</text>
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
    </view>

    <view class="task-preview">
      <view class="section-header">
        <text class="section-title">今日任务</text>
        <text class="section-link" @click="goToTaskBoard">全部任务</text>
      </view>
      <view class="task-list">
        <view class="task-item" v-for="task in previewTasks" :key="task.id">
          <view class="task-checkbox" :class="{ checked: task.status === 'completed' }">
            <text v-if="task.status === 'completed'">✓</text>
          </view>
          <view class="task-content">
            <text class="task-title">{{ task.content }}</text>
            <view class="task-meta">
              <text class="task-subject">{{ task.subject }}</text>
              <text class="task-duration">{{ task.duration }}分钟</text>
            </view>
          </view>
          <view class="task-type" :class="task.type">
            {{ taskTypeText(task.type) }}
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePlanStore } from '@/stores/plan'
import { useTaskStore } from '@/stores/task'
import { useFarmStore } from '@/stores/farm'
import { dateUtil } from '@/utils/date'

const userStore = useUserStore()
const planStore = usePlanStore()
const taskStore = useTaskStore()
const farmStore = useFarmStore()

const currentDate = ref('')
const daysRemaining = ref(0)
const progressPercent = ref(0)

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

function goToProfile() {
  uni.navigateTo({ url: '/pages/profile/profile' })
}

function goToPlan() {
  uni.navigateTo({ url: '/pages/plan/plan-overview' })
}

function goToTaskBoard() {
  uni.switchTab({ url: '/pages/daily/task-board' })
}

function goToReview() {
  uni.switchTab({ url: '/pages/review/flash-cards' })
}

function goToFarm() {
  uni.switchTab({ url: '/pages/farm/farm' })
}

function startPomodoro() {
  uni.navigateTo({ url: '/pages/daily/pomodoro' })
}

onMounted(async () => {
  currentDate.value = `${dateUtil.format(new Date(), 'YYYY年MM月DD日')} ${dateUtil.getWeekDay(new Date())}`
  
  await userStore.getUserInfo()
  
  if (userStore.isLoggedIn && userStore.user) {
    await planStore.getPlansByUserId()
    
    if (planStore.currentPlan) {
      const today = dateUtil.today()
      await taskStore.getTasksByDate(planStore.currentPlan.id, today)
      await farmStore.getPlantsByPlanId(planStore.currentPlan.id)
      
      daysRemaining.value = dateUtil.getDaysBetween(today, planStore.currentPlan.exam_date)
      
      if (taskStore.totalCount > 0) {
        progressPercent.value = Math.round((taskStore.completedCount / taskStore.totalCount) * 100)
      }
    }
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 24px;
  background: linear-gradient(135deg, $accent 0%, lighten($accent, 10%) 100%);
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
  
  .progress-bar {
    height: 8px;
    background: $soft;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
    
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, $accent, lighten($accent, 8%));
      border-radius: 4px;
      transition: width 0.6s ease;
    }
  }
  
  .progress-text {
    font-size: 12px;
    color: $muted;
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
    
    .task-subject, .task-duration {
      font-size: 12px;
      color: $muted;
    }
  }
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