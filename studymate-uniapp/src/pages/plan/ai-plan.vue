<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">AI 生成计划</text>
      <view style="width: 40px;"></view>
    </view>

    <view class="form-card">
      <text class="form-desc">告诉 AI 你的考试目标，它将为你生成科学的学习计划</text>

      <view class="form-group">
        <text class="form-label">考试名称</text>
        <view class="input-wrapper">
          <input class="input-field" v-model="form.examName" placeholder="如：2025年考研" />
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">考试日期</text>
        <view class="input-wrapper">
          <picker mode="date" :value="form.examDate" @change="onDateChange">
            <text class="picker-text" :class="{ placeholder: !form.examDate }">{{ form.examDate || '请选择考试日期' }}</text>
          </picker>
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">考试科目（逗号分隔）</text>
        <view class="input-wrapper">
          <input class="input-field" v-model="form.subjects" placeholder="如：数学, 英语, 政治, 专业课" />
        </view>
      </view>

      <!-- AI 分析科目框架图入口 -->
      <view class="syllabus-section">
        <view class="syllabus-header">
          <text class="syllabus-title">🤖 AI 分析科目框架图</text>
          <text class="syllabus-desc">上传科目大纲/目录图片，AI 自动解析章节结构</text>
        </view>
        <view class="image-upload-area">
          <view class="image-item" v-if="syllabusImage">
            <image :src="syllabusImage" mode="aspectFill" class="uploaded-image" />
            <view class="image-remove" @click="removeSyllabusImage">✕</view>
          </view>
          <view class="image-add-btn" @click="chooseSyllabusImage" v-if="!syllabusImage">
            <text class="add-icon">+</text>
            <text class="add-text">上传大纲图片</text>
          </view>
        </view>
        <view class="syllabus-actions">
          <view class="ai-btn" :class="{ disabled: !syllabusImage || analyzing }" @click="aiAnalyzeSyllabus">
            <text v-if="!analyzing">🔍 AI 解析图片</text>
            <text v-else>AI 解析中...</text>
          </view>
        </view>
        <view class="syllabus-result" v-if="syllabusResult">
          <text class="result-label">解析结果：</text>
          <view class="chapter-tags">
            <view class="chapter-tag" v-for="(ch, idx) in syllabusResult.chapters" :key="idx">
              {{ ch.name }}
            </view>
          </view>
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">目标分数（选填，格式：科目:分数）</text>
        <view class="input-wrapper">
          <textarea class="textarea-field" v-model="form.targetScores" placeholder="如：数学:130, 英语:80, 政治:75" />
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">每日可用学习时间（小时）</text>
        <view class="input-wrapper">
          <input class="input-field" v-model="form.dailyHours" type="number" placeholder="8" />
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">薄弱环节（选填）</text>
        <view class="input-wrapper">
          <input class="input-field" v-model="form.weakPoints" placeholder="如：英语阅读, 数学大题" />
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">当前阶段</text>
        <view class="phase-options">
          <view class="phase-option" :class="{ active: form.phase === '基础阶段' }" @click="form.phase = '基础阶段'">基础阶段</view>
          <view class="phase-option" :class="{ active: form.phase === '强化阶段' }" @click="form.phase = '强化阶段'">强化阶段</view>
          <view class="phase-option" :class="{ active: form.phase === '冲刺阶段' }" @click="form.phase = '冲刺阶段'">冲刺阶段</view>
        </view>
      </view>

      <view class="form-group">
        <text class="form-label">额外说明（选填）</text>
        <view class="input-wrapper">
          <textarea class="textarea-field" v-model="form.notes" placeholder="其他特殊要求..." />
        </view>
      </view>

      <view class="generate-btn" @click="generatePlan" :class="{ loading: generating }">
        <text v-if="!generating">🤖 开始生成</text>
        <text v-else>AI 正在制定计划...</text>
      </view>
    </view>

    <view class="result-card" v-if="generatedPlan">
      <text class="result-title">生成结果</text>
      <view class="result-content">
        <text class="result-text">{{ generatedPlan }}</text>
      </view>
      <view class="result-actions">
        <view class="result-btn secondary" @click="regenerate">
          <text>重新生成</text>
        </view>
        <view class="result-btn primary" @click="applyPlan">
          <text>应用此计划</text>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'

const planStore = usePlanStore()
const userStore = useUserStore()

