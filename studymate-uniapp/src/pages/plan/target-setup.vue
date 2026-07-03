<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">{{ isEdit ? '编辑计划' : '制定目标' }}</text>
      <view class="save-btn" @click="savePlan">
        <text class="save-text">保存</text>
      </view>
    </view>

    <view class="form">
      <view class="form-group">
        <text class="form-label">考试名称</text>
        <view class="input-wrapper">
          <input class="input-field" v-model="form.exam_name" placeholder="如：2025年考研" />
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">考试日期</text>
        <view class="input-wrapper">
          <picker mode="date" :value="form.exam_date" @change="onDateChange">
            <text class="picker-text" :class="{ placeholder: !form.exam_date }">{{ form.exam_date || '请选择考试日期' }}</text>
          </picker>
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">每日学习时长（分钟）</text>
        <view class="input-wrapper">
          <input class="input-field" v-model="form.daily_study_time" type="number" placeholder="480" />
        </view>
      </view>

      <!-- Custom Subjects -->
      <view class="form-group">
        <text class="form-label">科目设置（自定义添加，目标分数选填）</text>
        <view class="subject-list">
          <view class="subject-item" v-for="(subj, idx) in form.subjects" :key="idx">
            <view class="subject-row">
              <input class="subject-input name" v-model="subj.name" placeholder="科目名称" />
              <input class="subject-input score" v-model="subj.target_score" placeholder="目标分(选填)" />
              <view class="subject-remove" @click="form.subjects.splice(idx, 1)">✕</view>
            </view>
          </view>
          <view class="add-subject-btn" @click="form.subjects.push({ name: '', target_score: '' })">
            <text>+ 添加科目</text>
          </view>
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">学习阶段</text>
        <view class="phase-options">
          <view class="phase-option" :class="{ active: form.study_phase === '基础阶段' }" @click="form.study_phase = '基础阶段'">基础阶段</view>
          <view class="phase-option" :class="{ active: form.study_phase === '强化阶段' }" @click="form.study_phase = '强化阶段'">强化阶段</view>
          <view class="phase-option" :class="{ active: form.study_phase === '冲刺阶段' }" @click="form.study_phase = '冲刺阶段'">冲刺阶段</view>
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">备注</text>
        <view class="input-wrapper">
          <textarea class="textarea-field" v-model="form.notes" placeholder="其他说明..." />
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import { dateUtil } from '@/utils/date'

const planStore = usePlanStore()
const userStore = useUserStore()

const isEdit = ref(false)

const form = reactive({
  exam_name: '',
  exam_date: '',
  daily_study_time: 480,
  study_phase: '基础阶段',
  notes: '',
  subjects: [],
  subject_phases: {}
})

function goBack() {
  uni.navigateBack()
}

function onDateChange(e) {
  form.exam_date = e.detail.value
}

async function savePlan() {
  if (!form.exam_name || !form.exam_date) {
    uni.showToast({ title: '请填写考试名称和日期', icon: 'none' })
    return
  }

  // Filter out empty subjects
  const subjects = form.subjects.filter(s => s.name.trim())

  uni.showLoading({ title: '保存中...' })
  try {
    const data = {
      exam_name: form.exam_name,
      exam_date: form.exam_date,
      daily_study_time: parseInt(form.daily_study_time) || 480,
      study_phase: form.study_phase,
      notes: form.notes,
      subjects,
      subject_phases: form.subject_phases
    }

    if (isEdit.value && planStore.currentPlan) {
      await planStore.updatePlan(planStore.currentPlan.id, data)
    } else {
      await planStore.createPlan(data)
    }

    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1000)
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

onMounted(async () => {
  await userStore.getUserInfo()

  // Check if editing
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  isEdit.value = currentPage?.options?.edit === '1'

  if (isEdit.value && planStore.currentPlan) {
    const p = planStore.currentPlan
    form.exam_name = p.exam_name
    form.exam_date = p.exam_date
    form.daily_study_time = p.daily_study_time
    form.study_phase = p.study_phase
    form.notes = p.notes || ''
    form.subjects = p.subjects ? JSON.parse(JSON.stringify(p.subjects)) : []
    form.subject_phases = p.subject_phases ? JSON.parse(JSON.stringify(p.subject_phases)) : {}
  }
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 20px 20px;
  .back-btn { width: 40px; height: 40px; background: $bg2; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
  .back-icon { font-size: 20px; color: $ink; }
  .page-title { font-size: 20px; font-weight: 600; color: $ink; }
  .save-btn { padding: 8px 20px; background: $accent; border-radius: 20px; }
  .save-text { font-size: 14px; color: #fff; font-weight: 500; }
}

.form { padding: 20px 0; }
.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 80px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.picker-text { font-size: 15px; color: #1a1a2e; &.placeholder { color: #999; } }

.phase-options { display: flex; gap: 8px; }
.phase-option { flex: 1; padding: 12px; text-align: center; border-radius: 12px; font-size: 14px; color: #65746d; background: #f5f7f5; &.active { background: $accent; color: #fff; } }

.subject-list { display: flex; flex-direction: column; gap: 8px; }
.subject-item { background: #f5f7f5; border-radius: 10px; padding: 10px; }
.subject-row { display: flex; align-items: center; gap: 8px; }
.subject-input { flex: 1; padding: 8px 12px; border: 1px solid #e8ece9; border-radius: 8px; font-size: 14px; background: #fff; &.score { flex: 0 0 100px; } }
.subject-remove { font-size: 16px; color: #ef5350; padding: 4px; }
.add-subject-btn { padding: 10px; text-align: center; border: 1.5px dashed #d0d5d2; border-radius: 10px; font-size: 14px; color: $accent; }

.bottom-space { height: 60px; }
</style>