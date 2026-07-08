<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">AI 智能规划</text>
      <view class="sidebar-toggle" @click="showSidebar = !showSidebar"><text class="sidebar-icon">{{ showSidebar ? '✕' : '☰' }}</text></view>
    </view>

    <!-- 会话历史侧边栏 -->
    <view class="sidebar-overlay" v-if="showSidebar" @click="showSidebar = false">
      <view class="sidebar-panel" @click.stop>
        <text class="sidebar-title">历史会话</text>
        <scroll-view scroll-y class="sidebar-list">
          <view class="sidebar-item" v-for="(conv, ci) in conversationList" :key="ci" @click="loadConversation(ci)">
            <text class="sidebar-item-title">{{ conv.title }}</text>
            <text class="sidebar-item-date">{{ conv.date }}</text>
          </view>
          <text class="sidebar-empty" v-if="conversationList.length === 0">暂无历史会话</text>
        </scroll-view>
        <view class="sidebar-new-btn" @click="startNewConversation">+ 新会话</view>
      </view>
    </view>

    <!-- 引导式规划进度条 -->
    <view class="plan-progress" v-if="planStep.stage > 0">
      <view class="step-item" v-for="s in planSteps" :key="s.stage"
        :class="{ active: s.stage === planStep.stage, done: s.stage < planStep.stage }">
        <view class="step-dot">
          <text v-if="s.stage < planStep.stage">✓</text>
          <text v-else>{{ s.stage }}</text>
        </view>
        <text class="step-label">{{ s.label }}</text>
        <text class="step-sub" v-if="s.stage === planStep.stage && planStep.subject">{{ planStep.subject }}</text>
      </view>
    </view>

    <scroll-view scroll-y class="chat-messages" :scroll-into-view="scrollToMsg">
      <view v-for="(msg, idx) in displayMessages" :key="idx" :id="'msg-' + idx">
        <!-- AI 消息 -->
        <view class="msg-item ai" v-if="msg.role === 'ai'">
          <view class="msg-avatar ai">🤖</view>
          <view class="msg-bubble ai">
            <text class="msg-text" v-if="msg.displayText || msg.text">{{ msg.displayText || msg.text }}</text>
            <view class="msg-content" v-if="msg.content">
              <view class="content-section" v-if="msg.type === 'task' && msg.content.tasks && msg.content.tasks.length">
                <text class="section-title">📋 识别到的任务{{ msg._autoAdded ? '（已自动添加到日程）' : '' }}</text>
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
                <view class="msg-btn primary" v-if="!msg._autoAdded" @click="confirmTasks(msg.content.tasks)">确认添加任务</view>
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
        <!-- 用户消息 -->
        <view class="msg-item user" v-else-if="msg.role === 'user'">
          <view class="msg-bubble user">
            <text class="msg-text">{{ msg.text }}</text>
            <image v-if="msg.image" :src="msg.image" mode="widthFix" class="msg-image" />
          </view>
          <view class="msg-avatar user">👤</view>
        </view>
      </view>
      <view class="msg-item ai" v-if="loading">
        <view class="msg-avatar ai">🤖</view>
        <view class="msg-bubble ai loading">
          <text class="msg-text">AI 正在思考中...</text>
        </view>
      </view>
    </scroll-view>

    <view class="chat-input-area">
      <view class="quick-actions" v-if="displayMessages.filter(m => m.role === 'ai').length <= 1">
        <text class="quick-title">💡 试试这些：</text>
        <view class="quick-grid">
          <view class="quick-card" @click="quickFill('考研408计算机，还有150天，每天8小时')">
            <text class="quick-icon">📋</text>
            <text class="quick-label">规划学习计划</text>
            <text class="quick-example">考研408，150天，每天8小时</text>
          </view>
          <view class="quick-card" @click="quickFill('明天上午复习数据结构，下午做英语阅读')">
            <text class="quick-icon">✅</text>
            <text class="quick-label">添加任务</text>
            <text class="quick-example">明天复习数据结构</text>
          </view>
          <view class="quick-card" @click="chooseImage">
            <text class="quick-icon">📖</text>
            <text class="quick-label">分析教材目录</text>
            <text class="quick-example">上传目录图片</text>
          </view>
          <view class="quick-card" @click="quickFill('今天学了什么，给我复盘一下')">
            <text class="quick-icon">📊</text>
            <text class="quick-label">每日复盘</text>
            <text class="quick-example">今天学了什么</text>
          </view>
        </view>
      </view>
      <view class="input-row">
        <view class="upload-btn" @click="chooseImage">
          <text class="upload-icon">📷</text>
        </view>
        <input class="chat-input" v-model="inputText" placeholder="输入你的需求，或上传图片..." @confirm="sendMessage" />
        <view class="send-btn" v-if="!loading" :class="{ disabled: !inputText.trim() && !currentImageBase64 }" @click="sendMessage">
          <text class="send-icon">➤</text>
        </view>
        <view class="send-btn stop-btn" v-else @click="stopMessage">
          <text class="stop-icon">■</text>
        </view>
      </view>
      <image v-if="currentImage" :src="currentImage" mode="widthFix" class="preview-image-small" />
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useSubjectsStore } from '@/stores/subjects'
import * as api from '@/api/client'

