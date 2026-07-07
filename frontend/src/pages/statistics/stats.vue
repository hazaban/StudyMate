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
      <view class="time-tab custom-tab" :class="{ active: timeRange === 'custom' }" @click="openDateRange">
        <text class="tab-text">自定义</text>
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

    <!-- Trend Chart -->
    <view class="chart-section">
      <view class="section-header">
        <text class="section-title">{{ trendTitle }}</text>
        <text class="range-hint" v-if="timeRange === 'custom'">{{ customStart }} ~ {{ customEnd }}</text>
      </view>
      <view class="bar-chart" v-if="trendData.length > 0">
        <view class="chart-y-axis">
          <text class="y-label" v-for="v in yAxisLabels" :key="v">{{ v }}</text>
        </view>
        <scroll-view scroll-x class="chart-scroll" v-if="trendData.length > 7">
          <view class="chart-bars-area scrollable">
            <view class="bar-item" v-for="(item, idx) in trendData" :key="idx">
              <view class="bar-wrapper">
                <view
                  class="bar-fill"
                  :style="{ height: (item.minutes / yMax * 100) + '%' }"
                ></view>
              </view>
              <text class="bar-label">{{ item.label }}</text>
              <text class="bar-value">{{ item.minutes }}分</text>
            </view>
          </view>
        </scroll-view>
        <view class="chart-bars-area" v-else>
          <view class="bar-item" v-for="(item, idx) in trendData" :key="idx">
            <view class="bar-wrapper">
              <view
                class="bar-fill"
                :style="{ height: (item.minutes / yMax * 100) + '%' }"
              ></view>
            </view>
            <text class="bar-label">{{ item.label }}</text>
            <text class="bar-value">{{ item.minutes }}分</text>
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
            <text class="record-task">{{ r.task_name }}</text>
            <text class="record-detail">{{ r.subject || '' }}</text>
          </view>
          <text class="record-time">{{ r.duration }}分</text>
        </view>
      </view>
    </view>

    <!-- Date Range Picker Modal -->
    <view class="modal-overlay" v-if="showDatePicker" @click="closeDatePicker">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">选择统计日期范围</text>
          <view class="modal-close" @click="closeDatePicker">✕</view>
        </view>
        <view class="modal-body">
          <view class="date-picker-row">
            <view class="date-picker-item" @click="showStartPicker = true">
              <text class="date-picker-label">开始日期</text>
              <text class="date-picker-value">{{ customStart }}</text>
            </view>
            <text class="date-picker-sep">至</text>
            <view class="date-picker-item" @click="showEndPicker = true">
              <text class="date-picker-label">结束日期</text>
              <text class="date-picker-value">{{ customEnd }}</text>
            </view>
          </view>
          <picker mode="date" :value="customStart" :end="todayStr" @change="onStartChange">
            <view class="hidden-picker"></view>
          </picker>
          <picker mode="date" :value="customEnd" :end="todayStr" @change="onEndChange">
            <view class="hidden-picker"></view>
          </picker>
          <view class="quick-select-row">
            <view class="quick-btn" @click="setQuickRange(7)">近7天</view>
            <view class="quick-btn" @click="setQuickRange(14)">近14天</view>
            <view class="quick-btn" @click="setQuickRange(30)">近30天</view>
            <view class="quick-btn" @click="setQuickRange(90)">近90天</view>
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="closeDatePicker">取消</view>
          <view class="submit-btn" @click="confirmDateRange">确认查看</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { usePlanStore } from '@/stores/plan'
import {
  getFocusStats,
  getFocusSubjectStats,
  getFocusDailyStats,
  getFocusWeeklyStats,
  getFocusMonthlyStats,
  getFocusRecords
} from '@/api/client'

const planStore = usePlanStore()

const timeRange = ref('month')
const loading = ref(false)

const overviewStats = ref({ total_minutes: 0, total_sessions: 0, avg_minutes: 0 })
const subjectStats = ref([])
const dailyStats = ref([])
const weeklyStats = ref([])
const monthlyStats = ref([])
const recentRecords = ref([])

const showDatePicker = ref(false)
const showStartPicker = ref(false)
const showEndPicker = ref(false)
const customStart = ref('')
const customEnd = ref('')

const todayStr = computed(() => new Date().toISOString().split('T')[0])

const COLORS = ['#ef5350', '#5c6bc0', '#66bb6a', '#ffb74d', '#ab47bc', '#26c6da', '#ec407a', '#8d6e63']

const statsData = computed(() => ({
  totalMinutes: overviewStats.value.total_minutes,
  totalPomodoros: overviewStats.value.total_sessions,
  recordCount: overviewStats.value.total_sessions,
  avgMinutes: overviewStats.value.avg_minutes
}))