const generating = ref(false)
const generatedPlan = ref(null)
const generatedPlanData = ref(null)
const syllabusImage = ref('')
const syllabusImageBase64 = ref('')
const syllabusResult = ref(null)
const analyzing = ref(false)

const form = reactive({
  examName: '',
  examDate: '',
  subjects: '',
  targetScores: '',
  dailyHours: 8,
  weakPoints: '',
  phase: '基础阶段',
  notes: ''
})

function onDateChange(e) {
  form.examDate = e.detail.value
}

function goBack() {
  uni.navigateBack()
}

function chooseSyllabusImage() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const tempPath = res.tempFilePaths[0]
      syllabusImage.value = tempPath
      syllabusResult.value = null
      // #ifdef H5
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const maxWidth = 1024
        let width = img.width
        let height = img.height
        if (width > maxWidth) {
          height = (maxWidth / width) * height
          width = maxWidth
        }
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        syllabusImageBase64.value = canvas.toDataURL('image/jpeg', 0.8)
      }
      img.src = tempPath
      // #endif
      // #ifndef H5
      uni.getFileSystemManager().readFile({
        filePath: tempPath,
        encoding: 'base64',
        success: (data) => {
          syllabusImageBase64.value = `data:image/jpeg;base64,${data.data}`
        }
      })
      // #endif
    }
  })
}

function removeSyllabusImage() {
  syllabusImage.value = ''
  syllabusImageBase64.value = ''
  syllabusResult.value = null
}

async function aiAnalyzeSyllabus() {
  if (!syllabusImage.value) return
  if (!syllabusImageBase64.value) {
    uni.showToast({ title: '图片正在处理中，请稍等', icon: 'none' })
    return
  }

  analyzing.value = true
  uni.showLoading({ title: 'AI 解析中...' })

  try {
    const firstSubject = form.subjects.split(',')[0]?.trim() || ''
    const result = await api.aiAnalyzeSyllabus(syllabusImageBase64.value, firstSubject)
    syllabusResult.value = result
    uni.showToast({ title: '解析成功', icon: 'success' })
  } catch (e) {
    console.error('Syllabus analysis error:', e)
    uni.showToast({ title: e.message || '解析失败，请重试', icon: 'none' })
  } finally {
    analyzing.value = false
    uni.hideLoading()
  }
}

async function generatePlan() {
  if (!form.examName || !form.examDate || !form.subjects) {
    uni.showToast({ title: '请填写考试名称、日期和科目', icon: 'none' })
    return
  }

  generating.value = true
  uni.showLoading({ title: 'AI 生成中...' })

  try {
    const dailyStudyTime = parseInt(form.dailyHours) * 60
    const result = await api.aiGeneratePlan({
      exam_name: form.examName,
      exam_date: form.examDate,
      daily_study_time: dailyStudyTime,
      subjects: form.subjects.split(',').map(s => s.trim()).filter(Boolean),
      target_scores: form.targetScores,
      weak_points: form.weakPoints ? form.weakPoints.split(',').map(s => s.trim()).filter(Boolean) : [],
      study_phase: form.phase,
      notes: form.notes
    })

    generatedPlanData.value = result
    generatedPlan.value = formatPlan(result)
    uni.showToast({ title: '生成成功', icon: 'success' })
  } catch (e) {
    console.error('AI plan generation error:', e)
    uni.showToast({ title: '生成失败，请重试', icon: 'none' })
  } finally {
    generating.value = false
    uni.hideLoading()
  }
}

function formatPlan(result) {
  let text = ''
  if (result.plan) {
    const plan = result.plan
    if (plan.overview) text += `📋 总体规划：${plan.overview}\n\n`
    if (plan.phases && plan.phases.length > 0) {
      text += '📅 阶段规划：\n'
      plan.phases.forEach((p, i) => {
        text += `${i + 1}. ${p.name}：${p.description}\n`
      })
      text += '\n'
    }
    if (plan.daily_plan) text += `📝 每日安排：${plan.daily_plan}\n\n`
    if (plan.tips) text += `💡 学习建议：${plan.tips}`
  } else {
    text = JSON.stringify(result, null, 2)
  }
  return text
}

function regenerate() {
  generatedPlan.value = null
  generatedPlanData.value = null
}