const planStore = usePlanStore()
const subjectsStore = useSubjectsStore()

const messages = ref([
  { text: '你好！我是 AI 学习规划助手。你可以告诉我你的考试目标、添加学习任务、上传教材目录图片分析框架，或者让我帮你做每日复盘。', type: 'intro', content: null }
])
const userMessages = ref([])

// 交错排列 AI 消息和用户消息，保证对话顺序正确
const displayMessages = computed(() => {
  const stripMarker = (text) => (text || '').replace(/◆\S*/g, '').trim()
  const result = []
  let aiIdx = 0, userIdx = 0
  if (messages.value[0]?.type === 'intro') {
    result.push({ ...messages.value[0], role: 'ai', displayText: messages.value[0].text })
    aiIdx = 1
  }
  while (aiIdx < messages.value.length || userIdx < userMessages.value.length) {
    if (userIdx < userMessages.value.length) {
      result.push({ ...userMessages.value[userIdx], role: 'user', displayText: userMessages.value[userIdx].text })
      userIdx++
    }
    if (aiIdx < messages.value.length) {
      const msg = { ...messages.value[aiIdx], role: 'ai' }
      // plan 消息有结构化内容时，隐藏原始 JSON 正文，只显示简短提示
      if (msg.type === 'plan' && msg.content?.phases?.length) {
        msg.displayText = '学习计划已生成，详情见下方卡片 ↘'
      } else if (msg.text && (msg.text.startsWith('{') || msg.text.startsWith('```'))) {
        // GLM 返回了原始 JSON → 截断为提示
        msg.displayText = '处理完成，详情见下方卡片 ↘'
      } else {
        msg.displayText = stripMarker(msg.text)
      }
      result.push(msg)
      aiIdx++
    }
  }
  return result
})

// 引导式规划进度：解析 AI 消息中的阶段标记 ◆N/4 标签
const planSteps = [
  { stage: 1, label: '基本信息' },
  { stage: 2, label: '科目设置' },
  { stage: 3, label: '章节确认' },
  { stage: 4, label: '汇总生成' },
]
const planStep = computed(() => {
  // 从后往前扫描 AI 消息，找到最近的阶段标记
  const aiMsgs = messages.value
  let stage = 0, subject = ''
  for (let i = aiMsgs.length - 1; i >= 0; i--) {
    const text = aiMsgs[i].text || ''
    const m = text.match(/◆(\d)\/4\s*(\S*)/)
    if (m) {
      stage = parseInt(m[1])
      subject = m[2] || ''
      break
    }
  }
  // 如果 AI 已经调用了 tool=plan，标记为阶段4完成
  if (stage === 0 && aiMsgs.some(m => m.type === 'plan')) {
    stage = 4
  }
  return { stage, subject }
})

