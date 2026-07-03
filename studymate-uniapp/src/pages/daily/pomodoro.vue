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
        <view class="ctrl-btn start" @click="toggleTimer" :class="{ pause: isRunning }">
          <text>{{ isRunning ? '⏸ 暂停' : '▶ 开始专注' }}</text>
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
          <view class="time-btn" @click="adjustFocusTime(-5)">−</view>
          <view class="time-input-wrap">
            <input class="time-input" type="number" v-model="focusTimeInput" @blur="onFocusTimeBlur" />
          </view>
          <text class="time-unit">分钟</text>
          <view class="time-btn" @click="adjustFocusTime(5)">+</view>
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
            <text class="record-icon">{{ record.type === 'focus' ? '🍅' : '✏️' }}</text>
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

const taskStore = useTaskStore()
const farmStore = useFarmStore()
const planStore = usePlanStore()

// --- Time settings ---
const focusTime = ref(25)
const breakTime = ref(5)
const focusTimeInput = ref('25')
const breakTimeInput = ref('5')

// --- Timer state ---
const isRunning = ref(false)
const isPaused = ref(false)
const isBreak = ref(false)
const timeRemaining = ref(25 * 60)
const completedPomodoros = ref(0)
const totalMinutes = ref(0)
const todayRecords = ref([])
let timerInterval = null

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
const currentTotalSeconds = computed(() => isBreak.value ? currentBreakSeconds.value : currentFocusSeconds.value)
const hasProgress = computed(() => timeRemaining.value < currentTotalSeconds.value)

