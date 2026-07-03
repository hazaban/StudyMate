<template>
  <view class="page">
    <view class="header">
      <text class="page-title">学习农场</text>
      <view class="level-info">
        <text class="level-icon">🌾</text>
        <text class="level-text">Lv.{{ farmStore.level }}</text>
      </view>
    </view>

    <view class="status-bar">
      <view class="status-item">
        <text class="status-icon">💰</text>
        <text class="status-value">{{ farmStore.coins }}</text>
        <text class="status-label">金币</text>
      </view>
      <view class="status-item">
        <text class="status-icon">⭐</text>
        <text class="status-value">{{ farmStore.experience }}</text>
        <text class="status-label">经验</text>
      </view>
      <view class="status-item">
        <text class="status-icon">🌱</text>
        <text class="status-value">{{ farmStore.totalProgress }}%</text>
        <text class="status-label">总进度</text>
      </view>
    </view>

    <view class="farm-field">
      <view class="field-grid">
        <view class="plant-cell" v-for="plant in farmStore.plants" :key="plant.id">
          <view class="plant-container" @click="interactWithPlant(plant)">
            <view class="plant-emoji" :class="plant.type">
              {{ getPlantEmoji(plant.type) }}
            </view>
            <view class="plant-progress-bar">
              <view class="plant-progress-fill" :style="{ width: plant.progress + '%' }"></view>
            </view>
            <text class="plant-name">{{ plant.subject }}</text>
            <text class="plant-action" v-if="plant.type !== 'harvested'">
              {{ getPlantAction(plant.type) }}
            </text>
          </view>
        </view>
        
        <view class="plant-cell empty" @click="addPlant">
          <view class="add-plant-btn">
            <text class="add-icon">+</text>
            <text class="add-text">种植</text>
          </view>
        </view>
      </view>
    </view>

    <view class="store-section">
      <view class="section-header">
        <text class="section-title">商店</text>
      </view>
      <view class="store-grid">
        <view class="store-item" v-for="item in storeItems" :key="item.id">
          <view class="store-emoji">{{ item.emoji }}</view>
          <text class="store-name">{{ item.name }}</text>
          <text class="store-price">{{ item.price }} 💰</text>
          <view class="store-btn" @click="buyItem(item)">购买</view>
        </view>
      </view>
    </view>

    <view class="harvest-history">
      <view class="section-header">
        <text class="section-title">收获记录</text>
      </view>
      <view class="history-list">
        <view class="history-item" v-for="(plant, index) in farmStore.maturePlants" :key="plant.id">
          <text class="history-emoji">🎉</text>
          <view class="history-info">
            <text class="history-name">{{ plant.subject }} 植物成熟！</text>
            <text class="history-date">{{ formatDate(plant.updated_at) }}</text>
          </view>
          <text class="history-reward">+50 💰</text>
        </view>
        <view class="empty-history" v-if="farmStore.maturePlants.length === 0">
          <text class="empty-text">还没有收获记录，快去照顾你的植物吧！</text>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFarmStore } from '@/stores/farm'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'

const farmStore = useFarmStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const storeItems = ref([
  { id: 1, emoji: '🌱', name: '种子包', price: 10, description: '种植新植物' },
  { id: 2, emoji: '💧', name: '加速肥料', price: 20, description: '植物成长速度+20%' },
  { id: 3, emoji: '✨', name: '幸运符', price: 50, description: '收获时获得双倍奖励' },
  { id: 4, emoji: '🏠', name: '温室', price: 100, description: '解锁更多种植格子' }
])

function getPlantEmoji(type) {
  const map = {
    seed: '🌰',
    sprout: '🌱',
    growing: '🌿',
    mature: '🌳',
    harvested: '🎁'
  }
  return map[type] || '🌱'
}

function getPlantAction(type) {
  const map = {
    seed: '浇水',
    sprout: '浇水',
    growing: '浇水',
    mature: '收获'
  }
  return map[type] || ''
}

async function interactWithPlant(plant) {
  if (plant.type === 'mature') {
    const result = await farmStore.harvestPlant(plant.id)
    if (result.success) {
      uni.showToast({ title: '收获成功！', icon: 'success' })
    }
  } else if (plant.type !== 'harvested') {
    const result = await farmStore.waterPlant(plant.id)
    if (result.success) {
      uni.showToast({ title: '浇水成功！', icon: 'success' })
    }
  }
}

async function addPlant() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先设置学习计划', icon: 'none' })
    return
  }

  const subjects = Object.keys(planStore.currentPlan.target_scores || {})
  if (subjects.length === 0) {
    uni.showToast({ title: '请先添加科目', icon: 'none' })
    return
  }

  if (farmStore.coins < 10) {
    uni.showToast({ title: '金币不足', icon: 'none' })
    return
  }

  const subject = subjects[Math.floor(Math.random() * subjects.length)]
  const result = await farmStore.plantSeed(subject, planStore.currentPlan.id)
  
  if (result.success) {
    farmStore.coins -= 10
    uni.showToast({ title: `种植了${subject}植物！`, icon: 'success' })
  }
}