const conversationList = ref([])
const showSidebar = ref(false)
const CONV_KEY = 'studymate_ai_conversations'
const LAST_CONV_KEY = 'studymate_ai_last_conv'
function loadConversationList() { try { conversationList.value = JSON.parse(uni.getStorageSync(CONV_KEY) || '[]') } catch(e) { conversationList.value = [] } }
function saveCurrentConversation() {
  const aiMsgs = messages.value
  if (aiMsgs.length <= 1 && userMessages.value.length === 0) return
  const title = userMessages.value[0]?.text?.substring(0, 30) || '新会话'
  const conv = { title, date: new Date().toLocaleDateString(), messages: [...messages.value], userMessages: [...userMessages.value] }
  const list = conversationList.value.filter(c => c.title !== title)
  list.unshift(conv)
  if (list.length > 20) list.length = 20
  conversationList.value = list
  uni.setStorageSync(CONV_KEY, JSON.stringify(list))
  // 同时保存为"最近会话"，切换页面后自动恢复
  uni.setStorageSync(LAST_CONV_KEY, JSON.stringify(conv))
}
function restoreLastConversation() {
  try {
    const saved = JSON.parse(uni.getStorageSync(LAST_CONV_KEY) || 'null')
    if (saved && saved.messages?.length > 1) {
      messages.value = saved.messages
      userMessages.value = saved.userMessages || []
      return true
    }
  } catch(e) { /* ignore */ }
  return false
}
function startNewConversation() { saveCurrentConversation(); messages.value = [{text:'你好！我是 AI 学习规划助手。有什么可以帮你的？',type:'intro',content:null}]; userMessages.value = []; showSidebar.value = false; uni.removeStorageSync(LAST_CONV_KEY) }
function loadConversation(idx) { saveCurrentConversation(); const c = conversationList.value[idx]; if(!c) return; messages.value = c.messages; userMessages.value = c.userMessages||[]; showSidebar.value = false; uni.setStorageSync(LAST_CONV_KEY, JSON.stringify(c)) }
const inputText = ref('')
const loading = ref(false)
const abortFlag = ref(false)
const scrollToMsg = ref('')
const currentImage = ref('')
const currentImageBase64 = ref('')

function goBack() {
  uni.navigateBack()
}

function quickFill(text) {
  inputText.value = text
}

function chooseImage() {
  // #ifdef H5
  pickImage(['album'])
  // #endif
  // #ifndef H5
  uni.showActionSheet({
    itemList: ['拍照', '从相册选择'],
    success: (res) => {
      pickImage(res.tapIndex === 0 ? ['camera'] : ['album'])
    }
  })
  // #endif
}