const subjectDistribution = computed(() => {
  if (subjectStats.value.length === 0) return []
  const total = subjectStats.value.reduce((s, v) => s + v.minutes, 0) || 1
  return subjectStats.value
    .map((item, i) => ({
      name: item.subject,
      minutes: item.minutes,
      count: item.sessions,
      percent: Math.round(item.minutes / total * 100),
      color: COLORS[i % COLORS.length]
    }))
    .sort((a, b) => b.minutes - a.minutes)
})

const taskDistribution = computed(() => {
  if (recentRecords.value.length === 0) return []
  const map = {}
  recentRecords.value.forEach(r => {
    const key = r.task_name || '未命名任务'
    if (!map[key]) map[key] = 0
    map[key] += r.duration
  })
  const total = Object.values(map).reduce((s, v) => s + v, 0) || 1
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
  return taskDistribution.value.map((item) => {
    const seg = { ...item, offset: cumulative }
    cumulative += item.percent
    return seg
  })
})

const trendTitle = computed(() => {
  const map = {
    today: '📈 今日学习趋势',
    week: '📈 本周每日学习趋势',
    month: '📊 本月每周学习趋势',
    all: '📊 全部每月学习趋势',
    custom: '📈 学习趋势'
  }
  return map[timeRange.value] || '📈 学习趋势'
})

const trendData = computed(() => {
  if (timeRange.value === 'today') {
    if (dailyStats.value.length === 0) return []
    return dailyStats.value.map(d => ({
      label: '今日',
      minutes: d.minutes,
      sessions: d.sessions
    }))
  }
  if (timeRange.value === 'week') {
    if (dailyStats.value.length === 0) return []
    return dailyStats.value.map(d => {
      const date = new Date(d.date)
      const days = ['日', '一', '二', '三', '四', '五', '六']
      return {
        label: `周${days[date.getDay()]}`,
        minutes: d.minutes,
        sessions: d.sessions
      }
    })
  }
  if (timeRange.value === 'month') {
    if (weeklyStats.value.length === 0) return []
    return weeklyStats.value.map(w => ({
      label: w.label || `第${w.week}周`,
      minutes: w.minutes,
      sessions: w.sessions
    }))
  }
  if (timeRange.value === 'all') {
    if (monthlyStats.value.length === 0) return []
    return monthlyStats.value.map(m => ({
      label: m.label || `${m.month}月`,
      minutes: m.minutes,
      sessions: m.sessions
    }))
  }
  if (timeRange.value === 'custom') {
    if (dailyStats.value.length === 0) return []
    return dailyStats.value.map(d => {
      const date = new Date(d.date)
      return {
        label: `${date.getMonth() + 1}/${date.getDate()}`,
        minutes: d.minutes,
        sessions: d.sessions
      }
    })
  }
  return []
})

const yMax = computed(() => {
  const max = Math.max(...trendData.value.map(d => d.minutes), 1)
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

function getDateRange() {
  const today = new Date()
  const endDate = today.toISOString().split('T')[0]
  let startDate
  if (timeRange.value === 'today') {
    startDate = endDate
  } else if (timeRange.value === 'week') {
    const d = new Date(today)
    d.setDate(d.getDate() - 6)
    startDate = d.toISOString().split('T')[0]
  } else if (timeRange.value === 'month') {
    const d = new Date(today)
    d.setDate(d.getDate() - 29)
    startDate = d.toISOString().split('T')[0]
  } else if (timeRange.value === 'custom') {
    startDate = customStart.value
    const e = new Date(customEnd.value)
    e.setHours(23, 59, 59, 999)
    return { startDate, endDate: customEnd.value }
  } else {
    startDate = null
  }
  return { startDate, endDate }
}

async function loadStats() {
  const planId = planStore.currentPlan?.id
  if (!planId) return
  loading.value = true
  try {
    const { startDate, endDate } = getDateRange()
    const promises = [
      getFocusStats(planId, startDate, endDate),
      getFocusSubjectStats(planId, startDate, endDate),
      getFocusRecords(planId, startDate, endDate)
    ]

    let trendRes
    if (timeRange.value === 'month') {
      trendRes = getFocusWeeklyStats(planId, startDate, endDate)
    } else if (timeRange.value === 'all') {
      trendRes = getFocusMonthlyStats(planId, startDate, endDate)
    } else {
      trendRes = getFocusDailyStats(planId, startDate, endDate)
    }

    const [overview, subjectRes, recordsRes, trendDataRes] = await Promise.all([
      ...promises,
      trendRes
    ])

    overviewStats.value = overview
    subjectStats.value = subjectRes
    recentRecords.value = (recordsRes || []).slice(0, 15)

    if (timeRange.value === 'month') {
      weeklyStats.value = trendDataRes
    } else if (timeRange.value === 'all') {
      monthlyStats.value = trendDataRes
    } else {
      dailyStats.value = trendDataRes
    }
  } catch (e) {
    console.error('Failed to load stats:', e)
  } finally {
    loading.value = false
  }
}

function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    uni.switchTab({ url: '/pages/index/index' })
  }
}

