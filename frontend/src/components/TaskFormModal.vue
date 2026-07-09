<template>
  <view>
    <view class="modal-overlay" v-if="visible" @click="close">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ isEdit ? '编辑任务' : (isCopy ? '复制任务' : '添加任务') }}</text>
          <view class="modal-header-actions">
            <text class="modal-ai-btn" v-if="showAIMode && !isEdit && addMode === 'manual'" @click="addMode = 'ai'">🤖 AI添加</text>
            <text class="modal-ai-btn" v-if="showAIMode && !isEdit && addMode === 'ai'" @click="addMode = 'manual'">✏️ 手动输入</text>
            <view class="modal-close" @click="close">✕</view>
          </view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view v-if="showAIMode && addMode === 'ai' && !isEdit" class="ai-section">
            <view class="ai-hint-box">
              <text class="ai-hint-title">🤖 描述你的学习计划，AI自动解析为任务</text>
              <view class="ai-fields-guide">
                <text class="ai-field">📚 科目</text>
                <text class="ai-field">📖 章节</text>
                <text class="ai-field">⏱ 时长</text>
                <text class="ai-field">🕘 时间</text>
                <text class="ai-field">📅 日期</text>
                <text class="ai-field">📷 图片</text>
              </view>
              <text class="ai-hint-example">💡 试试：明天上午9点复习数据结构二叉树章节，45分钟；或上传手写计划/课程表图片</text>
            </view>
            <textarea class="ai-textarea-large" v-model="aiParseInput" placeholder="请描述你的学习安排，包含科目、内容、时间等信息..." />
            <view class="ai-image-upload" @click="selectImage">
              <view class="ai-image-preview" v-if="aiImageBase64">
                <image :src="aiImageBase64" mode="aspectFit" class="ai-image-preview-img" />
                <view class="ai-image-remove" @click.stop="removeImage">✕</view>
              </view>
              <view class="ai-image-upload-btn" v-else>
                <text class="upload-icon">📷</text>
                <text class="upload-text">拍照或上传图片</text>
              </view>
            </view>
            <view class="ai-parse-btn-primary" @click="parseWithAI">
              <text class="btn-icon">🔍</text>
              <text class="btn-text">开始解析</text>
            </view>
            <view class="ai-result-list" v-if="aiParseResult.length > 0">
              <view class="ai-result-header">
                <text class="result-title">解析结果（{{ aiParseResult.filter(t=>t.selected).length }}/{{ aiParseResult.length }}）</text>
                <text class="select-all-btn" @click="toggleSelectAll">{{ allSelected ? '取消全选' : '全选' }}</text>
              </view>
              <view class="ai-task-card" v-for="(task, idx) in aiParseResult" :key="idx" @click="task.selected = !task.selected">
                <view class="task-checkbox" :class="{ checked: task.selected }"></view>
                <view class="task-card-body">
                  <text class="task-card-content">{{ task.content }}</text>
                  <view class="task-card-meta">
                    <text class="meta-tag">{{ task.subject }}</text>
                    <text class="meta-text">{{ task.date }}</text>
                    <text class="meta-text">{{ task.duration }}分钟</text>
                  </view>
                </view>
              </view>
              <view class="ai-add-all-btn" @click="addParsedTasks">
                <text>添加选中的任务</text>
              </view>
            </view>
          </view>

          <view v-if="addMode === 'manual' || isEdit">
            <view class="form-group">
              <view class="form-label-row">
                <text class="form-label">科目</text>
                <text class="form-manage-link" @click="showManageSubjects = true">管理科目</text>
              </view>
              <view class="subject-grid">
                <view
                  class="subject-item"
                  v-for="s in subjectOptions"
                  :key="s"
                  :class="{ active: form.subject === s }"
                  @click="form.subject = s"
                >{{ s }}</view>
                <view class="subject-item subject-add" @click="showSubjectInput = !showSubjectInput">
                  <text v-if="!showSubjectInput">+ 自定义</text>
                  <text v-else>收起</text>
                </view>
              </view>
              <view class="subject-empty-hint" v-if="subjectOptions.length === 0 && !showSubjectInput">
                <text class="subject-empty-text">还没有科目，点击「+ 自定义」或「管理科目」添加你的科目</text>
              </view>
              <view class="input-wrapper" v-if="showSubjectInput" style="margin-top: 10px;">
                <input class="input-field" v-model="customSubject" placeholder="输入自定义科目，按回车添加..." @confirm="addCustomSubject" />
              </view>
            </view>

            <view class="form-group">
              <text class="form-label">章节</text>
              <picker v-if="availableChapters.length > 0" mode="selector" :range="availableChapters" @change="onChapterChange">
                <view class="input-wrapper picker-wrapper">
                  <text class="picker-value" :class="{ placeholder: !form.chapter }">{{ form.chapter || '选择章节（可选）' }}</text>
                  <text class="picker-arrow">▾</text>
                </view>
              </picker>
              <view class="input-wrapper" v-else>
                <input class="input-field" v-model="form.chapter" placeholder="如：第3章 二叉树（无预设章节时可手动输入）" />
              </view>
            </view>

            <view class="form-group">
              <text class="form-label">任务日期</text>
              <picker mode="date" :value="form.date" @change="onDateChange">
                <view class="input-wrapper picker-wrapper">
                  <text class="picker-value" :class="{ placeholder: !form.date }">{{ form.date || '选择日期' }}</text>
                  <text class="picker-arrow">▾</text>
                </view>
              </picker>
            </view>

            <view class="form-group">
              <text class="form-label">任务内容</text>
              <view class="input-wrapper">
                <textarea class="textarea-field" v-model="form.content" placeholder="请输入任务内容..." maxlength="500" />
              </view>
            </view>

            <view class="form-row">
              <view class="form-group half">
                <text class="form-label">开始时间</text>
                <view class="input-wrapper time-input-wrapper">
                  <picker mode="selector" :range="hourOptions" @change="onStartHourChange">
                    <text class="time-picker-value">{{ padZero(form.start_hour) }}</text>
                  </picker>
                  <text class="time-separator">:</text>
                  <picker mode="selector" :range="minuteOptions" @change="onStartMinuteChange">
                    <text class="time-picker-value">{{ padZero(form.start_minute) }}</text>
                  </picker>
                </view>
              </view>
              <view class="form-group half">
                <text class="form-label">预计时间</text>
                <view class="input-wrapper time-input-wrapper">
                  <input class="input-field time-duration-input" v-model="form.duration" type="number" placeholder="25" />
                  <text class="duration-suffix">分钟</text>
                </view>
              </view>
            </view>

            <view class="form-group">
              <text class="form-label">任务类型</text>
              <view class="type-row">
                <view class="type-item" :class="{ active: form.type === 'new_study' }" @click="form.type = 'new_study'">新学</view>
                <view class="type-item" :class="{ active: form.type === 'review' }" @click="form.type = 'review'">复习</view>
                <view class="type-item" :class="{ active: form.type === 'mistake' }" @click="form.type = 'mistake'">错题</view>
              </view>
            </view>

            <view class="form-group" v-if="enableQuadrant">
              <text class="form-label">四象限分类</text>
              <view class="type-row">
                <view class="type-item importance-item" :class="{ active: form.importance === 'important_urgent' }" @click="form.importance = 'important_urgent'">
                  <view class="imp-dot imp-red"></view>
                  <text>重要紧急</text>
                </view>
                <view class="type-item importance-item" :class="{ active: form.importance === 'important_not_urgent' }" @click="form.importance = 'important_not_urgent'">
                  <view class="imp-dot imp-blue"></view>
                  <text>重要不紧急</text>
                </view>
                <view class="type-item importance-item" :class="{ active: form.importance === 'urgent_not_important' }" @click="form.importance = 'urgent_not_important'">
                  <view class="imp-dot imp-orange"></view>
                  <text>紧急不重要</text>
                </view>
                <view class="type-item importance-item" :class="{ active: form.importance === 'not_important_not_urgent' }" @click="form.importance = 'not_important_not_urgent'">
                  <view class="imp-dot imp-gray"></view>
                  <text>不紧急不重要</text>
                </view>
              </view>
            </view>

            <view class="form-group">
              <text class="form-label">循环方式</text>
              <view class="type-row repeat-row">
                <view class="type-item" :class="{ active: form.repeat_type === 'none' }" @click="form.repeat_type = 'none'">不循环</view>
                <view class="type-item" :class="{ active: form.repeat_type === 'daily' }" @click="form.repeat_type = 'daily'">每天</view>
                <view class="type-item" :class="{ active: form.repeat_type === 'weekday' }" @click="form.repeat_type = 'weekday'">工作日</view>
                <view class="type-item" :class="{ active: form.repeat_type === 'holiday' }" @click="form.repeat_type = 'holiday'">节假日</view>
              </view>
            </view>

            <view class="form-group" v-if="isEdit">
              <text class="form-label">实际用时（系统根据番茄钟自动记录）</text>
              <view class="input-wrapper">
                <input class="input-field" v-model="form.actual_duration" type="number" placeholder="0" />
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="close">取消</view>
          <view class="delete-btn" v-if="isEdit" @click="confirmDelete">删除</view>
          <view class="submit-btn" @click="submitForm">{{ isEdit ? '保存' : '添加' }}</view>
        </view>
      </view>
    </view>

    <view class="manage-overlay" v-if="showManageSubjects" @click="showManageSubjects = false">
      <view class="manage-dialog" @click.stop>
        <view class="manage-dialog-top">
          <text class="manage-dialog-title">管理科目</text>
          <view class="manage-dialog-close" @click="showManageSubjects = false">✕</view>
        </view>
        <view class="manage-dialog-body">
          <view class="manage-empty" v-if="subjectOptions.length === 0">
            <text class="manage-empty-text">还没有科目，在下方添加你的第一个科目吧</text>
          </view>
          <view class="manage-item" v-for="s in subjectOptions" :key="s">
            <view class="manage-item-left">
              <text class="manage-item-name">{{ s }}</text>
            </view>
            <view class="manage-item-del" @click="removeSubjectFromManager(s)">删除</view>
          </view>
          <view class="manage-add-row">
            <input class="manage-add-input" v-model="manageNewSubject" placeholder="输入新科目名称" @confirm="addManageSubject" />
            <view class="manage-add-btn" @click="addManageSubject">添加</view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useTaskStore } from '@/stores/task'
