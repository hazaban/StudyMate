<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">学习统计</text>
      <view class="placeholder"></view>
    </view>

    <!-- Time Range Tabs -->
    <view class="time-tabs">
      <view class="time-tab" :class="{ active: timeRange === 'today' }" @click="timeRange = 'today'">
        <text class="tab-text">今日</text>
      </view>
      <view class="time-tab" :class="{ active: timeRange === 'week' }" @click="timeRange = 'week'">
        <text class="tab-text">本周</text>
      </view>
      <view class="time-tab" :class="{ active: timeRange === 'month' }" @click="timeRange = 'month'">
        <text class="tab-text">本月</text>
      </view>
      <view class="time-tab" :class="{ active: timeRange === 'all' }" @click="timeRange = 'all'">
        <text class="tab-text">全部</text>
      </view>
    </view>

    <!-- Overview Cards -->
    <view class="stats-overview">
      <view class="stat-card">
        <text class="stat-icon">⏱</text>
        <view class="stat-content">
          <text class="stat-value">{{ statsData.totalMinutes }}</text>
          <text class="stat-label">专注分钟</text>
        </view>
      </view>
      <view class="stat-card">
        <text class="stat-icon">🍅</text>
        <view class="stat-content">
          <text class="stat-value">{{ statsData.totalPomodoros }}</text>
          <text class="stat-label">完成番茄</text>
        </view>
      </view>
      <view class="stat-card">
        <text class="stat-icon">📝</text>
        <view class="stat-content">
          <text class="stat-value">{{ statsData.recordCount }}</text>
          <text class="stat-label">专注记录</text>
        </view>
      </view>
      <view class="stat-card">
        <text class="stat-icon">📊</text>
        <view class="stat-content">
          <text class="stat-value">{{ statsData.avgMinutes }}</text>
          <text class="stat-label">平均时长(分)</text>
        </view>
      </view>
    </view>

    <!-- Pie Chart: 任务时间分布 -->
    <view class="chart-section" v-if="taskDistribution.length > 0">
      <text class="section-title">🍩 任务时间分布</text>
      <view class="pie-chart-area">
        <!-- Simple CSS donut chart -->
        <view class="donut-container">
          <svg viewBox="0 0 200 200" class="donut-svg">
            <circle cx="100" cy="100" r="80" fill="none" stroke="#f0f0f0" stroke-width="28" />
            <circle
              v-for="(seg, idx) in donutSegments"
              :key="idx"
              cx="100" cy="100" r="80"
              fill="none"
              :stroke="seg.color"
              stroke-width="28"
              :stroke-dasharray="`${seg.percent * 5.027} ${502.7 - seg.percent * 5.027}`"
              :stroke-dashoffset="seg.offset * 5.027"
              transform="rotate(-90, 100, 100)"
            />
          </svg>
          <view class="donut-center">
            <text class="donut-total">{{ statsData.totalMinutes }}分</text>
          </view>
        </view>
        <!-- Legend -->
        <view class="pie-legend">
          <view class="legend-item" v-for="(item, idx) in taskDistribution" :key="idx">
            <view class="legend-dot" :style="{ background: item.color }"></view>
            <text class="legend-name">{{ item.name }}</text>
            <text class="legend-value">{{ item.minutes }}分 ({{ item.percent }}%)</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Subject Distribution (Progress Bars) -->
    <view class="chart-section" v-if="subjectDistribution.length > 0">
      <text class="section-title">📚 科目分布</text>
      <view class="subject-list">
        <view class="subject-item" v-for="(item, idx) in subjectDistribution" :key="idx">
          <view class="subject-header">
            <text class="subject-name">{{ item.name }}</text>
            <text class="subject-value">{{ item.minutes }}分钟 · {{ item.percent }}%</text>
          </view>
          <view class="subject-progress-bar">
            <view
              class="subject-progress-fill"
              :style="{ width: item.percent + '%', background: item.color }"
            ></view>
          </view>
          <text class="subject-count">{{ item.count }}次专注</text>
        </view>
      </view>
    </view>

    <!-- Daily Trend Bars -->
    <view class="chart-section">
      <text class="section-title">📈 每日学习趋势</text>
      <view class="bar-chart" v-if="dailyTrend.length > 0">
        <view class="chart-y-axis">
          <text class="y-label" v-for="v in yAxisLabels" :key="v">{{ v }}</text>
        </view>
        <view class="chart-bars-area">
          <view class="bar-item" v-for="(day, idx) in dailyTrend" :key="idx">
            <view class="bar-wrapper">
              <view
                class="bar-fill"
                :style="{ height: (day.minutes / yMax * 100) + '%' }"
              ></view>
            </view>
            <text class="bar-label">{{ day.label }}</text>
            <text class="bar-value">{{ day.minutes }}分</text>
          </view>
        </view>
      </view>
      <view class="empty-chart" v-else>
        <text class="empty-text">暂无数据</text>
      </view>
    </view>

    <!-- Recent Records -->
    <view class="chart-section" v-if="recentRecords.length > 0">
      <text class="section-title">📋 最近记录</text>
      <view class="record-list">
        <view class="record-item" v-for="(r, idx) in recentRecords" :key="idx">
          <text class="record-date">{{ r.date }}</text>
          <view class="record-info">
            <text class="record-task">{{ r.taskName }}</text>
            <text class="record-detail">第{{ r.sessionCount }}次 · {{ r.minutes }}分</text>
          </view>
          <text class="record-time">{{ r.time }}</text>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { usePlanStore } from '@/stores/plan'