function openDateRange() {
  const today = new Date()
  const twoWeeksAgo = new Date(today)
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 13)
  customStart.value = twoWeeksAgo.toISOString().split('T')[0]
  customEnd.value = today.toISOString().split('T')[0]
  showDatePicker.value = true
}

function closeDatePicker() {
  showDatePicker.value = false
}

function onStartChange(e) {
  customStart.value = e.detail.value
}

function onEndChange(e) {
  customEnd.value = e.detail.value
}

function setQuickRange(days) {
  const today = new Date()
  customEnd.value = today.toISOString().split('T')[0]
  const d = new Date(today)
  d.setDate(d.getDate() - (days - 1))
  customStart.value = d.toISOString().split('T')[0]
}

function confirmDateRange() {
  if (!customStart.value || !customEnd.value) {
    uni.showToast({ title: '请选择日期范围', icon: 'none' })
    return
  }
  if (new Date(customStart.value) > new Date(customEnd.value)) {
    uni.showToast({ title: '开始日期不能晚于结束日期', icon: 'none' })
    return
  }
  timeRange.value = 'custom'
  showDatePicker.value = false
}

watch(timeRange, () => { loadStats() })

onShow(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 44px 0 14px;
  .back-btn { width: 40px; height: 40px; background: $bg2; border-radius: 50%; display: flex; align-items: center; justify-content: center; .back-icon { font-size: 20px; color: $ink; } }
  .page-title { font-size: 20px; font-weight: 600; color: $ink; }
  .placeholder { width: 40px; }
}

.time-tabs {
  display: flex; background: $bg2; border-radius: 12px; padding: 4px;
  margin-bottom: 16px; border: 1px solid $rule;
  overflow-x: auto;
  flex-wrap: nowrap;
}
.time-tab {
  flex: 1; padding: 10px 6px; border-radius: 8px; text-align: center;
  min-width: 56px; flex-shrink: 0;
  &.active { background: $accent; .tab-text { color: #fff; } }
  .tab-text { font-size: 14px; color: $muted; }
}
.custom-tab {
  flex: none;
  padding: 10px 14px;
  min-width: auto;
  background: rgba(102, 126, 117, 0.08);
  .tab-text { font-size: 13px; color: #667e75; }
  &.active {
    background: $accent;
    .tab-text { color: #fff; }
  }
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  .section-title { margin-bottom: 0; }
  .range-hint { font-size: 12px; color: $muted; }
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
.chart-scroll {
  flex: 1;
  white-space: nowrap;
  overflow-x: auto;
  border-left: 1px solid $rule;
  border-bottom: 1px solid $rule;
}
.chart-bars-area {
  flex: 1; display: flex; justify-content: space-around; align-items: flex-end;
  border-left: 1px solid $rule; border-bottom: 1px solid $rule; padding-left: 8px;
  min-width: 100%;
}
.chart-bars-area.scrollable {
  border-left: none;
  border-bottom: none;
  display: inline-flex;
  justify-content: flex-start;
  gap: 12px;
  padding: 0 10px;
  min-width: auto;
}
.bar-item { display: flex; flex-direction: column; align-items: center; min-width: 28px; }
.chart-bars-area.scrollable .bar-item { min-width: 40px; }
.bar-wrapper { width: 22px; height: 100px; display: flex; align-items: flex-end; }
.chart-bars-area.scrollable .bar-wrapper { width: 28px; }
.bar-fill {
  width: 100%; background: linear-gradient(180deg, var(--color-accent, #2f7d4f) 0%, var(--color-header-green-end, #4a9d6a) 100%);
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

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-content {
  width: 85%;
  max-width: 360px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid $rule;
}
.modal-title { font-size: 16px; font-weight: 600; color: $ink; }
.modal-close { font-size: 16px; color: $muted; }
.modal-body {
  padding: 20px 18px;
}
.modal-footer {
  display: flex;
  border-top: 1px solid $rule;
}
.cancel-btn, .submit-btn {
  flex: 1;
  text-align: center;
  padding: 14px;
  font-size: 14px;
  font-weight: 500;
}
.cancel-btn { color: $muted; }
.submit-btn { color: $accent; font-weight: 600; }

.date-picker-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.date-picker-item {
  flex: 1;
  background: $bg2;
  border-radius: 10px;
  padding: 12px;
  text-align: center;
  border: 1px solid $rule;
}
.date-picker-label {
  font-size: 12px;
  color: $muted;
  display: block;
  margin-bottom: 4px;
}
.date-picker-value {
  font-size: 15px;
  font-weight: 600;
  color: $ink;
}
.date-picker-sep {
  font-size: 14px;
  color: $muted;
}
.hidden-picker {
  width: 0;
  height: 0;
  opacity: 0;
  position: absolute;
}
.quick-select-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.quick-btn {
  flex: 1;
  text-align: center;
  padding: 8px 4px;
  background: $bg2;
  border-radius: 8px;
  font-size: 12px;
  color: #667e75;
  border: 1px solid $rule;
  
  &:active {
    background: rgba(102, 126, 117, 0.15);
  }
}
</style>
