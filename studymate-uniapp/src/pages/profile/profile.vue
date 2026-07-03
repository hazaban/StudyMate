<template>
  <view class="page">
    <view class="header">
      <text class="title">设置</text>
    </view>

    <view class="settings-list">
      <!-- Night Mode -->
      <view class="settings-item">
        <view class="settings-left">
          <text class="settings-icon">🌙</text>
          <view class="settings-info">
            <text class="settings-title">夜间模式</text>
            <text class="settings-desc">切换深色/浅色主题</text>
          </view>
        </view>
        <switch :checked="isDarkMode" @change="toggleDarkMode" color="#2f7d4f" />
      </view>

      <!-- Study Reminder -->
      <view class="settings-item">
        <view class="settings-left">
          <text class="settings-icon">🔔</text>
          <view class="settings-info">
            <text class="settings-title">学习提醒</text>
            <text class="settings-desc">番茄钟完成时发送通知</text>
          </view>
        </view>
        <switch :checked="reminderEnabled" @change="toggleReminder" color="#2f7d4f" />
      </view>

      <!-- Reminder interval -->
      <view class="settings-item" v-if="reminderEnabled">
        <view class="settings-left">
          <text class="settings-icon">⏱</text>
          <view class="settings-info">
            <text class="settings-title">提醒间隔</text>
            <text class="settings-desc">每完成一个番茄钟提醒休息</text>
          </view>
        </view>
        <view class="setting-value">
          <input class="reminder-input" v-model="reminderInterval" type="number" placeholder="25" />
          <text class="reminder-unit">分钟</text>
        </view>
      </view>

      <!-- Test Notification -->
      <view class="settings-item" @click="testNotification" v-if="reminderEnabled">
        <view class="settings-left">
          <text class="settings-icon">📢</text>
          <view class="settings-info">
            <text class="settings-title">测试通知</text>
            <text class="settings-desc">点击发送测试通知</text>
          </view>
        </view>
        <text class="settings-arrow">›</text>
      </view>

      <!-- Notification permission status -->
      <view class="settings-item">
        <view class="settings-left">
          <text class="settings-icon">📱</text>
          <view class="settings-info">
            <text class="settings-title">通知权限</text>
            <text class="settings-desc">{{ notificationStatus }}</text>
          </view>
        </view>
        <view class="settings-btn" @click="requestNotificationPermission" v-if="notificationStatus !== '已授权'">
          <text>授权</text>
        </view>
      </view>

      <!-- About -->
      <view class="settings-item">
        <view class="settings-left">
          <text class="settings-icon">ℹ</text>
          <view class="settings-info">
            <text class="settings-title">关于 StudyMate</text>
            <text class="settings-desc">版本 1.0.0</text>
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isDarkMode = ref(false)
const reminderEnabled = ref(false)
const reminderInterval = ref(25)
const notificationStatus = ref('未知')

function toggleDarkMode(e) {
  isDarkMode.value = e.detail.value
  uni.setStorageSync('studymate_dark_mode', isDarkMode.value)
  applyDarkMode()
}

function toggleReminder(e) {
  reminderEnabled.value = e.detail.value
  uni.setStorageSync('studymate_reminder_enabled', reminderEnabled.value)
  if (reminderEnabled.value) {
    requestNotificationPermission()
  }
}

function applyDarkMode() {
  const app = document.querySelector('page') || document.documentElement
  if (isDarkMode.value) {
    app?.classList.add('dark-mode')
    document.documentElement.style.setProperty('--bg', '#1a1a2e')
    document.documentElement.style.setProperty('--bg2', '#252540')
    document.documentElement.style.setProperty('--ink', '#e0e0e0')
    document.documentElement.style.setProperty('--muted', '#a0a0a0')
    document.documentElement.style.setProperty('--rule', '#333')
    document.documentElement.style.setProperty('--soft', '#2a2a40')
    document.documentElement.style.setProperty('--accent', '#3d9a62')
  } else {
    app?.classList.remove('dark-mode')
    document.documentElement.style.setProperty('--bg', '#f5f7f5')
    document.documentElement.style.setProperty('--bg2', '#ffffff')
    document.documentElement.style.setProperty('--ink', '#1a1a2e')
    document.documentElement.style.setProperty('--muted', '#65746d')
    document.documentElement.style.setProperty('--rule', '#e8ece9')
    document.documentElement.style.setProperty('--soft', '#f0f4f0')
    document.documentElement.style.setProperty('--accent', '#2f7d4f')
  }
}

function requestNotificationPermission() {
  // #ifdef H5
  if ('Notification' in window) {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        notificationStatus.value = '已授权'
        uni.setStorageSync('studymate_notification_permission', 'granted')
      } else {
        notificationStatus.value = '未授权'
      }
    })
  } else {
    notificationStatus.value = '不支持'
  }
  // #endif
  // #ifndef H5
  notificationStatus.value = '已授权（App内通知）'
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

// Save settings periodically
function saveSettings() {
  uni.setStorageSync('studymate_reminder_interval', reminderInterval.value)
}

onMounted(() => {
  // Load settings
  isDarkMode.value = uni.getStorageSync('studymate_dark_mode') || false
  reminderEnabled.value = uni.getStorageSync('studymate_reminder_enabled') || false
  reminderInterval.value = uni.getStorageSync('studymate_reminder_interval') || 25
  applyDarkMode()

  // Check notification permission
  // #ifdef H5
  if ('Notification' in window) {
    const perm = uni.getStorageSync('studymate_notification_permission')
    if (perm === 'granted' || Notification.permission === 'granted') {
      notificationStatus.value = '已授权'
    } else {
      notificationStatus.value = '未授权'
    }
  } else {
    notificationStatus.value = '不支持'
  }
  // #endif
  // #ifndef H5
  notificationStatus.value = '已授权（App内通知）'
  // #endif
})
</script>

<style lang="scss" scoped>
.header {
  padding: 40px 0 20px;
  .title { font-size: 22px; font-weight: 700; color: var(--ink, #1a1a2e); }
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--bg2, #fff);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--rule, #e8ece9);
}

.settings-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg2, #fff);
  border-bottom: 1px solid var(--rule, #e8ece9);
  &:last-child { border-bottom: none; }
}

.settings-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.settings-icon {
  font-size: 22px;
}

.settings-info {
  flex: 1;
}

.settings-title {
  display: block;
  font-size: 15px;
  font-weight: 500;
  color: var(--ink, #1a1a2e);
}

.settings-desc {
  display: block;
  font-size: 12px;
  color: var(--muted, #65746d);
  margin-top: 2px;
}

.settings-arrow {
  font-size: 20px;
  color: var(--muted, #999);
}

.settings-btn {
  padding: 6px 16px;
  background: #2f7d4f;
  color: #fff;
  border-radius: 20px;
  font-size: 13px;
}

.setting-value {
  display: flex;
  align-items: center;
  gap: 4px;
}

.reminder-input {
  width: 50px;
  padding: 6px 8px;
  border: 1px solid var(--rule, #e8ece9);
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  background: var(--bg, #fafafa);
  color: var(--ink, #1a1a2e);
}

.reminder-unit {
  font-size: 13px;
  color: var(--muted, #65746d);
}

.bottom-space { height: 100px; }
</style>