import { usePlanStore } from '@/stores/plan'
import { useSubjectsStore } from '@/stores/subjects'
import * as api from '@/api/client'

const props = defineProps({
  visible: { type: Boolean, default: false },
  task: { type: Object, default: null },
  date: { type: String, default: '' },
  defaultImportance: { type: String, default: '' },
  enableQuadrant: { type: Boolean, default: false },
  showAIMode: { type: Boolean, default: true },
  planSubjects: { type: Array, default: () => [] },
  defaultHour: { type: Number, default: 9 },
  defaultMinute: { type: Number, default: 0 },
  // 复制来源任务：传入后会以新建模式预填该任务的字段
  copySource: { type: Object, default: null }
})

const emit = defineEmits(['update:visible', 'saved', 'deleted'])

const taskStore = useTaskStore()
const planStore = usePlanStore()
const subjectsStore = useSubjectsStore()

const isEdit = computed(() => !!props.task && !props.copySource)
const isCopy = computed(() => !!props.copySource)

const subjectOptions = computed(() => subjectsStore.mergedSubjects)
const showManageSubjects = ref(false)
const manageNewSubject = ref('')
const showSubjectInput = ref(false)
const customSubject = ref('')

const addMode = ref('manual')
const aiParseInput = ref('')
const aiParseResult = ref([])
const aiImageBase64 = ref('')
const hourOptions = Array.from({ length: 18 }, (_, i) => String(i + 6))
const minuteOptions = Array.from({ length: 60 }, (_, i) => String(i).padStart(2, '0'))

