<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">计划总览</text>
      <view class="edit-btn" @click="editPlan">
        <text class="edit-icon">✎</text>
      </view>
    </view>

    <view class="plan-card" v-if="planStore.currentPlan">
      <view class="plan-header">
        <text class="plan-name">{{ planStore.currentPlan.exam_name }}</text>
        <text class="plan-status">进行中</text>
      </view>

      <view class="plan-info">
        <view class="info-item">
          <text class="info-icon">📅</text>
          <view class="info-content">
            <text class="info-label">考试日期</text>
            <text class="info-value">{{ planStore.currentPlan.exam_date }}</text>
          </view>
        </view>

        <view class="info-item">
          <text class="info-icon">⏱</text>
          <view class="info-content">
            <text class="info-label">每日学习</text>
            <text class="info-value">{{ planStore.currentPlan.daily_study_time }}分钟</text>
          </view>
        </view>

        <view class="info-item">
          <text class="info-icon">📊</text>
          <view class="info-content">
            <text class="info-label">剩余天数</text>
            <text class="info-value highlight">{{ daysRemaining }}天</text>
          </view>
        </view>
      </view>

      <view class="score-section">
        <text class="section-title">目标分数</text>
        <view class="score-grid">
          <view class="score-card" v-for="(score, key) in planStore.currentPlan.target_scores" :key="key">
            <text class="score-subject">{{ subjectNames[key] || key }}</text>
            <text class="score-value">{{ score }}</text>
          </view>
        </view>
      </view>

      <view class="weak-section">
        <text class="section-title">薄弱科目</text>
        <view class="weak-tags">
          <view class="weak-tag" v-for="point in planStore.currentPlan.weak_points" :key="point">
            {{ point }}
          </view>
          <text class="no-weak" v-if="!planStore.currentPlan.weak_points || planStore.currentPlan.weak_points.length === 0">暂无</text>
        </view>
      </view>

      <view class="phase-section">
        <text class="section-title">学习阶段</text>
        <view class="phase-badge">{{ planStore.currentPlan.study_phase }}</view>
      </view>

      <view class="action-buttons">
        <view class="action-btn primary" @click="goToTaskBoard">
          <text class="btn-icon">📋</text>
          <text class="btn-text">今日任务</text>
        </view>
        <view class="action-btn secondary" @click="deletePlan">
          <text class="btn-icon">🗑</text>
          <text class="btn-text">删除计划</text>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无学习计划</text>
      <text class="empty-hint">点击下方按钮创建新计划</text>
      <view class="empty-btn" @click="createPlan">
        <text class="empty-btn-text">创建计划</text>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import { dateUtil } from '@/utils/date'

const planStore = usePlanStore()
const userStore = useUserStore()

const subjectNames = {
  math: '数学',
  english: '英语',
  politics: '政治',
  professional: '专业课'
}

const daysRemaining = computed(() => {
  if (!planStore.currentPlan) return 0
  return dateUtil.getDaysBetween(dateUtil.today(), planStore.currentPlan.exam_date)
})

function goBack() {
  uni.navigateBack()
}

function editPlan() {
  uni.showToast({ title: '编辑功能开发中', icon: 'none' })
}

function goToTaskBoard() {
  uni.switchTab({ url: '/pages/daily/task-board' })
}

function createPlan() {
  uni.navigateTo({ url: '/pages/plan/target-setup' })
}

async function deletePlan() {
  if (!planStore.currentPlan) return

  uni.showModal({
    title: '删除计划',
    content: '确定要删除这个学习计划吗？',
    success: async (res) => {
      if (res.confirm) {
        const result = await planStore.deletePlan(planStore.currentPlan.id)
        if (result.success) {
          uni.showToast({ title: '删除成功', icon: 'success' })
          setTimeout(() => {
            uni.switchTab({ url: '/pages/index/index' })
          }, 1000)
        }
      }
    }
  })
}

onMounted(async () => {
  await userStore.getUserInfo()
  
  if (userStore.isLoggedIn && userStore.user) {
    await planStore.getPlansByUserId(userStore.user.id)
  }
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 20px 20px;
  
  .back-btn, .edit-btn {
    width: 40px;
    height: 40px;
    background: $bg2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .back-icon, .edit-icon {
      font-size: 20px;
      color: $ink;
    }
  }
  
  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: $ink;
  }
}

.plan-card {
  background: $bg2;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid $rule;
}

.plan-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  
  .plan-name {
    font-size: 24px;
    font-weight: 700;
    color: $ink;
  }
  
  .plan-status {
    font-size: 12px;
    padding: 4px 12px;
    background: $soft;
    color: $accent;
    border-radius: 20px;
  }
}

.plan-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .info-icon {
    font-size: 20px;
  }
  
  .info-content {
    flex: 1;
    
    .info-label {
      display: block;
      font-size: 12px;
      color: $muted;
    }
    
    .info-value {
      display: block;
      font-size: 16px;
      color: $ink;
      font-weight: 500;
      
      &.highlight {
        color: $accent;
        font-size: 18px;
        font-weight: 700;
      }
    }
  }
}

.section-title {
  display: block;
  font-size: 14px;
  color: $muted;
  margin-bottom: 12px;
}

.score-section {
  margin-bottom: 20px;
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.score-card {
  background: $soft;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  
  .score-subject {
    display: block;
    font-size: 13px;
    color: $muted;
    margin-bottom: 8px;
  }
  
  .score-value {
    font-size: 24px;
    font-weight: 700;
    color: $accent;
  }
}

.weak-section {
  margin-bottom: 20px;
}

.weak-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  
  .no-weak {
    font-size: 14px;
    color: $muted;
  }
}

.weak-tag {
  padding: 8px 16px;
  background: #fff3e0;
  color: #e65100;
  border-radius: 20px;
  font-size: 13px;
}

.phase-section {
  margin-bottom: 24px;
}

.phase-badge {
  display: inline-block;
  padding: 10px 20px;
  background: $accent;
  color: #fff;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border-radius: 12px;
  
  &.primary {
    background: $accent;
    
    .btn-icon, .btn-text {
      color: #fff;
    }
  }
  
  &.secondary {
    background: #ffebee;
    
    .btn-icon, .btn-text {
      color: #c62828;
    }
  }
  
  .btn-icon {
    font-size: 16px;
  }
  
  .btn-text {
    font-size: 15px;
    font-weight: 500;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 20px;
  
  .empty-icon {
    font-size: 64px;
    margin-bottom: 20px;
  }
  
  .empty-text {
    font-size: 20px;
    color: $ink;
    margin-bottom: 8px;
    font-weight: 600;
  }
  
  .empty-hint {
    font-size: 14px;
    color: $muted;
    margin-bottom: 24px;
  }
  
  .empty-btn {
    padding: 14px 32px;
    background: $accent;
    border-radius: 50px;
    
    .empty-btn-text {
      font-size: 16px;
      color: #fff;
      font-weight: 500;
    }
  }
}

.bottom-space {
  height: 60px;
}
</style>