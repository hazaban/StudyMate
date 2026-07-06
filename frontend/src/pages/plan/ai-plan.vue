<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">AI 智能规划</text>
      <view style="width: 40px;"></view>
    </view>

    <!-- Tab 切换 -->
    <view class="tabs">
      <view class="tab-item" :class="{ active: activeTab === 'plan' }" @click="activeTab = 'plan'">
        <text class="tab-text">📋 整体规划对话</text>
      </view>
      <view class="tab-item" :class="{ active: activeTab === 'syllabus' }" @click="activeTab = 'syllabus'">
        <text class="tab-text">📖 科目框架分析</text>
      </view>
    </view>

    <!-- 整体规划对话 -->
    <view class="chat-section" v-if="activeTab === 'plan'">
      <scroll-view scroll-y class="chat-messages" :scroll-into-view="scrollToMsg">
        <view class="msg-item ai" v-for="(msg, idx) in planMessages" :key="idx" :id="'msg-' + idx">
          <view class="msg-avatar ai">🤖</view>
          <view class="msg-bubble ai">
            <text class="msg-text">{{ msg.text }}</text>
            <view class="msg-actions" v-if="msg.type === 'result' && !msg.confirmed">
              <view class="msg-btn secondary" @click="regeneratePlan">重新生成</view>
              <view class="msg-btn primary" @click="confirmPlan">确认应用此计划</view>
            </view>
            <view class="msg-confirmed" v-if="msg.confirmed">
              <text class="confirmed-text">✓ 已应用到计划</text>
            </view>
          </view>
        </view>
        <view class="msg-item user" v-for="(msg, idx) in userPlanMessages" :key="'u-' + idx">
          <view class="msg-bubble user">
            <text class="msg-text">{{ msg.text }}</text>
          </view>
          <view class="msg-avatar user">👤</view>
        </view>
        <view class="msg-item ai" v-if="planLoading">
          <view class="msg-avatar ai">🤖</view>
          <view class="msg-bubble ai loading">
            <text class="msg-text">AI 正在思考中...</text>
          </view>
        </view>
      </scroll-view>

      <view class="chat-input-area">
        <view class="quick-tips" v-if="planMessages.length <= 1">
          <view class="tip-item" @click="quickFill('考研408计算机，还有150天，每天8小时')">
            <text>考研408，150天，每天8小时</text>
          </view>
          <view class="tip-item" @click="quickFill('考公行测申论，还有90天，每天6小时')">
            <text>考公，90天，每天6小时</text>
          </view>
        </view>
        <view class="input-row">
          <input class="chat-input" v-model="planInput" placeholder="告诉我你的考试目标，AI 帮你规划..." @confirm="sendPlanMessage" />
          <view class="send-btn" :class="{ disabled: !planInput.trim() || planLoading }" @click="sendPlanMessage">
            <text class="send-icon">➤</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 科目框架分析 -->
    <view class="syllabus-section" v-if="activeTab === 'syllabus'">
      <view class="subject-selector">
        <text class="selector-label">选择科目</text>
        <view class="subject-options">
          <view
            class="subject-option"
            :class="{ active: currentSubject === subj }"
            v-for="subj in subjectList"
            :key="subj"
            @click="currentSubject = subj"
          >
            <text>{{ subj }}</text>
          </view>
          <view class="subject-option add" @click="showAddSubject = true">
            <text>+ 添加</text>
          </view>
        </view>
      </view>

      <!-- 上传区域 -->
      <view class="upload-area">
        <view class="image-upload-box" v-if="!syllabusImage" @click="chooseSyllabusImage">
          <text class="upload-icon">📷</text>
          <text class="upload-text">上传科目大纲/目录图片</text>
          <text class="upload-hint">AI 将自动解析章节结构</text>
        </view>
        <view class="image-preview" v-else>
          <image :src="syllabusImage" mode="aspectFit" class="preview-image" />
          <view class="image-actions">
            <view class="action-btn" @click="chooseSyllabusImage">
              <text>重新上传</text>
            </view>
            <view class="action-btn danger" @click="removeSyllabusImage">
              <text>删除</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 分析按钮 -->
      <view class="analyze-btn" :class="{ disabled: !syllabusImage || syllabusLoading }" @click="analyzeSyllabus">
        <text v-if="!syllabusLoading">🔍 AI 解析科目框架</text>
        <text v-else>AI 解析中...</text>
      </view>

      <!-- 分析结果 & 对话 -->
      <view class="syllabus-chat" v-if="syllabusResult">
        <view class="result-card">
          <view class="result-header">
            <text class="result-title">📊 章节分析结果</text>
            <text class="result-subject">{{ currentSubject }}</text>
          </view>
          <view class="chapter-list">
            <view class="chapter-item" v-for="(ch, idx) in syllabusChapters" :key="idx">
              <view class="chapter-info">
                <text class="chapter-name">{{ idx + 1 }}. {{ ch.name }}</text>
                <text class="chapter-desc" v-if="ch.description">{{ ch.description }}</text>
              </view>
              <view class="chapter-duration">
                <text class="duration-value">{{ ch.daily_duration || 30 }}</text>
                <text class="duration-unit">分钟/天</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 对话区域 -->
        <scroll-view scroll-y class="chat-area">
          <view class="chat-msg ai" v-for="(msg, idx) in syllabusMessages" :key="idx">
            <text class="msg-role">🤖 AI</text>
            <text class="msg-content">{{ msg.text }}</text>
          </view>
          <view class="chat-msg ai" v-if="syllabusChatLoading">
            <text class="msg-role">🤖 AI</text>
            <text class="msg-content">正在思考中...</text>
          </view>
        </scroll-view>

        <view class="chat-input-row">
          <input class="chat-input" v-model="syllabusInput" placeholder="对章节安排有疑问？问我..." @confirm="sendSyllabusMessage" />
          <view class="send-btn small" :class="{ disabled: !syllabusInput.trim() || syllabusChatLoading }" @click="sendSyllabusMessage">
            <text>发送</text>
          </view>
        </view>

        <!-- 确认按钮 -->
        <view class="confirm-section">
          <view class="confirm-btn" @click="confirmSyllabusToTasks">
            <text>✓ 确认并写入每日任务</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 添加科目弹窗 -->
    <view class="modal-overlay" v-if="showAddSubject" @click="showAddSubject = false">
      <view class="modal-content small" @click.stop>
        <view class="modal-header">
          <text class="modal-title">添加科目</text>
          <view class="modal-close" @click="showAddSubject = false">✕</view>
        </view>
        <view class="modal-body">
          <view class="input-wrapper">
            <input class="input-field" v-model="newSubjectName" placeholder="输入科目名称" />
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showAddSubject = false">取消</view>
          <view class="submit-btn" @click="addSubject">添加</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'

