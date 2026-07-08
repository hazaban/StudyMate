<template>
  <view class="page">
    <view class="profile-card" v-if="userStore.user">
      <view class="avatar-section">
        <view class="avatar" @click="chooseAvatar">
          <image v-if="avatarUrl" :src="avatarUrl" mode="aspectFill" class="avatar-img" />
          <text class="avatar-emoji" v-else>🧸</text>
        </view>
        <view class="user-info">
          <view class="nickname-row" @click="editNickname">
            <text class="username">{{ userStore.user?.nickname || '用户' }}</text>
            <text class="edit-icon">✎</text>
          </view>
          <text class="user-email">{{ userStore.user.email }}</text>
        </view>
        <view class="settings-btn" @click="goToSettings">
          <text class="settings-icon">⚙</text>
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
      <view class="menu-title">计划管理</view>
      <view class="menu-list">
        <view class="menu-item" @click="goToPlanOverview">
          <text class="menu-icon">📋</text>
          <text class="menu-text">我的计划</text>
          <text class="menu-text-sub" v-if="planCount > 0">{{ planCount }}个进行中</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToTargetSetup">
          <text class="menu-icon">🎯</text>
          <text class="menu-text">新建计划</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToAIPlan">
          <text class="menu-icon">🤖</text>
          <text class="menu-text">AI 生成计划</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-title">学习管理</view>
      <view class="menu-list">
        <view class="menu-item" @click="goToStats">
          <text class="menu-icon">📊</text>
          <text class="menu-text">学习统计</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-title">其他</view>
      <view class="menu-list">
        <view class="menu-item" @click="goToSettings">
          <text class="menu-icon">⚙</text>
          <text class="menu-text">设置</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { usePlanStore } from '@/stores/plan'
import * as api from '@/api/client'

const userStore = useUserStore()
const planStore = usePlanStore()

const planCount = ref(0)
const cardCount = ref(0)
const totalDays = ref(0)
const avatarUrl = ref('')
const editingNickname = ref(false)
const nicknameTemp = ref('')

function initAvatar() {
  avatarUrl.value = userStore.user?.avatar_url || ''
}

async function loadData() {
  await userStore.getUserInfo()

  if (!userStore.isLoggedIn || !userStore.user) {
    planCount.value = 0
    cardCount.value = 0
    totalDays.value = 0
    return
  }

  const planResult = await planStore.getPlansByUserId()
  if (planResult.success) {
    planCount.value = planStore.plans?.length || 0

    // Sum cards across ALL plans
    let totalCards = 0
    for (const p of planStore.plans) {
      try {
        const r = await api.getCards(p.id, null, null, false)
        totalCards += (r.cards || []).length
      } catch (e) { /* skip */ }
    }
    cardCount.value = totalCards
  } else {
    planCount.value = 0
    cardCount.value = 0
  }

  // Learning days: unique dates from backend FocusRecords across ALL plans
  try {
    const allDates = new Set()
    for (const p of planStore.plans) {
      try {
        const res = await api.getFocusRecords(p.id, null, null, null)
        // API returns list[FocusRecordResponse] directly (an array)
        const records = Array.isArray(res) ? res : (res.records || res.data || [])
        records.forEach(r => { if (r.date) allDates.add(r.date) })
      } catch (e) { /* skip */ }
    }
    totalDays.value = allDates.size
  } catch (e) {
    totalDays.value = 0
  }
}

