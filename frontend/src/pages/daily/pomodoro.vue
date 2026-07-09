<template>
  <view class="page">
    <!-- Header -->
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="title">番茄钟</text>
      <view class="header-placeholder"></view>
    </view>

    <!-- Task Link -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-title">📋 关联任务</text>
      </view>
      <view class="task-select" @click="showTaskPicker = true">
        <text class="task-select-label">{{ currentTaskName || '选择今日任务（可选）' }}</text>
        <text class="task-select-arrow">›</text>
      </view>
    </view>

    <!-- Timer Circle -->
    <view class="timer-section">
      <view class="timer-circle" :style="circleStyle">
        <view class="timer-inner">
          <text class="timer-text">{{ formattedTime }}</text>
          <text class="timer-status">{{ statusLabel }}</text>
          <text class="timer-task" v-if="currentTaskName">{{ currentTaskName }}</text>
        </view>
      </view>

      <view class="timer-controls">
        <view class="ctrl-btn reset" @click="resetTimer" v-if="isRunning || isPaused || hasProgress">
          <text>重置</text>
        </view>
        <view class="ctrl-btn complete" @click="completeSession(true)" v-if="timerMode === 'countup' && (isRunning || isPaused || hasProgress)">
          <text>✓ 完成</text>
        </view>
        <view class="ctrl-btn start" @click="toggleTimer" :class="{ pause: isRunning }">
          <text>{{ isRunning ? '⏸ 暂停' : '▶ 开始专注' }}</text>
        </view>
      </view>
    </view>

    <!-- Timer Mode -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-title">⏰ 计时模式</text>
      </view>
      <view class="mode-toggle">
        <view class="mode-btn" :class="{ active: timerMode === 'countdown' }" @click="switchMode('countdown')">
          <text class="mode-icon">⏳</text>
          <text class="mode-label">倒计时</text>
          <text class="mode-desc">设定时长，倒数完成</text>
        </view>
        <view class="mode-btn" :class="{ active: timerMode === 'countup' }" @click="switchMode('countup')">
          <text class="mode-icon">⏱</text>
          <text class="mode-label">正计时</text>
          <text class="mode-desc">自由计时，随时停止</text>
        </view>
      </view>
    </view>

    <!-- Time Settings -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-title">⏱ 时间设置</text>
      </view>
      <view class="time-row">
        <text class="time-label">专注时长</text>
        <view class="time-controls">
          <view class="time-btn" @click="adjustFocusTime(-1)">−</view>
          <view class="time-input-wrap">
            <input class="time-input" type="number" v-model="focusTimeInput" @blur="onFocusTimeBlur" />
          </view>
          <text class="time-unit">分钟</text>
          <view class="time-btn" @click="adjustFocusTime(1)">+</view>
        </view>
      </view>
      <view class="time-row">
        <text class="time-label">休息时长</text>
        <view class="time-controls">
          <view class="time-btn" @click="adjustBreakTime(-1)">−</view>
          <view class="time-input-wrap">
            <input class="time-input" type="number" v-model="breakTimeInput" @blur="onBreakTimeBlur" />
          </view>
          <text class="time-unit">分钟</text>
          <view class="time-btn" @click="adjustBreakTime(1)">+</view>
        </view>
      </view>
      <text class="time-hint">💡 专注时长以1分钟为刻度调整；休息时长设为0可跳过休息</text>
    </view>

    <!-- Stats -->
    <view class="stats-row">
      <view class="stat-item">
        <text class="stat-num">{{ completedPomodoros }}</text>
        <text class="stat-desc">今日番茄</text>
      </view>
      <view class="stat-item">
        <text class="stat-num">{{ totalMinutes }}</text>
        <text class="stat-desc">今日时长(分)</text>
      </view>
    </view>

    <!-- Today's Records -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-title">📝 今日番茄记录</text>
      </view>

      <view class="record-list" v-if="todayRecords.length > 0">
        <view class="record-item" v-for="(record, idx) in todayRecords" :key="idx">
          <view class="record-left">
            <text class="record-icon">{{ record.type === 'countup' ? '⏱' : (record.type === 'focus' ? '🍅' : '✏️') }}</text>
            <view class="record-info">
              <text class="record-name">{{ record.taskName }}</text>
              <text class="record-time">{{ record.time }}</text>
            </view>
          </view>
          <text class="record-dur">{{ record.duration }}分钟</text>
          <view class="record-actions">
            <text class="act-edit" @click="editRecord(idx)">编辑</text>
            <text class="act-del" @click="deleteRecord(idx)">删除</text>
          </view>
        </view>
      </view>
      <view class="empty" v-else>
        <text class="empty-text">暂无记录，开始专注吧 🍃</text>
      </view>

      <!-- Manual Add -->
      <view class="manual-row">
        <input class="manual-inp dur-inp" type="number" v-model="manualMinutes" placeholder="分钟" />
        <input class="manual-inp task-inp" type="text" v-model="manualTaskName" placeholder="任务描述" />
        <view class="manual-btn" @click="submitManualRecord">添加</view>
      </view>
    </view>

    <!-- Edit Modal -->
    <view class="modal-mask" v-if="showEditModal" @click="showEditModal = false">
      <view class="modal-sheet" @click.stop>
        <view class="modal-top">
          <text class="modal-title">编辑记录</text>
          <view class="modal-x" @click="showEditModal = false">✕</view>
        </view>
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">时长（分钟）</text>
            <input class="form-inp" type="number" v-model="editDuration" placeholder="请输入分钟数" />
          </view>
          <view class="form-group">
            <text class="form-label">任务描述</text>
            <input class="form-inp" type="text" v-model="editTaskName" placeholder="请输入任务描述" />
          </view>
        </view>
        <view class="modal-bot">
          <view class="btn-cancel" @click="showEditModal = false">取消</view>
          <view class="btn-submit" @click="saveEdit">保存</view>
        </view>
      </view>
    </view>

    <!-- Task Picker Modal -->
    <view class="modal-mask" v-if="showTaskPicker" @click="showTaskPicker = false">
      <view class="modal-sheet" @click.stop>
        <view class="modal-top">
          <text class="modal-title">选择今日任务</text>
          <view class="modal-x" @click="showTaskPicker = false">✕</view>
        </view>
        <view class="modal-body">
          <view class="picker-task" v-for="task in todayTasks" :key="task.id" @click="selectTask(task)">
            <view class="picker-info">
              <text class="picker-name">{{ task.subject }}{{ task.chapter ? ' - ' + task.chapter : '' }}: {{ task.content }}</text>
              <text class="picker-dur">预计: {{ task.duration }}分钟</text>
            </view>
            <view class="picker-check" :class="{ on: currentTaskId === task.id }">
              <text v-if="currentTaskId === task.id">✓</text>
            </view>
          </view>
          <view class="empty" v-if="todayTasks.length === 0">
            <text class="empty-text">暂无今日任务</text>
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
import { createFocusRecord, getFocusRecords, updateFocusRecord, deleteFocusRecord, createReflection } from '@/api/client'

