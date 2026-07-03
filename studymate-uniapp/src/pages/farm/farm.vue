<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <view class="header-left">
          <text class="title">学习农场</text>
          <text class="subtitle">每一份努力，都会种出果实</text>
        </view>
        <view class="guide-btn" @click="showGuide = true">
          <text class="guide-icon">❓</text>
          <text class="guide-text">说明</text>
        </view>
      </view>
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-icon">🪙</text>
          <text class="stat-num">{{ farmStore.coins }}</text>
          <text class="stat-label">金币</text>
        </view>
        <view class="stat-item">
          <text class="stat-icon">⭐</text>
          <text class="stat-num">Lv.{{ farmStore.level }}</text>
          <text class="stat-label">{{ farmStore.experience }} XP</text>
        </view>
        <view class="stat-item">
          <text class="stat-icon">🌱</text>
          <text class="stat-num">{{ farmStore.activePlants.length }}</text>
          <text class="stat-label">生长中</text>
        </view>
      </view>
    </view>

    <view class="farm-grid">
      <view class="plant-card" v-for="plant in farmStore.plants" :key="plant.id" :class="plant.type">
        <view class="plant-emoji">{{ getPlantEmoji(plant.type) }}</view>
        <text class="plant-name">{{ plant.subject }}</text>
        
        <view class="plant-progress-wrap">
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: plant.progress + '%' }"></view>
          </view>
          <text class="progress-text">{{ plant.progress }}%</text>
        </view>

        <view class="plant-counts" v-if="plant.type !== 'harvested'">
          <view class="count-item water">
            <text class="count-icon">💧</text>
            <text class="count-num">{{ plant.water_count || 0 }}</text>
          </view>
          <view class="count-item fertilizer">
            <text class="count-icon">🧪</text>
            <text class="count-num">{{ plant.fertilize_count || 0 }}</text>
          </view>
        </view>

        <view class="plant-actions">
          <view class="water-btn" 
                v-if="plant.type !== 'harvested' && plant.type !== 'mature'"
                :class="{ disabled: !(plant.water_count > 0) }"
                @click="water(plant)">
            <text class="water-icon">💧</text>
            <text class="water-text">浇水</text>
          </view>
          <view class="fertilize-btn" 
                v-if="plant.type !== 'harvested' && plant.type !== 'mature'"
                :class="{ disabled: !(plant.fertilize_count > 0) }"
                @click="fertilize(plant)">
            <text class="fertilize-icon">🧪</text>
            <text class="fertilize-text">施肥</text>
          </view>
          <view class="harvest-btn" v-if="plant.type === 'mature'" @click="harvest(plant)">
            <text class="harvest-icon">🌾</text>
            <text class="harvest-text">收获</text>
          </view>
          <view class="done-label" v-if="plant.type === 'harvested'">
            <text>✅ 已收获</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty" v-if="farmStore.plants.length === 0">
      <text class="empty-icon">🌍</text>
      <text class="empty-text">农场还是空的</text>
      <text class="empty-hint">完成番茄钟或任务，自动种下对应科目的植物</text>
    </view>

    <view class="bottom-space"></view>

    <!-- 说明弹窗 -->
    <view class="guide-mask" v-if="showGuide" @click="showGuide = false">
      <view class="guide-dialog" @click.stop>
        <view class="guide-header">
          <text class="guide-title">📖 农场奖励说明</text>
          <view class="guide-close" @click="showGuide = false">✕</view>
        </view>
        <scroll-view scroll-y class="guide-body">
          <view class="guide-section">
            <text class="guide-section-title">🌱 如何获得植物</text>
            <view class="guide-item">
              <text class="guide-item-icon">🍅</text>
              <view class="guide-item-content">
                <text class="guide-item-name">完成番茄钟</text>
                <text class="guide-item-desc">每完成一个番茄钟，自动为对应科目种下一株植物（如尚未种植）</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">✅</text>
              <view class="guide-item-content">
                <text class="guide-item-name">完成每日任务</text>
                <text class="guide-item-desc">每完成一个任务，自动为对应科目种下一株植物（如尚未种植）</text>
              </view>
            </view>
          </view>

          <view class="guide-section">
            <text class="guide-section-title">💧 浇水与施肥</text>
            <view class="guide-item">
              <text class="guide-item-icon">🍅</text>
              <view class="guide-item-content">
                <text class="guide-item-name">完成番茄钟 → 💧 +1 浇水次数</text>
                <text class="guide-item-desc">每完成一个番茄钟，对应科目植物的浇水次数 +1，每次浇水 +15% 进度，+5 XP</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">✅</text>
              <view class="guide-item-content">
                <text class="guide-item-name">完成任务 → 🧪 +1 施肥次数</text>
                <text class="guide-item-desc">每完成一个每日任务，对应科目植物的施肥次数 +1，每次施肥 +30% 进度，+12 XP</text>
              </view>
            </view>
          </view>

          <view class="guide-section">
            <text class="guide-section-title">🌻 植物成长阶段</text>
            <view class="guide-item">
              <text class="guide-item-icon">🌰</text>
              <view class="guide-item-content">
                <text class="guide-item-name">种子 (0-29%)</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">🌱</text>
              <view class="guide-item-content">
                <text class="guide-item-name">发芽 (30-69%)</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">🌿</text>
              <view class="guide-item-content">
                <text class="guide-item-name">成长 (70-99%)</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">🌻</text>
              <view class="guide-item-content">
                <text class="guide-item-name">成熟 (100%)</text>
              </view>
            </view>
          </view>

          <view class="guide-section">
            <text class="guide-section-title">🏆 收获奖励</text>
            <view class="guide-item">
              <text class="guide-item-icon">🌾</text>
              <view class="guide-item-content">
                <text class="guide-item-name">收获成熟植物</text>
                <text class="guide-item-desc">获得 +50 金币，+20 XP</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">🪙</text>
              <view class="guide-item-content">
                <text class="guide-item-name">金币用途</text>
                <text class="guide-item-desc">10 金币可手动种植一株新植物</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">⭐</text>
              <view class="guide-item-content">
                <text class="guide-item-name">等级经验</text>
                <text class="guide-item-desc">每次浇水 +5 XP，每次施肥 +12 XP，收获 +20 XP</text>
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="guide-footer">
          <view class="guide-confirm-btn" @click="showGuide = false">我知道了</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useFarmStore } from '@/stores/farm'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'