const formattedTime = computed(() => {
  const t = Math.max(0, timeRemaining.value)
  const m = Math.floor(t / 60)
  const s = t % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const statusLabel = computed(() => {
  if (isBreak.value) return '休息中 ☕'
  if (isRunning.value) return '专注中 🔥'
  if (isPaused.value) return '已暂停'
  return '准备专注'
})

const circleStyle = computed(() => {
  const total = currentTotalSeconds.value
  const elapsed = Math.max(0, total - timeRemaining.value)
  const pct = total > 0 ? Math.min(100, (elapsed / total) * 100) : 0
  const deg = pct * 3.6
  return { background: `conic-gradient(${isBreak.value ? '#66bb6a' : '#ef5350'} ${deg}deg, #e8ece9 ${deg}deg)` }
})

watch(focusTime, v => { focusTimeInput.value = String(v) })
watch(breakTime, v => { breakTimeInput.value = String(v) })
watch([focusTime, breakTime], () => {
  uni.setStorageSync('studymate_pomodoro_settings', JSON.stringify({
    focusTime: focusTime.value, breakTime: breakTime.value
  }))
})

// --- Time adjust ---
function adjustFocusTime(d) {
  const n = focusTime.value + d
  if (n < 5 || n > 120) return
  focusTime.value = n
  if (!isRunning.value && !isBreak.value) timeRemaining.value = n * 60
}
function adjustBreakTime(d) {
  const n = breakTime.value + d
  if (n < 1 || n > 30) return
  breakTime.value = n
  if (!isRunning.value && isBreak.value) timeRemaining.value = n * 60
}
function onFocusTimeBlur() {
  let v = parseInt(focusTimeInput.value)
  if (isNaN(v)) v = focusTime.value
  v = Math.max(5, Math.min(120, v))
  focusTime.value = v
  focusTimeInput.value = String(v)
  if (!isRunning.value && !isBreak.value) timeRemaining.value = v * 60
}
function onBreakTimeBlur() {
  let v = parseInt(breakTimeInput.value)
  if (isNaN(v)) v = breakTime.value
  v = Math.max(1, Math.min(30, v))
  breakTime.value = v
  breakTimeInput.value = String(v)
  if (!isRunning.value && isBreak.value) timeRemaining.value = v * 60
}

// --- Timer ---
function resetTimer() {
  isRunning.value = false; isPaused.value = false; isBreak.value = false
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
  timeRemaining.value = currentFocusSeconds.value
}
function toggleTimer() {
  if (isRunning.value) {
    isRunning.value = false; isPaused.value = true
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
  } else {
    isRunning.value = true; isPaused.value = false
    timerInterval = setInterval(() => {
      timeRemaining.value--
      if (timeRemaining.value <= 0) completeSession()
    }, 1000)
  }
}

async function completeSession() {
  isRunning.value = false; isPaused.value = false
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null }

  if (!isBreak.value) {
    const dur = Math.round(currentFocusSeconds.value / 60)
    completedPomodoros.value++
    totalMinutes.value += dur

    const name = currentTaskName.value || '番茄钟专注'
    const now = new Date()
    const ts = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`

    todayRecords.value.unshift({ type: 'focus', taskName: name, time: ts, duration: dur, date: today.value })
    saveRecords()

    if (currentTaskId.value) {
      try {
        const t = taskStore.todayTasks.find(t => t.id === currentTaskId.value)
        if (t) await taskStore.updateTask(currentTaskId.value, { actual_duration: (t.actual_duration || 0) + dur })
      } catch (e) { /* */ }
    }

    if (planStore.currentPlan) {
      try {
        let subj = ''
        const t = taskStore.todayTasks.find(t => t.id === currentTaskId.value)
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
      '🎉 番茄钟完成',
      `已完成 ${dur} 分钟专注学习${currentTaskName.value ? '：' + currentTaskName.value : ''}，休息一下吧！`,
      true
    )

    const bs = currentBreakSeconds.value
    if (bs > 0) {
      isBreak.value = true; timeRemaining.value = bs; isRunning.value = true
      timerInterval = setInterval(() => { timeRemaining.value--; if (timeRemaining.value <= 0) completeSession() }, 1000)
    } else {
      timeRemaining.value = currentFocusSeconds.value
    }
  } else {
    isBreak.value = false
    timeRemaining.value = currentFocusSeconds.value
    notifyCompletion(
      '☕ 休息结束',
      '休息时间到了，继续专注学习吧！',
      false
    )
  }
}

// --- Tasks ---
function selectTask(t) {
  currentTaskId.value = t.id
  currentTaskName.value = `${t.subject}${t.chapter ? ' - ' + t.chapter : ''}: ${t.content}`
  showTaskPicker.value = false
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
  showEditModal.value = false; editingIndex.value = -1
  uni.showToast({ title: '保存成功', icon: 'success' })
}
function deleteRecord(i) {
  uni.showModal({
    title: '确认删除', content: '确定要删除这条记录吗？',
    success: res => {
      if (res.confirm) {
        totalMinutes.value -= todayRecords.value[i].duration
        todayRecords.value.splice(i, 1)
        saveRecords()
        uni.showToast({ title: '删除成功', icon: 'success' })
      }
    }
  })
}

function saveRecords() {
  uni.setStorageSync('studymate_pomodoro_records', JSON.stringify(todayRecords.value))
}

// --- Notification: sound + popup + vibration ---
function playCompletionSound(isFocusEnd) {
  // #ifdef H5
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) return
    const ctx = new AudioCtx()
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

function vibrateDevice() {
  // #ifdef APP-PLUS
  try { uni.vibrateLong() } catch (e) { /* ignore */ }
  // #endif
  // #ifdef MP
  try { uni.vibrateShort({ type: 'medium' }) } catch (e) { /* ignore */ }
  // #endif
}

function notifyCompletion(title, body, isFocusEnd) {
  // 1. 播放提示音
  playCompletionSound(isFocusEnd)
  // 2. 震动（手机端）
  vibrateDevice()
  // 3. 弹窗
  uni.showModal({
    title,
    content: body,
    showCancel: false,
    confirmText: '知道了'
  })
  // #ifdef H5
  // 4. 浏览器通知（后台时也能收到）
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, { body, tag: 'pomodoro-complete' })
  } else if ('Notification' in window && Notification.permission !== 'denied') {
    Notification.requestPermission().then(p => {
      if (p === 'granted') new Notification(title, { body, tag: 'pomodoro-complete' })
    })
  }
  // #endif
}

function goBack() { uni.navigateBack() }

onMounted(() => {
  const s = uni.getStorageSync('studymate_pomodoro_settings')
  if (s) {
    try {
      const p = JSON.parse(s)
      if (p.focusTime) focusTime.value = p.focusTime
      if (p.breakTime) breakTime.value = p.breakTime
    } catch (e) { /* */ }
  }
  focusTimeInput.value = String(focusTime.value)
  breakTimeInput.value = String(breakTime.value)

  const pages = getCurrentPages()
  const opts = pages[pages.length - 1]?.options || pages[pages.length - 1]?.$page?.options || {}
  if (opts.taskContent) currentTaskName.value = decodeURIComponent(opts.taskContent)
  if (opts.taskId) currentTaskId.value = opts.taskId

  const all = JSON.parse(uni.getStorageSync('studymate_pomodoro_records') || '[]')
  todayRecords.value = all.filter(r => r.date === today.value)
  completedPomodoros.value = todayRecords.value.filter(r => r.type === 'focus').length
  totalMinutes.value = todayRecords.value.reduce((s, r) => s + (r.duration || 0), 0)

  timeRemaining.value = currentFocusSeconds.value

  // #ifdef H5
  // 请求浏览器通知权限（用于页面后台时提醒）
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
  // #endif
})

onUnmounted(() => {
  uni.setStorageSync('studymate_pomodoro_settings', JSON.stringify({
    focusTime: focusTime.value, breakTime: breakTime.value
  }))
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
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
  &.start {
    background: $accent; color: #fff; box-shadow: 0 4px 16px rgba($accent,.3);
    &.pause { background: #ef5350; box-shadow: 0 4px 16px rgba(#ef5350,.3); }
  }
}

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
.act-edit { font-size: 11px; color: $accent; padding: 3px 7px; background: rgba($accent,.08); border-radius: 6px; }
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
  box-shadow: 0 3px 10px rgba($accent,.2);
  &:active { transform: scale(0.97); }
}

.bottom-space { height: 100px; }
</style>