function padZero(n) {
  return String(n).padStart(2, '0')
}

const defaultForm = {
  subject: '',
  chapter: '',
  content: '',
  duration: 25,
  actual_duration: 0,
  type: 'new_study',
  repeat_type: 'none',
  importance: '',
  start_hour: 9,
  start_minute: 0
}

const form = ref({ ...defaultForm })

const availableChapters = computed(() => {
  const planSubjects = props.planSubjects.length ? props.planSubjects : (planStore.currentPlan?.subjects || [])
  const currentSubj = planSubjects.find(s => s.name === form.value.subject)
  if (!currentSubj?.chapters?.length) return []
  return currentSubj.chapters.map(c => c.name || '').filter(Boolean)
})

function resetForm() {
  const base = { ...defaultForm }
  base.subject = subjectOptions.value[0] || ''
  base.importance = props.defaultImportance || ''
  base.date = props.date || ''
  if (props.task) {
    form.value = {
      subject: props.task.subject || base.subject,
      chapter: props.task.chapter || '',
      content: props.task.content || '',
      duration: props.task.duration ?? 25,
      actual_duration: props.task.actual_duration ?? 0,
      type: props.task.type || 'new_study',
      repeat_type: props.task.repeat_type || 'none',
      importance: props.task.importance || props.defaultImportance || '',
      start_hour: props.task.start_hour || 9,
      start_minute: props.task.start_minute || 0,
      date: props.task.date || props.date || ''
    }
  } else if (props.copySource) {
    // 从已有任务复制：以新建模式预填字段，日期用传入的 date/格子日期，时间用传入的默认时间
    form.value = {
      subject: props.copySource.subject || base.subject,
      chapter: props.copySource.chapter || '',
      content: props.copySource.content || '',
      duration: props.copySource.duration ?? 25,
      actual_duration: 0,
      type: props.copySource.type || 'new_study',
      repeat_type: props.copySource.repeat_type || 'none',
      importance: props.copySource.importance || props.defaultImportance || '',
      start_hour: props.defaultHour ?? props.copySource.start_hour ?? 9,
      start_minute: props.defaultMinute ?? props.copySource.start_minute ?? 0,
      date: props.date || props.copySource.date || ''
    }
  } else {
    form.value = base
    form.value.start_hour = props.defaultHour
    form.value.start_minute = props.defaultMinute
  }
  addMode.value = 'manual'
  aiParseInput.value = ''
  aiParseResult.value = []
  showSubjectInput.value = false
  customSubject.value = ''
}