function buyItem(item) {
  if (farmStore.coins < item.price) {
    uni.showToast({ title: '金币不足', icon: 'none' })
    return
  }
  
  farmStore.coins -= item.price
  uni.showToast({ title: `购买了${item.name}！`, icon: 'success' })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

onMounted(async () => {
  await userStore.getUserInfo()
  
  if (userStore.isLoggedIn && userStore.user) {
    await planStore.getPlansByUserId(userStore.user.id)
    
    if (planStore.currentPlan) {
      await farmStore.getPlantsByPlanId(planStore.currentPlan.id)
    }
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, #8bc34a 0%, #689f38 100%);
  border-radius: 0 0 30px 30px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  
  .page-title {
    font-size: 28px;
    font-weight: 700;
    color: #fff;
  }
  
  .level-info {
    display: flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.2);
    padding: 6px 12px;
    border-radius: 20px;
    
    .level-icon {
      font-size: 14px;
    }
    
    .level-text {
      font-size: 14px;
      color: #fff;
      font-weight: 500;
    }
  }
}

.status-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.status-item {
  flex: 1;
  background: $bg2;
  border-radius: 12px;
  padding: 14px;
  text-align: center;
  border: 1px solid $rule;
  
  .status-icon {
    display: block;
    font-size: 20px;
    margin-bottom: 4px;
  }
  
  .status-value {
    display: block;
    font-size: 20px;
    font-weight: 700;
    color: $ink;
    margin-bottom: 2px;
  }
  
  .status-label {
    font-size: 12px;
    color: $muted;
  }
}

.farm-field {
  background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 100%);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 20px;
  border: 2px solid #8bc34a;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.plant-cell {
  aspect-ratio: 1;
  
  &.empty {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.plant-container {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.plant-emoji {
  font-size: 36px;
  margin-bottom: 8px;
  
  &.seed { animation: bounce 2s infinite; }
  &.sprout { animation: sway 3s infinite; }
  &.growing { animation: grow 2s infinite; }
  &.mature { animation: shine 1.5s infinite; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

@keyframes sway {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

@keyframes grow {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes shine {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.plant-progress-bar {
  width: 100%;
  height: 4px;
  background: #ddd;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 6px;
}

.plant-progress-fill {
  height: 100%;
  background: $accent;
  border-radius: 2px;
}

.plant-name {
  font-size: 12px;
  color: $ink;
  font-weight: 500;
  margin-bottom: 4px;
}

.plant-action {
  font-size: 10px;
  color: $accent;
  padding: 2px 8px;
  background: $soft;
  border-radius: 8px;
}

.add-plant-btn {
  width: 100%;
  height: 100%;
  border: 2px dashed #8bc34a;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  .add-icon {
    font-size: 32px;
    color: #8bc34a;
    margin-bottom: 4px;
  }
  
  .add-text {
    font-size: 12px;
    color: #8bc34a;
    font-weight: 500;
  }
}

.section-header {
  margin-bottom: 12px;
  
  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: $ink;
  }
}

.store-section {
  margin-bottom: 20px;
}

.store-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.store-item {
  background: $bg2;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  border: 1px solid $rule;
  
  .store-emoji {
    font-size: 28px;
    margin-bottom: 8px;
  }
  
  .store-name {
    display: block;
    font-size: 14px;
    color: $ink;
    margin-bottom: 4px;
  }
  
  .store-price {
    display: block;
    font-size: 12px;
    color: $accent;
    margin-bottom: 8px;
  }
  
  .store-btn {
    padding: 6px 12px;
    background: $accent;
    color: #fff;
    border-radius: 8px;
    font-size: 12px;
  }
}

.harvest-history {
  margin-bottom: 20px;
}

.history-list {
  background: $bg2;
  border-radius: 12px;
  padding: 12px;
  border: 1px solid $rule;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid $rule;
  
  &:last-child {
    border-bottom: none;
  }
  
  .history-emoji {
    font-size: 20px;
  }
  
  .history-info {
    flex: 1;
    
    .history-name {
      display: block;
      font-size: 14px;
      color: $ink;
      margin-bottom: 2px;
    }
    
    .history-date {
      font-size: 12px;
      color: $muted;
    }
  }
  
  .history-reward {
    font-size: 14px;
    color: $accent;
    font-weight: 600;
  }
}

.empty-history {
  padding: 20px;
  text-align: center;
  
  .empty-text {
    font-size: 14px;
    color: $muted;
  }
}

.bottom-space {
  height: 100px;
}
</style>