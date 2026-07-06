<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="title">四象限管理</text>
      <view class="header-placeholder"></view>
    </view>

    <view class="view-tabs">
      <view class="tab" :class="{ active: viewRange === 'day' }" @click="viewRange = 'day'">今日</view>
      <view class="tab" :class="{ active: viewRange === 'week' }" @click="viewRange = 'week'">本周</view>
      <view class="tab" :class="{ active: viewRange === 'month' }" @click="viewRange = 'month'">本月</view>
    </view>

    <scroll-view scroll-y class="quadrant-container">
      <view class="quadrant-grid">
        <view class="quadrant q1" @click="addTaskToQuadrant('important_urgent')">
          <view class="quadrant-header">
            <view class="quadrant-icon q1-icon">🔴</view>
            <text class="quadrant-title">重要紧急</text>
            <text class="quadrant-count">{{ getTaskCount('important_urgent') }}</text>
          </view>
          <view class="quadrant-body">
            <view class="task-item" v-for="task in getTasks('important_urgent')" :key="task.id" :class="{ completed: task.status === 'completed' }" @click="editTask(task)">
              <view class="task-subject">{{ task.subject }}</view>
              <text class="task-content">{{ task.content }}</text>
              <text class="task-time">{{ task.date }} · {{ task.duration }}min</text>
            </view>
            <view class="add-hint" @click="addTaskToQuadrant('important_urgent')">
              <text class="add-icon">+</text>
              <text class="add-text">添加任务</text>
            </view>
          </view>
        </view>

        <view class="quadrant q2" @click="addTaskToQuadrant('important_not_urgent')">
          <view class="quadrant-header">
            <view class="quadrant-icon q2-icon">🔵</view>
            <text class="quadrant-title">重要不紧急</text>
            <text class="quadrant-count">{{ getTaskCount('important_not_urgent') }}</text>
          </view>
          <view class="quadrant-body">
            <view class="task-item" v-for="task in getTasks('important_not_urgent')" :key="task.id" :class="{ completed: task.status === 'completed' }" @click="editTask(task)">
              <view class="task-subject">{{ task.subject }}</view>
              <text class="task-content">{{ task.content }}</text>
              <text class="task-time">{{ task.date }} · {{ task.duration }}min</text>
            </view>
            <view class="add-hint" @click="addTaskToQuadrant('important_not_urgent')">
              <text class="add-icon">+</text>
              <text class="add-text">添加任务</text>
            </view>
          </view>
        </view>

        <view class="quadrant q3" @click="addTaskToQuadrant('urgent_not_important')">
          <view class="quadrant-header">
            <view class="quadrant-icon q3-icon">🟠</view>
            <text class="quadrant-title">紧急不重要</text>
            <text class="quadrant-count">{{ getTaskCount('urgent_not_important') }}</text>
          </view>
          <view class="quadrant-body">
            <view class="task-item" v-for="task in getTasks('urgent_not_important')" :key="task.id" :class="{ completed: task.status === 'completed' }" @click="editTask(task)">
              <view class="task-subject">{{ task.subject }}</view>
              <text class="task-content">{{ task.content }}</text>
              <text class="task-time">{{ task.date }} · {{ task.duration }}min</text>
            </view>
            <view class="add-hint" @click="addTaskToQuadrant('urgent_not_important')">
              <text class="add-icon">+</text>
              <text class="add-text">添加任务</text>
            </view>
          </view>
        </view>

        <view class="quadrant q4" @click="addTaskToQuadrant('not_important_not_urgent')">
          <view class="quadrant-header">
            <view class="quadrant-icon q4-icon">🟢</view>
            <text class="quadrant-title">不紧急不重要</text>
            <text class="quadrant-count">{{ getTaskCount('not_important_not_urgent') }}</text>
          </view>
          <view class="quadrant-body">
            <view class="task-item" v-for="task in getTasks('not_important_not_urgent')" :key="task.id" :class="{ completed: task.status === 'completed' }" @click="editTask(task)">
              <view class="task-subject">{{ task.subject }}</view>
              <text class="task-content">{{ task.content }}</text>
              <text class="task-time">{{ task.date }} · {{ task.duration }}min</text>
            </view>
            <view class="add-hint" @click="addTaskToQuadrant('not_important_not_urgent')">
              <text class="add-icon">+</text>
              <text class="add-text">添加任务</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="modal-mask" v-if="showAddForm" @click="showAddForm = false">
      <view class="modal-sheet" @click.stop>
        <view class="modal-top">
          <text class="modal-title">{{ editingTask ? '编辑任务' : '添加任务' }}</text>
          <view class="modal-x" @click="showAddForm = false">✕</view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="form-group">
            <text class="form-label">科目</text>
            <view class="subject-grid">
              <view class="subject-item" v-for="s in subjectOptions" :key="s" :class="{ active: form.subject === s }" @click="form.subject = s">{{ s }}</view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">任务内容</text>
            <textarea class="textarea-field" v-model="form.content" placeholder="请输入任务内容..." />
          </view>
          <view class="form-group">
            <text class="form-label">预计时间（分钟）</text>
            <input class="input-field" type="number" v-model="form.duration" placeholder="25" />
          </view>
          <view class="form-group">
            <text class="form-label">日期</text>
            <picker mode="date" :value="form.date" @change="onDateChange">
              <view class="picker-value">{{ form.date }}</view>
            </picker>
          </view>
        </scroll-view>
        <view class="modal-bot">
          <view class="btn-cancel" @click="showAddForm = false">取消</view>
          <view class="btn-submit" @click="submitForm">保存</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useTaskStore } from '@/stores/task'
