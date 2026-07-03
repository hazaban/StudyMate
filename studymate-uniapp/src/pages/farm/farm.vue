<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <text class="title">学习农场</text>
        <text class="subtitle">每一份努力，都会种出果实</text>
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

        <view class="plant-actions">
          <view class="water-btn" v-if="plant.type !== 'harvested' && plant.type !== 'mature'" @click="water(plant)">
            <text class="water-icon">💧</text>
            <text class="water-text">浇水</text>
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
      <text class="empty-hint">创建学习计划后，开始学习即可种下第一株植物</text>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { onMounted } from 'vue'
import { useFarmStore } from '@/stores/farm'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'

const farmStore = useFarmStore()
const planStore = usePlanStore()
const userStore = useUserStore()

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
  const result = await farmStore.waterPlant(plant.id)
  if (result.success) {
    uni.showToast({ title: '💧 浇水成功！+5XP', icon: 'none' })
  }
}

async function harvest(plant) {
  const result = await farmStore.harvestPlant(plant.id)
  if (result.success) {
    uni.showToast({ title: '🌾 收获成功！+50金币', icon: 'none' })
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    if (planStore.currentPlan) {
      await farmStore.getPlantsByPlanId(planStore.currentPlan.id)
    }
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
  margin-bottom: 16px;
  
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
  margin-bottom: 12px;
  
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

.plant-actions {
  width: 100%;
}

.water-btn, .harvest-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px;
  border-radius: 12px;
  transition: all 0.2s;
  
  &:active { transform: scale(0.95); }
}

.water-btn {
  background: #e3f2fd;
  .water-icon { font-size: 16px; }
  .water-text { font-size: 13px; color: #1976d2; font-weight: 500; }
}

.harvest-btn {
  background: #fff3e0;
  .harvest-icon { font-size: 16px; }
  .harvest-text { font-size: 13px; color: #e65100; font-weight: 500; }
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
</style>