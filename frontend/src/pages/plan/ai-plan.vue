<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">AI 智能规划</text>
      <view style="width: 40px;"></view>
    </view>

    <!-- 聊天区域 -->
    <scroll-view scroll-y class="chat-messages" :scroll-into-view="scrollToMsg">
      <view class="msg-item ai" v-for="(msg, idx) in messages" :key="idx" :id="'msg-' + idx">
        <view class="msg-avatar ai">🤖</view>
        <view class="msg-bubble ai">
          <text class="msg-text">{{ msg.text }}</text>
          <view class="msg-content" v-if="msg.content">
            <view class="content-section" v-if="msg.type === 'tasks' && msg.content.tasks && msg.content.tasks.length">
              <text class="section-title">📋 识别到的任务</text>
              <view class="task-list">
                <view class="task-item" v-for="(t, tidx) in msg.content.tasks" :key="tidx">
                  <text class="task-content">{{ t.content }}</text>
                  <view class="task-meta">
                    <text class="task-subject">{{ t.subject }}</text>
                    <text class="task-duration">{{ t.duration }}分钟</text>
                    <text class="task-date">{{ t.date }}</text>
                  </view>
                </view>
              </view>
              <view class="msg-btn primary" @click="confirmTasks(msg.content.tasks)">确认添加任务</view>
            </view>
            <view class="content-section" v-if="msg.type === 'syllabus' && msg.content.chapters && msg.content.chapters.length">
              <text class="section-title">📖 章节分析结果</text>
              <view class="chapter-list">
                <view class="chapter-item" v-for="(ch, cidx) in msg.content.chapters" :key="cidx">
                  <text class="chapter-name">{{ cidx + 1 }}. {{ ch.name }}</text>
                  <view class="chapter-meta">
                    <text>{{ ch.daily_duration || 30 }}分钟/天</text>
                    <text>预计{{ ch.estimated_days || 1 }}天</text>
                  </view>
                </view>
              </view>
              <text class="section-total" v-if="msg.content.total_days">总计预计 {{ msg.content.total_days }} 天</text>
              <view class="msg-btn primary" @click="confirmSyllabus(msg.content)">确认写入计划</view>
            </view>
            <view class="content-section" v-if="msg.type === 'plan' && msg.content.phases && msg.content.phases.length">
              <text class="section-title">📅 生成的学习计划</text>
              <view class="plan-summary">
                <text class="plan-overview" v-if="msg.content.overview">{{ msg.content.overview }}</text>
                <view class="phase-list">
                  <view class="phase-item" v-for="(p, pidx) in msg.content.phases" :key="pidx">
                    <text class="phase-name">{{ pidx + 1 }}. {{ p.name }}</text>
                    <text class="phase-desc">{{ p.description }}</text>
                  </view>
                </view>
              </view>
              <view class="msg-btn primary" @click="confirmPlan(msg.content)">确认应用此计划</view>
            </view>
            <view class="content-section" v-if="msg.type === 'review' && msg.content.summary">
              <text class="section-title">📊 今日复盘</text>
              <text class="review-summary">{{ msg.content.summary }}</text>
              <view class="review-items" v-if="msg.content.achievements && msg.content.achievements.length">
                <text class="review-label">🎯 成就</text>
                <text class="review-item" v-for="(a, aidx) in msg.content.achievements" :key="aidx">✓ {{ a }}</text>
              </view>
              <view class="review-items" v-if="msg.content.suggestions && msg.content.suggestions.length">
                <text class="review-label">💡 建议</text>
                <text class="review-item" v-for="(s, sidx) in msg.content.suggestions" :key="sidx">• {{ s }}</text>
              </view>
              <text class="review-encourage" v-if="msg.content.encouragement">{{ msg.content.encouragement }}</text>
            </view>
          </view>
        </view>
      </view>
      <view class="msg-item user" v-for="(msg, idx) in userMessages" :key="'u-' + idx">
        <view class="msg-bubble user">
          <text class="msg-text">{{ msg.text }}</text>
          <image v-if="msg.image" :src="msg.image" mode="widthFix" class="msg-image" />
        </view>
        <view class="msg-avatar user">👤</view>
      </view>
      <view class="msg-item ai" v-if="loading">
        <view class="msg-avatar ai">🤖</view>
        <view class="msg-bubble ai loading">
          <text class="msg-text">AI 正在思考中...</text>
        </view>
      </view>
    </scroll-view>

    <!-- 输入区域 -->
    <view class="chat-input-area">
      <view class="chat-hint" v-if="messages.length <= 1">
        <view class="chat-hint-header" @click="toggleHint">
          <text class="chat-hint-title">💡 我可以帮你做这些事：</text>
          <text class="hint-toggle">{{ showHintDetail ? '▼' : '▶' }}</text>
        </view>
        <view class="chat-hint-tags" v-if="showHintDetail">
          <text class="hint-tag">📋 规划学习计划（如：考研408，150天，每天8小时）</text>
          <text class="hint-tag">✅ 添加任务（如：明天上午9点复习数据结构）</text>
          <text class="hint-tag">📖 分析教材目录（上传图片或输入章节列表）</text>
          <text class="hint-tag">📊 每日复盘（如：今天学了什么，给我复盘一下）</text>
        </view>
      </view>
      <view class="quick-tips" v-if="messages.length <= 1">
        <view class="tip-item" @click="quickFill('考研408计算机，还有150天，每天8小时')">
          <text>考研408，150天，每天8小时</text>
        </view>
        <view class="tip-item" @click="quickFill('明天上午复习数据结构，下午做英语阅读')">
          <text>添加任务：明天复习数据结构</text>
        </view>
        <view class="tip-item" @click="triggerUpload">
          <text>上传教材目录图片</text>
        </view>
      </view>
      <view class="input-row">
        <view class="upload-btn" @click="chooseImage">
          <text class="upload-icon">📷</text>
        </view>
        <input class="chat-input" v-model="inputText" placeholder="输入你的需求，或上传图片..." @confirm="sendMessage" />
        <view class="send-btn" :class="{ disabled: !inputText.trim() && !currentImageBase64 || loading }" @click="sendMessage">
          <text class="send-icon">➤</text>
        </view>
      </view>
      <image v-if="currentImage" :src="currentImage" mode="widthFix" class="preview-image-small" />
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useSubjectsStore } from '@/stores/subjects'
import * as api from '@/api/client'