const taskStore = useTaskStore()
const farmStore = useFarmStore()
const planStore = usePlanStore()

// --- Time settings ---
const timerMode = ref('countdown') // 'countdown' | 'countup'
const focusTime = ref(25)
const breakTime = ref(5)
const focusTimeInput = ref('25')
const breakTimeInput = ref('5')

// --- Timer state ---
const isRunning = ref(false)
const isPaused = ref(false)
const isBreak = ref(false)
const timeRemaining = ref(25 * 60)
const elapsedSeconds = ref(0) // 正计时模式下的已计时秒数
const completedPomodoros = ref(0)
const totalMinutes = ref(0)
const todayRecords = ref([])
let timerInterval = null

// --- 时间戳计时（后台也能准确计时，且离开后可恢复）---
// runningSession 是计时的事实来源；timeRemaining/elapsedSeconds 仅作显示，由 tick() 校准
const runningSession = ref(null)
// 结构: { mode, isBreak, focusSeconds, breakSeconds, startTimestamp, accumulatedElapsed, currentTaskId, currentTaskName, date }
// startTimestamp != null 表示正在运行；== null 表示已暂停（accumulatedElapsed 已累计）
const isCompleting = ref(false) // 防止 completeSession 重入
const POMODORO_SESSION_KEY = 'studymate_pomodoro_running'

function persistRunningSession() {
  if (!runningSession.value) {
    uni.removeStorageSync(POMODORO_SESSION_KEY)
    return
  }
  uni.setStorageSync(POMODORO_SESSION_KEY, JSON.stringify(runningSession.value))
}
function loadRunningSession() {
  try {
    const s = uni.getStorageSync(POMODORO_SESSION_KEY)
    if (s) return JSON.parse(s)
  } catch (e) { /* */ }
  return null
}
function clearRunningSession() {
  runningSession.value = null
  uni.removeStorageSync(POMODORO_SESSION_KEY)
}

// 每秒刷新显示；即便后台被节流，回到前台/visibilitychange 时也会用时间戳校准
function tick() {
  const rs = runningSession.value
  if (!rs || !rs.startTimestamp) return
  const now = Date.now()
  const segmentElapsed = (now - rs.startTimestamp) / 1000
  const totalElapsed = rs.accumulatedElapsed + segmentElapsed
  const targetSeconds = rs.isBreak ? rs.breakSeconds : rs.focusSeconds

  if (rs.mode === 'countup') {
    elapsedSeconds.value = Math.floor(totalElapsed)
  } else {
    const remaining = targetSeconds - totalElapsed
    if (remaining <= 0) {
      timeRemaining.value = 0
      // 自然结束（可能在后台）
      completeSession(false)
      return
    }
    timeRemaining.value = Math.ceil(remaining)
  }
}

function startInterval() {
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = setInterval(() => { tick() }, 1000)
}

function onVisibilityChange() {
  if (document.visibilityState === 'visible') {
    // 回到前台：用时间戳校准，若期间已结束则触发完成
    tick()
  }
}

function onWindowFocus() { tick() }

// --- Task association ---
const currentTaskId = ref(null)
const currentTaskName = ref('')
const showTaskPicker = ref(false)

// --- Manual record ---
const manualMinutes = ref('')
const manualTaskName = ref('')

// --- Edit ---
const showEditModal = ref(false)
const editingIndex = ref(-1)
const editDuration = ref('')
const editTaskName = ref('')

const today = computed(() => new Date().toISOString().split('T')[0])
const todayTasks = computed(() => taskStore.todayTasks || [])

const currentFocusSeconds = computed(() => focusTime.value * 60)
const currentBreakSeconds = computed(() => breakTime.value * 60)
// 运行中用会话快照的目标时长，避免运行中修改 focusTime 导致进度错乱
const currentTotalSeconds = computed(() => {
  const rs = runningSession.value
  if (rs) return rs.isBreak ? rs.breakSeconds : rs.focusSeconds
  return isBreak.value ? currentBreakSeconds.value : currentFocusSeconds.value
})
const hasProgress = computed(() => {
  if (timerMode.value === 'countup') return elapsedSeconds.value > 0
  return timeRemaining.value < currentTotalSeconds.value
})

