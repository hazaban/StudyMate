<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <view class="header-left">
          <view class="back-btn" @click="goBack">
            <text class="back-icon">←</text>
          </view>
          <view>
            <text class="title">学习农场</text>
            <text class="subtitle">每一份努力，都会种出果实</text>
          </view>
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

    <view class="subject-list">
      <view class="subject-card" v-for="group in subjectGroups" :key="group.subject">
        <view class="subject-card-header">
          <view class="subject-card-title">
            <text class="subject-emoji">{{ getPlantEmoji(group.mainType) }}</text>
            <text class="subject-name">{{ group.subject }}</text>
          </view>
          <text class="subject-count-badge">×{{ group.plants.length }}</text>
        </view>

        <scroll-view scroll-x class="plants-scroll" v-if="group.plants.length > 0">
          <view class="plants-row">
            <view class="plant-mini-card" v-for="plant in group.plants" :key="plant.id" :class="plant.type">
              <view class="mini-emoji">{{ getPlantEmoji(plant.type) }}</view>
              <view class="mini-progress-wrap">
                <view class="mini-progress-bar">
                  <view class="mini-progress-fill" :style="{ width: plant.progress + '%' }"></view>
                </view>
                <text class="mini-progress-text">{{ plant.progress }}%</text>
              </view>
              <view class="mini-counts" v-if="plant.type !== 'harvested'">
                <text class="mini-count water">💧{{ plant.water_count || 0 }}</text>
                <text class="mini-count fert">🧪{{ plant.fertilize_count || 0 }}</text>
              </view>
              <view class="mini-actions">
                <view class="mini-btn water" 
                      v-if="plant.type !== 'harvested' && plant.type !== 'mature'"
                      :class="{ disabled: !(plant.water_count > 0) }"
                      @click="water(plant)">
                  <text>💧浇水</text>
                </view>
                <view class="mini-btn fertilize" 
                      v-if="plant.type !== 'harvested' && plant.type !== 'mature'"
                      :class="{ disabled: !(plant.fertilize_count > 0) }"
                      @click="fertilize(plant)">
                  <text>🧪施肥</text>
                </view>
                <view class="mini-btn harvest" v-if="plant.type === 'mature'" @click="harvest(plant)">
                  <text>🌾收获</text>
                </view>
                <view class="mini-tag harvested" v-if="plant.type === 'harvested'">
                  <text>已收获</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
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
                <text class="guide-item-desc">浇水 2 次 或 施肥 1 次即可发芽</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">🌱</text>
              <view class="guide-item-content">
                <text class="guide-item-name">发芽 (30-69%)</text>
                <text class="guide-item-desc">再浇水 3 次 或 施肥 2 次进入成长期</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">🌿</text>
              <view class="guide-item-content">
                <text class="guide-item-name">成长 (70-99%)</text>
                <text class="guide-item-desc">再浇水 2 次 或 施肥 1 次即可成熟</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">🌻</text>
              <view class="guide-item-content">
                <text class="guide-item-name">成熟 (100%)</text>
                <text class="guide-item-desc">可以收获，获得金币和经验奖励</text>
              </view>
            </view>
          </view>

          <view class="guide-section">
            <text class="guide-section-title">🌾 关于植物数量</text>
            <view class="guide-item">
              <text class="guide-item-icon">📚</text>
              <view class="guide-item-content">
                <text class="guide-item-name">按科目分组展示</text>
                <text class="guide-item-desc">每个科目作为一个卡片，右上角显示该科目下的植物总数，卡片内可左右滑动查看所有植物</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">🍅</text>
              <view class="guide-item-content">
                <text class="guide-item-name">番茄钟与浇水</text>
                <text class="guide-item-desc">完成番茄钟会给该科目最新一株植物增加浇水次数；如果没有植物则自动种下一株新的</text>
              </view>
            </view>
            <view class="guide-item">
              <text class="guide-item-icon">✅</text>
              <view class="guide-item-content">
                <text class="guide-item-name">完成任务与施肥</text>
                <text class="guide-item-desc">完成任务会给该科目最新一株植物增加施肥次数；如果没有植物则自动种下一株新的</text>
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
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useFarmStore } from '@/stores/farm'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'

const farmStore = useFarmStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const showGuide = ref(false)
const WATER_PER = 15
const FERTILIZE_PER = 30

