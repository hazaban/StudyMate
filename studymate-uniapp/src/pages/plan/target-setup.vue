<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">目标设置</text>
      <view class="placeholder"></view>
    </view>

    <view class="form-section">
      <view class="step-indicator">
        <view class="step" :class="{ active: currentStep >= 1 }">1</view>
        <view class="step-line"></view>
        <view class="step" :class="{ active: currentStep >= 2 }">2</view>
        <view class="step-line"></view>
        <view class="step" :class="{ active: currentStep >= 3 }">3</view>
      </view>

      <view class="step-content" v-if="currentStep === 1">
        <text class="step-title">考试信息</text>
        
        <view class="input-group">
          <text class="input-label">考试名称</text>
          <input class="input-field" v-model="form.exam_name" placeholder="如：2026考研计算机" />
        </view>

        <view class="input-group">
          <text class="input-label">考试日期</text>
          <picker mode="date" :value="form.exam_date" @change="onDateChange">
            <view class="input-field input-field-picker">
              {{ form.exam_date || '请选择考试日期' }}
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>

        <view class="input-group">
          <text class="input-label">每日学习时间（分钟）</text>
          <input class="input-field" v-model="form.daily_study_time" placeholder="如：480" type="number" />
        </view>
      </view>

      <view class="step-content" v-if="currentStep === 2">
        <text class="step-title">目标分数</text>
        
        <view class="score-list">
          <view class="score-item" v-for="subject in subjects" :key="subject">
            <text class="subject-name">{{ subject.name }}</text>
            <input class="score-input" v-model="form.target_scores[subject.key]" :placeholder="subject.default" type="number" />
          </view>
        </view>

        <view class="total-score">
          <text class="total-label">总分目标：</text>
          <text class="total-value">{{ totalScore }}</text>
        </view>
      </view>

      <view class="step-content" v-if="currentStep === 3">
        <text class="step-title">学习特点</text>
        
        <view class="input-group">
          <text class="input-label">薄弱科目</text>
          <view class="tag-list">
            <view class="tag" :class="{ active: form.weak_points.includes(subject) }" v-for="subject in weakPointOptions" :key="subject" @click="toggleWeakPoint(subject)">
              {{ subject }}
            </view>
          </view>
        </view>

        <view class="input-group">
          <text class="input-label">学习阶段</text>
          <view class="radio-group">
            <view class="radio" :class="{ active: form.study_phase === phase }" v-for="phase in phases" :key="phase" @click="form.study_phase = phase">
              {{ phase }}
            </view>
          </view>
        </view>

        <view class="input-group">
          <text class="input-label">备注（可选）</text>
          <textarea class="textarea-field" v-model="form.notes" placeholder="请描述你的学习特点、备考经验等..." />
        </view>
      </view>

      <view class="button-group">
        <view class="btn-secondary" @click="prevStep" v-if="currentStep > 1">上一步</view>
        <view class="btn-primary" @click="nextStep" v-if="currentStep < 3">下一步</view>
        <view class="btn-primary" @click="submitPlan" v-if="currentStep === 3">生成计划</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import { dateUtil } from '@/utils/date'

const planStore = usePlanStore()
const userStore = useUserStore()

const currentStep = ref(1)

const subjects = [
  { key: 'math', name: '数学', default: '120' },
  { key: 'english', name: '英语', default: '70' },
  { key: 'politics', name: '政治', default: '65' },
  { key: 'professional', name: '专业课', default: '110' }
]

const weakPointOptions = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']

const phases = ['基础阶段', '强化阶段', '冲刺阶段']

const form = reactive({
  exam_name: '',
  exam_date: '',
  daily_study_time: '480',
  target_scores: {
    math: '',
    english: '',
    politics: '',
    professional: ''
  },
  weak_points: [],
  study_phase: '基础阶段',
  notes: ''
})

const totalScore = computed(() => {
  let sum = 0
  Object.values(form.target_scores).forEach(score => {
    sum += parseInt(score) || 0
  })
  return sum
})

function onDateChange(e) {
  form.exam_date = e.detail.value
}