const farmStore = useFarmStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const showGuide = ref(false)

const getPlantEmoji = (type) => {
  const map = {
    seed: '🌰',
    sprout: '🌱',
    growing: '🌿',
    mature: '🌻',
    harvested: '🏆'
  }
  return map[type] || '🌰'
}

async function water(plant) {
  if (!(plant.water_count > 0)) {
    uni.showToast({ title: '浇水次数不足，完成番茄钟可获得', icon: 'none' })
    return
  }
  const result = await farmStore.waterPlant(plant.id)
  if (result.success) {
    uni.showToast({ title: '💧 浇水成功！+5 XP', icon: 'none' })
  } else {
    uni.showToast({ title: result.error || '浇水失败', icon: 'none' })
  }
}

async function fertilize(plant) {
  if (!(plant.fertilize_count > 0)) {
    uni.showToast({ title: '施肥次数不足，完成任务可获得', icon: 'none' })
    return
  }
  const result = await farmStore.fertilizePlant(plant.id)
  if (result.success) {
    uni.showToast({ title: '🧪 施肥成功！+12 XP', icon: 'none' })
  } else {
    uni.showToast({ title: result.error || '施肥失败', icon: 'none' })
  }
}

async function harvest(plant) {
  const result = await farmStore.harvestPlant(plant.id)
  if (result.success) {
    uni.showToast({ title: '🌾 收获成功！+50金币', icon: 'none' })
  } else {
    uni.showToast({ title: result.error || '收获失败', icon: 'none' })
  }
}

async function loadFarm() {
  if (planStore.currentPlan) {
    await farmStore.getPlantsByPlanId(planStore.currentPlan.id)
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    if (planStore.currentPlan) {
      await loadFarm()
    }
  }
})