watch(() => props.visible, (v) => {
  if (v) {
    subjectsStore.load()
    resetForm()
  }
}, { immediate: true })

watch(() => props.task, () => {
  if (props.visible) resetForm()
})

watch(() => props.copySource, () => {
  if (props.visible) resetForm()
})

watch(() => form.value.subject, () => { form.value.chapter = '' })

function close() {
  emit('update:visible', false)
}

async function confirmDelete() {
  if (!props.task) return
  uni.showModal({
    title: '删除任务',
    content: `确定要删除「${props.task.content}」吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await taskStore.deleteTask(props.task.id)
          uni.showToast({ title: '已删除', icon: 'success' })
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
        emit('deleted', props.task)
        close()
      }
    }
  })
}

function addCustomSubject() {
  const name = customSubject.value.trim()
  if (!name) return
  subjectsStore.add(name)
  form.value.subject = name
  customSubject.value = ''
  showSubjectInput.value = false
}

function addManageSubject() {
  const name = manageNewSubject.value.trim()
  if (!name) return
  subjectsStore.add(name)
  manageNewSubject.value = ''
}

function removeSubjectFromManager(name) {
  uni.showModal({
    title: '删除科目', content: `确定要删除「${name}」吗？`,
    success: (res) => {
      if (res.confirm) {
        subjectsStore.remove(name)
        if (form.value.subject === name) form.value.subject = subjectOptions.value[0] || ''
      }
    }
  })
}

function onChapterChange(e) {
  const idx = e.detail.value
  if (availableChapters.value[idx]) {
    form.value.chapter = availableChapters.value[idx]
    const planSubjects = props.planSubjects.length ? props.planSubjects : (planStore.currentPlan?.subjects || [])
    const currentSubj = planSubjects.find(s => s.name === form.value.subject)
    if (currentSubj?.chapters?.[idx]?.duration) {
      form.value.duration = currentSubj.chapters[idx].duration
    }
  }
}

function onDateChange(e) {
  form.value.date = e.detail.value
}

function onStartHourChange(e) {
  form.value.start_hour = parseInt(hourOptions[e.detail.value])
}

function onStartMinuteChange(e) {
  form.value.start_minute = parseInt(minuteOptions[e.detail.value])
}

const allSelected = computed(() => {
  if (aiParseResult.value.length === 0) return false
  return aiParseResult.value.every(t => t.selected)
})

function toggleSelectAll() {
  const target = !allSelected.value
  aiParseResult.value.forEach(t => { t.selected = target })
}

async function submitForm() {
  if (!form.value.subject) {
    uni.showToast({ title: '请选择或添加科目', icon: 'none' })
    return
  }
  if (!form.value.content) {
    uni.showToast({ title: '请填写任务内容', icon: 'none' })
    return
  }

  uni.showLoading({ title: '保存中...' })
  try {
    const taskDate = form.value.date || props.date || new Date().toISOString().split('T')[0]
    if (isEdit.value) {
      await taskStore.updateTask(props.task.id, {
        subject: form.value.subject,
        chapter: form.value.chapter,
        content: form.value.content,
        duration: parseInt(form.value.duration) || 25,
        type: form.value.type,
        repeat_type: form.value.repeat_type,
        importance: form.value.importance,
        start_hour: form.value.start_hour || 9,
        start_minute: form.value.start_minute || 0,
        actual_duration: parseInt(form.value.actual_duration) || 0
      })
      emit('saved', { task: props.task, isEdit: true })
    } else {
      if (!planStore.currentPlan) {
        uni.showToast({ title: '请先创建学习计划', icon: 'none' })
        uni.hideLoading()
        return
      }
      const result = await taskStore.createTask({
        plan_id: planStore.currentPlan.id,
        date: taskDate,
        type: form.value.type,
        subject: form.value.subject,
        chapter: form.value.chapter,
        content: form.value.content,
        duration: parseInt(form.value.duration) || 25,
        repeat_type: form.value.repeat_type,
        importance: form.value.importance,
        start_hour: form.value.start_hour || 9,
        start_minute: form.value.start_minute || 0
      })
      if (!result.success) {
        uni.showToast({ title: '创建失败: ' + (result.error || '未知错误'), icon: 'none' })
        return
      }
      emit('saved', { task: result.task, isEdit: false })
    }
    if (planStore.currentPlan) {
      await taskStore.getAllTasks(planStore.currentPlan.id)
    }
    close()
    uni.showToast({ title: isEdit.value ? '已更新' : '已添加', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

function selectImage() {
  uni.showActionSheet({
    itemList: ['拍照', '从相册选择'],
    success: (res) => {
      const sourceType = res.tapIndex === 0 ? ['camera'] : ['album']
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: sourceType,
        success: async (res) => {
          const tempFilePath = res.tempFilePaths[0]
          aiImageBase64.value = tempFilePath
        },
        fail: () => {
          uni.showToast({ title: '选择图片失败', icon: 'none' })
        }
      })
    }
  })
}

function removeImage() {
  aiImageBase64.value = ''
}

async function imageToBase64(filePath) {
  return new Promise((resolve, reject) => {
    uni.getFileSystemManager().readFile({
      filePath: filePath,
      encoding: 'base64',
      success: (res) => {
        resolve(`data:image/jpeg;base64,${res.data}`)
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

async function parseWithAI() {
  if (!aiParseInput.value.trim() && !aiImageBase64.value) {
    uni.showToast({ title: '请输入文字计划或上传图片', icon: 'none' })
    return
  }
  uni.showLoading({ title: 'AI解析中...' })
  try {
    let imageData = ''
    if (aiImageBase64.value) {
      try {
        imageData = await imageToBase64(aiImageBase64.value)
      } catch (e) {
        console.error('图片转换失败:', e)
      }
    }
    const result = await api.aiParseTask({
      text: aiParseInput.value.trim(),
      image: imageData
    })
    aiParseResult.value = (result.tasks || []).map(t => ({ ...t, selected: true }))
  } catch (e) {
    console.error('AI 解析失败:', e)
    let errorMsg = 'AI 服务连接失败，请稍后重试'
    const detail = e?.data?.detail || e?.data?.error || e?.errMsg || e?.message || ''
    if (detail) {
      errorMsg = detail.length > 30 ? detail.substring(0, 30) + '...' : detail
    }
    uni.showToast({ title: errorMsg, icon: 'none', duration: 3000 })
  } finally {
    uni.hideLoading()
  }
}

async function addParsedTasks() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先创建学习计划', icon: 'none' })
    return
  }
  const selected = aiParseResult.value.filter(t => t.selected)
  if (selected.length === 0) {
    uni.showToast({ title: '请选择要添加的任务', icon: 'none' })
    return
  }
  uni.showLoading({ title: '添加中...' })
  let added = 0
  for (const task of selected) {
    try {
      await taskStore.createTask({
        plan_id: planStore.currentPlan.id,
        date: task.date || new Date().toISOString().split('T')[0],
        type: task.type || 'new_study',
        subject: task.subject || subjectOptions.value[0] || '',
        content: task.content,
        chapter: task.chapter || '',
        duration: task.duration || 30,
        repeat_type: task.repeat_type || 'none',
        start_hour: task.start_hour || 9,
        start_minute: task.start_minute || 0,
        importance: task.importance || ''
      })
      added++
    } catch (e) { /* skip */ }
  }
  uni.hideLoading()
  aiParseInput.value = ''
  aiParseResult.value = []
  addMode.value = 'manual'
  if (added > 0) {
    emit('saved', { task: null, isEdit: false })
    if (planStore.currentPlan) await taskStore.getAllTasks(planStore.currentPlan.id)
    uni.showToast({ title: `已添加 ${added} 个任务`, icon: 'success' })
    close()
  }
}
</script>

<style lang="scss" scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 24px; }
.modal-content { background: #fff; border-radius: 20px; width: 100%; max-width: 440px; max-height: 75vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 18px 22px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-header-actions { display: flex; align-items: center; gap: 8px; }
.modal-ai-btn { font-size: 13px; color: #6b4ce6; padding: 4px 10px; background: #f3f0ff; border-radius: 14px; font-weight: 500; cursor: pointer; }
.modal-close { font-size: 20px; color: #999; padding: 4px; cursor: pointer; }
.modal-body { padding: 20px 22px; flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch; }
.modal-footer { display: flex; gap: 12px; padding: 14px 22px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; cursor: pointer; }
.delete-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #ef5350; font-weight: 500; cursor: pointer; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #2f7d4f; font-weight: 600; cursor: pointer; }
.delete-hint { margin-bottom: 14px; padding: 8px 12px; background: #fff8e1; border-radius: 10px; }
.delete-hint-text { font-size: 12px; color: #9a7b00; }
.form-group { margin-bottom: 18px; &.half { flex: 1; min-width: 0; } }
.form-row { display: flex; gap: 14px; align-items: flex-start; }

/* ── 时间输入统一设计 ── */
.time-input-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 0 10px;
  min-height: 46px;
}
.time-separator {
  font-size: 17px; color: #2f7d4f; font-weight: 600; flex-shrink: 0;
  margin: 0 2px;
}
.time-picker-value {
  font-size: 16px; color: #1a1a2e; font-weight: 700;
  padding: 10px 4px; border-radius: 6px; min-width: 30px; text-align: center;
  cursor: pointer; line-height: 1;
  &:active { background: #e8f0eb; }
}
.time-duration-input {
  text-align: center; font-weight: 700; font-size: 16px; flex: 1; min-width: 0;
  height: 26px; line-height: 26px; padding: 0;
}
.duration-suffix {
  font-size: 13px; color: #888; flex-shrink: 0; font-weight: 500;
  margin-left: 4px;
}

.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 12px; padding: 12px 14px; background: #fafafa; display: flex; align-items: center; &:focus-within { border-color: #2f7d4f; box-shadow: 0 0 0 2px rgba(47,125,79,0.08); } }
.picker-wrapper { justify-content: space-between; cursor: pointer; }
.picker-value { font-size: 15px; color: #1a1a2e; flex: 1; &.placeholder { color: #999; } }
.picker-arrow { font-size: 14px; color: #999; margin-left: 8px; }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; line-height: 1.5; }
.textarea-field { width: 100%; min-height: 56px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.form-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.form-label-row .form-label { margin-bottom: 0; }
.form-manage-link {
  font-size: 12px; color: #2f7d4f; padding: 3px 10px; border-radius: 10px;
  background: rgba(47,125,79,0.06); font-weight: 500; cursor: pointer;
  &:active { background: rgba(47,125,79,0.15); }
}
.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-item {
  padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d;
  background: #f5f7f5; cursor: pointer; white-space: nowrap;
  transition: all 0.15s;
  &:active { transform: scale(0.96); }
  &.active { background: #2f7d4f; color: #fff; font-weight: 600; }
  &.subject-add { background: #fff; border: 1.5px dashed #d0d5d2; color: #2f7d4f; }
}
.type-row { display: flex; gap: 8px; flex-wrap: wrap; }
.type-item {
  flex: 1; min-width: 56px; padding: 10px 8px; text-align: center; border-radius: 10px;
  font-size: 13px; color: #65746d; background: #f5f7f5; cursor: pointer; white-space: nowrap;
  transition: all 0.15s;
  &:active { transform: scale(0.96); }
  &.active { background: #2f7d4f; color: #fff; font-weight: 600; }
}

.manage-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 250;
  display: flex; align-items: center; justify-content: center; padding: 30px;
}
.manage-dialog {
  background: #fff; border-radius: 20px; width: 100%; max-width: 360px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.15); overflow: hidden;
}
.manage-dialog-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 20px 14px;
}
.manage-dialog-title { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.manage-dialog-close {
  width: 28px; height: 28px; border-radius: 50%; background: #f5f7f5;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; color: #999; cursor: pointer;
  &:active { background: #e0e0e0; }
}
.manage-dialog-body { padding: 0 20px 20px; }
.manage-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-radius: 10px; margin-bottom: 6px;
  background: #f5f7f5;
}
.manage-item-left { display: flex; align-items: center; gap: 8px; }
.manage-item-name { font-size: 14px; color: #1a1a2e; font-weight: 500; }
.manage-empty { padding: 16px 12px; text-align: center; }
.manage-empty-text { font-size: 13px; color: #999; }
.manage-item-del {
  font-size: 12px; padding: 5px 12px; border-radius: 8px;
  background: #ffebee; color: #c62828; font-weight: 500; cursor: pointer;
  &:active { background: #ffcdd2; }
}
.subject-empty-hint { margin-top: 10px; padding: 10px 12px; background: #fff8e1; border-radius: 10px; }
.subject-empty-text { font-size: 12px; color: #9a7b00; }
.manage-add-row {
  display: flex; gap: 8px; margin-top: 12px; padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.manage-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 250;
  display: flex; align-items: center; justify-content: center; padding: 30px;
}
.manage-dialog {
  background: #fff; border-radius: 20px; width: 100%; max-width: 360px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.15); overflow: hidden;
}
.manage-dialog-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 20px 14px;
}
.manage-dialog-title { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.manage-dialog-close {
  width: 28px; height: 28px; border-radius: 50%; background: #f5f7f5;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; color: #999;
  &:active { background: #e0e0e0; }
}
.manage-dialog-body { padding: 0 20px 20px; }
.manage-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-radius: 10px; margin-bottom: 6px;
  background: #f5f7f5;
}
.manage-item-left { display: flex; align-items: center; gap: 8px; }
.manage-item-name { font-size: 14px; color: #1a1a2e; font-weight: 500; }
.manage-empty { padding: 16px 12px; text-align: center; }
.manage-empty-text { font-size: 13px; color: #999; }
.manage-item-del {
  font-size: 12px; padding: 5px 12px; border-radius: 8px;
  background: #ffebee; color: #c62828; font-weight: 500;
  &:active { background: #ffcdd2; }
}
.subject-empty-hint { margin-top: 10px; padding: 10px 12px; background: #fff8e1; border-radius: 10px; }
.subject-empty-text { font-size: 12px; color: #9a7b00; }
.manage-add-row {
  display: flex; gap: 8px; margin-top: 12px; padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}
.manage-add-input {
  flex: 1; padding: 10px 12px; border: 1.5px solid #e0e0e0; border-radius: 10px;
  font-size: 14px; color: #1a1a2e; background: #f5f7f5;
  height: 44px; line-height: 24px;
}
.manage-add-input:focus { border-color: #2f7d4f; }
.manage-add-btn {
  padding: 10px 20px; border-radius: 10px; background: #2f7d4f; color: #fff;
  font-size: 14px; font-weight: 600; white-space: nowrap;
  &:active { opacity: 0.85; }
}

.ai-section {
  .ai-hint-box {
    background: linear-gradient(135deg, #f3f0ff, #e8f5ff);
    border-radius: 12px; padding: 14px; margin-bottom: 16px;
  }
  .ai-hint-title { display: block; font-size: 15px; font-weight: 600; color: #333; margin-bottom: 10px; }
  .ai-fields-guide { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
  .ai-field { font-size: 12px; padding: 4px 10px; background: #f0f7ff; color: #1565c0; border-radius: 12px; font-weight: 500; }
  .ai-hint-example { display: block; font-size: 12px; color: #888; background: #fef9e7; padding: 8px 12px; border-radius: 8px; line-height: 1.5; }
  .ai-textarea-large {
    width: 100%; min-height: 120px; padding: 14px;
    border: 1px solid #e8ece9; border-radius: 12px;
    font-size: 14px; color: #333; background: #fafafa;
    margin-bottom: 12px;
  }
  .ai-image-upload {
    margin-bottom: 12px;
  }
  .ai-image-preview {
    position: relative;
    border: 1px solid #e8ece9;
    border-radius: 12px;
    overflow: hidden;
    background: #fafafa;
    .ai-image-preview-img {
      width: 100%;
      height: 180px;
    }
    .ai-image-remove {
      position: absolute;
      top: 8px;
      right: 8px;
      width: 28px;
      height: 28px;
      background: rgba(0,0,0,0.5);
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      &:active {
        background: rgba(0,0,0,0.7);
      }
    }
  }
  .ai-image-upload-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 16px;
    border: 2px dashed #d0d5d2;
    border-radius: 12px;
    background: #fafafa;
    .upload-icon { font-size: 24px; }
    .upload-text { font-size: 14px; color: #999; }
    &:active {
      background: #f0f0f0;
      border-color: #2f7d4f;
    }
  }
  .ai-parse-btn-primary {
    display: flex; align-items: center; justify-content: center; gap: 8px;
    padding: 14px; background: linear-gradient(135deg, #6b4ce6, #8b6df0);
    border-radius: 12px; margin-bottom: 20px;
    .btn-icon { font-size: 18px; }
    .btn-text { font-size: 15px; color: #fff; font-weight: 600; }
    &:active { opacity: 0.9; }
  }
}

.ai-result-list {
  .ai-result-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 12px;
  }
  .result-title { font-size: 14px; font-weight: 600; color: #333; }
  .select-all-btn { font-size: 13px; color: #2f7d4f; font-weight: 500; }
}

.ai-task-card {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 12px; background: #f5f7f5; border-radius: 12px;
  margin-bottom: 10px;
  &:active { background: #e8f0eb; }
  .task-checkbox {
    width: 22px; height: 22px; border: 2px solid #d0d5d2;
    border-radius: 6px; flex-shrink: 0; margin-top: 2px;
    &.checked { background: #2f7d4f; border-color: #2f7d4f; }
  }
  .task-card-body { flex: 1; min-width: 0; }
  .task-card-content {
    display: block; font-size: 14px; color: #333;
    margin-bottom: 6px; word-break: break-all;
  }
  .task-card-meta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .meta-tag {
    font-size: 11px; padding: 2px 8px; background: #e8f0eb;
    color: #2f7d4f; border-radius: 4px;
  }
  .meta-text { font-size: 11px; color: #999; }
}

.ai-add-all-btn {
  margin-top: 12px; padding: 14px; text-align: center;
  background: #2f7d4f; color: #fff; border-radius: 12px;
  font-size: 15px; font-weight: 600;
  &:active { opacity: 0.9; }
}

.importance-item {
  display: flex; align-items: center; justify-content: center; gap: 4px;
  .imp-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
  .imp-red { background: #ff4d4f; }
  .imp-blue { background: #1890ff; }
  .imp-orange { background: #fa8c16; }
  .imp-gray { background: #bfbfbf; }
}

@supports (-webkit-touch-callout: none) {
  .type-item, .subject-item {
    transition: none;
    &:active { transform: none; }
  }
}
</style>