const planStore = usePlanStore()
const userStore = useUserStore()

const activeTab = ref('plan')
const scrollToMsg = ref('')
const showAddSubject = ref(false)
const newSubjectName = ref('')

// ========== 整体规划对话 ==========
const planInput = ref('')
const planLoading = ref(false)
const planConfirmed = ref(false)
const planMessages = ref([
  { text: '你好！我是 AI 学习规划助手。告诉我你的考试目标（考试名称、科目、剩余时间、每天学习时间等），我来帮你制定科学的学习计划。', type: 'intro', confirmed: false }
])
const userPlanMessages = ref([])
const currentPlanResult = ref(null)

function quickFill(text) {
  planInput.value = text
}

async function sendPlanMessage() {
  if (!planInput.value.trim() || planLoading.value) return

  const userText = planInput.value.trim()
  userPlanMessages.value.push({ text: userText })
  planInput.value = ''
  planLoading.value = true

  await scrollToBottom()

  try {
    const result = await api.aiGeneratePlan({
      description: userText,
      subjects: [],
      daily_study_time: 480,
      study_phase: '基础阶段',
      exam_name: '',
      exam_date: ''
    })

    currentPlanResult.value = result
    const planText = formatPlanText(result)

    planMessages.value.push({
      text: planText,
      type: 'result',
      confirmed: false
    })
  } catch (e) {
    planMessages.value.push({
      text: '抱歉，生成计划失败了，请重试。',
      type: 'error',
      confirmed: false
    })
  } finally {
    planLoading.value = false
    await scrollToBottom()
  }
}

function formatPlanText(result) {
  let text = ''
  const plan = result.plan || result
  if (plan.overview) {
    text += `📋 总体规划：\n${plan.overview}\n\n`
  }
  if (plan.phases && plan.phases.length > 0) {
    text += '📅 阶段安排：\n'
    plan.phases.forEach((p, i) => {
      text += `  ${i + 1}. ${p.name}：${p.description}\n`
    })
    text += '\n'
  }
  if (plan.daily_plan) {
    text += `⏰ 每日安排：\n${plan.daily_plan}\n\n`
  }
  if (plan.tips) {
    text += `💡 学习建议：\n${plan.tips}`
  }
  if (!text) {
    text = JSON.stringify(result, null, 2)
  }
  text += '\n\n你觉得这个计划怎么样？可以继续和我对话调整细节，或者确认应用此计划。'
  return text
}