function pickImage(sourceType) {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: sourceType,
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

function stopMessage() {
  abortFlag.value = true
  loading.value = false
}

async function sendMessage() {
  if ((!inputText.value.trim() && !currentImageBase64.value) || loading.value) return

  abortFlag.value = false
  const userText = inputText.value.trim()
  userMessages.value.push({ text: userText || '[图片]', image: currentImage.value })
  inputText.value = ''
  loading.value = true
  await scrollToBottom()
  try {
    const data = { text: userText, image: currentImageBase64.value, plan_id: planStore.currentPlan?.id || null }
    // 构造最近6轮对话上下文
    const history = []
    const ru = userMessages.value.slice(-7, -1)
    const ra = messages.value.filter(m => m.type !== 'intro' && m.type !== 'error').slice(-6)
    for (let i = 0; i < Math.max(ru.length, ra.length); i++) {
      if (ru[i]) history.push({ role: 'user', content: ru[i].text })
      if (ra[i]) history.push({ role: 'assistant', content: ra[i].text || '' })
    }
    const result = await api.aiChat({ ...data, history })
    // 用户中途点了停止 → 丢弃结果
    if (abortFlag.value) return

    const newMsg = {
      text: result.summary,
      type: result.tool,
      content: result.data
    }

    // 如果是 task 意图且有解析出的任务，自动写入数据库
    if (result.tool === 'task' && result.data?.tasks?.length > 0) {
      if (planStore.currentPlan) {
        try {
          const { added, failed } = await confirmTasksSilent(result.data.tasks)
          if (added > 0 && failed === 0) {
            // 全部成功 → 标记为已自动添加
            newMsg._autoAdded = true
          } else if (added > 0) {
            // 部分成功 → 更新 summary 告知用户
            newMsg.text = `${result.summary}（${added}个已添加，${failed}个失败，可点击下方按钮手动添加）`
          }
          // 全部失败时 _autoAdded 为 false → 显示确认按钮让用户手动操作
        } catch (e) { /* 自动写入失败不影响对话展示 */ }
      }
    }

    messages.value.push(newMsg)
    // 每次 AI 回复后自动保存对话历史
    saveCurrentConversation()

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

// 数据清洗：GLM 返回的字段可能不符合后端 Pydantic schema
// duration 可能是浮点数(1.5)、type 可能是中文、repeat_type 可能是 "once"
function sanitizeTask(task) {
  const today = new Date().toISOString().split('T')[0]
  // type 标准化：中文/英文 → new_study / review / mistake
  const typeMap = {
    '新学': 'new_study', 'new_study': 'new_study', '学习': 'new_study', 'study': 'new_study',
    '复习': 'review', 'review': 'review',
    '错题': 'mistake', 'mistake': 'mistake', '做题': 'new_study', '刷题': 'new_study',
    '练习': 'new_study', '背诵': 'new_study', '阅读': 'new_study',
  }
  // repeat_type 标准化
  const repeatMap = { 'none': 'none', '不循环': 'none', 'once': 'none', '一次': 'none', 'daily': 'daily', '每天': 'daily', 'weekday': 'weekday', '工作日': 'weekday' }
  return {
    content: task.content || '学习任务',
    subject: task.subject || '未分类',
    chapter: task.chapter || '',
    duration: Math.round(Number(task.duration)) || 30,  // 浮点→整数，兜底30
    type: typeMap[task.type] || 'new_study',
    date: (task.date && /^\d{4}-\d{2}-\d{2}$/.test(task.date)) ? task.date : today,
    start_hour: Math.round(Number(task.start_hour)) || 9,
    start_minute: Math.round(Number(task.start_minute)) || 0,
    repeat_type: repeatMap[task.repeat_type] || 'none'
  }
}

async function confirmTasks(tasks) {
  if (!tasks || tasks.length === 0) return
  uni.showLoading({ title: '添加任务中...' })
  try {
    for (const task of tasks) {
      if (planStore.currentPlan) {
        const t = sanitizeTask(task)
        await api.createTask({
          plan_id: planStore.currentPlan.id,
          content: t.content,
          subject: t.subject,
          chapter: t.chapter,
          duration: t.duration,
          type: t.type,
          date: t.date,
          start_hour: t.start_hour,
          start_minute: t.start_minute,
          repeat_type: t.repeat_type
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

// 静默写入任务（不显示 toast，用于 AI 自动创建）
// 返回 { added: number, failed: number } 供调用方决定是否显示确认按钮
async function confirmTasksSilent(tasks) {
  if (!tasks || tasks.length === 0 || !planStore.currentPlan) return { added: 0, failed: 0 }
  let added = 0, failed = 0
  for (const task of tasks) {
    try {
      const t = sanitizeTask(task)
      await api.createTask({
        plan_id: planStore.currentPlan.id,
        content: t.content,
        subject: t.subject,
        chapter: t.chapter,
        duration: t.duration,
        type: t.type,
        date: t.date,
        start_hour: t.start_hour,
        start_minute: t.start_minute,
        repeat_type: t.repeat_type
      })
      added++
    } catch (e) {
      console.error('[confirmTasksSilent] 写入失败:', task.content, e)
      failed++
    }
  }
  return { added, failed }
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

      // 同步更新计划中的 subjects 数组，使章节在计划总览中可见
      try {
        const currentSubjects = planStore.currentPlan.subjects || []
        const existingIdx = currentSubjects.findIndex(s => s.name === subject)
        const chapters = data.chapters.map(ch => ({
          name: ch.name,
          duration: ch.daily_duration || 30,
          planned_start: '', planned_end: '', actual_start: '', actual_end: ''
        }))
        if (existingIdx >= 0) {
          // 合并章节（去重）
          const oldChapters = currentSubjects[existingIdx].chapters || []
          const merged = [...oldChapters]
          chapters.forEach(ch => {
            if (!merged.some(m => m.name === ch.name)) merged.push(ch)
          })
          currentSubjects[existingIdx] = { ...currentSubjects[existingIdx], chapters: merged }
        } else {
          currentSubjects.push({ name: subject, target_score: '', chapters })
        }
        await planStore.updatePlan(planStore.currentPlan.id, { subjects: currentSubjects })
      } catch (e) { /* 计划更新失败不影响任务写入 */ }
    }
    uni.showToast({ title: `已写入 ${data.total_days} 天任务，章节已同步到计划`, icon: 'success' })
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
  scrollToMsg.value = 'msg-' + (displayMessages.value.length - 1)
}

onMounted(async () => {
  loadConversationList()
  // 自动恢复上次未结束的会话（切换页面回来后不丢失对话）
  if (!restoreLastConversation()) {
    // 没有历史会话时，尝试从对话列表中恢复最近一条
    if (conversationList.value.length > 0) {
      const c = conversationList.value[0]
      messages.value = c.messages
      userMessages.value = c.userMessages || []
    }
  }
  await subjectsStore.load()
})

// 离开页面时自动保存当前对话
onUnmounted(() => {
  saveCurrentConversation()
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 20px 20px;
  background: $bg2;
  border-bottom: 1px solid $rule;
  .back-btn {
    width: 40px;
    height: 40px;
    background: $soft;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    &:active { opacity: 0.7; }
  }
  .back-icon { font-size: 20px; color: $ink; }
  .page-title { font-size: 20px; font-weight: 600; color: $ink; }
  .header-placeholder { width: 40px; }
}

/* 引导式规划进度条 */
.plan-progress {
  display: flex; justify-content: center; gap: 0;
  padding: 10px 16px; background: #fff;
  border-bottom: 1px solid #f0f0f0;
}
.step-item {
  display: flex; flex-direction: column; align-items: center; flex: 1; max-width: 90px;
  position: relative;
  &:not(:last-child)::after {
    content: ''; position: absolute; top: 14px; left: 55%; width: 100%; height: 2px;
    background: #e0e0e0; z-index: 0;
  }
  &.done::after { background: #2f7d4f; }
  &.done .step-dot { background: #2f7d4f; border-color: #2f7d4f; color: #fff; }
  &.active .step-dot { background: #fff; border-color: #2f7d4f; color: #2f7d4f; font-weight: 700; }
  &.active .step-label { color: #2f7d4f; font-weight: 600; }
}
.step-dot {
  width: 28px; height: 28px; border-radius: 50%; border: 2px solid #e0e0e0;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: #bbb; background: #fff; z-index: 1;
  transition: all 0.2s;
}
.step-label { font-size: 11px; color: #bbb; margin-top: 4px; transition: all 0.2s; }
.step-sub { font-size: 10px; color: #2f7d4f; margin-top: 1px; max-width: 80px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.msg-item {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}

.msg-item.ai { flex-direction: row; }
.msg-item.user { flex-direction: row-reverse; }

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

.msg-avatar.ai { background: $accent; color: #fff; }
.msg-avatar.user { background: $soft; color: $muted; }

.msg-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
}

.msg-bubble.ai {
  background: $bg2;
  margin-left: 10px;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.msg-bubble.user {
  background: $accent;
  margin-right: 10px;
  border-bottom-right-radius: 4px;
}

.msg-bubble.loading { opacity: 0.6; }

.msg-text {
  font-size: 14px;
  line-height: 1.6;
  color: $ink;
}

.msg-bubble.user .msg-text { color: #fff; }

.msg-image {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 8px;
}

.msg-content { margin-top: 12px; }

.content-section {
  background: $soft;
  border-radius: 12px;
  padding: 14px;
  margin-top: 10px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: $accent;
  margin-bottom: 10px;
  display: block;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  background: $bg2;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid $rule;
}

.task-content {
  font-size: 13px;
  font-weight: 500;
  color: $ink;
  display: block;
}

.task-meta {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.task-subject, .task-duration, .task-date {
  font-size: 11px;
  color: $muted;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-item {
  background: $bg2;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid $rule;
}

.chapter-name {
  font-size: 13px;
  font-weight: 500;
  color: $ink;
  display: block;
}

.chapter-meta {
  display: flex;
  gap: 14px;
  margin-top: 6px;
  font-size: 11px;
  color: $muted;
}

.section-total {
  font-size: 12px;
  color: $accent;
  margin-top: 8px;
  display: block;
  font-weight: 500;
}

.plan-summary {
  background: $bg2;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid $rule;
}

.plan-overview {
  font-size: 13px;
  color: $ink;
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
  padding: 10px;
  background: $soft;
  border-radius: 8px;
}

.phase-name {
  font-size: 13px;
  font-weight: 600;
  color: $accent;
  display: block;
}

.phase-desc {
  font-size: 12px;
  color: $muted;
  margin-top: 4px;
  display: block;
  line-height: 1.5;
}

.review-summary {
  font-size: 13px;
  color: $ink;
  line-height: 1.6;
  display: block;
  margin-bottom: 10px;
}

.review-items { margin-bottom: 10px; }

.review-label {
  font-size: 12px;
  font-weight: 600;
  color: $accent;
  display: block;
  margin-bottom: 6px;
}

.review-item {
  font-size: 12px;
  color: $muted;
  display: block;
  margin-bottom: 4px;
  line-height: 1.5;
}

.review-encourage {
  font-size: 13px;
  color: $accent;
  font-weight: 500;
  margin-top: 12px;
  display: block;
}

.msg-btn {
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  margin-top: 14px;
  text-align: center;
  &:active { opacity: 0.9; }
}

.msg-btn.primary {
  background: $accent;
  color: #fff;
}

.chat-input-area {
  padding: 16px;
  background: $bg2;
  border-top: 1px solid $rule;
}

.quick-actions {
  margin-bottom: 16px;
}

.quick-title {
  font-size: 13px;
  color: $muted;
  font-weight: 500;
  margin-bottom: 12px;
  display: block;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.quick-card {
  background: $soft;
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  &:active {
    opacity: 0.8;
    transform: scale(0.98);
  }
}

.quick-icon { font-size: 20px; }

.quick-label {
  font-size: 14px;
  font-weight: 600;
  color: $ink;
}

.quick-example {
  font-size: 11px;
  color: $muted;
  line-height: 1.4;
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
  background: $soft;
  border-radius: 12px;
  &:active { opacity: 0.7; }
}

.upload-icon { font-size: 20px; }

.chat-input {
  flex: 1;
  height: 44px;
  padding: 0 16px;
  background: $soft;
  border-radius: 22px;
  font-size: 14px;
  color: $ink;
}

.send-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $accent;
  border-radius: 12px;
  &:active { opacity: 0.9; }
  &.disabled { opacity: 0.5; }
}

.send-icon { font-size: 18px; color: #fff; }

.stop-btn {
  background: #ef5350;
  animation: pulse-stop 1.5s ease infinite;
}
.stop-icon { font-size: 14px; color: #fff; }

@keyframes pulse-stop {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239,83,80,0.5); }
  50% { box-shadow: 0 0 0 8px rgba(239,83,80,0); }
}

.preview-image-small {
  max-width: 200px;
  border-radius: 8px;
  margin-top: 12px;
}

.bottom-space { height: 20px; }
/* Sidebar */
.sidebar-toggle { width: 40px; height: 40px; background: $bg2; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.sidebar-icon { font-size: 18px; color: $ink; }
.sidebar-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 200; display: flex; justify-content: flex-end; }
.sidebar-panel { background: #fff; width: 280px; max-width: 80vw; height: 100%; display: flex; flex-direction: column; }
.sidebar-title { font-size: 17px; font-weight: 700; color: $ink; padding: 20px 16px 12px; border-bottom: 1px solid #f0f0f0; }
.sidebar-list { flex: 1; padding: 8px; }
.sidebar-item { padding: 12px; border-radius: 10px; margin-bottom: 4px; &:active { background: #f5f7f5; } }
.sidebar-item-title { display: block; font-size: 14px; color: $ink; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sidebar-item-date { font-size: 11px; color: $muted; }
.sidebar-empty { text-align: center; font-size: 14px; color: $muted; padding: 40px 0; display: block; }
.sidebar-new-btn { margin: 12px; padding: 14px; text-align: center; background: $accent; color: #fff; border-radius: 12px; font-size: 15px; font-weight: 600; }

</style>