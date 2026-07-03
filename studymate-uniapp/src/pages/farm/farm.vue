<template>
  <view class="page">
    <view class="header">
      <text class="title">学习农场</text>
      <view class="coins">
        <text class="coins-icon">🪙</text>
        <text class="coins-num">{{ farmStore.coins || 0 }}</text>
      </view>
    </view>

    <view class="farm-field">
      <view class="crop-card" v-for="plant in farmStore.plants" :key="plant.id">
        <view class="crop-icon">{{ getCropIcon(plant.type) }}</view>
        <view class="crop-info">
          <text class="crop-name">{{ plant.subject }}</text>
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: plant.progress + '%' }"></view>
          </view>
          <text class="crop-stage">{{ getStageLabel(plant.type) }}</text>
        </view>
        <view class="crop-actions">
          <view class="crop-btn water-btn" @click="waterCrop(plant)" v-if="plant.type !== 'harvested'">
            <text>💧</text>
          </view>
          <view class="crop-btn fertilize-btn" @click="fertilizeCrop(plant)" v-if="plant.type !== 'harvested'">
            <text>🪴</text>
          </view>
          <view class="crop-btn harvest-btn" @click="harvestCrop(plant)" v-if="plant.type === 'mature'">
            <text>🧺 收获</text>
          </view>
        </view>
      </view>

      <view class="empty" v-if="farmStore.plants.length === 0">
        <text class="empty-icon">🌱</text>
        <text class="empty-text">农场空空如也</text>
        <text class="empty-hint">完成今日任务或番茄钟后，作物会自动出现</text>
      </view>
    </view>

    <view class="rules-section">
      <text class="rules-title">农场规则</text>
      <view class="rule-item">
        <text class="rule-icon">✅</text>
        <text class="rule-text">完成一个小任务 → 获得一袋肥料（+10%进度）</text>
      </view>
      <view class="rule-item">
        <text class="rule-icon">🍅</text>
        <text class="rule-text">完成一个番茄钟 → 获得一次浇水（+20%进度）</text>
      </view>
      <view class="rule-item">
        <text class="rule-icon">📚</text>
        <text class="rule-text">完成一个章节 → 成熟一颗作物</text>
      </view>
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

function getCropIcon(type) {
  const map = { seed: '🌱', sprout: '🌿', growing: '🌳', mature: '🍎', harvested: '🧺' }
  return map[type] || '🌱'
}

function getStageLabel(type) {
  const map = { seed: '种子', sprout: '发芽', growing: '生长中', mature: '已成熟', harvested: '已收获' }
  return map[type] || '种子'
}

async function waterCrop(plant) {
  const result = await farmStore.waterPlant(plant.id)
  if (result.success) {
    uni.showToast({ title: '浇水成功！', icon: 'success' })
  }
}

async function fertilizeCrop(plant) {
  const result = await farmStore.fertilizePlant(plant.id)
  if (result.success) {
    uni.showToast({ title: '施肥成功！', icon: 'success' })
  }
}

async function harvestCrop(plant) {
  const result = await farmStore.harvestPlant(plant.id)
  if (result.success) {
    uni.showToast({ title: '收获成功！+50金币', icon: 'success' })
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    if (planStore.currentPlan) {
      await farmStore.getFarmState(planStore.currentPlan.id)
    }
  }
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40px 0 20px;
  .title { font-size: 22px; font-weight: 700; color: #1a1a2e; }
  .coins { display: flex; align-items: center; gap: 4px; background: #fff8e1; padding: 8px 16px; border-radius: 20px; }
  .coins-icon { font-size: 18px; }
  .coins-num { font-size: 16px; font-weight: 600; color: #f57f17; }
}

.farm-field {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.crop-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  border: 1px solid #e8ece9;
  .crop-icon { font-size: 40px; margin-bottom: 8px; }
  .crop-info { margin-bottom: 10px; }
  .crop-name { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 6px; }
  .progress-bar { height: 6px; background: #e8ece9; border-radius: 3px; overflow: hidden; margin-bottom: 4px; }
  .progress-fill { height: 100%; background: #2f7d4f; border-radius: 3px; transition: width 0.3s; }
  .crop-stage { font-size: 11px; color: #999; }
  .crop-actions { display: flex; gap: 8px; justify-content: center; }
  .crop-btn { padding: 6px 12px; border-radius: 8px; font-size: 12px; &.water-btn { background: #e3f2fd; } &.fertilize-btn { background: #fff3e0; } &.harvest-btn { background: #e8f5e9; color: #2e7d32; font-weight: 600; } }
}

.empty { grid-column: 1 / -1; text-align: center; padding: 40px 20px; .empty-icon { font-size: 48px; } .empty-text { display: block; font-size: 16px; color: #65746d; margin: 8px 0; } .empty-hint { display: block; font-size: 13px; color: #999; } }

.rules-section {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #e8ece9;
  .rules-title { font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 12px; display: block; }
  .rule-item { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; &:last-child { margin-bottom: 0; } }
  .rule-icon { font-size: 16px; }
  .rule-text { font-size: 13px; color: #65746d; }
}

.bottom-space { height: 100px; }
</style>