function regeneratePlan() {
  if (userPlanMessages.value.length > 0) {
    planMessages.value = planMessages.value.slice(0, 1)
    userPlanMessages.value = []
    currentPlanResult.value = null
  }
}

async function confirmPlan() {
  uni.showLoading({ title: '创建计划中...' })
  try {
    const data = {
      exam_name: 'AI 生成计划',
      exam_date: new Date(Date.now() + 150 * 24 * 3600 * 1000).toISOString().split('T')[0],
      daily_study_time: 480,
      weak_points: [],
      study_phase: '基础阶段',
      notes: '',
      ai_plan: currentPlanResult.value,
      subjects: [],
      subject_phases: {}
    }
    const result = await planStore.createPlan(data)
    if (result.success) {
      planMessages.value[planMessages.value.length - 1].confirmed = true
      planConfirmed.value = true
      uni.showToast({ title: '计划创建成功！', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 1500)
    }
  } catch (e) {
    uni.showToast({ title: '创建失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

async function scrollToBottom() {
  await nextTick()
  const total = planMessages.value.length + userPlanMessages.value.length
  scrollToMsg.value = 'msg-' + (total - 1)
}

// ========== 科目框架分析 ==========
const subjectList = ref(['数据结构', '操作系统', '计算机网络', '数学', '英语'])
const currentSubject = ref('数据结构')
const syllabusImage = ref('')
const syllabusImageBase64 = ref('')
const syllabusLoading = ref(false)
const syllabusChatLoading = ref(false)
const syllabusResult = ref(null)
const syllabusChapters = ref([])
const syllabusInput = ref('')
const syllabusMessages = ref([])

function addSubject() {
  if (!newSubjectName.value.trim()) return
  subjectList.value.push(newSubjectName.value.trim())
  currentSubject.value = newSubjectName.value.trim()
  newSubjectName.value = ''
  showAddSubject.value = false
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
      syllabusChapters.value = []
      syllabusMessages.value = []
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
  syllabusChapters.value = []
  syllabusMessages.value = []
}

async function analyzeSyllabus() {
  if (!syllabusImage.value || syllabusLoading.value) return
  if (!syllabusImageBase64.value) {
    uni.showToast({ title: '图片处理中，请稍等', icon: 'none' })
    return
  }

  syllabusLoading.value = true
  uni.showLoading({ title: 'AI 解析中...' })

  try {
    const result = await api.aiAnalyzeSyllabus(syllabusImageBase64.value, currentSubject.value)
    syllabusResult.value = result
    if (result.chapters) {
      syllabusChapters.value = result.chapters.map(c => ({
        name: c.name,
        description: c.description || '',
        daily_duration: c.daily_duration || c.estimated_days * 30 || 30
      }))
    }
    syllabusMessages.value = [{
      text: `我已解析完「${currentSubject.value}」的大纲，共识别出 ${syllabusChapters.value.length} 个章节，并为每个章节规划了每日学习时长。你觉得这个安排合理吗？有任何问题都可以问我，比如调整某章节的时长、增加/删除章节等。`
    }]
    uni.showToast({ title: '解析完成', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message || '解析失败', icon: 'none' })
  } finally {
    syllabusLoading.value = false
    uni.hideLoading()
  }
}

async function sendSyllabusMessage() {
  if (!syllabusInput.value.trim() || syllabusChatLoading.value) return
  const userText = syllabusInput.value.trim()
  syllabusInput.value = ''
  syllabusChatLoading.value = true

  try {
    const result = await api.aiAnalyzeSubjectPhase(
      `${userText}\n\n当前章节安排：${syllabusChapters.value.map(c => c.name + '(' + c.daily_duration + '分钟/天)').join('，')}`,
      currentSubject.value
    )

    if (result.chapters) {
      syllabusChapters.value = result.chapters.map(c => ({
        name: c.name,
        description: c.description || '',
        daily_duration: c.daily_duration || 30
      }))
    }

    syllabusMessages.value.push({
      text: result.description || '好的，我已经根据你的建议调整了章节安排。你看看还有什么需要调整的吗？'
    })
  } catch (e) {
    syllabusMessages.value.push({
      text: '抱歉，处理失败了，请重试。'
    })
  } finally {
    syllabusChatLoading.value = false
  }
}

async function confirmSyllabusToTasks() {
  if (!planStore.currentPlan) {
    uni.showToast({ title: '请先创建学习计划', icon: 'none' })
    return
  }
  if (syllabusChapters.value.length === 0) {
    uni.showToast({ title: '没有章节可添加', icon: 'none' })
    return
  }

  uni.showModal({
    title: '确认添加',
    content: `将「${currentSubject.value}」的 ${syllabusChapters.value.length} 个章节添加到今日任务？`,
    success: async (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '添加中...' })
        const today = new Date().toISOString().split('T')[0]
        let added = 0
        for (const ch of syllabusChapters.value) {
          try {
            await api.createTask({
              plan_id: planStore.currentPlan.id,
              date: today,
              type: 'new_study',
              subject: currentSubject.value,
              content: ch.name,
              duration: ch.daily_duration || 30,
              status: 'pending'
            })
            added++
          } catch (e) { /* skip */ }
        }
        uni.hideLoading()
        uni.showToast({ title: `已添加 ${added} 个任务`, icon: 'success' })
      }
    }
  })
}
function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) { uni.navigateBack() } else { uni.switchTab({ url: '/pages/index/index' }) }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg2;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 20px 16px;
  background: $bg2;

  .back-btn {
    width: 40px;
    height: 40px;
    background: #fff;
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

// Tabs
.tabs {
  display: flex;
  padding: 0 16px 12px;
  gap: 8px;

  .tab-item {
    flex: 1;
    padding: 12px;
    background: #fff;
    border-radius: 12px;
    text-align: center;
    border: 2px solid transparent;
    transition: all 0.2s;

    &.active {
      background: $accent;
      border-color: $accent;

      .tab-text {
        color: #fff;
        font-weight: 600;
      }
    }

    .tab-text {
      font-size: 14px;
      color: $muted;
    }
  }
}

// ===== 整体规划对话 =====
.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 16px;
}

.chat-messages {
  flex: 1;
  height: 0;
  padding: 8px 0;
}

.msg-item {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: flex-start;

  &.user {
    flex-direction: row-reverse;
  }

  .msg-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;

    &.ai {
      background: #e8f5e9;
    }

    &.user {
      background: #e3f2fd;
    }
  }

  .msg-bubble {
    max-width: 75%;
    padding: 12px 16px;
    border-radius: 14px;
    line-height: 1.6;

    &.ai {
      background: #fff;
      border-top-left-radius: 4px;

      .msg-text {
        font-size: 14px;
        color: $ink;
        white-space: pre-wrap;
      }

      &.loading {
        .msg-text {
          color: $muted;
          font-style: italic;
        }
      }
    }

    &.user {
      background: $accent;
      border-top-right-radius: 4px;

      .msg-text {
        font-size: 14px;
        color: #fff;
      }
    }

    .msg-actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid $rule;
    }

    .msg-btn {
      flex: 1;
      padding: 8px;
      text-align: center;
      border-radius: 8px;
      font-size: 13px;
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

    .msg-confirmed {
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid $rule;

      .confirmed-text {
        font-size: 13px;
        color: $accent;
        font-weight: 500;
      }
    }
  }
}