import { useTaskStore } from '@/stores/task'

const userStore = useUserStore()
const planStore = usePlanStore()
const taskStore = useTaskStore()

const timeRange = ref('today')
const refreshKey = ref(0)

const COLORS = ['#ef5350', '#5c6bc0', '#66bb6a', '#ffb74d', '#ab47bc', '#26c6da', '#ec407a', '#8d6e63']

// ── Stats computation from real storage ──
const statsData = computed(() => {
  const records = getFilteredRecords()
  const totalMinutes = records.reduce((s, r) => s + r.duration, 0)
  const pomodoroRecords = records.filter(r => r.type === 'focus')
  return {
    totalMinutes,
    totalPomodoros: pomodoroRecords.length,
    recordCount: records.length,
    avgMinutes: records.length > 0 ? Math.round(totalMinutes / records.length) : 0
  }
})

// ── Task distribution for donut chart ──
const taskDistribution = computed(() => {
  const records = getFilteredRecords()
  if (records.length === 0) return []
  const map = {}
  records.forEach(r => {
    const key = r.taskName || '未命名任务'
    if (!map[key]) map[key] = 0
    map[key] += r.duration
  })
  const total = Object.values(map).reduce((s, v) => s + v, 0)
  return Object.entries(map)
    .map(([name, minutes], i) => ({
      name,
      minutes,
      percent: Math.round(minutes / total * 100),
      color: COLORS[i % COLORS.length]
    }))
    .sort((a, b) => b.minutes - a.minutes)
    .slice(0, 8)
})

const donutSegments = computed(() => {
  let cumulative = 0
  return taskDistribution.value.map((item, i) => {
    const seg = { ...item, offset: cumulative }
    cumulative += item.percent
    return seg
  })
})

// ── Subject distribution ──
const subjectDistribution = computed(() => {
  const records = getFilteredRecords()
  if (records.length === 0) return []
  const map = {}
  records.forEach(r => {
    // Extract subject from task name (e.g., "数学 - 第三章: 做习题" -> "数学")
    const subject = extractSubject(r.taskName)
    if (!map[subject]) map[subject] = { minutes: 0, count: 0 }
    map[subject].minutes += r.duration
    map[subject].count++
  })
  const total = Object.values(map).reduce((s, v) => s + v.minutes, 0)
  return Object.entries(map)
    .map(([name, data], i) => ({
      name,
      minutes: data.minutes,
      count: data.count,
      percent: Math.round(data.minutes / total * 100),
      color: COLORS[i % COLORS.length]
    }))
    .sort((a, b) => b.minutes - a.minutes)
})

// ── Daily trend ──
const dailyTrend = computed(() => {
  const records = getFilteredRecords()
  const today = new Date()
  const days = []
  const count = timeRange.value === 'today' ? 1 : timeRange.value === 'week' ? 7 : 30
  for (let i = count - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().split('T')[0]
    const dayRecords = records.filter(r => r.date === dateStr)
    const minutes = dayRecords.reduce((s, r) => s + r.duration, 0)
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    days.push({
      label: `${d.getMonth() + 1}/${d.getDate()}`,
      weekday: weekdays[d.getDay()],
      date: dateStr,
      minutes
    })
  }
  return days
})

const yMax = computed(() => {
  const max = Math.max(...dailyTrend.value.map(d => d.minutes), 1)
  return Math.ceil(max / 60) * 60 || 60
})

const yAxisLabels = computed(() => {
  const steps = 4
  const max = yMax.value
  const step = Math.ceil(max / steps)
  const labels = []
  for (let i = steps; i >= 0; i--) {
    labels.push(i * step)
  }
  return labels
})