import { usePlanStore } from '@/stores/plan'

const taskStore = useTaskStore()
const planStore = usePlanStore()

const viewRange = ref('day')
const showAddForm = ref(false)
const editingTask = ref(null)
const selectedImportance = ref('')

const form = ref({
  subject: '数据结构',
  content: '',
  duration: 25,
  date: '',
  importance: ''
})

const subjectOptions = ['数据结构', '英语', '政治', '操作系统', '计算机组成原理', '计算机网络', '数学', 'C语言', '数据库', 'UML', '算法']

const today = computed(() => new Date().toISOString().split('T')[0])

function formatDate(date) {
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const filteredTasks = computed(() => {
  if (!taskStore.weekTasks.length) return []
  
  const startDate = new Date()
  let endDate = new Date()
  
  if (viewRange.value === 'day') {
    endDate = new Date(startDate)
  } else if (viewRange.value === 'week') {
    startDate.setDate(startDate.getDate() - startDate.getDay() + 1)
    endDate = new Date(startDate)
    endDate.setDate(endDate.getDate() + 6)
  } else if (viewRange.value === 'month') {
    startDate.setDate(1)
    endDate = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0)
  }
  
  const startStr = formatDate(startDate)
  const endStr = formatDate(endDate)
  
  return taskStore.weekTasks.filter(t => t.date >= startStr && t.date <= endStr && t.importance)
})

function getTasks(importance) {
  return filteredTasks.value.filter(t => t.importance === importance)
}

function getTaskCount(importance) {
  return getTasks(importance).length
}

function addTaskToQuadrant(importance) {
  selectedImportance.value = importance
  form.value = {
    subject: '数据结构',
    content: '',
    duration: 25,
    date: today.value,
    importance
  }
  editingTask.value = null
  showAddForm.value = true
}

function editTask(task) {
  editingTask.value = task
  form.value = {
    subject: task.subject,
    content: task.content,
    duration: task.duration,
    date: task.date,
    importance: task.importance
  }
  showAddForm.value = true
}

function onDateChange(e) {
  form.value.date = e.detail.value
}