const formattedTime = computed(() => {
  if (timerMode.value === 'countup') {
    // 正计时：显示已计时时间
    const t = elapsedSeconds.value
    const m = Math.floor(t / 60)
    const s = t % 60
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  } else {
    // 倒计时：显示剩余时间
    const t = Math.max(0, timeRemaining.value)
    const m = Math.floor(t / 60)
    const s = t % 60
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }
})

const statusLabel = computed(() => {
  if (isBreak.value) return '休息中 ☕'
  if (isRunning.value) return timerMode.value === 'countup' ? '计时中 🔥' : '专注中 🔥'
  if (isPaused.value) return '已暂停'
  return timerMode.value === 'countup' ? '准备计时' : '准备专注'
})

const circleStyle = computed(() => {
  if (timerMode.value === 'countup') {
    // 正计时：显示已计时的进度（以60分钟为最大值）
    const maxMinutes = 60
    const elapsedMinutes = elapsedSeconds.value / 60
    const pct = Math.min(100, (elapsedMinutes / maxMinutes) * 100)
    const deg = pct * 3.6
    return { background: `conic-gradient(#2f7d4f ${deg}deg, #e8ece9 ${deg}deg)` }
  } else {
    // 倒计时：显示剩余时间的进度
    const total = currentTotalSeconds.value
    const elapsed = Math.max(0, total - timeRemaining.value)
    const pct = total > 0 ? Math.min(100, (elapsed / total) * 100) : 0
    const deg = pct * 3.6
    return { background: `conic-gradient(${isBreak.value ? '#66bb6a' : '#ef5350'} ${deg}deg, #e8ece9 ${deg}deg)` }
  }
})

watch(focusTime, v => { focusTimeInput.value = String(v) })
watch(breakTime, v => { breakTimeInput.value = String(v) })
watch([focusTime, breakTime, timerMode], () => {
  uni.setStorageSync('studymate_pomodoro_settings', JSON.stringify({
    focusTime: focusTime.value, breakTime: breakTime.value, timerMode: timerMode.value
  }))
})

// --- Mode Switch ---
function switchMode(mode) {
  if (runningSession.value) {
    uni.showToast({ title: '计时进行中，无法切换模式', icon: 'none' })
    return
  }
  timerMode.value = mode
  if (mode === 'countup') {
    elapsedSeconds.value = 0
  } else {
    timeRemaining.value = currentFocusSeconds.value
  }
}

// --- Time adjust ---
function adjustFocusTime(d) {
  if (runningSession.value) { uni.showToast({ title: '计时中无法修改', icon: 'none' }); return }
  const n = focusTime.value + d
  if (n < 1 || n > 120) return
  focusTime.value = n
  if (!isRunning.value && !isBreak.value) timeRemaining.value = n * 60
}
function adjustBreakTime(d) {
  if (runningSession.value) { uni.showToast({ title: '计时中无法修改', icon: 'none' }); return }
  const n = breakTime.value + d
  if (n < 0 || n > 30) return
  breakTime.value = n
  if (!isRunning.value && isBreak.value) timeRemaining.value = n * 60
}
function onFocusTimeBlur() {
  let v = parseInt(focusTimeInput.value)
  if (isNaN(v)) v = focusTime.value
  v = Math.max(1, Math.min(120, v))
  focusTime.value = v
  focusTimeInput.value = String(v)
  if (!runningSession.value && !isRunning.value && !isBreak.value) timeRemaining.value = v * 60
}
function onBreakTimeBlur() {
  let v = parseInt(breakTimeInput.value)
  if (isNaN(v)) v = breakTime.value
  v = Math.max(0, Math.min(30, v))
  breakTime.value = v
  breakTimeInput.value = String(v)
  if (!runningSession.value && !isRunning.value && isBreak.value) timeRemaining.value = v * 60
}

// --- Timer ---
function resetTimer() {
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
  clearRunningSession()
  isRunning.value = false; isPaused.value = false; isBreak.value = false
  isCompleting.value = false
  if (timerMode.value === 'countup') {
    elapsedSeconds.value = 0
  } else {
    timeRemaining.value = currentFocusSeconds.value
  }
}

function toggleTimer() {
  if (isRunning.value) {
    // 暂停：把当前段已计时累加到 accumulatedElapsed，清空 startTimestamp
    const rs = runningSession.value
    if (rs && rs.startTimestamp) {
      rs.accumulatedElapsed += (Date.now() - rs.startTimestamp) / 1000
      rs.startTimestamp = null
      persistRunningSession()
      // 立即刷新显示（避免显示残留 1 秒误差）
      const target = rs.isBreak ? rs.breakSeconds : rs.focusSeconds
      if (rs.mode === 'countup') {
        elapsedSeconds.value = Math.floor(rs.accumulatedElapsed)
      } else {
        timeRemaining.value = Math.max(0, Math.ceil(target - rs.accumulatedElapsed))
      }
    }
    isRunning.value = false; isPaused.value = true
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
  } else {
    // 开始 或 继续
    if (!runningSession.value) {
      // 全新开始：记录绝对开始时间，快照目标时长
      runningSession.value = {
        mode: timerMode.value,
        isBreak: false,
        focusSeconds: focusTime.value * 60,
        breakSeconds: breakTime.value * 60,
        startTimestamp: Date.now(),
        accumulatedElapsed: 0,
        currentTaskId: currentTaskId.value,
        currentTaskName: currentTaskName.value,
        date: today.value
      }
    } else {
      // 从暂停继续
      runningSession.value.startTimestamp = Date.now()
    }
    persistRunningSession()
    isRunning.value = true; isPaused.value = false
    startInterval()
    tick()
  }
}

