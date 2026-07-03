<template>
  <view class="page">
    <view class="header">
      <text class="page-title">任务看板</text>
      <text class="date-text">{{ currentDate }}</text>
    </view>

    <view class="tabs">
      <view class="tab" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
        <text class="tab-text">全部</text>
        <text class="tab-count">{{ taskStore.totalCount }}</text>
      </view>
      <view class="tab" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">
        <text class="tab-text">待完成</text>
        <text class="tab-count">{{ taskStore.pendingTasks.length }}</text>
      </view>
      <view class="tab" :class="{ active: activeTab === 'completed' }" @click="activeTab = 'completed'">
        <text class="tab-text">已完成</text>
        <text class="tab-count">{{ taskStore.completedCount }}</text>
      </view>
    </view>

    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view class="filter-item" :class="{ active: activeFilter === 'all' }" @click="activeFilter = 'all'">
            全部科目
          </view>
          <view class="filter-item" :class="{ active: activeFilter === subject }" v-for="subject in subjects" :key="subject" @click="activeFilter = subject">
            {{ subject }}
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="task-list">
      <view class="empty-state" v-if="filteredTasks.length === 0">
        <text class="empty-icon">📝</text>
        <text class="empty-text">暂无任务</text>
        <text class="empty-hint">点击下方按钮生成今日任务</text>
      </view>

      <view class="task-card" v-for="task in filteredTasks" :key="task.id">
        <view class="task-header">
          <view class="task-type-tag" :class="task.type">
            {{ taskTypeText(task.type) }}
          </view>
          <view class="task-subject-tag">{{ task.subject }}</view>
        </view>
        
        <text class="task-content">{{ task.content }}</text>
        
        <view class="task-footer">
          <view class="task-duration">
            <text class="duration-icon">⏱</text>
            <text class="duration-text">{{ task.duration }}分钟</text>
          </view>
          <view class="task-actions">
            <view class="action-btn" :class="{ completed: task.status === 'completed' }" @click="toggleTask(task)">
              {{ task.status === 'completed' ? '已完成' : '完成' }}
            </view>
            <view class="action-btn secondary" @click="startTask(task)">
              开始
            </view>
          </view>
        </view>
        
        <view class="task-proof" v-if="task.proof_image_url">
          <image :src="task.proof_image_url" mode="aspectFill" class="proof-image" />
        </view>
        
        <view class="upload-area" v-if="task.status === 'completed' && !task.proof_image_url" @click="uploadProof(task)">
          <text class="upload-icon">📷</text>
          <text class="upload-text">上传完成凭证</text>
        </view>
      </view>
    </view>

    <view class="fab-area">
      <view class="fab" @click="generateTasks">
        <text class="fab-icon">✨</text>
        <text class="fab-text">生成任务</text>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTaskStore } from '@/stores/task'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import { dateUtil } from '@/utils/date'
import { uploadUtil } from '@/utils/upload'

const taskStore = useTaskStore()
const planStore = usePlanStore()
const userStore = useUserStore()

const activeTab = ref('all')
const activeFilter = ref('all')
const currentDate = ref('')

const subjects = computed(() => {
  return [...new Set(taskStore.todayTasks.map(t => t.subject))]
})

const filteredTasks = computed(() => {
  let tasks = taskStore.todayTasks
  
  if (activeTab.value === 'pending') {
    tasks = tasks.filter(t => t.status === 'pending')
  } else if (activeTab.value === 'completed') {
    tasks = tasks.filter(t => t.status === 'completed')
  }
  
  if (activeFilter.value !== 'all') {
    tasks = tasks.filter(t => t.subject === activeFilter.value)
  }
  
  return tasks
})

function taskTypeText(type) {
  const map = {
    new_study: '新学',
    review: '复习',
    mistake: '错题'
  }
  return map[type] || type
}

async function toggleTask(task) {
  if (task.status === 'completed') {
    await taskStore.updateTask(task.id, { status: 'pending', completed_at: null })
  } else {
    await taskStore.completeTask(task.id)
    uni.showToast({ title: '任务完成！', icon: 'success' })
  }
}

function startTask(task) {
  uni.navigateTo({
    url: `/pages/daily/pomodoro?taskId=${task.id}&taskContent=${encodeURIComponent(task.content)}`
  })
}

async function uploadProof(task) {
  try {
    const [imagePath] = await uploadUtil.chooseImage(1)
    const imageUrl = await uploadUtil.uploadProof(imagePath, userStore.user.id)
    await taskStore.updateTask(task.id, { proof_image_url: imageUrl })
    uni.showToast({ title: '上传成功！', icon: 'success' })
  } catch (error) {
    uni.showToast({ title: '上传失败', icon: 'none' })
    console.error(error)
  }
}

