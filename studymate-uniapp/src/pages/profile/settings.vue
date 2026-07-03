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

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

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
    Notification.requestPermission()
  }
  // #endif
}

function testNotification() {
  // #ifdef H5
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('StudyMate 学习提醒', {
      body: '这是一条测试通知，番茄钟完成后会收到类似提醒',
      icon: '/static/logo.png'
    })
    uni.showToast({ title: '通知已发送', icon: 'success' })
  } else {
    uni.showToast({ title: '请先授权通知权限', icon: 'none' })
  }
  // #endif
  // #ifndef H5
  uni.showToast({ title: '通知功能已就绪', icon: 'success' })
  // #endif
}

function showAbout() {
  uni.showModal({
    title: '关于 StudyMate',
    content: 'StudyMate学习星球 - AI抗遗忘备考工具\n\n版本：1.0.0\n\n让知识进脑子而不是走过场',
    showCancel: false
  })
}

function goBack() {
  uni.navigateBack()
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

.bottom-space {
  height: 100px;
}
</style>