<template>
  <view class="pomodoro-page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">番茄钟</text>
      <view class="placeholder"></view>
    </view>

    <view class="task-info" v-if="taskContent">
      <text class="task-label">当前任务</text>
      <text class="task-content">{{ taskContent }}</text>
    </view>

    <view class="timer-section">
      <view class="timer-circle">
        <view class="timer-progress" :style="progressStyle"></view>
        <view class="timer-content">
          <text class="timer-time">{{ formattedTime }}</text>
          <text class="timer-label">{{ isBreak ? '休息时间' : '专注学习' }}</text>
        </view>
      </view>

      <view class="mode-tabs">
        <view class="mode-tab" :class="{ active: pomodoroMode === 'pomodoro' }" @click="setMode('pomodoro')">
          <text class="mode-text">番茄专注</text>
        </view>
        <view class="mode-tab" :class="{ active: pomodoroMode === 'focus' }" @click="setMode('focus')">
          <text class="mode-text">自由专注</text>
        </view>
      </view>
    </view>

    <view class="control-section">
      <view class="time-settings">
        <view class="time-setting">
          <text class="setting-label">专注时长</text>
          <view class="setting-buttons">
            <view class="setting-btn" @click="adjustFocusTime(-5)">-</view>
            <text class="setting-value">{{ focusTime }}</text>
            <view class="setting-btn" @click="adjustFocusTime(5)">+</view>
          </view>
        </view>
        <view class="time-setting">
          <text class="setting-label">休息时长</text>
          <view class="setting-buttons">
            <view class="setting-btn" @click="adjustBreakTime(-1)">-</view>
            <text class="setting-value">{{ breakTime }}</text>
            <view class="setting-btn" @click="adjustBreakTime(1)">+</view>
          </view>
        </view>
      </view>

      <view class="action-buttons">
        <view class="action-btn secondary" @click="resetTimer" v-if="isRunning || isPaused">
          <text class="btn-text">重置</text>
        </view>
        <view class="action-btn primary" @click="toggleTimer">
          <text class="btn-text">{{ isRunning ? '暂停' : '开始' }}</text>
        </view>
      </view>
    </view>

    <view class="stats-section">
      <view class="stat-item">
        <text class="stat-value">{{ completedPomodoros }}</text>
        <text class="stat-label">今日完成</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ totalMinutes }}</text>
        <text class="stat-label">今日时长</text>
      </view>
    </view>

    <view class="history-section">
      <text class="section-title">今日记录</text>
      <view class="history-list">
        <view class="history-item" v-for="(record, index) in todayHistory" :key="index">
          <view class="history-icon" :class="record.type">
            {{ record.type === 'pomodoro' ? '🍅' : '☕' }}
          </view>
          <view class="history-info">
            <text class="history-type">{{ record.type === 'pomodoro' ? '专注学习' : '休息' }}</text>
            <text class="history-time">{{ record.time }}</text>
          </view>
          <text class="history-duration">{{ record.duration }}分钟</text>
        </view>
        <view class="empty-history" v-if="todayHistory.length === 0">
          <text class="empty-text">暂无记录，开始你的第一个番茄吧！</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { dateUtil } from '@/utils/date'

const taskContent = ref('')
const pomodoroMode = ref('pomodoro')
const focusTime = ref(25)
const breakTime = ref(5)
const isRunning = ref(false)
const isPaused = ref(false)
const isBreak = ref(false)
const timeRemaining = ref(25 * 60)
const completedPomodoros = ref(0)
const totalMinutes = ref(0)
const todayHistory = ref([])

let timer = null

const formattedTime = computed(() => {
  const minutes = Math.floor(timeRemaining.value / 60)
  const seconds = timeRemaining.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const progressStyle = computed(() => {
  const totalTime = isBreak.value ? breakTime.value * 60 : focusTime.value * 60
  const progress = ((totalTime - timeRemaining.value) / totalTime) * 360
  return {
    background: `conic-gradient(${isBreak.value ? '#66bb6a' : '#ef5350'} ${progress}deg, transparent ${progress}deg)`
  }
})

function setMode(mode) {
  pomodoroMode.value = mode
  resetTimer()
}

function adjustFocusTime(delta) {
  const newTime = focusTime.value + delta
  if (newTime >= 5 && newTime <= 60) {
    focusTime.value = newTime
    if (!isRunning && !isBreak.value) {
      timeRemaining.value = newTime * 60
    }
  }
}

function adjustBreakTime(delta) {
  const newTime = breakTime.value + delta
  if (newTime >= 1 && newTime <= 30) {
    breakTime.value = newTime
    if (!isRunning && isBreak.value) {
      timeRemaining.value = newTime * 60
    }
  }
}

function toggleTimer() {
  if (isRunning.value) {
    pauseTimer()
  } else {
    startTimer()
  }
}

function startTimer() {
  isRunning.value = true
  isPaused.value = false
  
  timer = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
    } else {
      completeTimer()
    }
  }, 1000)
}

