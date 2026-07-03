<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="title">番茄钟</text>
      <view class="header-placeholder"></view>
    </view>

    <!-- Mode Tabs -->
    <view class="mode-tabs">
      <view class="mode-tab" :class="{ active: pomodoroMode === 'pomodoro' }" @click="switchMode('pomodoro')">
        <text class="mode-tab-icon">🍅</text>
        <text class="mode-tab-text">番茄专注</text>
      </view>
      <view class="mode-tab" :class="{ active: pomodoroMode === 'focus' }" @click="switchMode('focus')">
        <text class="mode-tab-icon">🎯</text>
        <text class="mode-tab-text">自由专注</text>
      </view>
    </view>

    <!-- Task Link -->
    <view class="task-link-section">
      <view class="section-title">关联任务</view>
      <view class="task-select" @click="showTaskPicker = true">
        <view class="task-select-left">
          <text class="task-select-icon">📋</text>
          <text class="task-select-label">{{ currentTaskName || '选择今日任务（可选）' }}</text>
        </view>
        <text class="task-select-arrow">›</text>
      </view>
    </view>

    <!-- Timer Circle -->
    <view class="timer-section">
      <view class="timer-circle" :style="circleStyle">
        <view class="timer-inner">
          <text class="timer-text">{{ formattedTime }}</text>
          <text class="timer-label">{{ statusLabel }}</text>
          <text class="task-label" v-if="displayTaskName">{{ displayTaskName }}</text>
        </view>
      </view>

      <view class="timer-controls">
        <view class="control-btn reset-btn" @click="resetTimer" v-if="isRunning || isPaused || hasProgress">
          <text>重置</text>
        </view>
        <view class="control-btn start-btn" @click="toggleTimer" :class="{ pause: isRunning }">
          <text>{{ isRunning ? '暂停' : '开始' }}</text>
        </view>
      </view>
    </view>

    <!-- Time Settings (+/- buttons) -->
    <view class="settings-section">
      <view class="section-title">时间设置</view>
      <view class="time-setting">
        <text class="setting-label">专注时长</text>
        <view class="setting-buttons">
          <view class="setting-btn" @click="adjustFocusTime(-5)">-</view>
          <view class="input-wrapper">
            <input class="setting-input" type="number" v-model="focusTimeInput" @blur="onFocusTimeBlur" />
          </view>
          <text class="setting-unit">分钟</text>
          <view class="setting-btn" @click="adjustFocusTime(5)">+</view>
        </view>
      </view>
      <view class="time-setting">
        <text class="setting-label">休息时长</text>
        <view class="setting-buttons">
          <view class="setting-btn" @click="adjustBreakTime(-1)">-</view>
          <view class="input-wrapper">
            <input class="setting-input" type="number" v-model="breakTimeInput" @blur="onBreakTimeBlur" />
          </view>
          <text class="setting-unit">分钟</text>
          <view class="setting-btn" @click="adjustBreakTime(1)">+</view>
        </view>
      </view>
    </view>

    <!-- Stats -->
    <view class="stats-section">
      <view class="stat-item">
        <text class="stat-value">{{ completedPomodoros }}</text>
        <text class="stat-label">今日番茄</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-value">{{ totalMinutes }}</text>
        <text class="stat-label">今日时长(分)</text>
      </view>
    </view>

    <!-- Today's Records -->
    <view class="history-section">
      <view class="section-title">今日番茄记录</view>
      <view class="history-list" v-if="todayRecords.length > 0">
        <view class="history-item" v-for="(record, idx) in todayRecords" :key="idx">
          <view class="history-icon">{{ record.type === 'focus' ? '🍅' : '☕' }}</view>
          <view class="history-info">
            <view class="history-top">
              <text class="history-type">{{ record.type === 'focus' ? '专注' : '手动' }}</text>
              <text class="history-name">{{ record.taskName }}</text>
            </view>
            <text class="history-time">{{ record.time }}</text>
          </view>
          <view class="history-duration">{{ record.duration }}分钟</view>
          <view class="history-actions">
            <text class="history-action-btn" @click="editRecord(idx)">编辑</text>
            <text class="history-action-btn delete" @click="deleteRecord(idx)">删除</text>
          </view>
        </view>
      </view>
      <view class="empty" v-else>
        <text class="empty-text">暂无记录</text>
      </view>

      <!-- Manual Record Input -->
      <view class="manual-row">
        <input class="manual-input manual-minutes" v-model="manualMinutes" type="number" placeholder="分钟数" />
        <input class="manual-input manual-task" v-model="manualTaskName" placeholder="任务描述" />
        <view class="manual-submit" @click="submitManualRecord">添加</view>
      </view>
    </view>

    <!-- Edit Record Modal -->
    <view class="modal-overlay" v-if="showEditModal" @click="showEditModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑记录</text>
          <view class="modal-close" @click="showEditModal = false">✕</view>
        </view>
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">时长（分钟）</text>
            <input class="form-input" type="number" v-model="editDuration" placeholder="请输入分钟数" />
          </view>
          <view class="form-group">
            <text class="form-label">任务描述</text>
            <input class="form-input" type="text" v-model="editTaskName" placeholder="请输入任务描述" />
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showEditModal = false">取消</view>
          <view class="submit-btn" @click="saveEdit">保存</view>
        </view>
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
              <text class="picker-task-name">{{ task.subject }}{{ task.chapter ? ' - ' + task.chapter : '' }}: {{ task.content }}</text>
              <text class="picker-task-duration">预计: {{ task.duration }}分钟</text>
            </view>
            <view class="picker-check" :class="{ checked: currentTaskId === task.id }">
              <text v-if="currentTaskId === task.id">✓</text>
            </view>
          </view>
          <view class="empty" v-if="todayTasks.length === 0">
            <text class="empty-text">暂无今日任务，请先添加任务</text>
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useTaskStore } from '@/stores/task'
import { useFarmStore } from '@/stores/farm'
import { usePlanStore } from '@/stores/plan'