onShow(async () => {
  if (userStore.isLoggedIn && planStore.currentPlan) {
    await loadFarm()
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, #e8a838 0%, #f0c060 100%);
  border-radius: 0 0 32px 32px;
  margin-bottom: 24px;
  margin-left: -20px;
  margin-right: -20px;
  padding-left: 20px;
  padding-right: 20px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.header-left {
  .title {
    display: block;
    font-size: 26px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 4px;
  }
  .subtitle {
    font-size: 14px;
    color: rgba(255,255,255,0.8);
  }
}

.guide-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  background: rgba(255,255,255,0.2);
  padding: 8px 12px;
  border-radius: 12px;
  &:active { background: rgba(255,255,255,0.3); transform: scale(0.96); }
  .guide-icon { font-size: 18px; }
  .guide-text { font-size: 11px; color: #fff; font-weight: 500; }
}

.stats-row {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.15);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(255,255,255,0.2);
}

.stat-item {
  flex: 1;
  text-align: center;
  
  .stat-icon {
    font-size: 20px;
    display: block;
    margin-bottom: 4px;
  }
  .stat-num {
    display: block;
    font-size: 18px;
    font-weight: 700;
    color: #fff;
  }
  .stat-label {
    font-size: 12px;
    color: rgba(255,255,255,0.7);
    margin-top: 2px;
  }
}

.farm-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.plant-card {
  background: #fff;
  border-radius: 18px;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid #e8ece9;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
  transition: all 0.2s;
  
  &:active { transform: scale(0.97); }
  
  &.seed { border-color: #e8d5c4; background: #fdf8f4; }
  &.sprout { border-color: #c8e6c9; background: #f4fbf4; }
  &.growing { border-color: #a5d6a7; background: #f0faf0; }
  &.mature { border-color: #ffcc80; background: #fff8f0; }
  &.harvested { border-color: #e0e0e0; background: #f8f8f8; opacity: 0.7; }
}

.plant-emoji {
  font-size: 48px;
  margin-bottom: 8px;
  animation: bounce 2s ease infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.plant-card.sprout .plant-emoji { animation-duration: 1.5s; }
.plant-card.growing .plant-emoji { animation-duration: 1s; }
.plant-card.mature .plant-emoji { animation-duration: 0.6s; }

.plant-name {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.plant-progress-wrap {
  width: 100%;
  margin-bottom: 10px;
  
  .progress-bar {
    height: 6px;
    background: #f0f0f0;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 4px;
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4caf50, #81c784);
    border-radius: 3px;
    transition: width 0.5s ease;
  }
  
  .progress-text {
    font-size: 11px;
    color: #999;
    text-align: right;
    display: block;
  }
}

.plant-counts {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 10px;
  width: 100%;
}

.count-item {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 4px 8px;
  border-radius: 10px;
  
  &.water { background: #e3f2fd; }
  &.fertilizer { background: #f3e5f5; }
  
  .count-icon { font-size: 13px; }
  .count-num { font-size: 12px; font-weight: 600; }
  
  &.water .count-num { color: #1976d2; }
  &.fertilizer .count-num { color: #7b1fa2; }
}

.plant-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.water-btn, .fertilize-btn, .harvest-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px;
  border-radius: 10px;
  transition: all 0.2s;
  
  &:active { transform: scale(0.95); }
  
  &.disabled {
    opacity: 0.45;
    pointer-events: none;
  }
}

.water-btn {
  background: #e3f2fd;
  .water-icon { font-size: 14px; }
  .water-text { font-size: 12px; color: #1976d2; font-weight: 500; }
}

.fertilize-btn {
  background: #f3e5f5;
  .fertilize-icon { font-size: 14px; }
  .fertilize-text { font-size: 12px; color: #7b1fa2; font-weight: 500; }
}

.harvest-btn {
  background: #fff3e0;
  .harvest-icon { font-size: 14px; }
  .harvest-text { font-size: 12px; color: #e65100; font-weight: 500; }
}

.done-label {
  text-align: center;
  font-size: 13px;
  color: #999;
  padding: 10px;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  
  .empty-icon { font-size: 56px; margin-bottom: 12px; }
  .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; }
  .empty-hint { font-size: 13px; color: #999; text-align: center; line-height: 1.6; }
}

.bottom-space { height: 100px; }

/* 说明弹窗 */
.guide-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 40px 24px;
}

.guide-dialog {
  width: 100%;
  max-width: 480px;
  max-height: 80vh;
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.guide-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
}

.guide-close {
  font-size: 18px;
  color: #999;
  padding: 4px;
  line-height: 1;
}

.guide-body {
  flex: 1;
  padding: 16px 20px;
  overflow-y: auto;
}

.guide-section {
  margin-bottom: 20px;
  
  &:last-child { margin-bottom: 0; }
}

.guide-section-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.guide-item {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: #f9f9f9;
  border-radius: 12px;
  margin-bottom: 8px;
  
  &:last-child { margin-bottom: 0; }
}

.guide-item-icon {
  font-size: 22px;
  flex-shrink: 0;
  width: 28px;
  text-align: center;
}

.guide-item-content {
  flex: 1;
  min-width: 0;
}

.guide-item-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 3px;
}

.guide-item-desc {
  display: block;
  font-size: 12px;
  color: #888;
  line-height: 1.5;
}

.guide-footer {
  padding: 16px 20px 20px;
  border-top: 1px solid #f0f0f0;
}

.guide-confirm-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #e8a838 0%, #f0c060 100%);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  text-align: center;
  border-radius: 14px;
  
  &:active { opacity: 0.9; transform: scale(0.98); }
}
</style>
