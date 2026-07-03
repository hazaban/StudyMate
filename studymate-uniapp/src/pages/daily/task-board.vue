<template>
  <view class="page">
    <view class="header">
      <view class="header-top">
        <view class="header-left">
          <text class="title">今日任务</text>
          <text class="date">{{ currentDate }}</text>
        </view>
        <view class="header-actions">
          <view class="add-btn" @click="showAddForm = true">
            <text class="add-icon">+</text>
            <text class="add-text">添加任务</text>
          </view>
        </view>
      </view>
      <view class="progress-summary">
        <view class="progress-item">
          <text class="progress-num">{{ taskStore.completedCount }}</text>
          <text class="progress-label">已完成</text>
        </view>
        <view class="progress-divider"></view>
        <view class="progress-item">
          <text class="progress-num">{{ taskStore.pendingTasks.length }}</text>
          <text class="progress-label">待完成</text>
        </view>
        <view class="progress-divider"></view>
        <view class="progress-item">
          <text class="progress-num">{{ taskStore.totalCount }}</text>
          <text class="progress-label">总任务</text>
        </view>
      </view>
    </view>

    <view class="tabs">
      <view class="tab" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
        <text class="tab-text">全部</text>
      </view>
      <view class="tab" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">
        <text class="tab-text">待完成</text>
      </view>
      <view class="tab" :class="{ active: activeTab === 'completed' }" @click="activeTab = 'completed'">
        <text class="tab-text">已完成</text>
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
      <view class="task-item" v-for="task in filteredTasks" :key="task.id" :class="{ completed: task.status === 'completed' }">
        <view class="task-check" @click="toggleTask(task)">
          <view class="check-circle" :class="{ checked: task.status === 'completed' }">
            <text v-if="task.status === 'completed'" class="check-icon">✓</text>
          </view>
        </view>
        <view class="task-body" @click="editTask(task)">
          <view class="task-top">
            <text class="task-content">{{ task.content }}</text>
            <view class="task-type-tag" :class="getTypeClass(task.type)">
              {{ getTypeLabel(task.type) }}
            </view>
          </view>
          <view class="task-meta">
            <text class="task-subject">{{ task.subject }}</text>
            <text class="task-chapter" v-if="task.chapter">{{ task.chapter }}</text>
            <text class="task-duration">预计: {{ task.duration }}分钟</text>
            <text class="task-actual" v-if="task.actual_duration > 0">实际: {{ task.actual_duration }}分钟</text>
          </view>
        </view>
        <view class="task-pomodoro" @click="startPomodoro(task)">
          <text class="pomodoro-icon">🍅</text>
        </view>
      </view>
    </view>

    <view class="empty" v-if="filteredTasks.length === 0">
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无任务</text>
      <text class="empty-hint">点击上方「添加任务」按钮手动创建任务</text>
    </view>

    <!-- Add/Edit Task Modal -->
    <view class="modal-overlay" v-if="showAddForm || editingTask" @click="closeForm">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingTask ? '编辑任务' : '添加任务' }}</text>
          <view class="modal-close" @click="closeForm">✕</view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="form-group">
            <text class="form-label">科目</text>
            <view class="subject-grid">
              <view class="subject-item" v-for="s in subjectOptions" :key="s" :class="{ active: form.subject === s }" @click="form.subject = s">{{ s }}</view>
              <view class="subject-item subject-add" @click="showSubjectInput = !showSubjectInput">
                <text v-if="!showSubjectInput">+ 自定义</text>
                <text v-else>收起</text>
              </view>
            </view>
            <view class="input-wrapper" v-if="showSubjectInput" style="margin-top: 10px;">
              <input class="input-field" v-model="customSubject" placeholder="输入自定义科目..." @confirm="addCustomSubject" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">章节</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="form.chapter" placeholder="如：第3章 二叉树" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">任务内容</text>
            <view class="input-wrapper">
              <textarea class="textarea-field" v-model="form.content" placeholder="请输入任务内容..." maxlength="500" />
            </view>
          </view>

          <view class="form-row">
            <view class="form-group half">
              <text class="form-label">预计时间（分钟）</text>
              <view class="input-wrapper">
                <input class="input-field" v-model="form.duration" type="number" placeholder="25" />
              </view>
            </view>
            <view class="form-group half">
              <text class="form-label">任务类型</text>
              <view class="type-row">
                <view class="type-item" :class="{ active: form.type === 'new_study' }" @click="form.type = 'new_study'">新学</view>
                <view class="type-item" :class="{ active: form.type === 'review' }" @click="form.type = 'review'">复习</view>
                <view class="type-item" :class="{ active: form.type === 'mistake' }" @click="form.type = 'mistake'">错题</view>
              </view>
            </view>
          </view>

          <view class="form-group" v-if="editingTask">
            <text class="form-label">实际用时（系统根据番茄钟自动记录）</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="form.actual_duration" type="number" placeholder="0" />
            </view>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="closeForm">取消</view>
          <view class="submit-btn" @click="submitForm">{{ editingTask ? '保存' : '添加' }}</view>
        </view>
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
import { useFarmStore } from '@/stores/farm'