const taskStore = useTaskStore()
const farmStore = useFarmStore()
const planStore = usePlanStore()

// Mode
const pomodoroMode = ref('pomodoro') // 'pomodoro' | 'focus'

// Time settings - shared between modes
const focusTime = ref(25)
const breakTime = ref(5)
const focusTimeInput = ref('25')
const breakTimeInput = ref('5')

// Timer state
const isRunning = ref(false)
const isPaused = ref(false)
const isBreak = ref(false)
const timeRemaining = ref(25 * 60)
const completedPomodoros = ref(0)
const totalMinutes = ref(0)
const todayRecords = ref([])
let timerInterval = null

// Task association
const taskContent = ref('')
const currentTaskId = ref(null)
const currentTaskName = ref('')
const showTaskPicker = ref(false)

// Manual record
const manualMinutes = ref('')
const manualTaskName = ref('')

// Edit record
const showEditModal = ref(false)
const editingIndex = ref(-1)
const editDuration = ref('')
const editTaskName = ref('')

const today = computed(() => new Date().toISOString().split('T')[0])
const todayTasks = computed(() => taskStore.todayTasks || [])

const currentFocusSeconds = computed(() => focusTime.value * 60)

const currentBreakSeconds = computed(() => breakTime.value * 60)

const currentTotalSeconds = computed(() => {
  return isBreak.value ? currentBreakSeconds.value : currentFocusSeconds.value
})

const hasProgress = computed(() => timeRemaining.value < currentTotalSeconds.value)