function pauseTimer() {
  isRunning.value = false
  isPaused.value = true
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function resetTimer() {
  isRunning.value = false
  isPaused.value = false
  isBreak.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  timeRemaining.value = focusTime.value * 60
}

function completeTimer() {
  isRunning.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }

  if (!isBreak.value) {
    completedPomodoros.value++
    totalMinutes.value += focusTime.value
    todayHistory.value.push({
      type: 'pomodoro',
      time: dateUtil.format(new Date(), 'HH:mm'),
      duration: focusTime.value
    })

    uni.showToast({ title: '专注完成！休息一下吧', icon: 'success', duration: 2000 })

    if (pomodoroMode.value === 'pomodoro') {
      isBreak.value = true
      timeRemaining.value = breakTime.value * 60
      startTimer()
    }
  } else {
    todayHistory.value.push({
      type: 'break',
      time: dateUtil.format(new Date(), 'HH:mm'),
      duration: breakTime.value
    })

    uni.showToast({ title: '休息结束！继续专注', icon: 'success', duration: 2000 })

    isBreak.value = false
    timeRemaining.value = focusTime.value * 60
    startTimer()
  }
}

function goBack() {
  if (timer) {
    clearInterval(timer)
  }
  uni.navigateBack()
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  if (currentPage?.options?.taskContent) {
    taskContent.value = decodeURIComponent(currentPage.options.taskContent)
  }
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style lang="scss" scoped>
.pomodoro-page {
  min-height: 100vh;
  background: $bg;
  padding-bottom: 40px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 20px 20px;
  
  .back-btn {
    width: 40px;
    height: 40px;
    background: $bg2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .back-icon {
      font-size: 20px;
      color: $ink;
    }
  }
  
  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: $ink;
  }
  
  .placeholder {
    width: 40px;
  }
}

.task-info {
  background: $bg2;
  margin: 0 20px 20px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid $rule;
  
  .task-label {
    display: block;
    font-size: 12px;
    color: $muted;
    margin-bottom: 4px;
  }
  
  .task-content {
    font-size: 15px;
    color: $ink;
    font-weight: 500;
  }
}

.timer-section {
  padding: 0 20px;
  margin-bottom: 20px;
}

.timer-circle {
  width: 280px;
  height: 280px;
  border-radius: 50%;
  margin: 0 auto;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg2;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.timer-progress {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  opacity: 0.3;
}

.timer-content {
  position: relative;
  z-index: 1;
  text-align: center;
  
  .timer-time {
    display: block;
    font-size: 56px;
    font-weight: 700;
    color: $ink;
    margin-bottom: 8px;
  }
  
  .timer-label {
    font-size: 16px;
    color: $muted;
  }
}

.mode-tabs {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

.mode-tab {
  padding: 10px 24px;
  border-radius: 20px;
  background: $bg2;
  border: 1px solid $rule;
  
  &.active {
    background: $accent;
    border-color: $accent;
    
    .mode-text {
      color: #fff;
    }
  }
  
  .mode-text {
    font-size: 14px;
    color: $muted;
  }
}

.control-section {
  padding: 0 20px;
  margin-bottom: 20px;
}

.time-settings {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 24px;
}

.time-setting {
  text-align: center;
  
  .setting-label {
    display: block;
    font-size: 12px;
    color: $muted;
    margin-bottom: 8px;
  }
  
  .setting-buttons {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .setting-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: $bg2;
    border: 1px solid $rule;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: $accent;
  }
  
  .setting-value {
    font-size: 24px;
    font-weight: 700;
    color: $ink;
    min-width: 40px;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
  
  .action-btn {
    flex: 1;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    
    &.primary {
      background: $accent;
      
      .btn-text {
        color: #fff;
      }
    }
    
    &.secondary {
      background: $bg2;
      border: 1px solid $rule;
      
      .btn-text {
        color: $ink;
      }
    }
    
    .btn-text {
      font-size: 16px;
      font-weight: 600;
    }
  }
}

.stats-section {
  display: flex;
  gap: 12px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.stat-item {
  flex: 1;
  background: $bg2;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  border: 1px solid $rule;
  
  .stat-value {
    display: block;
    font-size: 28px;
    font-weight: 700;
    color: $accent;
    margin-bottom: 4px;
  }
  
  .stat-label {
    font-size: 12px;
    color: $muted;
  }
}

.history-section {
  padding: 0 20px;
  
  .section-title {
    display: block;
    font-size: 16px;
    font-weight: 600;
    color: $ink;
    margin-bottom: 12px;
  }
}

.history-list {
  background: $bg2;
  border-radius: 12px;
  padding: 12px;
  border: 1px solid $rule;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid $rule;
  
  &:last-child {
    border-bottom: none;
  }
  
  .history-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    
    &.pomodoro {
      background: #ffebee;
    }
    
    &.break {
      background: #e8f5e9;
    }
  }
  
  .history-info {
    flex: 1;
    
    .history-type {
      display: block;
      font-size: 14px;
      color: $ink;
      margin-bottom: 2px;
    }
    
    .history-time {
      font-size: 12px;
      color: $muted;
    }
  }
  
  .history-duration {
    font-size: 14px;
    color: $accent;
    font-weight: 500;
  }
}

.empty-history {
  padding: 20px;
  text-align: center;
  
  .empty-text {
    font-size: 14px;
    color: $muted;
  }
}
</style>