const planStore = usePlanStore()
const subjectsStore = useSubjectsStore()

const messages = ref([
  { text: '你好！我是 AI 学习规划助手。你可以告诉我你的考试目标、添加学习任务、上传教材目录图片分析框架，或者让我帮你做每日复盘。', type: 'intro', content: null }
])
const userMessages = ref([])
const inputText = ref('')
const loading = ref(false)
const scrollToMsg = ref('')
const showHintDetail = ref(false)
const currentImage = ref('')
const currentImageBase64 = ref('')

function goBack() {
  uni.navigateBack()
}

function toggleHint() {
  showHintDetail.value = !showHintDetail.value
}

function quickFill(text) {
  inputText.value = text
}

function triggerUpload() {
  chooseImage()
}

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const tempPath = res.tempFilePaths[0]
      currentImage.value = tempPath
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
        currentImageBase64.value = canvas.toDataURL('image/jpeg', 0.8)
      }
      img.src = tempPath
      // #endif
      // #ifndef H5
      uni.getFileSystemManager().readFile({
        filePath: tempPath,
        encoding: 'base64',
        success: (data) => {
          currentImageBase64.value = `data:image/jpeg;base64,${data.data}`
        }
      })
      // #endif
    }
  })
}

async function sendMessage() {
  if ((!inputText.value.trim() && !currentImageBase64.value) || loading.value) return

  const userText = inputText.value.trim()
  userMessages.value.push({ text: userText || '[图片]', image: currentImage.value })
  inputText.value = ''
  loading.value = true

  await scrollToBottom()

  try {
    const data = {
      text: userText,
      image: currentImageBase64.value,
      plan_id: planStore.currentPlan?.id || null
    }

    const result = await api.aiChat(data)

    messages.value.push({
      text: result.summary,
      type: result.tool,
      content: result.data
    })

    currentImage.value = ''
    currentImageBase64.value = ''
  } catch (e) {
    messages.value.push({
      text: '抱歉，处理失败了，请重试。',
      type: 'error',
      content: null
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function confirmTasks(tasks) {
  if (!tasks || tasks.length === 0) return
  uni.showLoading({ title: '添加任务中...' })
  try {
    for (const task of tasks) {
      if (planStore.currentPlan) {
        await api.createTask({
          plan_id: planStore.currentPlan.id,
          content: task.content,
          subject: task.subject,
          chapter: task.chapter || '',
          duration: task.duration || 30,
          type: task.type || 'new_study',
          date: task.date,
          start_hour: task.start_hour || 9,
          start_minute: task.start_minute || 0,
          repeat_type: task.repeat_type || 'none',
          selected: true
        })
      }
    }
    uni.showToast({ title: `已添加 ${tasks.length} 个任务`, icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '添加失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

async function confirmSyllabus(data) {
  if (!data || !data.chapters || data.chapters.length === 0) return
  uni.showLoading({ title: '写入计划中...' })
  try {
    const subject = data.subject || '未知科目'
    subjectsStore.add(subject)

    if (planStore.currentPlan) {
      let dayOffset = 0
      for (const chapter of data.chapters) {
        const days = chapter.estimated_days || 1
        const duration = chapter.daily_duration || 30
        for (let i = 0; i < days; i++) {
          const date = new Date()
          date.setDate(date.getDate() + dayOffset + i)
          await api.createTask({
            plan_id: planStore.currentPlan.id,
            content: `学习 ${chapter.name}`,
            subject: subject,
            chapter: chapter.name,
            duration: duration,
            type: 'new_study',
            date: date.toISOString().split('T')[0],
            start_hour: 9,
            start_minute: 0,
            repeat_type: 'none',
            selected: true
          })
        }
        dayOffset += days
      }
    }
    uni.showToast({ title: `已写入 ${data.total_days} 天任务`, icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '写入失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

async function confirmPlan(data) {
  uni.showLoading({ title: '创建计划中...' })
  try {
    const planData = {
      exam_name: 'AI 生成计划',
      exam_date: new Date(Date.now() + 150 * 24 * 3600 * 1000).toISOString().split('T')[0],
      daily_study_time: 480,
      weak_points: [],
      notes: '',
      ai_plan: data,
      subjects: [],
      subject_phases: {}
    }
    const result = await planStore.createPlan(planData)
    if (result.success) {
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
  const total = messages.value.length + userMessages.value.length
  scrollToMsg.value = 'msg-' + (total - 1)
}

onMounted(async () => {
  await subjectsStore.load()
})
</script>

<style lang="scss">
.page {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: linear-gradient(135deg, #6b4ce6 0%, #8b5cf6 100%);
  color: #fff;
}

.back-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 24px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.msg-item {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
}

.msg-item.ai {
  flex-direction: row;
}

.msg-item.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.msg-avatar.ai {
  background: linear-gradient(135deg, #6b4ce6 0%, #8b5cf6 100%);
}

.msg-avatar.user {
  background: #ddd;
}

.msg-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
}

.msg-bubble.ai {
  background: #fff;
  margin-left: 10px;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.msg-bubble.user {
  background: linear-gradient(135deg, #6b4ce6 0%, #8b5cf6 100%);
  margin-right: 10px;
  border-bottom-right-radius: 4px;
}

.msg-bubble.loading {
  opacity: 0.6;
}

.msg-text {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.msg-bubble.user .msg-text {
  color: #fff;
}

.msg-image {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 8px;
}

.msg-content {
  margin-top: 12px;
}

.content-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
  margin-top: 10px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #6b4ce6;
  margin-bottom: 10px;
  display: block;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  background: #fff;
  padding: 10px;
  border-radius: 8px;
}

.task-content {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  display: block;
}

.task-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.task-subject, .task-duration, .task-date {
  font-size: 11px;
  color: #999;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-item {
  background: #fff;
  padding: 10px;
  border-radius: 8px;
}

.chapter-name {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  display: block;
}

.chapter-meta {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  font-size: 11px;
  color: #999;
}

.section-total {
  font-size: 12px;
  color: #6b4ce6;
  margin-top: 8px;
  display: block;
}

.plan-summary {
  background: #fff;
  padding: 10px;
  border-radius: 8px;
}

.plan-overview {
  font-size: 13px;
  color: #333;
  line-height: 1.6;
  display: block;
  margin-bottom: 10px;
}

.phase-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.phase-item {
  padding: 8px;
  background: #f0f4ff;
  border-radius: 6px;
}

.phase-name {
  font-size: 13px;
  font-weight: 600;
  color: #6b4ce6;
  display: block;
}

.phase-desc {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
  display: block;
}

.review-summary {
  font-size: 13px;
  color: #333;
  line-height: 1.6;
  display: block;
  margin-bottom: 10px;
}

.review-items {
  margin-bottom: 8px;
}

.review-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b4ce6;
  display: block;
  margin-bottom: 4px;
}

.review-item {
  font-size: 12px;
  color: #666;
  display: block;
  margin-bottom: 2px;
}

.review-encourage {
  font-size: 13px;
  color: #4caf50;
  font-weight: 500;
  margin-top: 10px;
  display: block;
}

.msg-btn {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  margin-top: 12px;
  text-align: center;
}

.msg-btn.primary {
  background: linear-gradient(135deg, #6b4ce6 0%, #8b5cf6 100%);
  color: #fff;
}

.chat-input-area {
  padding: 15px;
  background: #fff;
  border-top: 1px solid #eee;
}

.chat-hint {
  margin-bottom: 10px;
}

.chat-hint-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-hint-title {
  font-size: 13px;
  color: #999;
}

.hint-toggle {
  font-size: 12px;
  color: #999;
}

.chat-hint-tags {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hint-tag {
  font-size: 12px;
  color: #666;
  padding: 4px 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.quick-tips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.tip-item {
  padding: 6px 12px;
  background: #f0f4ff;
  border-radius: 16px;
  font-size: 12px;
  color: #6b4ce6;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.upload-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 12px;
}

.upload-icon {
  font-size: 20px;
}

.chat-input {
  flex: 1;
  height: 44px;
  padding: 0 15px;
  background: #f5f5f5;
  border-radius: 22px;
  font-size: 14px;
}

.send-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6b4ce6 0%, #8b5cf6 100%);
  border-radius: 12px;
}

.send-btn.disabled {
  opacity: 0.5;
}

.send-icon {
  font-size: 18px;
  color: #fff;
}

.preview-image-small {
  max-width: 200px;
  border-radius: 8px;
  margin-top: 10px;
}

.bottom-space {
  height: 20px;
}
</style>
