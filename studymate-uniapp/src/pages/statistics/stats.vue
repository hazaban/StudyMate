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
            <text class="record-task">{{ r.task_name }}</text>
            <text class="record-detail">{{ r.subject || '' }}</text>
          </view>
          <text class="record-time">{{ r.duration }}分</text>
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
import { getFocusStats, getFocusSubjectStats, getFocusDailyStats, getFocusRecords } from '@/api/client'

const planStore = usePlanStore()

const timeRange = ref('month')
const loading = ref(false)

const overviewStats = ref({ total_minutes: 0, total_sessions: 0, avg_minutes: 0 })
const subjectStats = ref([])
const dailyStats = ref([])
const recentRecords = ref([])

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

const dailyTrend = computed(() => {
  if (dailyStats.value.length === 0) return []
  return dailyStats.value.map(d => {
    const date = new Date(d.date)
    return {
      label: `${date.getMonth() + 1}/${date.getDate()}`,
      date: d.date,
      minutes: d.minutes,
      sessions: d.sessions
    }
  })
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
    const [overview, subjectRes, dailyRes, recordsRes] = await Promise.all([
      getFocusStats(planId, startDate, endDate),
      getFocusSubjectStats(planId, startDate, endDate),
      getFocusDailyStats(planId, startDate, endDate),
      getFocusRecords(planId, startDate, endDate)
    ])
    overviewStats.value = overview
    subjectStats.value = subjectRes
    dailyStats.value = dailyRes
    recentRecords.value = (recordsRes || []).slice(0, 15)
  } catch (e) {
    console.error('Failed to load stats:', e)
  } finally {
    loading.value = false
  }
}

function goBack() { uni.navigateBack() }

watch(timeRange, () => { loadStats() })

onShow(() => {
  loadStats()
})
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
