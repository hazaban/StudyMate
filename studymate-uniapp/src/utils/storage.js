export const storage = {
  getItem(key) {
    try {
      const value = uni.getStorageSync(key)
      return value ? JSON.parse(value) : null
    } catch {
      return uni.getStorageSync(key)
    }
  },

  setItem(key, value) {
    try {
      uni.setStorageSync(key, JSON.stringify(value))
    } catch {
      uni.setStorageSync(key, value)
    }
  },

  removeItem(key) {
    uni.removeStorageSync(key)
  },

  clear() {
    uni.clearStorageSync()
  },

  getToken() {
    return this.getItem('token')
  },

  setToken(token) {
    this.setItem('token', token)
  },

  removeToken() {
    this.removeItem('token')
  },

  getUserId() {
    return this.getItem('userId')
  },

  setUserId(userId) {
    this.setItem('userId', userId)
  },

  removeUserId() {
    this.removeItem('userId')
  },

  getCurrentPlanId() {
    return this.getItem('currentPlanId')
  },

  setCurrentPlanId(planId) {
    this.setItem('currentPlanId', planId)
  },

  removeCurrentPlanId() {
    this.removeItem('currentPlanId')
  }
}