const subjectGroups = computed(() => {
  const map = {}
  for (const p of farmStore.plants) {
    if (!map[p.subject]) {
      map[p.subject] = { subject: p.subject, plants: [], types: [] }
    }
    map[p.subject].plants.push(p)
    map[p.subject].types.push(p.type)
  }
  const result = Object.values(map)
  for (const g of result) {
    const priority = ['mature', 'growing', 'sprout', 'seed', 'harvested']
    g.mainType = g.types.sort((a, b) => priority.indexOf(a) - priority.indexOf(b))[0]
    g.plants.sort((a, b) => {
      if (a.type === 'harvested' && b.type !== 'harvested') return 1
      if (b.type === 'harvested' && a.type !== 'harvested') return -1
      return b.progress - a.progress
    })
  }
  return result
})

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

function getWaterNeeded(plant) {
  const remain = 100 - plant.progress
  return Math.ceil(remain / WATER_PER)
}

function getFertilizeNeeded(plant) {
  const remain = 100 - plant.progress
  return Math.ceil(remain / FERTILIZE_PER)
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

function goBack() {
  uni.navigateBack()
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
  display: flex; align-items: center; gap: 12px;
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

.back-btn {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; border: 1px solid rgba(255,255,255,0.3);
  &:active { transform: scale(0.92); background: rgba(255,255,255,0.35); }
  .back-icon { font-size: 18px; color: #fff; }
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

.subject-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.subject-card {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  border: 1px solid #eef2ef;
}

.subject-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: linear-gradient(135deg, #f7f9f8 0%, #eef2ef 100%);
  border-bottom: 1px solid #eef2ef;
}

.subject-card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .subject-emoji { font-size: 22px; }
  .subject-name { font-size: 15px; font-weight: 600; color: #1a1a2e; }
}

.subject-count-badge {
  font-size: 13px;
  font-weight: 600;
  color: #667e75;
  background: rgba(102,126,117,0.1);
  padding: 4px 10px;
  border-radius: 10px;
}

.plants-scroll {
  white-space: nowrap;
  width: 100%;
}

.plants-row {
  display: inline-flex;
  gap: 10px;
  padding: 14px;
}

.plant-mini-card {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 110px;
  flex-shrink: 0;
  background: #fafbfb;
  border-radius: 14px;
  padding: 12px 10px;
  border: 1px solid #eef2ef;
  transition: all 0.2s;
  
  &.seed { border-color: #e8d5c4; background: #fdf8f4; }
  &.sprout { border-color: #c8e6c9; background: #f4fbf4; }
  &.growing { border-color: #a5d6a7; background: #f0faf0; }
  &.mature { border-color: #ffcc80; background: #fff8f0; }
  &.harvested { border-color: #e0e0e0; background: #f5f5f5; opacity: 0.7; }
}

.mini-emoji {
  font-size: 36px;
  margin-bottom: 6px;
  animation: bounce 2s ease infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.plant-mini-card.sprout .mini-emoji { animation-duration: 1.5s; }
.plant-mini-card.growing .mini-emoji { animation-duration: 1s; }
.plant-mini-card.mature .mini-emoji { animation-duration: 0.6s; }
.plant-mini-card.harvested .mini-emoji { animation: none; }

.mini-progress-wrap {
  width: 100%;
  margin-bottom: 8px;
  
  .mini-progress-bar {
    height: 4px;
    background: #e8ece9;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 3px;
  }
  .mini-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4caf50, #81c784);
    border-radius: 2px;
    transition: width 0.5s ease;
  }
  .mini-progress-text {
    font-size: 10px;
    color: #999;
    text-align: right;
    display: block;
  }
}

.mini-counts {
  display: flex;
  justify-content: center;
  gap: 6px;
  width: 100%;
  margin-bottom: 8px;
  
  .mini-count {
    font-size: 11px;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: 6px;
    
    &.water { background: #e3f2fd; color: #1976d2; }
    &.fert { background: #f3e5f5; color: #7b1fa2; }
  }
}

.mini-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mini-btn {
  text-align: center;
  padding: 6px 4px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  
  &:active { transform: scale(0.95); }
  
  &.disabled {
    opacity: 0.45;
    pointer-events: none;
  }
  
  &.water { background: #e3f2fd; color: #1976d2; }
  &.fertilize { background: #f3e5f5; color: #7b1fa2; }
  &.harvest { background: #fff3e0; color: #e65100; }
}

.mini-tag {
  text-align: center;
  padding: 6px 4px;
  font-size: 11px;
  border-radius: 8px;
  
  &.harvested {
    background: #f0f0f0;
    color: #999;
  }
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