const recentRecords = computed(() => {
  const records = getFilteredRecords()
  // Group by date+taskName
  const grouped = {}
  records.forEach(r => {
    const key = `${r.date}|${r.taskName}`
    if (!grouped[key]) {
      grouped[key] = { ...r, sessionCount: 0, totalMinutes: 0 }
    }
    grouped[key].sessionCount++
    grouped[key].totalMinutes += r.duration
  })
  return Object.values(grouped)
    .map(g => ({ ...g, minutes: g.totalMinutes }))
    .sort((a, b) => {
      if (a.date !== b.date) return b.date.localeCompare(a.date)
      return b.totalMinutes - a.totalMinutes
    })
    .slice(0, 15)
})

// ── Helpers ──
function getFilteredRecords() {
  // refreshKey 依赖确保数据刷新
  void refreshKey.value
  const all = JSON.parse(uni.getStorageSync('studymate_pomodoro_records') || '[]')
  const today = new Date().toISOString().split('T')[0]

  if (timeRange.value === 'today') {
    return all.filter(r => r.date === today)
  }
  if (timeRange.value === 'week') {
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    const cutoff = weekAgo.toISOString().split('T')[0]
    return all.filter(r => r.date >= cutoff)
  }
  if (timeRange.value === 'month') {
    const monthAgo = new Date()
    monthAgo.setDate(monthAgo.getDate() - 30)
    const cutoff = monthAgo.toISOString().split('T')[0]
    return all.filter(r => r.date >= cutoff)
  }
  return all
}

function extractSubject(taskName) {
  if (!taskName) return '其他'
  // Try "科目 - xxx" or "科目: xxx" pattern
  const dashIdx = taskName.indexOf(' - ')
  const colonIdx = taskName.indexOf(': ')
  if (dashIdx > 0) return taskName.substring(0, dashIdx)
  if (colonIdx > 0) return taskName.substring(0, colonIdx)
  // Try predefined subjects
  const known = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']
  for (const s of known) {
    if (taskName.includes(s)) return s
  }
  return '其他'
}

function goBack() {
  uni.navigateBack()
}

onMounted(() => {
  // 如果没有番茄钟记录，生成模拟种子数据用于展示统计效果
  const existing = uni.getStorageSync('studymate_pomodoro_records')
  if (!existing || existing === '[]') {
    generateSeedRecords()
  }

  // 监听番茄钟记录更新事件
  uni.$on('pomodoroRecordUpdated', () => {
    refreshKey.value++
  })
})

// 页面每次显示时刷新数据（从番茄钟页面返回时触发）
onShow(() => {
  refreshKey.value++
})

onUnmounted(() => {
  uni.$off('pomodoroRecordUpdated')
})

// 生成模拟番茄钟记录数据（30天）
function generateSeedRecords() {
  const subjects = [
    { name: '数据结构', chapters: ['二叉树遍历', '哈希表', '排序算法', '图论', 'BST操作'] },
    { name: '操作系统', chapters: ['进程管理', '内存管理', 'PV操作', '死锁', '文件系统'] },
    { name: '计算机网络', chapters: ['TCP/IP', 'OSI模型', '子网划分', 'HTTP协议'] },
    { name: '英语', chapters: ['词汇Unit5', '阅读理解', '长难句分析', '写作练习'] },
    { name: '政治', chapters: ['马原', '毛中特', '史纲', '时政'] }
  ]
  const records = []
  const today = new Date()

  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().split('T')[0]
    const weekday = d.getDay()

    // 周末学习时间多一些，工作日少一些
    const sessionsPerDay = weekday === 0 || weekday === 6
      ? Math.floor(Math.random() * 4) + 3  // 3-6次
      : Math.floor(Math.random() * 3) + 2  // 2-4次

    for (let j = 0; j < sessionsPerDay; j++) {
      const subj = subjects[Math.floor(Math.random() * subjects.length)]
      const chapter = subj.chapters[Math.floor(Math.random() * subj.chapters.length)]
      const duration = [25, 25, 25, 50, 50][Math.floor(Math.random() * 5)]
      const hour = 8 + j * 2 + Math.floor(Math.random() * 2)
      const minute = Math.floor(Math.random() * 60)
      const ts = `${hour}:${String(minute).padStart(2, '0')}`

      records.push({
        type: 'focus',
        taskName: `${subj.name} - ${chapter}`,
        time: ts,
        duration,
        date: dateStr
      })
    }
  }

  uni.setStorageSync('studymate_pomodoro_records', JSON.stringify(records))
}
</script>