const formattedTime = computed(() => {
  const t = Math.max(0, timeRemaining.value)
  const mins = Math.floor(t / 60)
  const secs = t % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

const statusLabel = computed(() => {
  if (isBreak.value) return '休息中'
  if (isRunning.value) return '专注中'
  if (isPaused.value) return '已暂停'
  return '准备专注'
})

const displayTaskName = computed(() => {
  if (pomodoroMode.value === 'focus') {
    return '自由专注'
  }
  return currentTaskName.value
})

const circleStyle = computed(() => {
  const total = currentTotalSeconds.value
  const elapsed = Math.max(0, total - timeRemaining.value)
  const percent = total > 0 ? Math.min(100, (elapsed / total) * 100) : 0
  const deg = percent * 3.6
  const color = isBreak.value ? '#66bb6a' : '#ef5350'
  return {
    background: `conic-gradient(${color} ${deg}deg, #e8ece9 ${deg}deg)`
  }
})

// Sync inputs with refs
watch(focusTime, (val) => { focusTimeInput.value = String(val) })
watch(breakTime, (val) => { breakTimeInput.value = String(val) })

// Persist settings on change
watch([focusTime, breakTime, pomodoroMode], saveSettings)

// +/- adjust handlers
function adjustFocusTime(delta) {
  const newTime = focusTime.value + delta
  if (newTime >= 5 && newTime <= 60) {
    focusTime.value = newTime
    if (!isRunning.value && !isBreak.value) {
      timeRemaining.value = newTime * 60
    }
  }
}

function adjustBreakTime(delta) {
  const newTime = breakTime.value + delta
  if (newTime >= 1 && newTime <= 30) {
    breakTime.value = newTime
    if (!isRunning.value && isBreak.value) {
      timeRemaining.value = newTime * 60
    }
  }
}

// Input blur handlers - validate & clamp
function onFocusTimeBlur() {
  let val = parseInt(focusTimeInput.value)
  if (isNaN(val)) val = focusTime.value
  val = Math.max(5, Math.min(60, val))
  focusTime.value = val
  focusTimeInput.value = String(val)
  if (!isRunning.value && !isBreak.value) {
    timeRemaining.value = val * 60
  }
}

function onBreakTimeBlur() {
  let val = parseInt(breakTimeInput.value)
  if (isNaN(val)) val = breakTime.value
  val = Math.max(1, Math.min(30, val))
  breakTime.value = val
  breakTimeInput.value = String(val)
  if (!isRunning.value && isBreak.value) {
    timeRemaining.value = val * 60
  }
}

function switchMode(mode) {
  if (pomodoroMode.value === mode) return
  pomodoroMode.value = mode
  resetTimer()
}

function resetTimer() {
  isRunning.value = false
  isPaused.value = false
  isBreak.value = false
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  timeRemaining.value = currentFocusSeconds.value
}

function toggleTimer() {
  if (isRunning.value) {
    isRunning.value = false
    isPaused.value = true
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  } else {
    isRunning.value = true
    isPaused.value = false
    timerInterval = setInterval(() => {
      timeRemaining.value--
      if (timeRemaining.value <= 0) {
        completeSession()
      }
    }, 1000)
  }
}

async function completeSession() {
  isRunning.value = false
  isPaused.value = false
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }

  if (!isBreak.value) {
    // Focus phase complete
    const sessionDuration = Math.round(currentFocusSeconds.value / 60)
    completedPomodoros.value++
    totalMinutes.value += sessionDuration

    const taskName = pomodoroMode.value === 'focus'
      ? '自由专注'
      : (currentTaskName.value || '番茄钟专注')

    const now = new Date()
    const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`

    todayRecords.value.unshift({
      type: 'focus',
      taskName,
      time: timeStr,
      duration: sessionDuration,
      date: today.value
    })
    saveRecords()

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

    // Farm integration: ensure crop & water plant
    if (planStore.currentPlan) {
      try {
        let subject = ''
        if (pomodoroMode.value === 'focus') {
          subject = '自由专注'
        } else {
          const task = taskStore.todayTasks.find(t => t.id === currentTaskId.value)
          if (task) {
            subject = task.subject
          } else if (currentTaskName.value) {
            subject = currentTaskName.value.split(':')[0].split(' - ')[0].trim()
          }
        }
        if (subject) {
          const crop = await farmStore.ensureCrop(planStore.currentPlan.id, subject)
          if (crop && crop.plant) {
            await farmStore.waterPlant(crop.plant.id)
          }
        }
      } catch (e) { /* silent */ }
    }

    uni.showToast({ title: `完成 ${sessionDuration} 分钟专注!`, icon: 'success' })

    // H5 notification
    // #ifdef H5
    const reminderEnabled = uni.getStorageSync('studymate_reminder_enabled')
    if (reminderEnabled && 'Notification' in window && Notification.permission === 'granted') {
      new Notification('StudyMate - 番茄钟完成', {
        body: `已完成 ${sessionDuration} 分钟专注学习: ${taskName}`,
        tag: 'pomodoro-complete'
      })
    }
    // #endif

    // Start break (skip when break duration is 0)
    const breakSeconds = currentBreakSeconds.value
    if (breakSeconds > 0) {
      isBreak.value = true
      timeRemaining.value = breakSeconds
      isRunning.value = true
      timerInterval = setInterval(() => {
        timeRemaining.value--
        if (timeRemaining.value <= 0) {
          completeSession()
        }
      }, 1000)
    } else {
      // No break, reset to focus phase
      timeRemaining.value = currentFocusSeconds.value
    }
  } else {
    // Break phase complete
    isBreak.value = false
    timeRemaining.value = currentFocusSeconds.value
    uni.showToast({ title: '休息结束，继续加油！', icon: 'none' })
  }
}

function selectTask(task) {
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
    type: 'manual',
    taskName,
    time: timeStr,
    duration: mins,
    date: today.value
  })
  saveRecords()
  totalMinutes.value += mins
  manualMinutes.value = ''
  manualTaskName.value = ''
  uni.showToast({ title: '记录成功', icon: 'success' })
}

function editRecord(idx) {
  const record = todayRecords.value[idx]
  editingIndex.value = idx
  editDuration.value = String(record.duration)
  editTaskName.value = record.taskName
  showEditModal.value = true
}

function saveEdit() {
  const mins = parseInt(editDuration.value)
  if (!mins || mins <= 0) {
    uni.showToast({ title: '请输入有效分钟数', icon: 'none' })
    return
  }
  const taskName = editTaskName.value.trim() || '手动记录'
  const record = todayRecords.value[editingIndex.value]
  const oldDuration = record.duration
  record.duration = mins
  record.taskName = taskName
  totalMinutes.value = totalMinutes.value - oldDuration + mins
  saveRecords()
  showEditModal.value = false
  editingIndex.value = -1
  uni.showToast({ title: '保存成功', icon: 'success' })
}

function deleteRecord(idx) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这条记录吗？',
    success: (res) => {
      if (res.confirm) {
        const record = todayRecords.value[idx]
        totalMinutes.value -= record.duration
        todayRecords.value.splice(idx, 1)
        saveRecords()
        uni.showToast({ title: '删除成功', icon: 'success' })
      }
    }
  })
}

function saveRecords() {
  uni.setStorageSync('studymate_pomodoro_records', JSON.stringify(todayRecords.value))
}

function saveSettings() {
  uni.setStorageSync('studymate_pomodoro_settings', JSON.stringify({
    pomodoroMode: pomodoroMode.value,
    focusTime: focusTime.value,
    breakTime: breakTime.value
  }))
}

function goBack() {
  uni.navigateBack()
}

onMounted(() => {
  // Load settings from storage
  const saved = uni.getStorageSync('studymate_pomodoro_settings')
  if (saved) {
    try {
      const s = JSON.parse(saved)
      if (s.focusTime) focusTime.value = s.focusTime
      if (s.breakTime) breakTime.value = s.breakTime
      if (s.pomodoroMode) pomodoroMode.value = s.pomodoroMode
    } catch (e) { /* silent */ }
  }

  // Sync input fields
  focusTimeInput.value = String(focusTime.value)
  breakTimeInput.value = String(breakTime.value)

  // Receive URL params (jump from task-board)
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = currentPage?.options || (currentPage?.$page?.options) || {}
  if (options.taskContent) {
    taskContent.value = decodeURIComponent(options.taskContent)
    currentTaskName.value = taskContent.value
    // Force task mode when coming from task-board
    pomodoroMode.value = 'pomodoro'
  }
  if (options.taskId) {
    currentTaskId.value = options.taskId
  }

  // Load today records
  const allRecords = JSON.parse(uni.getStorageSync('studymate_pomodoro_records') || '[]')
  todayRecords.value = allRecords.filter(r => r.date === today.value)

  // Load today stats
  completedPomodoros.value = todayRecords.value.filter(r => r.type === 'focus').length
  totalMinutes.value = todayRecords.value.reduce((sum, r) => sum + (r.duration || 0), 0)

  // Init timer
  timeRemaining.value = currentFocusSeconds.value
})

onUnmounted(() => {
  saveSettings()
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40px 0 20px;
  .back-btn, .header-placeholder {
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }
  .back-btn {
    background: $bg2;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid $rule;
  }
  .back-icon { font-size: 20px; color: $ink; }
  .title { font-size: 20px; font-weight: 700; color: $ink; }
}

.mode-tabs {
  display: flex;
  background: $bg2;
  border-radius: 16px;
  padding: 6px;
  margin-bottom: 16px;
  border: 1px solid $rule;
  .mode-tab {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 10px;
    border-radius: 12px;
    transition: all 0.2s;
    .mode-tab-icon { font-size: 16px; }
    .mode-tab-text { font-size: 14px; color: $muted; font-weight: 500; }
    &.active {
      background: $accent;
      .mode-tab-text { color: #fff; }
    }
  }
}

.task-link-section, .settings-section, .stats-section, .history-section {
  background: $bg2;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid $rule;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: $ink;
  margin-bottom: 12px;
}

.task-select {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: $soft;
  border-radius: 12px;
  .task-select-left { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0; }
  .task-select-icon { font-size: 16px; }
  .task-select-label { font-size: 14px; color: $ink; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .task-select-arrow { font-size: 20px; color: $muted; }
}

.timer-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0 24px;
}

.timer-circle {
  width: 240px;
  height: 240px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  transition: background 0.3s;
}

.timer-inner {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: $bg2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  .timer-text { font-size: 48px; font-weight: 700; color: $ink; line-height: 1.1; }
  .timer-label { font-size: 14px; color: $muted; margin-top: 4px; }
  .task-label {
    font-size: 12px;
    color: $accent;
    margin-top: 6px;
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.timer-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.control-btn {
  padding: 12px 24px;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  &.reset-btn {
    background: $bg;
    color: $muted;
    border: 1px solid $rule;
  }
  &.start-btn {
    background: $accent;
    color: #fff;
    padding: 14px 40px;
    &.pause { background: #ef5350; }
  }
}

.time-setting {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid $rule;
  &:last-child { border-bottom: none; }
  .setting-label { font-size: 14px; color: $ink; font-weight: 500; }
  .setting-buttons {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .setting-btn {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: $soft;
    color: $accent;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 600;
    border: 1px solid $rule;
    &:active { transform: scale(0.92); background: $accent; color: #fff; }
  }
  .setting-unit { font-size: 12px; color: $muted; }
  .input-wrapper {
    width: 56px;
    padding: 6px 4px;
    border-radius: 10px;
    background: $bg;
    border: 1px solid $rule;
  }
  .setting-input {
    width: 100%;
    text-align: center;
    font-size: 16px;
    font-weight: 700;
    color: $ink;
  }
}

.stats-section {
  display: flex;
  align-items: center;
  justify-content: space-around;
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    .stat-value { font-size: 28px; font-weight: 700; color: $accent; }
    .stat-label { font-size: 12px; color: $muted; margin-top: 4px; }
  }
  .stat-divider { width: 1px; height: 40px; background: $rule; }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: $bg;
  border-radius: 12px;
  .history-icon { font-size: 20px; flex-shrink: 0; }
  .history-info { flex: 1; min-width: 0; }
  .history-top { display: flex; align-items: center; gap: 6px; }
  .history-type {
    font-size: 12px;
    color: $accent;
    background: $soft;
    padding: 2px 6px;
    border-radius: 6px;
    flex-shrink: 0;
  }
  .history-name {
    font-size: 14px;
    color: $ink;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .history-time { display: block; font-size: 11px; color: $muted; margin-top: 2px; }
  .history-duration { font-size: 14px; font-weight: 700; color: $accent; white-space: nowrap; }
  .history-actions { display: flex; flex-direction: column; gap: 4px; flex-shrink: 0; }
  .history-action-btn {
    font-size: 11px;
    color: $accent;
    padding: 2px 6px;
    background: $soft;
    border-radius: 4px;
    &.delete { color: #f44336; }
  }
}

.manual-row {
  display: flex;
  gap: 8px;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid $rule;
  .manual-input {
    padding: 10px 12px;
    border: 1px solid $rule;
    border-radius: 10px;
    background: $bg;
    font-size: 14px;
    color: $ink;
  }
  .manual-minutes { width: 90px; flex-shrink: 0; }
  .manual-task { flex: 1; min-width: 0; }
  .manual-submit {
    padding: 10px 16px;
    background: $accent;
    color: #fff;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    white-space: nowrap;
  }
}

.empty { text-align: center; padding: 20px; .empty-text { font-size: 13px; color: $muted; } }

/* Task Picker Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}
.modal-content {
  background: $bg2;
  border-radius: 24px 24px 0 0;
  width: 100%;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid $rule;
  .modal-title { font-size: 18px; font-weight: 700; color: $ink; }
  .modal-close { font-size: 20px; color: $muted; padding: 4px; }
}
.modal-body { padding: 16px 24px; flex: 1; overflow-y: auto; }
.picker-task {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid $rule;
  &:last-child { border-bottom: none; }
  .picker-task-info { flex: 1; min-width: 0; }
  .picker-task-name { display: block; font-size: 14px; color: $ink; }
  .picker-task-duration { display: block; font-size: 12px; color: $muted; margin-top: 4px; }
  .picker-check {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid $rule;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: transparent;
    &.checked { background: $accent; border-color: $accent; color: #fff; }
  }
}

.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid $rule; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: $accent; font-weight: 600; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; color: $muted; margin-bottom: 8px; }
.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid $rule;
  border-radius: 10px;
  background: $bg;
  color: $ink;
  font-size: 15px;
  box-sizing: border-box;
}

.bottom-space { height: 100px; }
</style>