function chooseAvatar() {
  // #ifdef H5
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = async (ev) => {
      const base64 = ev.target.result
      avatarUrl.value = base64
      try {
        await api.updateMe({ avatar_url: base64 })
        uni.showToast({ title: '头像已更新', icon: 'success' })
      } catch (e) { uni.showToast({ title: '头像更新失败', icon: 'none' }) }
    }
    reader.readAsDataURL(file)
  }
  input.click()
  // #endif
  // #ifndef H5
  uni.chooseImage({
    count: 1, sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const path = res.tempFilePaths[0]
      avatarUrl.value = path
      try {
        uni.getFileSystemManager().readFile({
          filePath: path, encoding: 'base64',
          success: async (data) => {
            const b64 = 'data:image/jpeg;base64,' + data.data
            await api.updateMe({ avatar_url: b64 })
            uni.showToast({ title: '头像已更新', icon: 'success' })
          }
        })
      } catch (e) { uni.showToast({ title: '头像更新失败', icon: 'none' }) }
    }
  })
  // #endif
}

function editNickname() {
  nicknameTemp.value = userStore.user?.nickname || ''
  editingNickname.value = true
  uni.showModal({
    title: '修改昵称',
    editable: true,
    placeholderText: '请输入新昵称',
    content: nicknameTemp.value,
    success: async (res) => {
      if (res.confirm && res.content) {
        const newName = res.content.trim()
        if (newName) {
          try {
            await api.updateMe({ nickname: newName })
            await userStore.getUserInfo()
            uni.showToast({ title: '昵称已更新', icon: 'success' })
          } catch (e) { uni.showToast({ title: '更新失败', icon: 'none' }) }
        }
      }
      editingNickname.value = false
    }
  })
}

function goToLogin() {
  uni.navigateTo({ url: '/pages/auth/login' })
}

function goToTargetSetup() {
  uni.navigateTo({ url: '/pages/plan/target-setup' })
}

function goToAIPlan() {
  uni.navigateTo({ url: '/pages/plan/ai-plan' })
}

function goToPlanOverview() {
  uni.navigateTo({ url: '/pages/plan/plan-overview' })
}

function goToStats() {
  uni.navigateTo({ url: '/pages/statistics/stats' })
}

function goToSettings() {
  uni.navigateTo({ url: '/pages/profile/settings' })
}

onMounted(async () => {
  await loadData()
  initAvatar()
})

onShow(async () => {
  await loadData()
  initAvatar()
})
</script>

<style lang="scss" scoped>
.page { padding-top: 20px; }
.profile-card {
  background: $bg2;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 12px;
  border: 1px solid $rule;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 14px;
}

.settings-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f5f7f5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-left: auto;

  .settings-icon {
    font-size: 20px;
    color: #65746d;
  }

  &:active { background: #e8ece9; }
}

.avatar {
  width: 64px; height: 64px; border-radius: 50%;
  background: #f0f0f0; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  &:active { opacity: 0.8; }
  .avatar-img { width: 100%; height: 100%; }
}
.avatar-emoji { font-size: 40px; }

.user-info {
  .nickname-row { display: flex; align-items: center; gap: 6px; cursor: pointer; }
  .username { display: block; font-size: 18px; font-weight: 600; color: $ink; }
  .edit-icon { font-size: 14px; color: $muted; opacity: 0.5; }
  &:active .edit-icon { opacity: 1; }
  .user-email { font-size: 13px; color: $muted; }
}

.stats-row {
  display: flex;
  gap: 8px;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 8px 6px;
  background: $soft;
  border-radius: 10px;

  .stat-value {
    display: block;
    font-size: 17px;
    font-weight: 700;
    color: $accent;
  }

  .stat-label {
    font-size: 11px;
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
  border-radius: 16px;
  margin-bottom: 10px;
  border: 1px solid $rule;
  overflow: hidden;
}

.menu-title {
  padding: 8px 20px;
  font-size: 12px;
  color: $muted;
  border-bottom: 1px solid $rule;
}

.menu-list {
  padding: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;

  .menu-icon { font-size: 16px; margin-right: 8px; }
  .menu-text { flex: 1; font-size: 14px; color: $ink; }
  .menu-text-sub { font-size: 11px; color: $muted; margin-right: 6px; }
  .menu-arrow { font-size: 15px; color: $muted; }
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

.bottom-space {
  height: 100px;
}
</style>