<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">学习统计</text>
      <view class="placeholder"></view>
    </view>

    <view class="time-tabs">
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

    <view class="stats-overview">
      <view class="stat-card">
        <text class="stat-icon">⏱</text>
        <view class="stat-content">
          <text class="stat-value">{{ totalHours }}</text>
          <text class="stat-label">总学习时长（小时）</text>
        </view>
      </view>
      <view class="stat-card">
        <text class="stat-icon">🍅</text>
        <view class="stat-content">
          <text class="stat-value">{{ totalPomodoros }}</text>
          <text class="stat-label">完成番茄数</text>
        </view>
      </view>
      <view class="stat-card">
        <text class="stat-icon">📚</text>
        <view class="stat-content">
          <text class="stat-value">{{ completedTasks }}</text>
          <text class="stat-label">完成任务数</text>
        </view>
      </view>
      <view class="stat-card">
        <text class="stat-icon">✅</text>
        <view class="stat-content">
          <text class="stat-value">{{ completionRate }}%</text>
          <text class="stat-label">任务完成率</text>
        </view>
      </view>
    </view>

    <view class="chart-section">
      <text class="section-title">学习时长趋势</text>
      <view class="chart-container">
        <view class="chart-y-axis">
          <text class="y-label">8</text>
          <text class="y-label">6</text>
          <text class="y-label">4</text>
          <text class="y-label">2</text>
          <text class="y-label">0</text>
        </view>
        <view class="chart-content">
          <view class="chart-bars">
            <view class="bar-item" v-for="(day, index) in chartData" :key="index">
              <view class="bar-wrapper">
                <view class="bar" :style="{ height: day.hours * 12 + 'px' }"></view>
              </view>
              <text class="bar-label">{{ day.label }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="subject-section">
      <text class="section-title">科目分布</text>
      <view class="subject-list">
        <view class="subject-item" v-for="subject in subjectStats" :key="subject.name">
          <view class="subject-header">
            <text class="subject-name">{{ subject.name }}</text>
            <text class="subject-percent">{{ subject.percent }}%</text>
          </view>
          <view class="subject-progress-bar">
            <view class="subject-progress-fill" :style="{ width: subject.percent + '%', background: subject.color }"></view>
          </view>
          <text class="subject-hours">{{ subject.hours }}小时</text>
        </view>
      </view>
    </view>

    <view class="achievement-section">
      <text class="section-title">成就徽章</text>
      <view class="achievement-grid">
        <view class="achievement-item" v-for="achievement in achievements" :key="achievement.id">
          <view class="achievement-icon" :class="{ unlocked: achievement.unlocked }">
            {{ achievement.icon }}
          </view>
          <text class="achievement-name">{{ achievement.name }}</text>
          <text class="achievement-desc">{{ achievement.description }}</text>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const timeRange = ref('week')

const totalHours = ref(42.5)
const totalPomodoros = ref(85)
const completedTasks = ref(127)
const completionRate = ref(89)

const chartData = computed(() => {
  const days = ['一', '二', '三', '四', '五', '六', '日']
  return days.map((day, index) => ({
    label: day,
    hours: Math.floor(Math.random() * 6) + 2
  }))
})

const subjectStats = ref([
  { name: '数学', hours: 15.2, percent: 36, color: '#ef5350' },
  { name: '英语', hours: 10.1, percent: 24, color: '#5c6bc0' },
  { name: '政治', hours: 8.6, percent: 20, color: '#66bb6a' },
  { name: '专业课', hours: 8.6, percent: 20, color: '#ffb74d' }
])

const achievements = ref([
  { id: 1, icon: '🔥', name: '学习达人', description: '连续学习7天', unlocked: true },
  { id: 2, icon: '💯', name: '满分完成', description: '单日任务全完成', unlocked: true },
  { id: 3, icon: '⚡', name: '闪电速度', description: '完成50个番茄', unlocked: true },
  { id: 4, icon: '🌱', name: '播种新手', description: '种植第一棵植物', unlocked: true },
  { id: 5, icon: '🌳', name: '丰收季节', description: '收获10棵植物', unlocked: false },
  { id: 6, icon: '🎯', name: '目标达成', description: '完成一个学习计划', unlocked: false }
])

function goBack() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
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

.time-tabs {
  display: flex;
  background: $bg2;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 20px;
  border: 1px solid $rule;
}

.time-tab {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
  
  &.active {
    background: $accent;
    
    .tab-text {
      color: #fff;
    }
  }
  
  .tab-text {
    font-size: 14px;
    color: $muted;
  }
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: $bg2;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid $rule;
  
  .stat-icon {
    font-size: 28px;
  }
  
  .stat-content {
    .stat-value {
      display: block;
      font-size: 22px;
      font-weight: 700;
      color: $accent;
      margin-bottom: 2px;
    }
    
    .stat-label {
      font-size: 11px;
      color: $muted;
    }
  }
}

.section-title {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: $ink;
  margin-bottom: 12px;
}

.chart-section {
  background: $bg2;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid $rule;
}

.chart-container {
  display: flex;
  height: 160px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 12px;
  
  .y-label {
    font-size: 11px;
    color: $muted;
  }
}

.chart-content {
  flex: 1;
  border-left: 1px solid $rule;
  border-bottom: 1px solid $rule;
  padding-left: 12px;
}

.chart-bars {
  display: flex;
  justify-content: space-between;
  height: 100%;
  align-items: flex-end;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.bar-wrapper {
  width: 24px;
  height: 120px;
  display: flex;
  align-items: flex-end;
}

.bar {
  width: 100%;
  background: linear-gradient(180deg, $accent 0%, lighten($accent, 20%) 100%);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
}

.bar-label {
  font-size: 11px;
  color: $muted;
  margin-top: 8px;
}

.subject-section {
  background: $bg2;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid $rule;
}

.subject-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.subject-item {
  .subject-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    
    .subject-name {
      font-size: 14px;
      color: $ink;
      font-weight: 500;
    }
    
    .subject-percent {
      font-size: 14px;
      color: $muted;
    }
  }
  
  .subject-progress-bar {
    height: 8px;
    background: $soft;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 4px;
    
    .subject-progress-fill {
      height: 100%;
      border-radius: 4px;
    }
  }
  
  .subject-hours {
    font-size: 12px;
    color: $muted;
  }
}

.achievement-section {
  margin-bottom: 20px;
}

.achievement-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.achievement-item {
  background: $bg2;
  border-radius: 12px;
  padding: 16px 8px;
  text-align: center;
  border: 1px solid $rule;
  
  .achievement-icon {
    font-size: 32px;
    margin-bottom: 8px;
    opacity: 0.3;
    
    &.unlocked {
      opacity: 1;
    }
  }
  
  .achievement-name {
    display: block;
    font-size: 13px;
    color: $ink;
    font-weight: 500;
    margin-bottom: 4px;
  }
  
  .achievement-desc {
    font-size: 10px;
    color: $muted;
  }
}

.bottom-space {
  height: 60px;
}
</style>