.chat-input-area {
  padding: 12px 0 20px;
  background: $bg2;
}

.quick-tips {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  overflow-x: auto;

  .tip-item {
    flex-shrink: 0;
    padding: 6px 12px;
    background: #fff;
    border-radius: 20px;
    font-size: 12px;
    color: $accent;
    border: 1px solid $accent;
  }
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: center;
  background: #fff;
  border-radius: 24px;
  padding: 6px 6px 6px 16px;
}

.chat-input {
  flex: 1;
  font-size: 15px;
  color: $ink;
  border: none;
  outline: none;
  background: transparent;
  height: 40px;
}

.send-btn {
  width: 40px;
  height: 40px;
  background: $accent;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  &.disabled {
    opacity: 0.5;
  }

  .send-icon {
    color: #fff;
    font-size: 16px;
  }

  &.small {
    width: auto;
    padding: 0 16px;
    border-radius: 20px;
    font-size: 14px;
    color: #fff;
  }
}

// ===== 科目框架分析 =====
.syllabus-section {
  flex: 1;
  padding: 0 16px 16px;
  display: flex;
  flex-direction: column;
}

.subject-selector {
  margin-bottom: 16px;

  .selector-label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: $ink;
    margin-bottom: 10px;
  }

  .subject-options {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .subject-option {
      padding: 8px 14px;
      background: #fff;
      border-radius: 20px;
      font-size: 13px;
      color: $muted;
      border: 1px solid $rule;

      &.active {
        background: $accent;
        color: #fff;
        border-color: $accent;
      }

      &.add {
        border-style: dashed;
        color: $accent;
      }
    }
  }
}