async function completeSession(isManual = false) {
  if (isCompleting.value) return
  const rs = runningSession.value
  if (!rs) return
  isCompleting.value = true
  try {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
    isRunning.value = false; isPaused.value = false

    // 用时间戳计算实际已计时长（后台也能准确）
    const now = Date.now()
    const segmentElapsed = rs.startTimestamp ? (now - rs.startTimestamp) / 1000 : 0
    const totalElapsed = rs.accumulatedElapsed + segmentElapsed
    const targetSeconds = rs.isBreak ? rs.breakSeconds : rs.focusSeconds

    if (rs.isBreak) {
      // 休息结束
      isBreak.value = false
      clearRunningSession()
      timeRemaining.value = currentFocusSeconds.value
      elapsedSeconds.value = 0
      notifyCompletion('☕ 休息结束', '休息时间到了，继续专注学习吧！', false)
      return
    }

    // 专注结束：计算时长
    let dur = 0
    if (rs.mode === 'countup') {
      dur = Math.round(totalElapsed / 60)
    } else {
      // 倒计时：自然结束用目标时长；手动提前结束用实际已计时长
      dur = isManual ? Math.max(0, Math.round(totalElapsed / 60)) : Math.round(targetSeconds / 60)
    }
    if (dur < 1 && totalElapsed >= 60) dur = 1

    if (dur > 0) {
      completedPomodoros.value++
      totalMinutes.value += dur

      const name = currentTaskName.value || (rs.mode === 'countup' ? '正计时专注' : '番茄钟专注')
      const nowDate = new Date()
      const ts = `${nowDate.getHours()}:${String(nowDate.getMinutes()).padStart(2, '0')}`

      todayRecords.value.unshift({ type: rs.mode === 'countup' ? 'countup' : 'focus', taskName: name, time: ts, duration: dur, date: today.value })
      saveRecords()

      if (planStore.currentPlan) {
        try {
          let subj = ''
          const t = taskStore.todayTasks.find(t => t.id === rs.currentTaskId)
          if (t) subj = t.subject
          else if (currentTaskName.value) subj = currentTaskName.value.split(':')[0].split(' - ')[0].trim()
          const endTime = nowDate.toISOString()
          const startTime = new Date(nowDate.getTime() - dur * 60 * 1000).toISOString()
          await createFocusRecord({
            plan_id: planStore.currentPlan.id,
            date: today.value,
            type: rs.mode === 'countup' ? 'countup' : 'focus',
            subject: subj,
            task_id: rs.currentTaskId || null,
            task_name: name,
            duration: dur,
            start_time: startTime,
            end_time: endTime
          })
        } catch (e) { console.warn('Sync focus record failed:', e) }
      }

      if (rs.currentTaskId) {
        try {
          const t = taskStore.todayTasks.find(t => t.id === rs.currentTaskId)
          if (t) {
            const newActual = (t.actual_duration || 0) + dur
            const updateData = { actual_duration: newActual }
            // 任务未设置开始时间时，用番茄钟自动填充
            if (!t.start_hour || (t.start_hour === 9 && !t.start_minute && !t.actual_duration)) {
              const start = new Date(new Date().getTime() - dur * 60 * 1000)
              updateData.start_hour = start.getHours()
              updateData.start_minute = start.getMinutes()
            }
            await taskStore.updateTask(rs.currentTaskId, updateData)
          }
          // 自动创建/更新任务反思记录（累加实际用时）
          if (planStore.currentPlan) {
            await createReflection({
              task_id: rs.currentTaskId,
              plan_id: planStore.currentPlan.id,
              task_date: today.value,
              actual_duration: dur,
              completion_issues: '',
              incomplete_reason: ''
            })
          }
        } catch (e) { /* */ }
      }

      if (planStore.currentPlan) {
        try {
          let subj = ''
          const t = taskStore.todayTasks.find(t => t.id === rs.currentTaskId)
          if (t) subj = t.subject
          else if (currentTaskName.value) subj = currentTaskName.value.split(':')[0].split(' - ')[0].trim()
          if (subj) {
            const crop = await farmStore.ensureCrop(planStore.currentPlan.id, subj)
            if (crop?.plant) await farmStore.waterPlant(crop.plant.id)
          }
        } catch (e) { /* */ }
      }

      uni.showToast({ title: `完成 ${dur} 分钟专注!`, icon: 'success' })
      notifyCompletion(
        '🎉 专注完成',
        `已完成 ${dur} 分钟专注学习${currentTaskName.value ? '：' + currentTaskName.value : ''}`,
        true
      )
    }

    // 倒计时模式：专注结束后自动进入休息阶段（建立新的会话段）
    if (rs.mode === 'countdown') {
      const bs = rs.breakSeconds
      if (bs > 0) {
        isBreak.value = true
        runningSession.value = {
          mode: 'countdown',
          isBreak: true,
          focusSeconds: rs.focusSeconds,
          breakSeconds: rs.breakSeconds,
          startTimestamp: Date.now(),
          accumulatedElapsed: 0,
          currentTaskId: rs.currentTaskId,
          currentTaskName: rs.currentTaskName,
          date: today.value
        }
        persistRunningSession()
        isRunning.value = true; isPaused.value = false
        startInterval()
        return // finally 会释放完成锁，让休息的 tick 正常工作
      }
    }

    // 正计时模式 或 倒计时无休息：彻底结束
    clearRunningSession()
    if (rs.mode === 'countup') {
      elapsedSeconds.value = 0
    } else {
      timeRemaining.value = currentFocusSeconds.value
    }
  } finally {
    isCompleting.value = false
  }
}

