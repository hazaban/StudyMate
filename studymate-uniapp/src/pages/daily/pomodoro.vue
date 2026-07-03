<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="title">番茄钟</text>
      <view class="mode-toggle" @click="showModePicker = !showModePicker">
        <text class="mode-text">{{ isFreeMode ? '自由专注' : '任务模式' }}</text>
      </view>
    </view>

    <!-- Timer Circle -->
    <view class="timer-section">
      <view class="timer-circle" :class="{ running: timerRunning, break: isBreak }">
        <view class="timer-inner">
          <text class="timer-text">{{ formattedTime }}</text>
          <text class="timer-label">{{ isBreak ? '休息中' : '专注中' }}</text>
          <text class="task-label" v-if="currentTaskName">{{ currentTaskName }}</text>
        </view>
      </view>

      <view class="timer-controls">
        <view class="control-btn reset-btn" @click="resetTimer" v-if="timerRunning || elapsed > 0">
          <text>重置</text>
        </view>
        <view class="control-btn start-btn" @click="toggleTimer" :class="{ pause: timerRunning }">
          <text>{{ timerRunning ? '暂停' : '开始' }}</text>
        </view>
        <view class="control-btn skip-btn" @click="skipTimer" v-if="timerRunning">
          <text>跳过</text>
        </view>
      </view>
    </view>

    <!-- Mode Picker -->
    <view class="mode-picker" v-if="showModePicker">
      <view class="mode-option" :class="{ active: !isFreeMode }" @click="switchMode(false)">
        <text class="mode-option-icon">📋</text>
        <view class="mode-option-info">
          <text class="mode-option-title">任务模式</text>
          <text class="mode-option-desc">与今日任务挂钩，专注完成指定任务</text>
        </view>
      </view>
      <view class="mode-option" :class="{ active: isFreeMode }" @click="switchMode(true)">
        <text class="mode-option-icon">🎯</text>
        <view class="mode-option-info">
          <text class="mode-option-title">自由专注</text>
          <text class="mode-option-desc">不限任务，自由安排学习时间，休息时间可设为0</text>
        </view>
      </view>
    </view>

    <!-- Task Link (Task Mode) -->
    <view class="task-link-section" v-if="!isFreeMode">
      <view class="section-title">关联任务</view>
      <view class="task-select" @click="showTaskPicker = true">
        <text class="task-select-label">{{ currentTaskName || '选择今日任务' }}</text>
        <text class="task-select-arrow">›</text>
      </view>
    </view>

    <!-- Free Focus Settings -->
    <view class="settings-section" v-if="isFreeMode">
      <view class="section-title">自由专注设置</view>
      <view class="setting-row">
        <text class="setting-label">专注时长（分钟）</text>
        <input class="setting-input" v-model="freeFocusDuration" type="number" placeholder="25" />
      </view>
      <view class="setting-row">
        <text class="setting-label">休息时长（分钟）</text>
        <input class="setting-input" v-model="freeBreakDuration" type="number" placeholder="0" />
      </view>
      <view class="setting-row">
        <text class="setting-label">任务名称（选填）</text>
        <input class="setting-input" v-model="freeTaskName" placeholder="如：复习数据结构" />
      </view>
    </view>

    <!-- Task Picker Modal -->
    <view class="modal-overlay" v-if="showTaskPicker" @click="showTaskPicker = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">选择今日任务</text>
          <view class="modal-close" @click="showTaskPicker = false">✕</view>
        </view>
        <view class="modal-body">
          <view class="picker-task" v-for="task in todayTasks" :key="task.id" @click="selectTask(task)">
            <view class="picker-task-info">
              <text class="picker-task-name">{{ task.subject }} - {{ task.content }}</text>
              <text class="picker-task-duration">预计: {{ task.duration }}分钟</text>
            </view>
            <view class="picker-check" :class="{ checked: selectedTaskId === task.id }">
              <text v-if="selectedTaskId === task.id">✓</text>
            </view>
          </view>
          <view class="empty" v-if="todayTasks.length === 0">
            <text class="empty-text">暂无今日任务，请先添加任务</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Timer Settings -->
    <view class="settings-section">
      <view class="section-title">计时设置</view>
      <view class="setting-row">
        <text class="setting-label">专注时长（分钟）</text>
        <input class="setting-input" v-model="focusDuration" type="number" />
      </view>
      <view class="setting-row" v-if="!isFreeMode">
        <text class="setting-label">短休息（分钟）</text>
        <input class="setting-input" v-model="shortBreak" type="number" />
      </view>
      <view class="setting-row" v-if="!isFreeMode">
        <text class="setting-label">长休息（分钟）</text>
        <input class="setting-input" v-model="longBreak" type="number" />
      </view>
    </view>

    <!-- Manual Time Recording -->
    <view class="manual-section">
      <view class="section-title">手动记录时间</view>
      <view class="manual-row">
        <input class="manual-input" v-model="manualMinutes" type="number" placeholder="分钟数" />
        <input class="manual-input" v-model="manualTaskName" placeholder="任务描述" />
        <view class="manual-submit" @click="submitManualRecord">记录</view>
      </view>
    </view>

    <!-- Today's Records -->
    <view class="history-section">
      <view class="section-title">今日番茄记录</view>
      <view class="history-list">
        <view class="history-item" v-for="(record, idx) in todayRecords" :key="idx">
          <view class="history-left">
            <text class="history-name">{{ record.taskName }}</text>
            <text class="history-time">{{ record.time }}</text>
          </view>
          <view class="history-duration">{{ record.duration }}分钟</view>
        </view>
      </view>
      <view class="empty" v-if="todayRecords.length === 0">
        <text class="empty-text">暂无记录</text>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTaskStore } from '@/stores/task'