.upload-area {
  margin-bottom: 16px;

  .image-upload-box {
    background: #fff;
    border: 2px dashed $accent;
    border-radius: 16px;
    padding: 40px 20px;
    text-align: center;

    .upload-icon {
      display: block;
      font-size: 48px;
      margin-bottom: 12px;
    }

    .upload-text {
      display: block;
      font-size: 16px;
      font-weight: 600;
      color: $accent;
      margin-bottom: 4px;
    }

    .upload-hint {
      font-size: 13px;
      color: $muted;
    }
  }

  .image-preview {
    background: #fff;
    border-radius: 16px;
    padding: 12px;

    .preview-image {
      width: 100%;
      height: 200px;
      border-radius: 12px;
      margin-bottom: 12px;
    }

    .image-actions {
      display: flex;
      gap: 10px;

      .action-btn {
        flex: 1;
        padding: 10px;
        text-align: center;
        border-radius: 10px;
        background: $soft;
        font-size: 13px;
        color: $ink;

        &.danger {
          color: #ef5350;
        }
      }
    }
  }
}

.analyze-btn {
  padding: 14px;
  background: $accent;
  border-radius: 14px;
  text-align: center;
  font-size: 15px;
  color: #fff;
  font-weight: 600;
  margin-bottom: 16px;

  &.disabled {
    opacity: 0.5;
  }
}

.syllabus-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.result-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    .result-title {
      font-size: 15px;
      font-weight: 600;
      color: $ink;
    }

    .result-subject {
      font-size: 12px;
      padding: 4px 10px;
      background: $soft;
      color: $accent;
      border-radius: 12px;
    }
  }

  .chapter-list {
    max-height: 200px;
    overflow-y: auto;

    .chapter-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid $rule;

      &:last-child {
        border-bottom: none;
      }

      .chapter-info {
        flex: 1;

        .chapter-name {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: $ink;
          margin-bottom: 2px;
        }

        .chapter-desc {
          font-size: 12px;
          color: $muted;
        }
      }

      .chapter-duration {
        text-align: right;
        margin-left: 12px;

        .duration-value {
          display: block;
          font-size: 18px;
          font-weight: 700;
          color: $accent;
        }

        .duration-unit {
          font-size: 11px;
          color: $muted;
        }
      }
    }
  }
}

.chat-area {
  flex: 1;
  height: 0;
  background: #fff;
  border-radius: 16px;
  padding: 12px;
  margin-bottom: 10px;
}

.chat-msg {
  margin-bottom: 12px;

  .msg-role {
    display: block;
    font-size: 12px;
    color: $accent;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .msg-content {
    font-size: 13px;
    color: $ink;
    line-height: 1.6;
    background: $soft;
    padding: 10px 12px;
    border-radius: 10px;
    display: inline-block;
  }
}

.chat-input-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;

  .chat-input {
    flex: 1;
    height: 40px;
    padding: 0 16px;
    background: #fff;
    border-radius: 20px;
    font-size: 14px;
    color: $ink;
    border: 1px solid $rule;
  }
}

.confirm-section {
  .confirm-btn {
    padding: 14px;
    background: #4caf50;
    border-radius: 14px;
    text-align: center;
    font-size: 15px;
    color: #fff;
    font-weight: 600;
  }
}

// Modal
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: #fff;
  border-radius: 20px;
  width: 85%;
  max-width: 400px;

  &.small {
    width: 80%;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px;
  border-bottom: 1px solid $rule;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: $ink;
}

.modal-close {
  font-size: 20px;
  color: $muted;
  padding: 4px;
}

.modal-body {
  padding: 20px 24px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px 24px;
}

.cancel-btn, .submit-btn {
  flex: 1;
  padding: 14px;
  text-align: center;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
}

.cancel-btn {
  background: $soft;
  color: $ink;
}

.submit-btn {
  background: $accent;
  color: #fff;
}

.input-wrapper {
  border: 1.5px solid $rule;
  border-radius: 12px;
  padding: 10px 14px;
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

.bottom-space {
  height: 20px;
}
</style>