const taskStore = useTaskStore()
const planStore = usePlanStore()
const userStore = useUserStore()
const farmStore = useFarmStore()

const activeTab = ref('all')
const activeFilter = ref('all')
const showAddForm = ref(false)
const editingTask = ref(null)
const showSubjectInput = ref(false)
const customSubject = ref('')

const allSubjects = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']
const subjectOptions = ref(JSON.parse(uni.getStorageSync('studymate_subjects') || JSON.stringify(allSubjects)))

function addCustomSubject() {
  const name = customSubject.value.trim()
  if (!name) return
  if (!subjectOptions.value.includes(name)) {
    subjectOptions.value.push(name)
    uni.setStorageSync('studymate_subjects', JSON.stringify(subjectOptions.value))
  }
  form.value.subject = name
  customSubject.value = ''
  showSubjectInput.value = false
}

const defaultForm = {
  subject: '数据结构',
  chapter: '',
  content: '',
  duration: 25,
  actual_duration: 0,
  type: 'new_study'
}

const form = ref({ ...defaultForm })

const currentDate = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 ${['日','一','二','三','四','五','六'][d.getDay()]}`
})

const subjects = computed(() => {
  const set = new Set()
  taskStore.todayTasks.forEach(t => set.add(t.subject))
  return [...set]
})

const filteredTasks = computed(() => {
  let tasks = taskStore.todayTasks
  if (activeTab.value === 'pending') tasks = tasks.filter(t => t.status === 'pending')
  if (activeTab.value === 'completed') tasks = tasks.filter(t => t.status === 'completed')
  if (activeFilter.value !== 'all') tasks = tasks.filter(t => t.subject === activeFilter.value)
  return tasks
})

const getTypeLabel = (type) => {
  const map = { new_study: '新学', review: '复习', mistake: '错题' }
  return map[type] || type
}

const getTypeClass = (type) => {
  const map = { new_study: 'tag-green', review: 'tag-orange', mistake: 'tag-red' }
  return map[type] || ''
}

async function toggleTask(task) {
  if (task.status === 'completed') {
    await taskStore.updateTask(task.id, { status: 'pending' })
  } else {
    await taskStore.completeTask(task.id)
    // Auto-link to farm: fertilize the crop
    if (planStore.currentPlan) {
      try {
        const crop = await farmStore.ensureCrop(planStore.currentPlan.id, task.subject)
        if (crop.plant) {
          await farmStore.fertilizePlant(crop.plant.id)
        }
      } catch (e) { /* silent */ }
    }
  }
}

function startPomodoro(task) {
  taskStore.currentTask = task
  const taskContent = `${task.subject}${task.chapter ? ' - ' + task.chapter : ''}: ${task.content}`
  uni.navigateTo({ url: `/pages/daily/pomodoro?taskContent=${encodeURIComponent(taskContent)}&taskId=${task.id}` })
}

function editTask(task) {
  editingTask.value = task
  form.value = {
    subject: task.subject,
    chapter: task.chapter || '',
    content: task.content,
    duration: task.duration,
    actual_duration: task.actual_duration || 0,
    type: task.type
  }
  showAddForm.value = false
}

function closeForm() {
  showAddForm.value = false
  editingTask.value = null
  form.value = { ...defaultForm }
}

async function submitForm() {
  if (!form.value.subject || !form.value.content) {
    uni.showToast({ title: '请填写科目和内容', icon: 'none' })
    return
  }

  uni.showLoading({ title: '保存中...' })
  try {
    if (editingTask.value) {
      await taskStore.updateTask(editingTask.value.id, { ...form.value, duration: parseInt(form.value.duration) || 25 })
    } else {
      if (!planStore.currentPlan) {
        uni.showToast({ title: '请先创建学习计划', icon: 'none' })
        return
      }
      await taskStore.createTask({
        plan_id: planStore.currentPlan.id,
        date: new Date().toISOString().split('T')[0],
        type: form.value.type,
        subject: form.value.subject,
        chapter: form.value.chapter,
        content: form.value.content,
        duration: parseInt(form.value.duration) || 25
      })
    }
    closeForm()
    uni.showToast({ title: editingTask.value ? '已更新' : '已添加', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    if (planStore.currentPlan) {
      const today = new Date().toISOString().split('T')[0]
      await taskStore.getTasksByDate(planStore.currentPlan.id, today)
    }
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 60px 0 20px;
  background: linear-gradient(135deg, #2f7d4f 0%, #3d9a62 100%);
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
  margin-bottom: 20px;
}

.header-left {
  .title { display: block; font-size: 26px; font-weight: 700; color: #fff; margin-bottom: 4px; }
  .date { font-size: 14px; color: rgba(255,255,255,0.8); }
}

.header-actions {
  display: flex; gap: 8px;
}

.add-btn {
  display: flex; align-items: center; gap: 4px; background: rgba(255,255,255,0.2); padding: 10px 16px; border-radius: 25px;
  &:active { background: rgba(255,255,255,0.3); transform: scale(0.96); }
  .add-icon { font-size: 18px; color: #fff; }
  .add-text { font-size: 14px; color: #fff; font-weight: 500; }
}

.progress-summary {
  display: flex; align-items: center; background: rgba(255,255,255,0.12); border-radius: 16px; padding: 16px; border: 1px solid rgba(255,255,255,0.15);
}
.progress-item { flex: 1; text-align: center; .progress-num { display: block; font-size: 22px; font-weight: 700; color: #fff; } .progress-label { font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 2px; } }
.progress-divider { width: 1px; height: 32px; background: rgba(255,255,255,0.2); }

.tabs { display: flex; margin-bottom: 16px; background: #f5f7f5; border-radius: 12px; padding: 4px; }
.tab { flex: 1; text-align: center; padding: 10px; border-radius: 10px; transition: all 0.2s;
  &.active { background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.08); .tab-text { color: #2f7d4f; font-weight: 600; } }
  .tab-text { font-size: 14px; color: #65746d; }
}

.filter-section { margin-bottom: 16px; }
.filter-scroll { white-space: nowrap; }
.filter-list { display: flex; gap: 8px; }
.filter-item { padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; white-space: nowrap; &.active { background: #2f7d4f; color: #fff; } }

.task-list { display: flex; flex-direction: column; gap: 10px; }
.task-item {
  display: flex; align-items: center; gap: 12px; background: #fff; border-radius: 14px; padding: 14px 16px; border: 1px solid #e8ece9; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  &:active { transform: scale(0.99); }
  &.completed { opacity: 0.7; .task-content { text-decoration: line-through; } }
}
.task-check { flex-shrink: 0; }
.check-circle { width: 24px; height: 24px; border-radius: 50%; border: 2px solid #d0d5d2; display: flex; align-items: center; justify-content: center; &.checked { background: #2f7d4f; border-color: #2f7d4f; } .check-icon { color: #fff; font-size: 14px; font-weight: 700; } }
.task-body { flex: 1; min-width: 0; }
.task-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 6px; }
.task-content { font-size: 15px; color: #1a1a2e; line-height: 1.5; flex: 1; }
.task-type-tag { font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 500; white-space: nowrap; flex-shrink: 0; &.tag-green { background: #e8f5e9; color: #2e7d32; } &.tag-orange { background: #fff3e0; color: #e65100; } &.tag-red { background: #ffebee; color: #c62828; } }
.task-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.task-subject { font-size: 12px; color: #2f7d4f; background: #e8f5e9; padding: 2px 8px; border-radius: 8px; }
.task-chapter { font-size: 12px; color: #6b4ce6; background: #f3f0ff; padding: 2px 8px; border-radius: 8px; }
.task-duration, .task-actual { font-size: 12px; color: #999; }
.task-pomodoro { flex-shrink: 0; .pomodoro-icon { font-size: 24px; } }

.empty { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .empty-icon { font-size: 48px; margin-bottom: 12px; } .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; } .empty-hint { font-size: 13px; color: #999; text-align: center; } }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; }
.modal-content { background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #2f7d4f; font-weight: 600; }
.form-group { margin-bottom: 16px; &.half { flex: 1; } }
.form-row { display: flex; gap: 12px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; &:focus-within { border-color: #2f7d4f; } }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 60px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-item { padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; &.active { background: #2f7d4f; color: #fff; } &.subject-add { background: #fff; border: 1.5px dashed #d0d5d2; color: #2f7d4f; } }
.type-row { display: flex; gap: 8px; }
.type-item { flex: 1; padding: 10px; text-align: center; border-radius: 10px; font-size: 13px; color: #65746d; background: #f5f7f5; &.active { background: #2f7d4f; color: #fff; } }

.bottom-space { height: 100px; }
</style>