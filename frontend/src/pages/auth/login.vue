<template>
  <view class="login-page">
    <view class="logo-section">
      <text class="logo-emoji">🌍</text>
      <text class="app-name">StudyMate学习星球</text>
      <text class="app-slogan">让知识进脑子而不是走过场</text>
    </view>

    <view class="form-section">
      <view class="input-group">
        <text class="input-label">邮箱</text>
        <view class="input-wrapper">
          <input class="input-field" v-model="email" placeholder="请输入邮箱" type="email" />
        </view>
      </view>

      <view class="input-group">
        <text class="input-label">密码</text>
        <view class="input-wrapper">
          <input class="input-field" v-model="password" placeholder="请输入密码" type="password" />
        </view>
      </view>

      <view class="remember-row">
        <view class="checkbox" :class="{ checked: rememberMe }" @click="rememberMe = !rememberMe">
          <text v-if="rememberMe">✓</text>
        </view>
        <text class="remember-text">记住我</text>
        <text class="forgot-link">忘记密码？</text>
      </view>

      <view class="login-btn" :class="{ disabled: !isFormValid }" @click="handleLogin">
        <text class="btn-text">登录</text>
      </view>

      <view class="register-row">
        <text class="register-text">还没有账号？</text>
        <text class="register-link" @click="goToRegister">立即注册</text>
      </view>
    </view>

    <view class="footer">
      <text class="footer-text">StudyMate学习星球 - AI抗遗忘备考工具</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)

const isFormValid = computed(() => {
  return email.value && password.value && password.value.length >= 6
})

async function handleLogin() {
  if (!isFormValid.value) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' })
    return
  }

  uni.showLoading({ title: '登录中...' })

  const result = await userStore.login(email.value, password.value)

  uni.hideLoading()

  if (result.success) {
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1000)
  } else {
    uni.showToast({ title: result.error || '登录失败', icon: 'none' })
  }
}

function goToRegister() {
  uni.navigateTo({ url: '/pages/auth/register' })
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--color-header-green-start, #2f7d4f) 0%, var(--color-header-green-end, #4a9d6a) 100%);
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
}

.logo-section {
  text-align: center;
  padding: 60px 0 40px;
  
  .logo-emoji {
    display: block;
    font-size: 64px;
    margin-bottom: 20px;
  }
  
  .app-name {
    display: block;
    font-size: 28px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 8px;
  }
  
  .app-slogan {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
  }
}

.form-section {
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  margin-bottom: auto;
}

.input-group {
  margin-bottom: 20px;
  
  .input-label {
    display: block;
    font-size: 14px;
    color: $ink;
    margin-bottom: 8px;
    font-weight: 500;
  }
  
  .input-field {
    width: 100%;
    font-size: 16px;
    color: $ink;
    border: none;
    outline: none;
    background: transparent;
    padding: 0;
    line-height: 1.5;
  }

  .input-wrapper {
    width: 100%;
    padding: 14px 16px;
    border: 1px solid $rule;
    border-radius: 12px;
    background: $bg2;
    
    &:focus-within {
      border-color: $accent;
    }
  }
}

.remember-row {
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
  
  .remember-text {
    flex: 1;
    font-size: 14px;
    color: $muted;
  }
  
  .forgot-link {
    font-size: 14px;
    color: $accent;
  }
}

.login-btn {
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

.register-row {
  text-align: center;
  
  .register-text {
    font-size: 14px;
    color: $muted;
  }
  
  .register-link {
    font-size: 14px;
    color: $accent;
    margin-left: 4px;
  }
}

.footer {
  text-align: center;
  padding-top: 20px;
  
  .footer-text {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
  }
}
</style>