import { usePlanStore } from '@/stores/plan'
import { useFarmStore } from '@/stores/farm'

const taskStore = useTaskStore()
const planStore = usePlanStore()
const farmStore = useFarmStore()

// Timer state
const focusDuration = ref(25)
const shortBreak = ref(5)
const longBreak = ref(15)
const freeFocusDuration = ref(25)
const freeBreakDuration = ref(0)
const freeTaskName = ref('')
const timerRunning = ref(false)
const isBreak = ref(false)
const elapsed = ref(0)
const totalDuration = ref(25 * 60)
const pomodoroCount = ref(0)
let timerInterval = null

// Mode
const isFreeMode = ref(false)
const showModePicker = ref(false)

// Task link
const currentTaskName = ref('')
const currentTaskId = ref('')
const showTaskPicker = ref(false)
const selectedTaskId = ref('')

// Manual record
const manualMinutes = ref('')
const manualTaskName = ref('')

// Records - persist to localStorage
const todayRecords = ref(JSON.parse(uni.getStorageSync('studymate_pomodoro_records') || '[]'))

const today = computed(() => new Date().toISOString().split('T')[0])

const todayTasks = computed(() => {
  return taskStore.todayTasks || []
})

const formattedTime = computed(() => {
  const remaining = totalDuration.value - elapsed.value
  const mins = Math.floor(remaining / 60)
  const secs = remaining % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

function switchMode(free) {
  isFreeMode.value = free
  showModePicker.value = false
  resetTimer()
}

function resetTimer() {
  timerRunning.value = false
  isBreak.value = false
  elapsed.value = 0
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  const dur = isFreeMode.value ? freeFocusDuration.value : focusDuration.value
  totalDuration.value = parseInt(dur) * 60
}

function toggleTimer() {
  if (timerRunning.value) {
    // Pause
    timerRunning.value = false
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  } else {
    // Start
    if (elapsed.value === 0) {
      const dur = isFreeMode.value ? freeFocusDuration.value : focusDuration.value
      totalDuration.value = parseInt(dur) * 60
    }
    timerRunning.value = true
    timerInterval = setInterval(() => {
      elapsed.value++
      if (elapsed.value >= totalDuration.value) {
        completeSession()
      }
    }, 1000)
  }
}

function skipTimer() {
  completeSession()
}

async function completeSession() {
  timerRunning.value = false
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }

  const sessionDuration = Math.round(elapsed.value / 60)
  const now = new Date()
  const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`

  if (!isBreak.value) {
    pomodoroCount.value++

    // Record session
    const taskName = isFreeMode.value
      ? (freeTaskName.value || '自由专注')
      : (currentTaskName.value || '番茄钟专注')

    todayRecords.value.unshift({
      taskName,
      time: timeStr,
      duration: sessionDuration,
      date: today.value
    })
    // Persist to localStorage
    uni.setStorageSync('studymate_pomodoro_records', JSON.stringify(todayRecords.value))

    // Update task actual_duration if linked
    if (currentTaskId.value) {
      try {
        const task = taskStore.todayTasks.find(t => t.id === currentTaskId.value)
        if (task) {
          const newActual = (task.actual_duration || 0) + sessionDuration
          await taskStore.updateTask(currentTaskId.value, { actual_duration: newActual })
        }
      } catch (e) { /* silent */ }
    }

    // Link to farm: water the crop
    if (planStore.currentPlan && currentTaskName.value) {
      try {
        // Try to find subject from task name
        const subject = currentTaskName.value.split(' - ')[0] || currentTaskName.value.split(':')[0] || ''
        if (subject) {
          const crop = await farmStore.ensureCrop(planStore.currentPlan.id, subject)
          if (crop.plant) {
            await farmStore.waterPlant(crop.plant.id)
          }
        }
      } catch (e) { /* silent */ }
    }

    // Notify
    uni.showToast({ title: `完成 ${sessionDuration} 分钟专注!`, icon: 'success' })

    // H5 notification
    // #ifdef H5
    const reminderEnabled = uni.getStorageSync('studymate_reminder_enabled')
    if (reminderEnabled && 'Notification' in window && Notification.permission === 'granted') {
      new Notification('StudyMate - 番茄钟完成', {
        body: `已完成 ${sessionDuration} 分钟专注学习: ${taskName}`,
        icon: '/static/logo.png',
        tag: 'pomodoro-complete'
      })
    }
    // #endif

    // Start break (except free mode with break=0)
    if (isFreeMode.value && parseInt(freeBreakDuration.value) === 0) {
      elapsed.value = 0
      totalDuration.value = parseInt(freeFocusDuration.value) * 60
    } else {
      isBreak.value = true
      elapsed.value = 0
      const breakDur = isFreeMode.value ? freeBreakDuration.value : (pomodoroCount.value % 4 === 0 ? longBreak.value : shortBreak.value)
      totalDuration.value = parseInt(breakDur) * 60
      timerRunning.value = true
      timerInterval = setInterval(() => {
        elapsed.value++
        if (elapsed.value >= totalDuration.value) {
          // Break complete
          timerRunning.value = false
          clearInterval(timerInterval)
          timerInterval = null
          isBreak.value = false
          elapsed.value = 0
          const dur = isFreeMode.value ? freeFocusDuration.value : focusDuration.value
          totalDuration.value = parseInt(dur) * 60
          uni.showToast({ title: '休息结束，继续加油！', icon: 'none' })
        }
      }, 1000)
    }
  } else {
    // Break complete
    isBreak.value = false
    elapsed.value = 0
    const dur = isFreeMode.value ? freeFocusDuration.value : focusDuration.value
    totalDuration.value = parseInt(dur) * 60
  }
}

function selectTask(task) {
  selectedTaskId.value = task.id
  currentTaskId.value = task.id
  currentTaskName.value = `${task.subject}${task.chapter ? ' - ' + task.chapter : ''}: ${task.content}`
  showTaskPicker.value = false
}

function submitManualRecord() {
  const mins = parseInt(manualMinutes.value)
  if (!mins || mins <= 0) {
    uni.showToast({ title: '请输入有效分钟数', icon: 'none' })
    return
  }
  const taskName = manualTaskName.value.trim() || '手动记录'
  const now = new Date()
  const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`

  todayRecords.value.unshift({
    taskName,
    time: timeStr,
    duration: mins,
    date: today.value
  })
  uni.setStorageSync('studymate_pomodoro_records', JSON.stringify(todayRecords.value))
  manualMinutes.value = ''
  manualTaskName.value = ''
  uni.showToast({ title: '记录成功', icon: 'success' })
}

function goBack() {
  uni.navigateBack()
}

// Load settings from storage
onMounted(() => {
  const saved = uni.getStorageSync('studymate_pomodoro_settings')
  if (saved) {
    try {
      const s = JSON.parse(saved)
      focusDuration.value = s.focusDuration || 25
      shortBreak.value = s.shortBreak || 5
      longBreak.value = s.longBreak || 15
    } catch (e) {}
  }

  // Load records and filter by today
  const allRecords = JSON.parse(uni.getStorageSync('studymate_pomodoro_records') || '[]')
  todayRecords.value = allRecords.filter(r => r.date === today.value)

  totalDuration.value = focusDuration.value * 60
})

// Save settings
function saveSettings() {
  uni.setStorageSync('studymate_pomodoro_settings', JSON.stringify({
    focusDuration: focusDuration.value,
    shortBreak: shortBreak.value,
    longBreak: longBreak.value
  }))
}

// Save settings on change
const stopWatch = () => {}
onUnmounted(() => {
  saveSettings()
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40px 0 20px;
  .back-btn { width: 40px; height: 40px; background: $bg2; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
  .back-icon { font-size: 20px; color: $ink; }
  .title { font-size: 20px; font-weight: 600; color: $ink; }
  .mode-toggle { padding: 8px 16px; background: $soft; border-radius: 20px; }
  .mode-text { font-size: 13px; color: $accent; font-weight: 500; }
}

.timer-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
}

.timer-circle {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  border: 6px solid #2f7d4f;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  transition: all 0.3s;
  &.running { border-color: #2f7d4f; background: linear-gradient(135deg, #c8e6c9, #a5d6a7); }
  &.break { border-color: #ff9800; background: linear-gradient(135deg, #fff3e0, #ffe0b2); }
}

.timer-inner {
  text-align: center;
  .timer-text { display: block; font-size: 48px; font-weight: 700; color: #1a1a2e; }
  .timer-label { display: block; font-size: 14px; color: #65746d; margin-top: 4px; }
  .task-label { display: block; font-size: 12px; color: #2f7d4f; margin-top: 4px; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
}

.timer-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.control-btn {
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 15px;
  font-weight: 500;
  &.reset-btn { background: #f5f7f5; color: #65746d; }
  &.start-btn { background: #2f7d4f; color: #fff; padding: 14px 36px; &.pause { background: #ff9800; } }
  &.skip-btn { background: #fff3e0; color: #e65100; }
}

.mode-picker {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e8ece9;
}

.mode-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
  margin-bottom: 8px;
  &:last-child { margin-bottom: 0; }
  &.active { background: #e8f5e9; border: 1px solid #2f7d4f; }
  .mode-option-icon { font-size: 24px; }
  .mode-option-info { flex: 1; }
  .mode-option-title { display: block; font-size: 15px; font-weight: 600; color: #1a1a2e; }
  .mode-option-desc { display: block; font-size: 12px; color: #999; margin-top: 2px; }
}

.task-link-section, .settings-section, .manual-section, .history-section {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e8ece9;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.task-select {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7f5;
  border-radius: 10px;
  .task-select-label { font-size: 14px; color: #1a1a2e; }
  .task-select-arrow { font-size: 20px; color: #999; }
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  &:last-child { margin-bottom: 0; }
  .setting-label { font-size: 14px; color: #65746d; }
  .setting-input {
    width: 80px;
    padding: 8px 12px;
    border: 1px solid #e8ece9;
    border-radius: 8px;
    font-size: 14px;
    text-align: center;
    background: #fafafa;
  }
}

.manual-row {
  display: flex;
  gap: 8px;
  align-items: center;
  .manual-input {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #e8ece9;
    border-radius: 10px;
    font-size: 14px;
    background: #fafafa;
  }
  .manual-submit {
    padding: 10px 16px;
    background: #2f7d4f;
    color: #fff;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    white-space: nowrap;
  }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f5f7f5;
  border-radius: 10px;
  .history-left { flex: 1; min-width: 0; }
  .history-name { display: block; font-size: 14px; color: #1a1a2e; }
  .history-time { display: block; font-size: 11px; color: #999; }
  .history-duration { font-size: 14px; font-weight: 600; color: #2f7d4f; white-space: nowrap; margin-left: 12px; }
}

.empty { text-align: center; padding: 20px; .empty-text { font-size: 13px; color: #999; } }

/* Task Picker Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; }
.modal-content { background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 60vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 16px 24px; flex: 1; overflow-y: auto; }
.picker-task { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid #f0f0f0; }
.picker-task-info { flex: 1; }
.picker-task-name { display: block; font-size: 14px; color: #1a1a2e; }
.picker-task-duration { display: block; font-size: 12px; color: #999; margin-top: 4px; }
.picker-check { width: 24px; height: 24px; border-radius: 50%; border: 2px solid #d0d5d2; display: flex; align-items: center; justify-content: center; font-size: 14px; &.checked { background: #2f7d4f; border-color: #2f7d4f; color: #fff; } }

.bottom-space { height: 100px; }
</style>