function toggleWeakPoint(subject) {
  const index = form.weak_points.indexOf(subject)
  if (index === -1) {
    form.weak_points.push(subject)
  } else {
    form.weak_points.splice(index, 1)
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

function nextStep() {
  if (currentStep.value === 1) {
    if (!form.exam_name || !form.exam_date || !form.daily_study_time) {
      uni.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }
  }
  currentStep.value++
}

async function submitPlan() {
  uni.showLoading({ title: 'AI生成计划中...' })

  try {
    const aiPlan = await planStore.generatePlanByAI({
      exam_name: form.exam_name,
      exam_date: form.exam_date,
      target_scores: form.target_scores,
      daily_study_time: parseInt(form.daily_study_time),
      weak_points: form.weak_points,
      study_phase: form.study_phase
    })

    const planData = {
      user_id: userStore.user.id,
      exam_name: form.exam_name,
      exam_date: form.exam_date,
      target_scores: form.target_scores,
      daily_study_time: parseInt(form.daily_study_time),
      weak_points: form.weak_points,
      study_phase: form.study_phase,
      notes: form.notes,
      ai_plan: aiPlan
    }

    const result = await planStore.createPlan(planData)

    if (result.success) {
      uni.showToast({ title: '计划创建成功', icon: 'success' })
      setTimeout(() => {
        uni.redirectTo({ url: '/pages/plan/plan-overview' })
      }, 1000)
    } else {
      uni.showToast({ title: '创建失败', icon: 'none' })
    }
  } catch (error) {
    uni.showToast({ title: '创建失败', icon: 'none' })
    console.error(error)
  } finally {
    uni.hideLoading()
  }
}

function goBack() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 20px 20px;
  
  .back-btn {
    width: 40px;
    height: 40px;
    background: $bg2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .back-icon {
      font-size: 20px;
      color: $ink;
    }
  }
  
  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: $ink;
  }
  
  .placeholder {
    width: 40px;
  }
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  gap: 8px;
}

.step {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: $soft;
  color: $muted;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  
  &.active {
    background: $accent;
    color: #fff;
  }
}

.step-line {
  width: 40px;
  height: 2px;
  background: $rule;
  
  .step.active + & {
    background: $accent;
  }
}

.step-content {
  margin-bottom: 30px;
}

.step-title {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: $ink;
  margin-bottom: 20px;
}

.input-group {
  margin-bottom: 16px;
  
  .input-label {
    display: block;
    font-size: 14px;
    color: $ink;
    margin-bottom: 8px;
    font-weight: 500;
  }
  
  .input-field {
    width: 100%;
    padding: 14px 16px;
    border: 1px solid $rule;
    border-radius: 12px;
    font-size: 16px;
    color: $ink;
    background: $bg2;
    
    &:focus {
      border-color: $accent;
      outline: none;
    }
    
    .picker-arrow {
      font-size: 12px;
      color: $muted;
    }
  }

  .input-field-picker {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .textarea-field {
    width: 100%;
    padding: 14px 16px;
    border: 1px solid $rule;
    border-radius: 12px;
    font-size: 16px;
    color: $ink;
    background: $bg2;
    height: 120px;
  }
}

.score-list {
  background: $bg2;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid $rule;
}

.score-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid $rule;
  
  &:last-child {
    border-bottom: none;
  }
  
  .subject-name {
    font-size: 16px;
    color: $ink;
  }
  
  .score-input {
    width: 80px;
    padding: 10px 12px;
    border: 1px solid $rule;
    border-radius: 8px;
    font-size: 16px;
    color: $ink;
    text-align: center;
  }
}

.total-score {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: 16px;
  padding: 12px;
  background: $soft;
  border-radius: 8px;
  
  .total-label {
    font-size: 14px;
    color: $muted;
  }
  
  .total-value {
    font-size: 24px;
    font-weight: 700;
    color: $accent;
    margin-left: 8px;
  }
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  background: $bg2;
  color: $muted;
  border: 1px solid $rule;
  
  &.active {
    background: $soft;
    color: $accent;
    border-color: $accent;
  }
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.radio {
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 14px;
  background: $bg2;
  color: $muted;
  border: 1px solid $rule;
  
  &.active {
    background: $accent;
    color: #fff;
    border-color: $accent;
  }
}

.button-group {
  display: flex;
  gap: 12px;
  
  .btn-secondary, .btn-primary {
    flex: 1;
    padding: 14px;
    border-radius: 12px;
    text-align: center;
    font-size: 16px;
    font-weight: 500;
  }
  
  .btn-secondary {
    background: $bg2;
    color: $ink;
    border: 1px solid $rule;
  }
  
  .btn-primary {
    background: $accent;
    color: #fff;
  }
}
</style>