// --- Tasks ---
function selectTask(t) {
  currentTaskId.value = t.id
  currentTaskName.value = `${t.subject}${t.chapter ? ' - ' + t.chapter : ''}: ${t.content}`
  showTaskPicker.value = false
  // 若计时进行中，同步更新会话关联的任务
  if (runningSession.value) {
    runningSession.value.currentTaskId = currentTaskId.value
    runningSession.value.currentTaskName = currentTaskName.value
    persistRunningSession()
  }
}

// --- Manual record ---
function submitManualRecord() {
  const m = parseInt(manualMinutes.value)
  if (!m || m <= 0) { uni.showToast({ title: '请输入有效分钟数', icon: 'none' }); return }
  const name = manualTaskName.value.trim() || '手动记录'
  const now = new Date()
  const ts = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`
  todayRecords.value.unshift({ type: 'manual', taskName: name, time: ts, duration: m, date: today.value })
  saveRecords()
  totalMinutes.value += m
  manualMinutes.value = ''; manualTaskName.value = ''

  if (planStore.currentPlan) {
    try {
      const endTime = now.toISOString()
      const startTime = new Date(now.getTime() - m * 60 * 1000).toISOString()
      createFocusRecord({
        plan_id: planStore.currentPlan.id,
        date: today.value,
        type: 'manual',
        subject: '',
        task_name: name,
        duration: m,
        start_time: startTime,
        end_time: endTime
      })
    } catch (e) { console.warn('Sync manual record failed:', e) }
  }

  uni.showToast({ title: '记录成功', icon: 'success' })
}

// --- Edit / Delete ---
function editRecord(i) {
  const r = todayRecords.value[i]; editingIndex.value = i
  editDuration.value = String(r.duration); editTaskName.value = r.taskName
  showEditModal.value = true
}
function saveEdit() {
  const m = parseInt(editDuration.value)
  if (!m || m <= 0) { uni.showToast({ title: '请输入有效分钟数', icon: 'none' }); return }
  const name = editTaskName.value.trim() || '手动记录'
  const r = todayRecords.value[editingIndex.value]
  totalMinutes.value = totalMinutes.value - r.duration + m
  r.duration = m; r.taskName = name
  saveRecords()
  // Sync to backend if we have a focus record ID
  if (r._focusId) {
    updateFocusRecord(r._focusId, { duration: m, task_name: name }).catch(e => console.warn('Sync edit failed:', e))
  }
  showEditModal.value = false; editingIndex.value = -1
  uni.showToast({ title: '保存成功', icon: 'success' })
}
function deleteRecord(i) {
  uni.showModal({
    title: '确认删除', content: '确定要删除这条记录吗？',
    success: res => {
      if (res.confirm) {
        const r = todayRecords.value[i]
        totalMinutes.value -= r.duration
        todayRecords.value.splice(i, 1)
        saveRecords()
        // Sync to backend if we have a focus record ID
        if (r._focusId) {
          deleteFocusRecord(r._focusId).catch(e => console.warn('Sync delete failed:', e))
        }
        uni.showToast({ title: '删除成功', icon: 'success' })
      }
    }
  })
}

function saveRecords() {
  uni.setStorageSync('studymate_pomodoro_records', JSON.stringify(todayRecords.value))
  // 通知统计页面刷新数据
  uni.$emit('pomodoroRecordUpdated')
}

// --- Notification: sound + popup + vibration ---
// 全局复用的 AudioContext，便于在后台标签页恢复播放
let _audioCtx = null
function getAudioCtx() {
  // #ifdef H5
  try {
    if (!_audioCtx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext
      if (!AudioCtx) return null
      _audioCtx = new AudioCtx()
    }
    // 后台标签页 AudioContext 可能被挂起，尝试恢复
    if (_audioCtx.state === 'suspended') {
      _audioCtx.resume().catch(() => {})
    }
    return _audioCtx
  } catch (e) { return null }
  // #endif
  // #ifndef H5
  return null
  // #endif
}

function playCompletionSound(isFocusEnd) {
  // #ifdef H5
  try {
    const ctx = getAudioCtx()
    if (!ctx) return
    // Play 3 ascending beeps for focus end, 2 gentle beeps for break end
    const beeps = isFocusEnd ? [
      { freq: 523.25, time: 0, dur: 0.15 },   // C5
      { freq: 659.25, time: 0.18, dur: 0.15 }, // E5
      { freq: 783.99, time: 0.36, dur: 0.3 }   // G5
    ] : [
      { freq: 659.25, time: 0, dur: 0.2 },     // E5
      { freq: 523.25, time: 0.24, dur: 0.3 }   // C5
    ]
    beeps.forEach(b => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.type = 'sine'
      osc.frequency.value = b.freq
      gain.gain.setValueAtTime(0, ctx.currentTime + b.time)
      gain.gain.linearRampToValueAtTime(0.3, ctx.currentTime + b.time + 0.02)
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + b.time + b.dur)
      osc.start(ctx.currentTime + b.time)
      osc.stop(ctx.currentTime + b.time + b.dur)
    })
  } catch (e) { /* ignore */ }
  // #endif
  // #ifndef H5
  // App端：使用系统默认提示音
  try {
    const audio = uni.createInnerAudioContext()
    audio.src = isFocusEnd
      ? 'https://web.cdn.dcloud.net.cn/uni-app/static/notice.wav'
      : 'https://web.cdn.dcloud.net.cn/uni-app/static/notice.wav'
    audio.play()
    setTimeout(() => audio.destroy(), 3000)
  } catch (e) { /* ignore */ }
  // #endif
}

function vibrateDevice(type = 'focus') {
  // #ifdef H5
  // H5端（含手机浏览器）：使用 Vibration API
  try {
    if ('vibrate' in navigator) {
      // 专注结束：震动 200ms 停 100ms 再震动 200ms
      // 休息结束：单次震动 300ms
      const pattern = type === 'break' ? [300] : [200, 100, 200]
      navigator.vibrate(pattern)
    }
  } catch (e) { /* ignore */ }
  // #endif
  // #ifdef APP-PLUS
  try { uni.vibrateLong() } catch (e) { /* ignore */ }
  // #endif
  // #ifdef MP
  try { uni.vibrateShort({ type: 'medium' }) } catch (e) { /* ignore */ }
  // #endif
}

function notifyCompletion(title, body, isFocusEnd) {
  // 1. 播放提示音（所有平台）
  playCompletionSound(isFocusEnd)
  // 2. 震动（手机端）
  vibrateDevice(isFocusEnd ? 'focus' : 'break')
  // 3. 弹窗（所有平台都能看到）
  uni.showModal({
    title,
    content: body,
    showCancel: false,
    confirmText: '知道了'
  })
  // #ifdef H5
  // 4. 浏览器桌面通知（仅桌面端，iOS/部分移动端不支持）
  if ('Notification' in window && Notification.permission === 'granted') {
    try { new Notification(title, { body, tag: 'pomodoro-complete' }) } catch(e) { /* iOS等不支持 */ }
  }
  // #endif
}

function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    uni.switchTab({ url: '/pages/daily/task-board' })
  }
}

onMounted(async () => {
  const s = uni.getStorageSync('studymate_pomodoro_settings')
  if (s) {
    try {
      const p = JSON.parse(s)
      if (p.focusTime) focusTime.value = p.focusTime
      if (p.breakTime) breakTime.value = p.breakTime
      if (p.timerMode) timerMode.value = p.timerMode
    } catch (e) { /* */ }
  }
  focusTimeInput.value = String(focusTime.value)
  breakTimeInput.value = String(breakTime.value)

  const pages = getCurrentPages()
  const opts = pages[pages.length - 1]?.options || pages[pages.length - 1]?.$page?.options || {}
  if (opts.taskContent) currentTaskName.value = decodeURIComponent(opts.taskContent)
  if (opts.taskId) currentTaskId.value = opts.taskId

  // Load records from backend (primary) → fallback to localStorage (secondary)
  let allRecords = []
  try {
    if (planStore.currentPlan) {
      const res = await getFocusRecords(planStore.currentPlan.id, null, null, null)
      const serverRecords = Array.isArray(res) ? res : (res.records || [])
      // Convert FocusRecord to pomodoro record format
      allRecords = serverRecords.map(r => ({
        type: r.type || 'focus',
        taskName: r.task_name || '番茄钟专注',
        time: r.start_time ? r.start_time.split(' ')[1]?.substring(0,5) : '',
        duration: r.duration || 25,
        date: r.date,
        _focusId: r.id  // keep for edit/delete sync
      }))
      // Merge local records not yet synced (no _focusId)
      const localRecords = JSON.parse(uni.getStorageSync('studymate_pomodoro_records') || '[]')
      localRecords.forEach(lr => {
        if (!allRecords.find(sr => sr.date === lr.date && sr.taskName === lr.taskName && sr.duration === lr.duration)) {
          allRecords.unshift(lr)
        }
      })
    }
  } catch (e) {
    // Backend unavailable, use localStorage
    allRecords = JSON.parse(uni.getStorageSync('studymate_pomodoro_records') || '[]')
  }

  todayRecords.value = allRecords.filter(r => r.date === today.value)
  completedPomodoros.value = todayRecords.value.filter(r => r.type === 'focus').length
  totalMinutes.value = todayRecords.value.reduce((s, r) => s + (r.duration || 0), 0)
  // Save merged records back to localStorage
  uni.setStorageSync('studymate_pomodoro_records', JSON.stringify(allRecords))

  // 恢复未完成的番茄钟（退出页面/切换标签后再进入，计时不会丢失）
  const saved = loadRunningSession()
  if (saved) {
    if (saved.date !== today.value) {
      // 跨天了，旧的会话作废
      clearRunningSession()
      uni.showToast({ title: '上次的番茄钟已过期', icon: 'none' })
    } else {
      // 用会话快照同步设置
      if (saved.mode) timerMode.value = saved.mode
      if (saved.focusSeconds) focusTime.value = Math.round(saved.focusSeconds / 60)
      if (saved.breakSeconds != null) breakTime.value = Math.round(saved.breakSeconds / 60)
      focusTimeInput.value = String(focusTime.value)
      breakTimeInput.value = String(breakTime.value)
      currentTaskId.value = saved.currentTaskId || null
      currentTaskName.value = saved.currentTaskName || ''
      isBreak.value = !!saved.isBreak
      runningSession.value = saved

      const nowMs = Date.now()
      const seg = saved.startTimestamp ? (nowMs - saved.startTimestamp) / 1000 : 0
      const totalElapsed = (saved.accumulatedElapsed || 0) + seg
      const target = saved.isBreak ? saved.breakSeconds : saved.focusSeconds

      if (saved.startTimestamp) {
        // 离开时正在运行
        if (saved.mode === 'countdown' && totalElapsed >= target) {
          // 在后台已自然结束 → 询问是否记录
          uni.showModal({
            title: '番茄钟已完成',
            content: `上次的${saved.isBreak ? '休息' : '专注'}在后台已结束，是否记录本次专注？`,
            confirmText: '记录',
            cancelText: '放弃',
            success: res => {
              if (res.confirm) {
                completeSession(false)
              } else {
                clearRunningSession()
                isBreak.value = false
                timeRemaining.value = currentFocusSeconds.value
                elapsedSeconds.value = 0
              }
            }
          })
        } else {
          // 未结束，继续运行
          isRunning.value = true; isPaused.value = false
          startInterval()
          tick()
          uni.showToast({ title: '已恢复未完成的番茄钟', icon: 'none' })
        }
      } else {
        // 暂停状态
        isRunning.value = false; isPaused.value = true
        if (saved.mode === 'countup') {
          elapsedSeconds.value = Math.floor(saved.accumulatedElapsed || 0)
        } else {
          timeRemaining.value = Math.max(0, Math.ceil(target - (saved.accumulatedElapsed || 0)))
        }
        uni.showToast({ title: '已恢复暂停的番茄钟，点开始继续', icon: 'none' })
      }
    }
  } else {
    // 无未完成会话，按模式初始化显示
    if (timerMode.value === 'countup') {
      elapsedSeconds.value = 0
    } else {
      timeRemaining.value = currentFocusSeconds.value
    }
  }

  // #ifdef H5
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
  // 注册可见性监听，回到前台时用时间戳校准（修复后台计时不准/暂停问题）
  document.addEventListener('visibilitychange', onVisibilityChange)
  window.addEventListener('pageshow', onVisibilityChange)
  window.addEventListener('focus', onWindowFocus)
  // #endif
})

onUnmounted(() => {
  uni.setStorageSync('studymate_pomodoro_settings', JSON.stringify({
    focusTime: focusTime.value, breakTime: breakTime.value, timerMode: timerMode.value
  }))
  // 仅清理 interval；不清理 runningSession 持久化，让用户离开后仍可恢复
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
  // #ifdef H5
  document.removeEventListener('visibilitychange', onVisibilityChange)
  window.removeEventListener('pageshow', onVisibilityChange)
  window.removeEventListener('focus', onWindowFocus)
  // #endif
})
</script>

<style lang="scss" scoped>
/* ===== Header ===== */
.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 40px 0 20px;
}
.back-btn, .header-placeholder { width: 40px; height: 40px; border-radius: 50%; }
.back-btn {
  background: $bg2; display: flex; align-items: center; justify-content: center;
  border: 1px solid $rule;
  &:active { transform: scale(0.92); background: $soft; }
}
.back-icon { font-size: 20px; color: $ink; }
.title { font-size: 20px; font-weight: 700; color: $ink; }

/* ===== Section Card ===== */
.section-card {
  background: $bg2; border-radius: 18px; padding: 18px;
  margin-bottom: 14px; border: 1px solid $rule;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.section-title { font-size: 15px; font-weight: 700; color: $ink; }

/* ===== Task Link ===== */
.task-select {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; background: $bg; border-radius: 12px; border: 1px solid $rule;
  &:active { border-color: $accent; }
}
.task-select-label {
  font-size: 14px; color: $ink; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1;
}
.task-select-arrow { font-size: 22px; color: $muted; margin-left: 8px; }

/* ===== Timer ===== */
.timer-section {
  display: flex; flex-direction: column; align-items: center;
  padding: 10px 0 8px;
}
.timer-circle {
  width: 220px; height: 220px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 24px; transition: background 0.4s;
  box-shadow: 0 6px 24px rgba(0,0,0,0.06);
}
.timer-inner {
  width: 184px; height: 184px; border-radius: 50%; background: $bg2;
  display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
  box-shadow: inset 0 2px 6px rgba(0,0,0,0.03);
}
.timer-text { font-size: 44px; font-weight: 700; color: $ink; line-height: 1.1; font-variant-numeric: tabular-nums; }
.timer-status { font-size: 13px; color: $muted; margin-top: 4px; }
.timer-task {
  font-size: 11px; color: $accent; margin-top: 6px; max-width: 160px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 500;
}

.timer-controls { display: flex; gap: 14px; align-items: center; }
.ctrl-btn {
  padding: 12px 28px; border-radius: 28px; font-size: 15px; font-weight: 600;
  transition: all 0.15s;
  &:active { transform: scale(0.95); }
  &.reset { background: $bg; color: $muted; border: 1px solid $rule; }
  &.complete {
    background: $accent; color: #fff; box-shadow: 0 4px 16px rgba(47,125,79,0.3);
  }
  &.start {
    background: $accent; color: #fff; box-shadow: 0 4px 16px rgba(47,125,79,0.3);
    &.pause { background: #ef5350; box-shadow: 0 4px 16px rgba(#ef5350,.3); }
  }
}

/* ===== Timer Mode ===== */
.mode-toggle {
  display: flex; gap: 12px;
}
.mode-btn {
  flex: 1; padding: 14px; border-radius: 14px; background: $bg; border: 2px solid $rule;
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  transition: all 0.2s;
  &:active { transform: scale(0.97); }
  &.active {
    background: linear-gradient(135deg, rgba(47,125,79,0.08), rgba(47,125,79,0.15));
    border-color: $accent;
  }
}
.mode-icon { font-size: 24px; }
.mode-label { font-size: 14px; font-weight: 600; color: $ink; }
.mode-desc { font-size: 11px; color: $muted; }
.mode-btn.active .mode-label { color: $accent; }

/* ===== Time Settings ===== */
.time-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid $rule;
  &:last-child { border-bottom: none; padding-bottom: 0; }
}
.time-label { font-size: 14px; color: $ink; font-weight: 500; }
.time-controls { display: flex; align-items: center; gap: 8px; }
.time-btn {
  width: 38px; height: 38px; border-radius: 50%; background: $soft; color: $accent;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 600; border: 1px solid $rule;
  &:active { transform: scale(0.9); background: $accent; color: #fff; }
}
.time-unit { font-size: 12px; color: $muted; }
.time-hint { font-size: 11px; color: $muted; display: block; margin-top: 8px; }
.time-input-wrap {
  width: 50px; padding: 4px 2px; border-radius: 10px; background: $bg; border: 1px solid $rule;
  &:focus-within { border-color: $accent; }
}
.time-input {
  width: 100%; text-align: center; font-size: 16px; font-weight: 700; color: $ink;
  height: 32px; line-height: 32px;
}

/* ===== Stats ===== */
.stats-row {
  display: flex; gap: 12px; margin-bottom: 14px;
}
.stat-item {
  flex: 1; background: $bg2; border-radius: 16px; padding: 16px 12px;
  border: 1px solid $rule; display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.stat-num { font-size: 28px; font-weight: 700; color: $accent; line-height: 1.2; }
.stat-desc { font-size: 11px; color: $muted; margin-top: 4px; }

/* ===== Records ===== */
.record-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.record-item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; background: $bg; border-radius: 12px;
  &:active { background: $soft; }
}
.record-left { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0; }
.record-icon { font-size: 18px; flex-shrink: 0; }
.record-info { flex: 1; min-width: 0; }
.record-name { display: block; font-size: 13px; color: $ink; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.record-time { display: block; font-size: 11px; color: $muted; margin-top: 2px; }
.record-dur { font-size: 13px; font-weight: 700; color: $accent; flex-shrink: 0; }
.record-actions { display: flex; gap: 2px; flex-shrink: 0; }
.act-edit { font-size: 11px; color: $accent; padding: 3px 7px; background: rgba(47,125,79,0.08); border-radius: 6px; }
.act-del { font-size: 11px; color: #e53935; padding: 3px 7px; background: rgba(#e53935,.06); border-radius: 6px; }

/* ===== Manual Row ===== */
.manual-row {
  display: flex; gap: 8px; align-items: center; padding-top: 12px; border-top: 1px solid $rule;
}
.manual-inp {
  padding: 10px 12px; border: 1.5px solid $rule; border-radius: 10px;
  background: $bg; font-size: 13px; color: $ink; height: 40px; line-height: 20px;
  transition: border-color 0.2s;
  &:focus { border-color: $accent; }
}
.dur-inp { width: 72px; flex-shrink: 0; }
.task-inp { flex: 1; min-width: 0; }
.manual-btn {
  padding: 10px 16px; background: $accent; color: #fff; border-radius: 10px;
  font-size: 13px; font-weight: 700; white-space: nowrap;
  &:active { transform: scale(0.95); opacity: 0.9; }
}

/* ===== Empty ===== */
.empty { text-align: center; padding: 24px; }
.empty-text { font-size: 13px; color: $muted; }

/* ===== Modal ===== */
.modal-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 100;
  display: flex; align-items: flex-end;
}
.modal-sheet {
  background: $bg2; border-radius: 24px 24px 0 0; width: 100%; max-height: 60vh;
  display: flex; flex-direction: column;
  animation: up 0.25s ease;
}
@keyframes up { from { transform: translateY(100%); } to { transform: translateY(0); } }
.modal-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 22px; border-bottom: 1px solid $rule;
}
.modal-title { font-size: 17px; font-weight: 700; color: $ink; }
.modal-x {
  width: 30px; height: 30px; border-radius: 50%; background: $bg;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; color: $muted;
  &:active { background: $soft; }
}
.modal-body { padding: 16px 22px; flex: 1; overflow-y: auto; }
.modal-bot { display: flex; gap: 12px; padding: 16px 22px; border-top: 1px solid $rule; }

.picker-task {
  display: flex; justify-content: space-between; align-items: center;
  padding: 13px 0; border-bottom: 1px solid $rule;
  &:last-child { border-bottom: none; }
  &:active { opacity: 0.7; }
}
.picker-info { flex: 1; min-width: 0; }
.picker-name { display: block; font-size: 14px; color: $ink; font-weight: 500; }
.picker-dur { display: block; font-size: 11px; color: $muted; margin-top: 3px; }
.picker-check {
  width: 22px; height: 22px; border-radius: 50%; border: 2px solid $rule;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; color: transparent; flex-shrink: 0; margin-left: 12px;
  transition: all 0.2s;
  &.on { background: $accent; border-color: $accent; color: #fff; }
}

.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 13px; color: $muted; margin-bottom: 6px; font-weight: 500; }
.form-inp {
  width: 100%; padding: 12px 14px; border: 1.5px solid $rule; border-radius: 10px;
  background: $bg; color: $ink; font-size: 14px; box-sizing: border-box;
  height: 44px; line-height: 20px;
  transition: border-color 0.2s;
  &:focus { border-color: $accent; }
}

.btn-cancel {
  flex: 1; padding: 13px; text-align: center; border-radius: 12px;
  font-size: 15px; color: $muted; background: $bg; font-weight: 500;
  &:active { background: $soft; }
}
.btn-submit {
  flex: 2; padding: 13px; text-align: center; border-radius: 12px;
  font-size: 15px; color: #fff; background: $accent; font-weight: 700;
  box-shadow: 0 3px 10px rgba(47,125,79,0.2);
  &:active { transform: scale(0.97); }
}

.bottom-space { height: 100px; }
</style>
