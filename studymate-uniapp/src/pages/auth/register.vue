<template>
  <view class="register-page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">注册账号</text>
      <view class="placeholder"></view>
    </view>

    <view class="form-section">
      <view class="input-group">
        <text class="input-label">昵称</text>
        <input class="input-field" v-model="nickname" placeholder="请输入昵称" />
      </view>

      <view class="input-group">
        <text class="input-label">邮箱</text>
        <input class="input-field" v-model="email" placeholder="请输入邮箱" type="email" />
      </view>

      <view class="input-group">
        <text class="input-label">密码</text>
        <input class="input-field" v-model="password" placeholder="请输入密码（至少6位）" type="password" />
      </view>

      <view class="input-group">
        <text class="input-label">确认密码</text>
        <input class="input-field" v-model="confirmPassword" placeholder="请再次输入密码" type="password" />
      </view>

      <view class="agreement-row">
        <view class="checkbox" :class="{ checked: agreed }" @click="agreed = !agreed">
          <text v-if="agreed">✓</text>
        </view>
        <text class="agreement-text">我已阅读并同意</text>
        <text class="agreement-link">《用户协议》</text>
        <text class="agreement-text">和</text>
        <text class="agreement-link">《隐私政策》</text>
      </view>

      <view class="register-btn" :class="{ disabled: !isFormValid }" @click="handleRegister">
        <text class="btn-text">注册</text>
      </view>

      <view class="login-row">
        <text class="login-text">已有账号？</text>
        <text class="login-link" @click="goToLogin">立即登录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const nickname = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const agreed = ref(false)

const isFormValid = computed(() => {
  return (
    nickname.value &&
    email.value &&
    password.value.length >= 6 &&
    password.value === confirmPassword.value &&
    agreed.value
  )
})

async function handleRegister() {
  if (!isFormValid.value) {
    if (password.value !== confirmPassword.value) {
      uni.showToast({ title: '两次密码不一致', icon: 'none' })
    } else {
      uni.showToast({ title: '请填写完整信息', icon: 'none' })
    }
    return
  }

  uni.showLoading({ title: '注册中...' })

  const result = await userStore.register(email.value, password.value, nickname.value)

  uni.hideLoading()

  if (result.success) {
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1000)
  } else {
    uni.showToast({ title: result.error || '注册失败', icon: 'none' })
  }
}

function goBack() {
  uni.navigateBack()
}

function goToLogin() {
  uni.redirectTo({ url: '/pages/auth/login' })
}
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  background: $bg;
}

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

.form-section {
  padding: 20px;
}

.input-group {
  margin-bottom: 16px;
  
  .input-label {
    display: block;
    font-size: 14px;
    color: $ink;
    margin-bottom: 8px;
    font-weight: 500;
  }
  
  .input-field {
    width: 100%;
    padding: 14px 16px;
    border: 1px solid $rule;
    border-radius: 12px;
    font-size: 16px;
    color: $ink;
    background: $bg2;
    
    &:focus {
      border-color: $accent;
      outline: none;
    }
  }
}

.agreement-row {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  
  .checkbox {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid $rule;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;
    color: #fff;
    font-size: 12px;
    
    &.checked {
      background: $accent;
      border-color: $accent;
    }
  }
  
  .agreement-text {
    font-size: 13px;
    color: $muted;
  }
  
  .agreement-link {
    font-size: 13px;
    color: $accent;
  }
}

.register-btn {
  width: 100%;
  padding: 16px;
  background: $accent;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 20px;
  
  &.disabled {
    opacity: 0.5;
  }
  
  .btn-text {
    font-size: 18px;
    font-weight: 600;
    color: #fff;
  }
}

.login-row {
  text-align: center;
  
  .login-text {
    font-size: 14px;
    color: $muted;
  }
  
  .login-link {
    font-size: 14px;
    color: $accent;
    margin-left: 4px;
  }
}
</style>