<style lang="scss" scoped>
.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 60px 20px 20px;
  .back-btn { width: 40px; height: 40px; background: $bg2; border-radius: 50%; display: flex; align-items: center; justify-content: center; .back-icon { font-size: 20px; color: $ink; } }
  .page-title { font-size: 20px; font-weight: 600; color: $ink; }
  .placeholder { width: 40px; }
}

.time-tabs {
  display: flex; background: $bg2; border-radius: 12px; padding: 4px;
  margin-bottom: 16px; border: 1px solid $rule;
}
.time-tab {
  flex: 1; padding: 10px; border-radius: 8px; text-align: center;
  &.active { background: $accent; .tab-text { color: #fff; } }
  .tab-text { font-size: 14px; color: $muted; }
}

/* Overview */
.stats-overview {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px;
}
.stat-card {
  background: $bg2; border-radius: 14px; padding: 16px;
  display: flex; align-items: center; gap: 12px; border: 1px solid $rule;
  .stat-icon { font-size: 26px; }
  .stat-content { .stat-value { display: block; font-size: 22px; font-weight: 700; color: $accent; } .stat-label { font-size: 11px; color: $muted; } }
}

/* Chart Sections */
.chart-section {
  background: $bg2; border-radius: 16px; padding: 18px;
  margin-bottom: 16px; border: 1px solid $rule;
}
.section-title {
  display: block; font-size: 16px; font-weight: 600; color: $ink; margin-bottom: 16px;
}

/* Donut Chart */
.pie-chart-area { display: flex; align-items: flex-start; gap: 20px; }
.donut-container { position: relative; width: 140px; height: 140px; flex-shrink: 0; }
.donut-svg { width: 100%; height: 100%; }
.donut-center {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;
  .donut-total { font-size: 16px; font-weight: 700; color: $ink; }
}
.pie-legend { flex: 1; display: flex; flex-direction: column; gap: 8px; padding-top: 4px; }
.legend-item { display: flex; align-items: center; gap: 8px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-name { font-size: 12px; color: $ink; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.legend-value { font-size: 11px; color: $muted; white-space: nowrap; }

/* Subject */
.subject-list { display: flex; flex-direction: column; gap: 14px; }
.subject-item {
  .subject-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
  .subject-name { font-size: 13px; color: $ink; font-weight: 500; }
  .subject-value { font-size: 12px; color: $muted; }
  .subject-progress-bar { height: 8px; background: $soft; border-radius: 4px; overflow: hidden; }
  .subject-progress-fill { height: 100%; border-radius: 4px; transition: width 0.4s ease; }
  .subject-count { font-size: 11px; color: $muted; margin-top: 4px; display: block; }
}

/* Bar Chart */
.bar-chart { display: flex; height: 140px; }
.chart-y-axis {
  display: flex; flex-direction: column; justify-content: space-between;
  padding-right: 8px; flex-shrink: 0;
  .y-label { font-size: 10px; color: $muted; }
}
.chart-bars-area {
  flex: 1; display: flex; justify-content: space-around; align-items: flex-end;
  border-left: 1px solid $rule; border-bottom: 1px solid $rule; padding-left: 8px;
}
.bar-item { display: flex; flex-direction: column; align-items: center; min-width: 28px; }
.bar-wrapper { width: 22px; height: 100px; display: flex; align-items: flex-end; }
.bar-fill {
  width: 100%; background: linear-gradient(180deg, $accent 0%, lighten($accent, 15%) 100%);
  border-radius: 4px 4px 0 0; min-height: 2px; transition: height 0.3s ease;
}
.bar-label { font-size: 10px; color: $muted; margin-top: 4px; }
.bar-value { font-size: 9px; color: $muted; }

.empty-chart { text-align: center; padding: 30px 0; .empty-text { font-size: 13px; color: $muted; } }

/* Recent Records */
.record-list { display: flex; flex-direction: column; gap: 8px; }
.record-item {
  display: flex; align-items: center; gap: 10px; padding: 8px 0;
  border-bottom: 1px solid $rule; &:last-child { border-bottom: none; }
  .record-date { font-size: 11px; color: $muted; white-space: nowrap; }
  .record-info { flex: 1; min-width: 0; }
  .record-task { font-size: 13px; color: $ink; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; }
  .record-detail { font-size: 11px; color: $muted; }
  .record-time { font-size: 13px; font-weight: 600; color: $accent; white-space: nowrap; }
}

.bottom-space { height: 80px; }
</style>