async function generateTasks() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先设置学习计划', icon: 'none' })
    return
  }

  uni.showLoading({ title: 'AI生成任务中...' })
  
  try {
    const result = await taskStore.generateDailyTasks({
      exam_name: planStore.currentPlan.exam_name,
      date: dateUtil.today(),
      subjects: Object.keys(planStore.currentPlan.target_scores || {}),
      days_remaining: dateUtil.getDaysBetween(dateUtil.today(), planStore.currentPlan.exam_date),
      available_time: planStore.currentPlan.daily_study_time
    })

    if (result.tasks && result.tasks.length > 0) {
      for (const task of result.tasks) {
        await taskStore.createTask({
          plan_id: planStore.currentPlan.id,
          date: dateUtil.today(),
          type: task.type,
          subject: task.subject,
          content: task.content,
          duration: task.duration,
          status: 'pending'
        })
      }
      uni.showToast({ title: `生成了${result.tasks.length}个任务`, icon: 'success' })
    } else {
      uni.showToast({ title: '生成失败', icon: 'none' })
    }
  } catch (error) {
    uni.showToast({ title: '生成失败', icon: 'none' })
    console.error(error)
  } finally {
    uni.hideLoading()
  }
}

onMounted(async () => {
  currentDate.value = `${dateUtil.format(new Date(), 'YYYY年MM月DD日')} ${dateUtil.getWeekDay(new Date())}`
  
  await userStore.getUserInfo()
  
  if (userStore.isLoggedIn && userStore.user) {
    await planStore.getPlansByUserId(userStore.user.id)
    
    if (planStore.currentPlan) {
      await taskStore.getTasksByDate(planStore.currentPlan.id, dateUtil.today())
    }
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, $accent 0%, lighten($accent, 10%) 100%);
  border-radius: 0 0 30px 30px;
  margin-bottom: 20px;
  
  .page-title {
    display: block;
    font-size: 28px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 4px;
  }
  
  .date-text {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
  }
}

.tabs {
  display: flex;
  background: $bg2;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 16px;
  border: 1px solid $rule;
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.2s;
  
  &.active {
    background: $accent;
    
    .tab-text {
      color: #fff;
    }
    
    .tab-count {
      background: rgba(255, 255, 255, 0.2);
      color: #fff;
    }
  }
  
  .tab-text {
    font-size: 14px;
    color: $muted;
  }
  
  .tab-count {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 10px;
    background: $soft;
    color: $accent;
  }
}

.filter-scroll {
  white-space: nowrap;
}

.filter-list {
  display: inline-flex;
  gap: 8px;
}

.filter-item {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  background: $bg2;
  color: $muted;
  border: 1px solid $rule;
  
  &.active {
    background: $accent;
    color: #fff;
    border-color: $accent;
  }
}

.task-list {
  padding-bottom: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .empty-text {
    font-size: 18px;
    color: $ink;
    margin-bottom: 8px;
  }
  
  .empty-hint {
    font-size: 14px;
    color: $muted;
  }
}

.task-card {
  background: $bg2;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
  border: 1px solid $rule;
}

.task-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.task-type-tag {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 10px;
  
  &.new_study {
    background: #e8f5e9;
    color: #2e7d32;
  }
  
  &.review {
    background: #fff3e0;
    color: #e65100;
  }
  
  &.mistake {
    background: #ffebee;
    color: #c62828;
  }
}

.task-subject-tag {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 10px;
  background: $soft;
  color: $accent;
}

.task-content {
  font-size: 16px;
  color: $ink;
  line-height: 1.6;
  margin-bottom: 12px;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  
  .duration-icon {
    font-size: 14px;
  }
  
  .duration-text {
    font-size: 13px;
    color: $muted;
  }
}

.task-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  background: $accent;
  color: #fff;
  
  &.secondary {
    background: $soft;
    color: $accent;
  }
  
  &.completed {
    background: #ccc;
    color: #fff;
  }
}

.task-proof {
  margin-top: 12px;
}

.proof-image {
  width: 100%;
  height: 120px;
  border-radius: 8px;
  object-fit: cover;
}

.upload-area {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  border: 2px dashed $rule;
  border-radius: 8px;
  
  .upload-icon {
    font-size: 20px;
  }
  
  .upload-text {
    font-size: 14px;
    color: $muted;
  }
}

.fab-area {
  position: fixed;
  right: 20px;
  bottom: 120px;
}

.fab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  background: $accent;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba($accent, 0.3);
  
  .fab-icon {
    font-size: 18px;
  }
  
  .fab-text {
    font-size: 15px;
    color: #fff;
    font-weight: 500;
  }
}

.bottom-space {
  height: 100px;
}
</style>