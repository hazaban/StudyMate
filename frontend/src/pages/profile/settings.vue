<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">设置</text>
      <view style="width: 40px;"></view>
    </view>

    <view class="settings-list">
      <view class="setting-item">
        <view class="setting-left">
          <text class="setting-icon">🔔</text>
          <view class="setting-info">
            <text class="setting-title">学习提醒</text>
            <text class="setting-desc">番茄钟完成时发送通知</text>
          </view>
        </view>
        <view class="setting-switch">
          <view class="switch" :class="{ on: notificationEnabled }" @click="toggleNotification"></view>
        </view>
      </view>

      <view class="setting-item">
        <view class="setting-left">
          <text class="setting-icon">🌙</text>
          <view class="setting-info">
            <text class="setting-title">夜间模式</text>
            <text class="setting-desc">切换深色/浅色主题</text>
          </view>
        </view>
        <view class="setting-switch">
          <view class="switch" :class="{ on: darkMode }" @click="toggleDarkMode"></view>
        </view>
      </view>

      <view class="setting-item" @click="testNotification">
        <view class="setting-left">
          <text class="setting-icon">📢</text>
          <view class="setting-info">
            <text class="setting-title">测试通知</text>
            <text class="setting-desc">发送一条测试通知</text>
          </view>
        </view>
        <text class="setting-arrow">›</text>
      </view>

      <view class="setting-item" @click="showAbout">
        <view class="setting-left">
          <text class="setting-icon">ℹ️</text>
          <view class="setting-info">
            <text class="setting-title">关于 StudyMate</text>
            <text class="setting-desc">版本 1.0.0</text>
          </view>
        </view>
        <text class="setting-arrow">›</text>
      </view>
    </view>

    <view class="account-section" v-if="isLoggedIn">
      <view class="account-btn switch-btn" @click="handleSwitchAccount">
        <text class="account-btn-text">切换账号</text>
      </view>
      <view class="account-btn logout-btn" @click="handleLogout">
        <text class="account-btn-text">退出登录</text>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)

const darkMode = ref(false)
const notificationEnabled = ref(false)

function toggleDarkMode() {
  darkMode.value = !darkMode.value
  uni.setStorageSync('studymate_dark_mode', darkMode.value)
  applyDarkMode()
}

function toggleNotification() {
  notificationEnabled.value = !notificationEnabled.value
  uni.setStorageSync('studymate_reminder_enabled', notificationEnabled.value)
  if (notificationEnabled.value) {
    requestNotificationPermission()
  }
}

function applyDarkMode() {
  if (darkMode.value) {
    document.documentElement.classList.add('dark-mode')
  } else {
    document.documentElement.classList.remove('dark-mode')
  }
}

function requestNotificationPermission() {
  // #ifdef H5
  if ('Notification' in window) {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        uni.showToast({ title: '通知权限已开启', icon: 'success' })
      } else if (permission === 'denied') {
        notificationEnabled.value = false
        uni.setStorageSync('studymate_reminder_enabled', false)
        uni.showToast({ title: '通知权限被拒绝，请在浏览器设置中开启', icon: 'none' })
      }
    })
  }
  // #endif
}

function testNotification() {
  // #ifdef H5
  if (!('Notification' in window)) {
    uni.showToast({ title: '当前浏览器不支持通知', icon: 'none' })
    return
  }
  if (Notification.permission === 'granted') {
    new Notification('StudyMate 学习提醒', {
      body: '这是一条测试通知，番茄钟完成后会收到类似提醒',
      icon: '/static/logo.png'
    })
    uni.showToast({ title: '通知已发送', icon: 'success' })
  } else if (Notification.permission === 'default') {
    // 还没问过用户 → 立即请求权限
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        new Notification('StudyMate 学习提醒', {
          body: '通知权限已开启，番茄钟完成后会收到提醒',
          icon: '/static/logo.png'
        })
        notificationEnabled.value = true
        uni.setStorageSync('studymate_reminder_enabled', true)
      } else {
        uni.showToast({ title: '通知权限被拒绝', icon: 'none' })
      }
    })
  } else {
    uni.showToast({ title: '通知权限已被拒绝，请在浏览器设置中开启', icon: 'none' })
  }
  // #endif
  // #ifndef H5
  uni.showToast({ title: '请在手机设置中开启通知权限', icon: 'none' })
  // #endif
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
          setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 800)
        }
      }
    }
  })
}

function handleSwitchAccount() {
  uni.showModal({
    title: '切换账号',
    content: '切换账号将退出当前登录，确定继续吗？',
    success: async (res) => {
      if (res.confirm) {
        await userStore.logout()
        uni.navigateTo({ url: '/pages/auth/login' })
      }
    }
  })
}

function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) { uni.navigateBack() } else { uni.switchTab({ url: '/pages/profile/profile' }) }
}

onMounted(() => {
  darkMode.value = uni.getStorageSync('studymate_dark_mode') || false
  notificationEnabled.value = uni.getStorageSync('studymate_reminder_enabled') || false
  applyDarkMode()
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 0 20px;
  
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
}

.settings-list {
  background: $bg2;
  border-radius: 20px;
  border: 1px solid $rule;
  overflow: hidden;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid $rule;
  
  &:last-child {
    border-bottom: none;
  }
}

.setting-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.setting-icon {
  font-size: 22px;
}

.setting-info {
  flex: 1;
}

.setting-title {
  display: block;
  font-size: 15px;
  font-weight: 500;
  color: $ink;
}

.setting-desc {
  display: block;
  font-size: 12px;
  color: $muted;
  margin-top: 2px;
}

.setting-arrow {
  font-size: 20px;
  color: $muted;
}

.setting-switch {
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

.account-section {
  padding: 24px 0 0;
  display: flex; flex-direction: column; gap: 12px;
}
.account-btn {
  padding: 14px; text-align: center; border-radius: 12px;
  .account-btn-text { font-size: 15px; font-weight: 500; }
}
.switch-btn {
  background: #f5f7f5; border: 1px solid #e0e0e0;
  .account-btn-text { color: #1a1a2e; }
  &:active { background: #e8ece9; }
}
.logout-btn {
  background: #ffebee;
  .account-btn-text { color: #c62828; }
  &:active { background: #ffcdd2; }
}

.bottom-space {
  height: 100px;
}
</style>