async function applyPlan() {
  if (!generatedPlanData.value) return

  uni.showLoading({ title: '创建计划中...' })
  try {
    const dailyStudyTime = parseInt(form.dailyHours) * 60
    const data = {
      exam_name: form.examName,
      exam_date: form.examDate,
      daily_study_time: dailyStudyTime,
      weak_points: form.weakPoints ? form.weakPoints.split(',').map(s => s.trim()).filter(Boolean) : [],
      study_phase: form.phase,
      notes: form.notes,
      ai_plan: generatedPlanData.value,
      subjects: form.subjects.split(',').map(s => ({ name: s.trim(), target_score: '', chapters: [] })).filter(s => s.name),
      subject_phases: {}
    }

    const result = await planStore.createPlan(data)
    if (result.success) {
      uni.showToast({ title: '计划创建成功！', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 1000)
    }
  } catch (e) {
    console.error('Create plan error:', e)
    uni.showToast({ title: '创建失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 0 20px;
  
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
}

.form-card {
  background: $bg2;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid $rule;
  margin-bottom: 20px;
}

.form-desc {
  display: block;
  font-size: 14px;
  color: $muted;
  margin-bottom: 20px;
  line-height: 1.6;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: $ink;
  margin-bottom: 8px;
}

.input-wrapper {
  border: 1.5px solid $rule;
  border-radius: 14px;
  padding: 12px 16px;
  background: $soft;
}

.input-field {
  width: 100%;
  font-size: 15px;
  color: $ink;
  border: none;
  outline: none;
  background: transparent;
}

.textarea-field {
  width: 100%;
  min-height: 60px;
  font-size: 15px;
  color: $ink;
  line-height: 1.6;
  border: none;
  outline: none;
  background: transparent;
  resize: none;
}

.picker-text {
  font-size: 15px;
  color: $ink;
  
  &.placeholder {
    color: $muted;
  }
}

.phase-options {
  display: flex;
  gap: 8px;
}

.phase-option {
  flex: 1;
  padding: 12px;
  text-align: center;
  border-radius: 12px;
  font-size: 14px;
  color: $muted;
  background: $soft;
  
  &.active {
    background: $accent;
    color: #fff;
  }
}

.generate-btn {
  padding: 16px;
  background: $accent;
  border-radius: 14px;
  text-align: center;
  font-size: 16px;
  color: #fff;
  font-weight: 600;
  margin-top: 8px;
  
  &.loading {
    opacity: 0.7;
  }
}

.syllabus-section {
  background: $soft;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px dashed $accent;

  .syllabus-header {
    margin-bottom: 12px;

    .syllabus-title {
      display: block;
      font-size: 15px;
      font-weight: 600;
      color: $accent;
      margin-bottom: 4px;
    }

    .syllabus-desc {
      font-size: 12px;
      color: $muted;
    }
  }

  .image-upload-area {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;

    .image-item {
      position: relative;
      width: 100%;
      height: 160px;
      border-radius: 10px;
      overflow: hidden;

      .uploaded-image {
        width: 100%;
        height: 100%;
      }

      .image-remove {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 24px;
        height: 24px;
        background: rgba(0, 0, 0, 0.5);
        color: #fff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
      }
    }

    .image-add-btn {
      width: 100%;
      height: 120px;
      border: 2px dashed $rule;
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;

      .add-icon {
        font-size: 28px;
        color: $muted;
      }

      .add-text {
        font-size: 13px;
        color: $muted;
      }
    }
  }

  .syllabus-actions {
    .ai-btn {
      padding: 12px;
      background: $accent;
      border-radius: 10px;
      text-align: center;
      font-size: 14px;
      color: #fff;
      font-weight: 500;

      &.disabled {
        opacity: 0.5;
      }
    }
  }

  .syllabus-result {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid $rule;

    .result-label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: $ink;
      margin-bottom: 8px;
    }

    .chapter-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;

      .chapter-tag {
        padding: 4px 10px;
        background: #fff;
        border: 1px solid $rule;
        border-radius: 6px;
        font-size: 12px;
        color: $ink;
      }
    }
  }
}

.result-card {
  background: $bg2;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid $accent;
  margin-bottom: 20px;
}

.result-title {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: $accent;
  margin-bottom: 16px;
}

.result-content {
  background: $soft;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.result-text {
  font-size: 14px;
  color: $ink;
  line-height: 1.8;
  white-space: pre-wrap;
}

.result-actions {
  display: flex;
  gap: 12px;
}

.result-btn {
  flex: 1;
  padding: 14px;
  text-align: center;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  
  &.primary {
    background: $accent;
    color: #fff;
  }
  
  &.secondary {
    background: $soft;
    color: $ink;
  }
}

.bottom-space {
  height: 100px;
}
</style>