async function submitForm() {
  if (!form.value.content.trim()) {
    uni.showToast({ title: '请输入任务内容', icon: 'none' })
    return
  }
  
  try {
    if (editingTask.value) {
      await taskStore.updateTask(editingTask.value.id, {
        subject: form.value.subject,
        content: form.value.content,
        duration: parseInt(form.value.duration) || 25,
        importance: form.value.importance,
        date: form.value.date
      })
    } else {
      await taskStore.createTask({
        plan_id: planStore.currentPlan.id,
        date: form.value.date,
        type: 'new_study',
        subject: form.value.subject,
        content: form.value.content,
        duration: parseInt(form.value.duration) || 25,
        importance: form.value.importance
      })
    }
    await taskStore.getAllTasks(planStore.currentPlan.id)
    showAddForm.value = false
    uni.showToast({ title: editingTask.value ? '保存成功' : '添加成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

async function loadTasks() {
  if (planStore.currentPlan) {
    await taskStore.getAllTasks(planStore.currentPlan.id)
  }
}

function goBack() {
  uni.navigateBack()
}

watch(viewRange, () => {
  loadTasks()
})

onMounted(async () => {
  form.value.date = today.value
  await loadTasks()
})
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; background: #f8fbf6; }

.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 40px 0 20px;
}
.back-btn, .header-placeholder { width: 40px; height: 40px; border-radius: 50%; }
.back-btn {
  background: #fff; display: flex; align-items: center; justify-content: center;
  border: 1px solid #e8ece9;
  &:active { transform: scale(0.92); }
}
.back-icon { font-size: 20px; color: #1a1a2e; }
.title { font-size: 20px; font-weight: 700; color: #1a1a2e; }

.view-tabs {
  display: flex; gap: 10px; padding: 0 0 16px;
}
.tab {
  flex: 1; padding: 10px; text-align: center; border-radius: 12px;
  font-size: 14px; color: #999; background: #fff; border: 1px solid #e8ece9;
  &.active {
    background: #2f7d4f; color: #fff; border-color: #2f7d4f;
    font-weight: 600;
  }
}

.quadrant-container { height: calc(100vh - 160px); padding-bottom: 80px; }

.quadrant-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;
}

.quadrant {
  background: #fff; border-radius: 16px; padding: 14px;
  border: 2px solid transparent;
  &.q1 { border-color: rgba(239,83,80,0.3); background: rgba(239,83,80,0.04); }
  &.q2 { border-color: rgba(66,165,245,0.3); background: rgba(66,165,245,0.04); }
  &.q3 { border-color: rgba(255,152,0,0.3); background: rgba(255,152,0,0.04); }
  &.q4 { border-color: rgba(76,175,80,0.3); background: rgba(76,175,80,0.04); }
}

.quadrant-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
  padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;
}
.quadrant-icon { font-size: 18px; }
.quadrant-title { flex: 1; font-size: 14px; font-weight: 600; color: #1a1a2e; }
.quadrant-count {
  background: rgba(0,0,0,0.08); padding: 2px 8px; border-radius: 10px;
  font-size: 12px; color: #666; font-weight: 600;
}

.quadrant-body { max-height: 200px; overflow-y: auto; }

.task-item {
  background: #fff; border-radius: 10px; padding: 10px; margin-bottom: 8px;
  border: 1px solid #f0f0f0;
  &.completed { opacity: 0.6; }
  &:active { background: #f8f8f8; }
}
.task-subject {
  font-size: 11px; padding: 2px 6px; border-radius: 4px; display: inline-block;
  margin-bottom: 4px; color: #fff; font-weight: 500;
  background: #2f7d4f;
}
.task-content {
  display: block; font-size: 13px; color: #1a1a2e; margin-bottom: 4px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.task-time { font-size: 11px; color: #999; }

.add-hint {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 12px; border: 2px dashed #d0d5d2; border-radius: 10px;
  margin-top: 8px;
  &:active { background: rgba(47,125,79,0.04); }
}
.add-icon { font-size: 18px; color: #2f7d4f; font-weight: 600; }
.add-text { font-size: 13px; color: #999; }

.modal-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 100;
  display: flex; align-items: flex-end;
}
.modal-sheet {
  background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 70vh;
  display: flex; flex-direction: column;
}
.modal-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 22px; border-bottom: 1px solid #f0f0f0;
}
.modal-title { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.modal-x {
  width: 30px; height: 30px; border-radius: 50%; background: #f5f7f5;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; color: #999;
  &:active { background: #e8f0eb; }
}
.modal-body { padding: 16px 22px; flex: 1; overflow-y: auto; }
.modal-bot { display: flex; gap: 12px; padding: 16px 22px; border-top: 1px solid #f0f0f0; }

.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 13px; color: #999; margin-bottom: 8px; font-weight: 500; }
.subject-grid {
  display: flex; flex-wrap: wrap; gap: 8px;
}
.subject-item {
  padding: 6px 12px; border-radius: 20px; background: #f5f7f5;
  font-size: 13px; color: #1a1a2e; border: 1px solid #e8ece9;
  &.active { background: #2f7d4f; color: #fff; border-color: #2f7d4f; }
}
.textarea-field {
  width: 100%; min-height: 80px; padding: 12px; border: 1px solid #e8ece9;
  border-radius: 12px; font-size: 14px; color: #1a1a2e; background: #fafafa;
}
.input-field {
  width: 100%; padding: 12px; border: 1px solid #e8ece9;
  border-radius: 12px; font-size: 14px; color: #1a1a2e; background: #fafafa;
}
.picker-value {
  padding: 12px; border: 1px solid #e8ece9; border-radius: 12px;
  font-size: 14px; color: #1a1a2e; background: #fafafa;
}

.btn-cancel {
  flex: 1; padding: 13px; text-align: center; border-radius: 12px;
  font-size: 15px; color: #999; background: #f5f7f5; font-weight: 500;
  &:active { background: #e8f0eb; }
}
.btn-submit {
  flex: 2; padding: 13px; text-align: center; border-radius: 12px;
  font-size: 15px; color: #fff; background: #2f7d4f; font-weight: 700;
  box-shadow: 0 3px 10px rgba(47,125,79,0.2);
  &:active { transform: scale(0.97); }
}

.bottom-space { height: 80px; }
</style>