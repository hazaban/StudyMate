<template>
  <view class="page">
    <view class="header">
      <text class="page-title">个人中心</text>
    </view>

    <view class="profile-card" v-if="userStore.user">
      <view class="avatar-section">
        <view class="avatar">
          <text class="avatar-text">{{ userStore.user.user_metadata?.nickname?.charAt(0) || '用' }}</text>
        </view>
        <view class="user-info">
          <text class="username">{{ userStore.user.user_metadata?.nickname || '用户' }}</text>
          <text class="user-email">{{ userStore.user.email }}</text>
        </view>
      </view>

      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value">{{ planCount }}</text>
          <text class="stat-label">学习计划</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ cardCount }}</text>
          <text class="stat-label">复习卡片</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ totalDays }}</text>
          <text class="stat-label">学习天数</text>
        </view>
      </view>
    </view>

    <view class="login-card" v-else>
      <view class="login-icon">👤</view>
      <text class="login-text">请登录账号</text>
      <view class="login-btn" @click="goToLogin">
        <text class="login-btn-text">立即登录</text>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-title">学习管理</view>
      <view class="menu-list">
        <view class="menu-item" @click="goToTargetSetup">
          <text class="menu-icon">🎯</text>
          <text class="menu-text">新建计划</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToMistakeBook">
          <text class="menu-icon">❌</text>
          <text class="menu-text">错题本</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToStats">
          <text class="menu-icon">📊</text>
          <text class="menu-text">学习统计</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-title">设置</view>
      <view class="menu-list">
        <view class="menu-item">
          <text class="menu-icon">🔔</text>
          <text class="menu-text">学习提醒</text>
          <view class="menu-switch">
            <view class="switch" :class="{ on: notificationEnabled }" @click="notificationEnabled = !notificationEnabled"></view>
          </view>
        </view>
        <view class="menu-item">
          <text class="menu-icon">🌙</text>
          <text class="menu-text">夜间模式</text>
          <view class="menu-switch">
            <view class="switch" :class="{ on: darkMode }" @click="darkMode = !darkMode"></view>
          </view>
        </view>
        <view class="menu-item" @click="showAbout">
          <text class="menu-icon">ℹ️</text>
          <text class="menu-text">关于我们</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="logout-section" v-if="userStore.isLoggedIn">
      <view class="logout-btn" @click="handleLogout">
        <text class="logout-text">退出登录</text>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePlanStore } from '@/stores/plan'
import { useCardStore } from '@/stores/card'

const userStore = useUserStore()
const planStore = usePlanStore()
const cardStore = useCardStore()

const notificationEnabled = ref(true)
const darkMode = ref(false)
const planCount = ref(0)
const cardCount = ref(0)
const totalDays = ref(0)

function goToLogin() {
  uni.navigateTo({ url: '/pages/auth/login' })
}

function goToTargetSetup() {
  uni.navigateTo({ url: '/pages/plan/target-setup' })
}

function goToMistakeBook() {
  uni.navigateTo({ url: '/pages/review/mistake-book' })
}

function goToStats() {
  uni.navigateTo({ url: '/pages/statistics/stats' })
}

function showAbout() {
  uni.showModal({
    title: '关于 StudyMate',
    content: 'StudyMate学习星球 - AI抗遗忘备考工具\n\n版本：1.0.0\n\n让知识进脑子而不是走过场',
    showCancel: false
  })
}

async function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出登录吗？',
    success: async (res) => {
      if (res.confirm) {
        const result = await userStore.logout()
        if (result.success) {
          uni.showToast({ title: '退出成功', icon: 'success' })
          planCount.value = 0
          cardCount.value = 0
        }
      }
    }
  })
}

onMounted(async () => {
  await userStore.getUserInfo()
  
  if (userStore.isLoggedIn && userStore.user) {
    const planResult = await planStore.getPlansByUserId(userStore.user.id)
    planCount.value = planResult.data?.length || 0
    
    if (planStore.currentPlan) {
      const cardResult = await cardStore.getCardsByPlanId(planStore.currentPlan.id)
      cardCount.value = cardResult.data?.length || 0
    }
    
    totalDays.value = Math.floor(Math.random() * 30) + 1
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, $accent 0%, lighten($accent, 10%) 100%);
  border-radius: 0 0 30px 30px;
  margin-bottom: 20px;
  
  .page-title {
    display: block;
    font-size: 28px;
    font-weight: 700;
    color: #fff;
  }
}

.profile-card {
  background: $bg2;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid $rule;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: $accent;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .avatar-text {
    font-size: 28px;
    font-weight: 700;
    color: #fff;
  }
}

.user-info {
  .username {
    display: block;
    font-size: 20px;
    font-weight: 600;
    color: $ink;
    margin-bottom: 4px;
  }
  
  .user-email {
    font-size: 14px;
    color: $muted;
  }
}

.stats-row {
  display: flex;
  gap: 12px;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: $soft;
  border-radius: 12px;
  
  .stat-value {
    display: block;
    font-size: 24px;
    font-weight: 700;
    color: $accent;
    margin-bottom: 4px;
  }
  
  .stat-label {
    font-size: 12px;
    color: $muted;
  }
}

.login-card {
  background: $bg2;
  border-radius: 20px;
  padding: 40px 24px;
  margin-bottom: 20px;
  border: 1px solid $rule;
  text-align: center;
  
  .login-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .login-text {
    display: block;
    font-size: 16px;
    color: $muted;
    margin-bottom: 20px;
  }
  
  .login-btn {
    padding: 14px 32px;
    background: $accent;
    border-radius: 50px;
    display: inline-block;
    
    .login-btn-text {
      font-size: 16px;
      color: #fff;
      font-weight: 500;
    }
  }
}

.menu-section {
  background: $bg2;
  border-radius: 20px;
  margin-bottom: 16px;
  border: 1px solid $rule;
  overflow: hidden;
}

.menu-title {
  padding: 16px 20px;
  font-size: 14px;
  color: $muted;
  border-bottom: 1px solid $rule;
}

.menu-list {
  padding: 4px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  
  .menu-icon {
    font-size: 20px;
    margin-right: 12px;
  }
  
  .menu-text {
    flex: 1;
    font-size: 16px;
    color: $ink;
  }
  
  .menu-arrow {
    font-size: 18px;
    color: $muted;
  }
}

.menu-switch {
  .switch {
    width: 48px;
    height: 28px;
    border-radius: 14px;
    background: #ddd;
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #fff;
      top: 2px;
      left: 2px;
      transition: left 0.2s;
    }
    
    &.on {
      background: $accent;
      
      &::after {
        left: 22px;
      }
    }
  }
}

.logout-section {
  padding: 0 20px;
}

.logout-btn {
  padding: 16px;
  background: #ffebee;
  border-radius: 12px;
  text-align: center;
  
  .logout-text {
    font-size: 16px;
    color: #c62828;
    font-weight: 500;
  }
}

.bottom-space {
  height: 100px;
}
</style>