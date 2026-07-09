<template>
  <view class="page" @click="closeCalMenu">
    <view class="header">
      <view class="header-top">
        <view class="header-row">
          <view class="view-toggle">
            <view class="toggle-btn" :class="{ active: viewMode === 'today' }" @click="switchView('today')">今日</view>
            <view class="toggle-btn" :class="{ active: viewMode === 'week' }" @click="switchView('week')">周视图</view>
            <view class="toggle-btn" :class="{ active: viewMode === 'month' }" @click="switchView('month')">月视图</view>
          </view>
          <view class="quadrant-group">
            <view class="quadrant-switch" @click="toggleQuadrant">
              <view class="switch-track" :class="{ active: enableQuadrant }">
                <view class="switch-thumb"></view>
              </view>
              <text class="switch-label">四象限</text>
            </view>
            <view class="quadrant-entry-btn" v-if="enableQuadrant" @click="goToQuadrant">
              <view class="quadrant-grid-icon">
                <view class="qg-cell"></view><view class="qg-cell"></view>
                <view class="qg-cell"></view><view class="qg-cell"></view>
              </view>
            </view>
          </view>
        </view>
        <view class="title-row">
          <text class="title">{{ headerTitle }}</text>
          <text class="date">{{ currentDate }}</text>
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

    <view class="calendar" v-if="viewMode === 'month'">
      <view class="cal-header">
        <view class="cal-arrow" @click="switchMonth(-1)">‹</view>
        <text class="cal-title">{{ calTitle }}</text>
        <view class="cal-arrow" @click="switchMonth(1)">›</view>
      </view>
      <view class="cal-weekdays">
        <text class="cal-weekday" v-for="w in ['日','一','二','三','四','五','六']" :key="w">{{w}}</text>
      </view>
      <view class="cal-days">
        <view class="cal-day"
          v-for="(day, idx) in calendarDays"
          :key="idx"
          :class="{
            other: !day.currentMonth,
            today: day.isToday,
            selected: day.dateStr === selectedDate,
            'has-task': allVisibleTaskDates.has(day.dateStr)
          }"
          @click="selectDate(day.dateStr)"
          @contextmenu.prevent="handleCalRightClick(day.dateStr, $event)"
          @touchstart="onCalTouchStart(day.dateStr)"
          @touchend="onCalTouchEnd"
          @mousedown="onCalMouseDown(day.dateStr, $event)"
          @mouseup="onCalMouseUp"
          @mouseleave="onCalMouseUp">
          <text class="day-num">{{ day.day }}</text>
          <view class="day-dot" v-if="allVisibleTaskDates.has(day.dateStr)"></view>
        </view>
      </view>
    </view>

    <view class="cal-menu" v-if="showCalMenu" :style="{ left: calMenuX + 'px', top: calMenuY + 'px' }" @click.stop>
      <view class="cal-menu-item" @click="addTaskFromCal">
        <text class="cal-menu-icon">+</text>
        <text class="cal-menu-text">添加任务</text>
      </view>
    </view>

    <view class="week-view" v-if="viewMode === 'week'" id="weekViewContainer">
      <!-- 周视图操作提示 -->
      <view class="week-tip-bar">
        <text class="week-tip-text">💡 点击格子展开 · 长按编辑或添加 · 请在电脑端下载完整周计划</text>
      </view>
      <view class="week-header">
        <view class="week-arrow" @click="switchWeek(-1)">‹</view>
        <text class="week-title">{{ weekTitle }}</text>
        <view class="week-arrow" @click="switchWeek(1)">›</view>
        <view class="week-download-btn" @click="downloadWeekView">
          <text class="download-icon">📥</text>
          <text class="download-text">下载周计划</text>
        </view>
      </view>
      <!-- 周视图主体容器 -->
      <view class="week-container">
        <!-- 左侧固定时间轴 -->
        <view class="week-timeline-container">
          <view class="week-timeline-header">时间</view>
          <scroll-view scroll-y class="week-timeline-scroll" :scroll-top="weekScrollTop" scroll-with-animation>
            <view class="week-timeline">
              <view class="time-label" v-for="hour in timelineHours" :key="hour">
                <text>{{ formatTimelineHour(hour) }}</text>
              </view>
            </view>
          </scroll-view>
        </view>
        <!-- 右侧日期区域（横向滚动） -->
        <view class="week-dates-container">
          <scroll-view scroll-x class="week-dates-hscroll" @touchstart="onWeekHScrollTouchStart" @touchmove="onWeekHScrollTouchMove" @touchend="onWeekHScrollTouchEnd">
            <view class="week-dates-table" :style="{ minWidth: 7 * colWidth + 'px' }">
              <!-- 日期头行 -->
              <view class="week-days-header">
                <view class="week-day-header" v-for="(day, idx) in weekDays" :key="idx" :class="{ today: day.isToday, weekend: day.isWeekend }" :style="{ width: colWidth + 'px' }">
                  <text class="week-day-name">{{ day.dayName }}</text>
                  <text class="week-day-num">{{ day.day }}</text>
                  <view class="week-day-dot" v-if="allVisibleTaskDates.has(day.dateStr)"></view>
                </view>
              </view>
              <!-- 格子体（纵向滚动） -->
              <scroll-view scroll-y class="week-dates-scroll" :scroll-top="weekScrollTop" scroll-with-animation @scroll="onWeekScroll">
                <view class="week-grid">
                  <view class="week-column" v-for="(day, colIdx) in weekDays" :key="colIdx" :data-col="colIdx" :class="{ weekend: day.isWeekend }" :style="{ width: colWidth + 'px' }">
                    <view class="week-cell" v-for="(hour, hourIdx) in timelineHours" :key="hourIdx" :data-hour="hour" :data-date="day.dateStr"
                      @click.stop="onWeekCellClick(day.dateStr, hour)"
                      @contextmenu.prevent="handleWeekCellRightClick(day.dateStr, hour, $event)"
                      @touchstart="onWeekCellTouchStart(day.dateStr, hour, $event)"
                      @touchmove="onWeekCellTouchCancel"
                      @touchend.prevent="onWeekCellTouchEnd"
                      @mousedown="onWeekCellMouseDown(day.dateStr, hour, $event)"
                      @mouseup="onWeekCellMouseUp" />
                    <view class="week-task" v-for="task in getDayTasks(day.dateStr)" :key="task.id" :class="{ completed: task.status === 'completed', scrolled: scrollTaskId === task.id, [getSubjectClass(task.subject)]: true }"
                      :style="getTaskStyle(task)"
                      @click.stop="scrollTaskId = scrollTaskId === task.id ? '' : task.id"
                      @contextmenu.prevent.stop="editTask(task)"
                      @touchstart.stop="onTaskCardTouchStart(task)"
                      @touchend="onTaskCardTouchEnd"
                      @touchmove="onTaskCardTouchEnd">
                      <view class="task-importance-dot" :class="getImportanceClass(task.importance)" v-if="task.importance && enableQuadrant"></view>
                      <text class="week-task-content">{{ task.content }}</text>
                      <text class="week-task-time">{{ formatTaskTime(task) }}</text>
                      <text class="week-task-duration">{{ task.duration }}min</text>
                    </view>
                  </view>
                </view>
              </scroll-view>
            </view>
          </scroll-view>
        </view>
      </view>
    </view>


    <!-- 周视图右键菜单 -->
    <view class="cal-menu" v-if="showWeekMenu" :style="{ left: weekMenuX + 'px', top: weekMenuY + 'px' }" @click.stop>
      <view class="cal-menu-item" @click="addTaskFromWeekCell(weekCellDate, weekCellHour)">
        <text class="cal-menu-icon">+</text>
        <text class="cal-menu-text">新建任务</text>
      </view>
      <view class="cal-menu-item" @click="copyFromWeekCell(weekCellDate, weekCellHour)">
        <text class="cal-menu-icon">📋</text>
        <text class="cal-menu-text">从已有任务复制</text>
      </view>
    </view>

    <view class="tabs" v-if="viewMode !== 'week'">
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

    <view class="filter-section" v-if="viewMode !== 'week'">
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

    <view class="task-list" v-if="viewMode !== 'week'">
      <view class="task-item" v-for="task in filteredTasks" :key="task.id" :class="{ completed: task.status === 'completed' }" @click="onTaskCardClick(task)" @contextmenu.prevent="editTask(task)" @touchstart="onTaskTouchStart(task)" @touchend="onTaskTouchEnd" @touchmove="onTaskTouchEnd">
        <view class="task-check" @click.stop="toggleTask(task)">
          <view class="check-circle" :class="{ checked: task.status === 'completed' }">
            <text v-if="task.status === 'completed'" class="check-icon">✓</text>
          </view>
        </view>
        <view class="task-body">
          <view class="task-top">
            <text class="task-content">{{ task.content }}</text>
            <view class="task-type-tag" :class="getTypeClass(task.type)">
              {{ getTypeLabel(task.type) }}
            </view>
          </view>
          <view class="task-meta">
            <text class="task-subject">{{ task.subject }}</text>
            <text class="task-chapter" v-if="task.chapter">{{ task.chapter }}</text>
            <view class="task-importance-tag" :class="getImportanceClass(task.importance)" v-if="task.importance && enableQuadrant">{{ getImportanceLabel(task.importance) }}</view>
            <text class="task-repeat-tag" v-if="task.repeat_type && task.repeat_type !== 'none'">{{ getRepeatLabel(task.repeat_type) }}</text>
            <text class="task-time">{{ formatTaskTime(task) }}</text>
            <text class="task-duration">预计: {{ task.duration }}分钟</text>
            <text class="task-actual" v-if="task.actual_duration > 0">实际: {{ task.actual_duration }}分钟</text>
          </view>
        </view>
        <view class="task-pomodoro" @click.stop="startPomodoro(task)">
          <text class="pomodoro-icon">🍅</text>
        </view>
        <view class="task-reflection" @click.stop="showTaskReflection(task, selectedDate, task.status === 'completed')">
          <text class="reflection-icon">✎</text>
        </view>
      </view>
    </view>

    <view class="empty" v-if="viewMode !== 'week' && filteredTasks.length === 0">
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无任务</text>
      <text class="empty-hint">点击右下角 + 按钮手动创建任务</text>
    </view>

    <view class="focus-records-section" v-if="viewMode !== 'week' && dateFocusRecords.length > 0">
      <view class="focus-records-header">
        <text class="focus-records-title">🍅 番茄钟专注记录</text>
        <text class="focus-records-count">共 {{ dateFocusRecords.length }} 条 · {{ totalFocusMinutes }}分钟</text>
      </view>
      <view class="focus-record-item" v-for="(r, idx) in dateFocusRecords" :key="idx">
        <view class="focus-record-icon">
          <text class="focus-record-emoji">{{ r.type === 'manual' ? '📝' : '🍅' }}</text>
        </view>
        <view class="focus-record-body">
          <text class="focus-record-task">{{ r.task_name || '专注学习' }}</text>
          <text class="focus-record-meta">
            {{ r.subject || '未分类' }} · {{ r.duration }}分钟
            <text v-if="r.start_time"> · {{ formatTime(r.start_time) }}</text>
          </text>
        </view>
        <text class="focus-record-duration">{{ r.duration }}m</text>
      </view>
    </view>

    <TaskFormModal
      v-model:visible="showAddForm"
      :task="editingTask"
      :copy-source="copySourceTask"
      :date="selectedDate"
      :enable-quadrant="enableQuadrant"
      :show-a-i-mode="true"
      :default-hour="weekDefaultHour"
      :default-minute="weekDefaultMinute"
      @saved="onTaskSaved"
      @deleted="onTaskDeleted"
    />

    <!-- 复制任务选择弹窗 -->
    <view class="modal-mask" v-if="showCopyPicker" @click="showCopyPicker = false">
      <view class="modal-sheet" @click.stop>
        <view class="modal-top">
          <text class="modal-title">从已有任务复制</text>
          <view class="modal-x" @click="showCopyPicker = false">✕</view>
        </view>
        <view class="modal-body">
          <view class="copy-search-wrap">
            <input class="copy-search-input" v-model="copyKeyword" placeholder="输入关键字搜索（科目/章节/内容）" />
          </view>
          <view class="copy-target-hint">
            将复制到：<text class="copy-target-date">{{ copyContextDate || selectedDate }}</text>
            <text class="copy-target-time"> {{ (copyContextHour || 9) }}:{{ String(copyContextMinute || 0).padStart(2,'0') }}</text>
          </view>
          <view class="copy-list">
            <view class="copy-item" v-for="t in copyCandidates" :key="t.id" @click="confirmCopyFromTask(t)">
              <view class="copy-item-body">
                <text class="copy-item-content">{{ t.content }}</text>
                <view class="copy-item-meta">
                  <text class="copy-item-subj">{{ t.subject }}</text>
                  <text class="copy-item-chap" v-if="t.chapter">{{ t.chapter }}</text>
                  <text class="copy-item-dur">{{ t.duration }}分钟</text>
                  <text class="copy-item-date">来源: {{ t.date }}</text>
                </view>
              </view>
              <text class="copy-item-arrow">›</text>
            </view>
            <view class="copy-empty" v-if="copyCandidates.length === 0">
              <text class="copy-empty-text">暂无匹配任务，换个关键字试试</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="fab" @click="openManualAdd"><text class="fab-icon">+</text></view>
    <view class="bottom-space"></view>

    <TaskReflectionModal
      :visible="showReflectionModal"
      :task="reflectionTask"
      :task-date="reflectionDate"
      :is-complete="reflectionIsComplete"
      :existing-reflection="existingReflection"
      :default-duration="reflectionDefaultDuration"
      @close="closeReflectionModal"
      @submitted="onReflectionSubmitted"
    />
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useTaskStore } from '@/stores/task'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import { useFarmStore } from '@/stores/farm'
import { useSubjectsStore } from '@/stores/subjects'
import TaskFormModal from '@/components/TaskFormModal.vue'
import TaskReflectionModal from '@/components/TaskReflectionModal.vue'
import * as api from '@/api/client'

const taskStore = useTaskStore()
const planStore = usePlanStore()
const userStore = useUserStore()
const farmStore = useFarmStore()
const subjectsStore = useSubjectsStore()

const activeTab = ref('all')
const activeFilter = ref('all')
const showAddForm = ref(false)
const editingTask = ref(null)
// 复制来源任务（传入 TaskFormModal 以新建模式预填）
const copySourceTask = ref(null)
// 复制任务选择弹窗
const showCopyPicker = ref(false)
const copyKeyword = ref('')
// 复制时的目标日期/时间上下文（来自周视图格子或今日默认）
const copyContextDate = ref('')
const copyContextHour = ref(9)
const copyContextMinute = ref(0)

// 平台检测：桌面端(无触控)用点击编辑，移动端用长按编辑
const isDesktop = ref(false)
try {
  // #ifdef H5
  isDesktop.value = !('ontouchstart' in window) && (navigator.maxTouchPoints || 0) === 0
  // #endif
} catch (e) { /* non-H5 */ }

const QUADRANT_KEY = 'studymate_quadrant_enabled'
const enableQuadrant = ref(uni.getStorageSync(QUADRANT_KEY) === 'true')

function toggleQuadrant() {
  enableQuadrant.value = !enableQuadrant.value
  uni.setStorageSync(QUADRANT_KEY, enableQuadrant.value ? 'true' : 'false')
}

const viewMode = ref('today')
const selectedDate = ref(formatDate(new Date()))
const calendarMonth = ref(new Date())
const calendarDays = ref([])
const taskDates = ref(new Set())
const dateFocusRecords = ref([])

const timelineHours = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
// 列宽：桌面端(≥768px)均分7列但封顶115px，手机端最小75px可横向滑动
// 页面全局 max-width=1080px，桌面端 windowWidth 可能远超此值
const PAGE_MAX_WIDTH = 1080
const colWidth = computed(() => {
  try {
    const raw = uni.getSystemInfoSync().windowWidth || 375
    const w = Math.min(raw, PAGE_MAX_WIDTH)
    if (w >= 768) {
      // 桌面/平板：7列均匀分布，单列封顶115px避免过宽
      return Math.min(115, Math.floor((w - 100) / 7))
    }
    // 手机端：时间轴36px，最小75px，7列=525px可横向滑动
    return Math.max(75, Math.floor((w - 40) / 7))
  } catch (e) { return 100 }
})
const CELL_H = 72
const weekScrollTop = ref(0)

function onWeekScroll(e) {
  weekScrollTop.value = e.detail.scrollTop
}
const weekStartDate = ref(getWeekStart(new Date()))
const weekDays = ref([])

const showCalMenu = ref(false)
const calMenuX = ref(0)
const calMenuY = ref(0)
const calSelectedDate = ref('')
const calLongPressTimer = ref(null)
let calMouseTimer = null

// 周视图时间格交互
const showWeekMenu = ref(false)
const weekMenuX = ref(0)
const weekMenuY = ref(0)
const weekCellDate = ref('')
const weekCellHour = ref(9)
// 从周视图格子弹窗添加任务时，传递格子的时间
const weekDefaultHour = ref(9)
const weekDefaultMinute = ref(0)
let weekCellTouchTimer = null
// 页面刚切到周视图时禁止长按，防止加载过程中滑动误触

// 任务反思
const showReflectionModal = ref(false)
const reflectionTask = ref(null)
const reflectionIsComplete = ref(false)
const reflectionDate = ref('')
const reflectionDefaultDuration = ref(0)
const existingReflection = ref(null)
const dailyReflections = ref({})

// 23:30 未完成任务提醒
const UNFINISHED_REMIND_KEY = 'studymate_unfinished_remind_date'
const lastRemindDate = ref(uni.getStorageSync(UNFINISHED_REMIND_KEY) || '')
const weekViewReady = ref(false)
let weekViewReadyTimer = null

const subjectOptions = computed(() => subjectsStore.mergedSubjects)

async function loadTaskSubjects() {
  await subjectsStore.load()
}

// Saved/deleted callbacks from the shared TaskFormModal
async function onTaskSaved() {
  if (planStore.currentPlan) {
    await taskStore.getAllTasks(planStore.currentPlan.id)
    if (viewMode.value === 'today') {
      await taskStore.getTasksByDate(planStore.currentPlan.id, selectedDate.value)
    }
  }
  taskDates.value.add(selectedDate.value)
  saveTaskDatesToStorage()
  generateCalendar()
  editingTask.value = null
}

async function onTaskDeleted() {
  if (planStore.currentPlan) {
    await taskStore.getAllTasks(planStore.currentPlan.id)
    if (viewMode.value === 'today') {
      await taskStore.getTasksByDate(planStore.currentPlan.id, selectedDate.value)
    }
  }
  editingTask.value = null
}

function formatDate(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function formatDateLabel(d) {
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 ${['日','一','二','三','四','五','六'][d.getDay()]}`
}

function getWeekStart(d) {
  const date = new Date(d)
  const day = date.getDay()
  const diff = date.getDate() - day + (day === 0 ? -6 : 1)
  return new Date(date.setDate(diff))
}

const currentDate = computed(() => {
  if (viewMode.value === 'today') {
    return formatDateLabel(new Date())
  } else if (viewMode.value === 'week') {
    const end = new Date(weekStartDate.value)
    end.setDate(end.getDate() + 6)
    return `${weekStartDate.value.getMonth() + 1}/${weekStartDate.value.getDate()} - ${end.getMonth() + 1}/${end.getDate()}`
  }
  // 月视图：显示年月
  const y = calendarMonth.value.getFullYear()
  const m = calendarMonth.value.getMonth() + 1
  return `${y}年${m}月`
})

const headerTitle = computed(() => {
  if (viewMode.value === 'today') return '今日任务'
  if (viewMode.value === 'week') return '周视图'
  return '月视图'
})

const calTitle = computed(() => {
  const y = calendarMonth.value.getFullYear()
  const m = calendarMonth.value.getMonth() + 1
  return `${y}年${m}月`
})

const weekTitle = computed(() => {
  const y = weekStartDate.value.getFullYear()
  const m = weekStartDate.value.getMonth() + 1
  const day = weekStartDate.value.getDate()
  // 月内第几周：1-7日=第1周, 8-14日=第2周, ...
  const weekOfMonth = Math.ceil(day / 7)
  return `${y}年${m}月第${weekOfMonth}周`
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

const totalFocusMinutes = computed(() => {
  return dateFocusRecords.value.reduce((s, r) => s + (r.duration || 0), 0)
})

function formatTime(isoStr) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch (e) { return '' }
}

const getTypeLabel = (type) => {
  const map = { new_study: '新学', review: '复习', mistake: '错题' }
  return map[type] || type
}

const getTypeClass = (type) => {
  const map = { new_study: 'tag-green', review: 'tag-orange', mistake: 'tag-red' }
  return map[type] || ''
}

const getRepeatLabel = (type) => {
  const map = { daily: '每天', weekday: '工作日', holiday: '节假日' }
  return map[type] || ''
}

const getImportanceLabel = (type) => {
  const map = { important_urgent: '重要紧急', important_not_urgent: '重要不紧急', urgent_not_important: '紧急不重要', not_important_not_urgent: '不紧急不重要' }
  return map[type] || ''
}

const getImportanceClass = (type) => {
  const map = { important_urgent: 'importance-red', important_not_urgent: 'importance-blue', urgent_not_important: 'importance-orange', not_important_not_urgent: 'importance-gray' }
  return map[type] || ''
}

const getSubjectClass = (subject) => {
  if (!subject) return 'subject-default'
  const map = {
    '数据结构': 'subject-ds',
    '操作系统': 'subject-os',
    '计算机网络': 'subject-cn',
    '计算机组成原理': 'subject-co',
    '英语': 'subject-en',
    '政治': 'subject-pol',
    '数学': 'subject-math',
    '数据库': 'subject-db',
    'UML': 'subject-uml',
    '算法': 'subject-algo',
    'C语言': 'subject-c'
  }
  return map[subject] || 'subject-default'
}

// 当前时间线（周视图中显示红色横线标识当前时间）
const currentTimeLineStyle = computed(() => {
  const now = new Date()
  const hour = now.getHours()
  const minute = now.getMinutes()
  const CELL_H = 72
  if (hour < timelineHours[0] || hour > timelineHours[timelineHours.length - 1]) return { display: 'none' }
  const top = (hour - timelineHours[0]) * CELL_H + (minute / 60) * CELL_H
  return {
    position: 'absolute',
    left: '40px',
    right: '0',
    top: top + 'px',
    height: '2px',
    background: '#ef5350',
    zIndex: 6,
    pointerEvents: 'none'
  }
})

function getDayTasks(dateStr) {
  return taskStore.weekTasks.filter(t => shouldRepeatOnDate(t, dateStr))
}
function getTasksAt(dateStr, hour) {
  return taskStore.weekTasks.filter(t => shouldRepeatOnDate(t, dateStr) && (t.start_hour || 9) === hour)
}

// 循环任务在指定日期是否应出现（与后端 _should_repeat 逻辑一致）
function shouldRepeatOnDate(task, dateStr) {
  if (!task || !task.date) return false
  if (!task.repeat_type || task.repeat_type === 'none') return task.date === dateStr
  if (task.date > dateStr) return false
  if (task.repeat_type === 'daily') return true
  let day
  try { day = new Date(dateStr + 'T00:00:00').getDay() } catch (e) { return false }
  if (task.repeat_type === 'weekday') return day >= 1 && day <= 5
  if (task.repeat_type === 'holiday') return day === 0 || day === 6
  return false
}

// 当前月视图+周视图范围内，所有任务(含循环展开)出现的日期集合
const allVisibleTaskDates = computed(() => {
  const set = new Set()
  const checkDates = new Set()
  calendarDays.value.forEach(d => checkDates.add(d.dateStr))
  weekDays.value.forEach(d => checkDates.add(d.dateStr))
  taskStore.weekTasks.forEach(t => {
    if (t.date) set.add(t.date)
    checkDates.forEach(ds => { if (shouldRepeatOnDate(t, ds)) set.add(ds) })
  })
  return set
})

function formatTimelineHour(hour) {
  return `${hour}:00`
}

function getTaskStyle(task) {
  const h = task.start_hour || 9
  const m = task.start_minute || 0
  const dur = task.duration || 30
  const top = (h - timelineHours[0]) * CELL_H + (m / 60) * CELL_H
  const height = Math.max(36, (dur / 60) * CELL_H)
  return {
    position: 'absolute',
    top: top + 'px',
    height: height + 'px',
    left: '2px',
    right: '2px',
    zIndex: 1
  }
}

function formatTaskTime(task) {
  const h = task.start_hour || 9
  const m = task.start_minute || 0
  return `${h}:${String(m).padStart(2, '0')}`
}

async function toggleTask(task) {
  if (task.status === 'completed') {
    await taskStore.uncompleteTask(task.id, selectedDate.value)
  } else {
    await taskStore.completeTask(task.id, selectedDate.value)
    if (planStore.currentPlan) {
      try {
        const crop = await farmStore.ensureCrop(planStore.currentPlan.id, task.subject)
        if (crop.plant) {
          await farmStore.fertilizePlant(crop.plant.id)
        }
      } catch (e) { /* silent */ }
    }
    // 完成任务时弹出反思弹窗（预填番茄钟累计的实际用时）
    const taskDate = selectedDate.value
    const pomodoroDuration = task.actual_duration || 0
    showTaskReflection(task, taskDate, true, pomodoroDuration)
  }
  if (planStore.currentPlan && viewMode.value === 'week') {
    await taskStore.getAllTasks(planStore.currentPlan.id)
  }
}

function showTaskReflection(task, taskDate, isComplete, defaultDuration = 0) {
  reflectionTask.value = task
  reflectionDate.value = taskDate
  reflectionIsComplete.value = isComplete
  reflectionDefaultDuration.value = defaultDuration
  // 查找是否已有该任务当天的反思记录
  const key = `${task.id}-${taskDate}`
  existingReflection.value = dailyReflections.value[key] || null
  showReflectionModal.value = true
}

function closeReflectionModal() {
  showReflectionModal.value = false
  reflectionTask.value = null
  existingReflection.value = null
}

function onReflectionSubmitted(data) {
  const key = `${data.task_id}-${data.task_date}`
  dailyReflections.value[key] = data
}

async function loadDailyReflections(dateStr) {
  if (!planStore.currentPlan) return
  try {
    const records = await api.getReflections(planStore.currentPlan.id, dateStr)
    records.forEach(r => {
      const key = `${r.task_id}-${r.task_date}`
      dailyReflections.value[key] = r
    })
  } catch (e) { /* ignore */ }
}

function checkUnfinishedReminder() {
  const now = new Date()
  const todayStr = formatDate(now)
  const hour = now.getHours()
  const minute = now.getMinutes()

  // 仅在 23:30-23:59 之间，且今天尚未提醒过
  if (hour === 23 && minute >= 30 && lastRemindDate.value !== todayStr) {
    const pendingTasks = taskStore.todayTasks.filter(t => t.status !== 'completed')
    if (pendingTasks.length > 0) {
      uni.showModal({
        title: '今日未完成任务',
        content: `还有 ${pendingTasks.length} 个任务未完成，是否记录原因？`,
        confirmText: '记录原因',
        cancelText: '明天再说',
        success: (res) => {
          if (res.confirm) {
            // 逐个打开未完成原因弹窗
            let idx = 0
            const showNext = () => {
              if (idx < pendingTasks.length) {
                showTaskReflection(pendingTasks[idx], todayStr, false)
                idx++
              }
            }
            showNext()
          }
        }
      })
      lastRemindDate.value = todayStr
      uni.setStorageSync(UNFINISHED_REMIND_KEY, todayStr)
    }
  }
}

// 定时检查 23:30 提醒
let unfinishedReminderTimer = null
function startUnfinishedReminder() {
  if (unfinishedReminderTimer) clearInterval(unfinishedReminderTimer)
  unfinishedReminderTimer = setInterval(() => {
    checkUnfinishedReminder()
  }, 60000)
}

function startPomodoro(task) {
  taskStore.currentTask = task
  const taskContent = `${task.subject}${task.chapter ? ' - ' + task.chapter : ''}: ${task.content}`
  uni.navigateTo({ url: `/pages/daily/pomodoro?taskContent=${encodeURIComponent(taskContent)}&taskId=${task.id}` })
}

function editTask(task) {
  editingTask.value = task
  copySourceTask.value = null
  showAddForm.value = true
}

function openManualAdd() {
  // 今日任务版块：点击加号弹出"新建 / 从已有任务复制"两种选择
  uni.showActionSheet({
    itemList: ['✚ 新建任务', '📋 从已有任务复制'],
    success: (res) => {
      if (res.tapIndex === 0) startNewTask()
      else if (res.tapIndex === 1) startCopyPicker()
    }
  })
}

function startNewTask() {
  editingTask.value = null
  copySourceTask.value = null
  weekDefaultHour.value = 9
  weekDefaultMinute.value = 0
  showAddForm.value = true
}

function startCopyPicker() {
  copyKeyword.value = ''
  // 复制目标默认为当前选中日期
  copyContextDate.value = selectedDate.value
  copyContextHour.value = 9
  copyContextMinute.value = 0
  showCopyPicker.value = true
}

// 复制候选任务列表（按关键字搜索匹配 科目/章节/内容）
const copyCandidates = computed(() => {
  const kw = copyKeyword.value.trim().toLowerCase()
  let list = taskStore.weekTasks || []
  if (kw) {
    list = list.filter(t =>
      (t.subject || '').toLowerCase().includes(kw) ||
      (t.chapter || '').toLowerCase().includes(kw) ||
      (t.content || '').toLowerCase().includes(kw)
    )
  }
  // 去重：相同 subject+content 只保留一条最新
  const seen = new Set()
  const result = []
  for (const t of list) {
    const key = (t.subject || '') + '|' + (t.content || '')
    if (seen.has(key)) continue
    seen.add(key)
    result.push(t)
  }
  return result.slice(0, 50)
})

function confirmCopyFromTask(task) {
  showCopyPicker.value = false
  editingTask.value = null
  copySourceTask.value = task
  // 复制时使用复制上下文的日期与时间
  selectedDate.value = copyContextDate.value || selectedDate.value
  weekDefaultHour.value = copyContextHour.value || 9
  weekDefaultMinute.value = copyContextMinute.value || 0
  showAddForm.value = true
}

function goToQuadrant() {
  uni.navigateTo({ url: '/pages/daily/quadrant' })
}

function generateCalendar() {
  const year = calendarMonth.value.getFullYear()
  const month = calendarMonth.value.getMonth()
  const firstWeekday = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const today = formatDate(new Date())

  const days = []
  for (let i = firstWeekday - 1; i >= 0; i--) {
    const d = new Date(year, month, -i)
    days.push({ day: d.getDate(), dateStr: formatDate(d), currentMonth: false, isToday: formatDate(d) === today })
  }
  for (let i = 1; i <= daysInMonth; i++) {
    const d = new Date(year, month, i)
    days.push({ day: i, dateStr: formatDate(d), currentMonth: true, isToday: formatDate(d) === today })
  }
  const trailingNeeded = (7 - (days.length % 7)) % 7
  for (let i = 1; i <= trailingNeeded; i++) {
    const d = new Date(year, month + 1, i)
    days.push({ day: d.getDate(), dateStr: formatDate(d), currentMonth: false, isToday: formatDate(d) === today })
  }
  calendarDays.value = days
}

function generateWeekDays() {
  const days = []
  const dayNames = ['一', '二', '三', '四', '五', '六', '日']
  const todayStr = formatDate(new Date())
  
  for (let i = 0; i < 7; i++) {
    const d = new Date(weekStartDate.value)
    d.setDate(d.getDate() + i)
    days.push({
      day: d.getDate(),
      dayName: dayNames[i],
      dateStr: formatDate(d),
      isToday: formatDate(d) === todayStr,
      isWeekend: i === 5 || i === 6
    })
  }
  weekDays.value = days
}

function switchMonth(delta) {
  const d = new Date(calendarMonth.value)
  d.setMonth(d.getMonth() + delta)
  calendarMonth.value = d
  generateCalendar()
  loadTaskDates()
}

function switchWeek(delta) {
  const d = new Date(weekStartDate.value)
  d.setDate(d.getDate() + delta * 7)
  weekStartDate.value = d
  generateWeekDays()
  selectedDate.value = formatDate(d)
  loadTasks()
}

async function downloadWeekView() {
  // #ifdef H5
  uni.showLoading({ title: '正在生成图片...' })
  try {
    const container = document.getElementById('weekViewContainer')
    if (!container) { uni.hideLoading(); return }

    // 保存原始样式
    const origStyles = new Map()
    const saveStyle = (el, prop) => {
      if (!el) return
      origStyles.set(`${prop}-${el.className || el.id}`, { el, prop, val: el.style[prop] })
    }

    // 需要临时展开的元素
    const weekView = container
    const datesScroll = container.querySelector('.week-dates-scroll')
    const datesHScroll = container.querySelector('.week-dates-hscroll')
    const weekContainer = container.querySelector('.week-container')
    const timelineScroll = container.querySelector('.week-timeline-scroll')
    const grid = container.querySelector('.week-grid')

    // 展开所有内容：移除滚动限制
    const elementsToExpand = [weekView, datesScroll, datesHScroll, weekContainer, timelineScroll, grid]
    elementsToExpand.forEach(el => {
      if (!el) return
      saveStyle(el, 'overflow')
      saveStyle(el, 'overflowX')
      saveStyle(el, 'overflowY')
      saveStyle(el, 'maxHeight')
      saveStyle(el, 'height')
      saveStyle(el, 'width')
      el.style.overflow = 'visible'
      el.style.overflowX = 'visible'
      el.style.overflowY = 'visible'
      el.style.maxHeight = 'none'
      el.style.height = 'auto'
    })

    // 扩展格子区高度显示全部时间轴
    if (datesScroll) {
      datesScroll.style.height = 'auto'
      datesScroll.style.maxHeight = 'none'
    }

    // 确保横向7列完整显示
    if (datesHScroll) {
      datesHScroll.style.width = 'auto'
      datesHScroll.style.overflowX = 'visible'
    }

    // 容器宽度确保完整
    if (weekContainer) {
      weekContainer.style.width = 'auto'
      weekContainer.style.minWidth = 'auto'
    }

    // 强制 reflow
    container.offsetHeight

    // 用 html2canvas 截取
    const canvas = await window.html2canvas(container, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      logging: false,
      windowWidth: container.scrollWidth + 100,
      windowHeight: container.scrollHeight + 100
    })

    // 恢复原始样式
    origStyles.forEach(({ el, prop, val }) => {
      el.style[prop] = val
    })

    // 下载图片
    const link = document.createElement('a')
    link.download = `周计划_${weekTitle.value.replace(/[/:]/g, '_')}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()

    uni.hideLoading()
    uni.showToast({ title: '周计划图片已生成', icon: 'success' })
  } catch (e) {
    uni.hideLoading()
    console.error('下载周视图失败:', e)
    uni.showToast({ title: '生成失败，请重试', icon: 'none' })
  }
  // #endif
  // #ifndef H5
  uni.showToast({ title: '请在电脑端使用此功能', icon: 'none' })
  // #endif
}

function handleCalRightClick(date, event) {
  showCalMenu.value = false
  calSelectedDate.value = date
  // UniApp H5 下事件可能被包装，从原生事件或 detail 中取坐标
  const nativeEvent = event.detail || event
  calMenuX.value = nativeEvent.clientX || event.x || 0
  calMenuY.value = nativeEvent.clientY || event.y || 0
  showCalMenu.value = true
}

function onCalTouchStart(date) {
  calSelectedDate.value = date
  calLongPressTimer.value = setTimeout(() => {
    addTaskFromCal()
  }, 500)
}

function onCalTouchEnd() {
  if (calLongPressTimer.value) {
    clearTimeout(calLongPressTimer.value)
    calLongPressTimer.value = null
  }
}

function onCalMouseDown(date, e) {
  calSelectedDate.value = date
  clearTimeout(calMouseTimer)
  // 右键点击（button === 2）直接弹出菜单
  const nativeEvent = (e && e.detail) || e || window.event
  if (nativeEvent && nativeEvent.button === 2) {
    handleCalRightClick(date, nativeEvent)
    return
  }
  // 左键长按 500ms 弹出菜单
  calMouseTimer = setTimeout(() => {
    addTaskFromCal()
  }, 500)
}

function onCalMouseUp() {
  clearTimeout(calMouseTimer)
}

function addTaskFromCal() {
  showCalMenu.value = false
  selectedDate.value = calSelectedDate.value
  editingTask.value = null
  showAddForm.value = true
}

function selectCalDate() {
  showCalMenu.value = false
  selectedDate.value = calSelectedDate.value
  loadTasks()
}

function closeCalMenu() {
  showCalMenu.value = false
}

function selectDate(date) {
  selectedDate.value = date
  loadTasks()
}

function getTaskDatesStorageKey() {
  const planId = planStore.currentPlan?.id
  return planId ? `studymate_task_dates_${planId}` : null
}

function saveTaskDatesToStorage() {
  const key = getTaskDatesStorageKey()
  if (!key) return
  uni.setStorageSync(key, JSON.stringify([...taskDates.value]))
}

function loadTaskDates() {
  const key = getTaskDatesStorageKey()
  if (!key) return
  try {
    const arr = JSON.parse(uni.getStorageSync(key) || '[]')
    taskDates.value = new Set(arr)
  } catch (e) {
    taskDates.value = new Set()
  }
}

// ==================== 周视图时间格交互 ====================

// 展开格子的 key: "日期-小时"
const expandedCell = ref('')
const scrollTaskId = ref('')

function onWeekCellClick(dateStr, hour) {
  if (weekCellDidLong) return
  const key = dateStr + '-' + hour
  // 点击展开/收起
  if (expandedCell.value === key) {
    expandedCell.value = ''
  } else {
    expandedCell.value = key
  }
}

// 右键菜单
function handleWeekCellRightClick(dateStr, hour, event) {
  showWeekMenu.value = false
  weekCellDate.value = dateStr
  weekCellHour.value = hour
  const nativeEvent = event.detail || event
  weekMenuX.value = nativeEvent.clientX || event.x || 0
  weekMenuY.value = nativeEvent.clientY || event.y || 0
  showWeekMenu.value = true
}

// 右键菜单选择添加
function addTaskFromWeekCell(dateStr, hour) {
  showWeekMenu.value = false
  selectedDate.value = dateStr
  editingTask.value = null
  copySourceTask.value = null
  weekDefaultHour.value = hour || 9
  weekDefaultMinute.value = 0
  showAddForm.value = true
}

// 周视图：从已有任务复制，自动使用当前格子的日期与开始时间
function copyFromWeekCell(dateStr, hour) {
  showWeekMenu.value = false
  copyContextDate.value = dateStr
  copyContextHour.value = hour || 9
  copyContextMinute.value = 0
  copyKeyword.value = ''
  showCopyPicker.value = true
}

// === 单元格交互：点击展开任务详情，长按编辑/添加 ===
let weekCellDownTime = 0
let weekCellDidLong = false
let weekCellDownDate = ''
let weekCellDownHour = 0
let weekCellMouseTimer = null

let weekCellDownX = 0
let weekCellDownY = 0

function onWeekCellTouchStart(dateStr, hour, event) {
  // 页面加载中禁止长按，防止滑动误触
  if (!weekViewReady.value) return

  weekCellDidLong = false
  weekCellDownDate = dateStr
  weekCellDownHour = hour
  weekCellDownTime = Date.now()
  const touch = event.touches && event.touches[0]
  if (touch) {
    weekCellDownX = touch.clientX
    weekCellDownY = touch.clientY
  }
  clearTimeout(weekCellTouchTimer)
  weekCellTouchTimer = setTimeout(() => {
    weekCellDidLong = true
    const tasksAtCell = getTasksAt(dateStr, hour)
    if (tasksAtCell.length > 0) {
      editTask(tasksAtCell[0])
    } else {
      weekCellDate.value = dateStr
      weekCellHour.value = hour
      showWeekMenu.value = true
      weekMenuX.value = weekCellDownX
      weekMenuY.value = weekCellDownY
    }
  }, 600)
}

function onWeekCellTouchCancel() {
  // 滑动时取消长按，防止误触
  clearTimeout(weekCellTouchTimer)
  weekCellDidLong = false
}

function onWeekCellTouchEnd() {
  clearTimeout(weekCellTouchTimer)
  setTimeout(() => { weekCellDidLong = false }, 50)
}

// 任务卡片触摸——点击展开，长按编辑
let taskCardTimer = null
function onTaskCardTouchStart(task) {
  clearTimeout(taskCardTimer)
  taskCardTimer = setTimeout(() => {
    editTask(task)
  }, 600)
}
function onTaskCardTouchEnd() {
  clearTimeout(taskCardTimer)
}

function onWeekCellMouseDown(dateStr, hour, event) {
  if (!weekViewReady.value) return
  weekCellDidLong = false
  weekCellDownDate = dateStr
  weekCellDownHour = hour
  weekCellDownTime = Date.now()
  const nativeEvent = event && event.detail ? event.detail : event
  if (nativeEvent && nativeEvent.button === 2) {
    handleWeekCellRightClick(dateStr, hour, nativeEvent)
    return
  }
  if (nativeEvent && typeof nativeEvent.clientX === 'number') {
    weekCellDownX = nativeEvent.clientX
    weekCellDownY = nativeEvent.clientY
  }
  clearTimeout(weekCellMouseTimer)
  weekCellMouseTimer = setTimeout(() => {
    weekCellDidLong = true
    const tasksAtCell = getTasksAt(dateStr, hour)
    if (tasksAtCell.length > 0) {
      editTask(tasksAtCell[0])
    } else {
      weekCellDate.value = dateStr
      weekCellHour.value = hour
      showWeekMenu.value = true
      weekMenuX.value = weekCellDownX
      weekMenuY.value = weekCellDownY
    }
  }, 600)
}

function onWeekCellMouseUp() {
  clearTimeout(weekCellMouseTimer)
}

// === 横向滚动区域触摸处理：区分横向滚动和长按 ===
let weekHScrollStartX = 0
let weekHScrollStartY = 0
let weekHScrollIsScrolling = false

function onWeekHScrollTouchStart(event) {
  const touch = event.touches && event.touches[0]
  if (touch) {
    weekHScrollStartX = touch.clientX
    weekHScrollStartY = touch.clientY
  }
  weekHScrollIsScrolling = false
}

function onWeekHScrollTouchMove(event) {
  const touch = event.touches && event.touches[0]
  if (!touch) return
  const dx = Math.abs(touch.clientX - weekHScrollStartX)
  const dy = Math.abs(touch.clientY - weekHScrollStartY)
  if (dx > 10 && dx > dy) {
    weekHScrollIsScrolling = true
    clearTimeout(weekCellTouchTimer)
    weekCellDidLong = false
  }
}

function onWeekHScrollTouchEnd() {
  weekHScrollIsScrolling = false
}

function closeWeekMenu() {
  showWeekMenu.value = false
}

function confirmDeleteTask(task) {
  uni.showModal({
    title: '删除任务',
    content: `确定要删除「${task.content}」吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await taskStore.deleteTask(task.id)
          uni.showToast({ title: '已删除', icon: 'success' })
          await loadTasks()
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}

// Long-press to edit task (mobile)
let taskLongPressTimer = null
function onTaskTouchStart(task) {
  taskLongPressTimer = setTimeout(() => {
    taskLongPressTimer = null
    editTask(task)
  }, 600)
}
function onTaskTouchEnd() {
  if (taskLongPressTimer) { clearTimeout(taskLongPressTimer); taskLongPressTimer = null }
}

// 桌面端：任务卡片点击即编辑（移动端无此处理，避免误触，仍用长按）
function onTaskCardClick(task) {
  if (isDesktop.value) editTask(task)
}

async function switchView(mode) {
  if (viewMode.value === mode) return
  viewMode.value = mode
  // 切换视图时重置周视图长按就绪状态
  clearTimeout(weekViewReadyTimer)
  weekViewReady.value = false
  expandedCell.value = ''
  if (mode === 'month') {
    loadTaskDates()
    generateCalendar()
    await loadTasks()
    if (planStore.currentPlan) await taskStore.getAllTasks(planStore.currentPlan.id)
  } else if (mode === 'week') {
    weekViewReady.value = false
    clearTimeout(weekViewReadyTimer)
    weekViewReadyTimer = setTimeout(() => { weekViewReady.value = true }, 800)
    generateWeekDays()
    await loadWeekTasks()
  } else {
    selectedDate.value = formatDate(new Date())
    calendarMonth.value = new Date()
    await loadTasks()
  }
}

async function loadWeekTasks() {
  if (!planStore.currentPlan) return
  const result = await taskStore.getAllTasks(planStore.currentPlan.id)
  if (result.success) {
    const dates = new Set(result.tasks.map(t => t.date))
    dates.forEach(d => taskDates.value.add(d))
    saveTaskDatesToStorage()
    generateCalendar()
  }
}

async function loadTasks() {
  if (!planStore.currentPlan) return
  const result = await taskStore.getTasksByDate(planStore.currentPlan.id, selectedDate.value)
  if (result.success) {
    if (taskStore.todayTasks.length > 0) {
      taskDates.value.add(selectedDate.value)
    } else {
      taskDates.value.delete(selectedDate.value)
    }
    saveTaskDatesToStorage()
    generateCalendar()
  }
  await loadFocusRecords()
}

async function loadFocusRecords() {
  if (!planStore.currentPlan) { dateFocusRecords.value = []; return }
  try {
    const records = await api.getFocusRecords(planStore.currentPlan.id, selectedDate.value, selectedDate.value)
    dateFocusRecords.value = records || []
  } catch (e) {
    dateFocusRecords.value = []
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) {
    await planStore.getPlansByUserId()
    await loadTaskSubjects()
    if (planStore.currentPlan) {
      loadTaskDates()
      await loadTasks()
      // 预加载全部任务，供月视图/周视图循环任务展开使用
      await taskStore.getAllTasks(planStore.currentPlan.id)
      // 加载今日反思记录
      await loadDailyReflections(selectedDate.value)
    }
  }
  // 启动23:30未完成任务提醒
  startUnfinishedReminder()
})

onShow(async () => {
  if (planStore.currentPlan && userStore.isLoggedIn) {
    await loadTasks()
    await loadDailyReflections(selectedDate.value)
  }
})

watch(() => planStore.currentPlan?.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadTaskDates()
    await loadTasks()
  }
})
</script>

<style lang="scss" scoped>
.header {
  padding: 44px 0 14px;
  background: linear-gradient(135deg, var(--color-header-green-start, #2f7d4f) 0%, var(--color-header-green-end, #3d9a62) 100%);
  border-radius: 0 0 24px 24px;
  margin: 0 -20px 24px;
  padding-left: 20px; padding-right: 20px;
}

.header-top {
  margin-bottom: 14px;
  .title-row { display: flex; justify-content: space-between; align-items: baseline; }
  .title { font-size: 26px; font-weight: 700; color: #fff; }
  .date { font-size: 15px; color: rgba(255,255,255,0.8); font-weight: 500; }
  @media (max-width: 767px) {
    .title { font-size: 20px; }
    .date { font-size: 12px; }
  }
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.view-toggle {
  display: inline-flex;
  background: rgba(255,255,255,0.2);
  border-radius: 22px;
  padding: 3px;
  gap: 2px;
}
.toggle-btn {
  padding: 7px 16px;
  border-radius: 19px;
  font-size: 13px;
  color: rgba(255,255,255,0.85);
  font-weight: 500;
  transition: all 0.2s;
  &.active {
    background: #fff;
    color: #2f7d4f;
    font-weight: 600;
  }
  &:active { transform: scale(0.96); }
}

.quadrant-group {
  display: flex; gap: 6px; align-items: center; flex-shrink: 0;
}

.quadrant-switch {
  display: flex; align-items: center; gap: 6px;
  .switch-track {
    width: 40px; height: 22px; border-radius: 11px; background: rgba(255,255,255,0.3); transition: all 0.3s; position: relative;
    &.active { background: #fff; }
    .switch-thumb {
      width: 18px; height: 18px; border-radius: 50%; background: #fff; position: absolute; top: 2px; left: 2px; transition: all 0.3s;
    }
    &.active .switch-thumb { left: 20px; background: #2f7d4f; }
  }
  .switch-label { font-size: 13px; color: rgba(255,255,255,0.85); }
}
.quadrant-entry-btn {
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(255,255,255,0.25); border: 1px solid rgba(255,255,255,0.35);
  display: flex; align-items: center; justify-content: center;
  &:active { background: rgba(255,255,255,0.4); transform: scale(0.92); }
}
.quadrant-grid-icon { display: grid; grid-template-columns: 5px 5px; grid-template-rows: 5px 5px; gap: 2px; }
.qg-cell { background: #fff; border-radius: 1px; }

/* FAB — 右下角添加任务 */
.fab { position: fixed; right: 20px; bottom: 60px; z-index: 50; width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0,0,0,0.35); background: #2f7d4f; &:active { transform: scale(0.92); } .fab-icon { font-size: 28px; color: #fff; font-weight: 300; } }

.progress-summary {
  display: flex; align-items: center; background: rgba(255,255,255,0.1); border-radius: 10px; padding: 8px;
}
.progress-item { flex: 1; text-align: center; .progress-num { display: block; font-size: 17px; font-weight: 700; color: #fff; } .progress-label { font-size: 11px; color: rgba(255,255,255,0.7); } }
.progress-divider { width: 1px; height: 20px; background: rgba(255,255,255,0.2); }

.calendar {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e8ece9;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.cal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.cal-arrow {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #2f7d4f;
  border-radius: 50%;
  font-weight: 600;
  &:active { background: #f5f7f5; }
}
.cal-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}
.cal-weekdays {
  display: flex;
  margin-bottom: 4px;
}
.cal-weekday {
  flex: 1;
  text-align: center;
  font-size: 12px;
  color: #999;
  font-weight: 500;
}
.cal-days {
  display: flex;
  flex-wrap: wrap;
}
.cal-day {
  width: calc(100% / 7);
  height: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  &:active { background: rgba(47, 125, 79, 0.06); border-radius: 8px; }
}
.day-num {
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
  border-radius: 50%;
  font-size: 14px;
  color: #1a1a2e;
}
.cal-day.other .day-num { color: #ccc; }
.cal-day.today .day-num { color: #2f7d4f; font-weight: 700; }
.cal-day.selected .day-num { background: #2f7d4f; color: #fff; font-weight: 600; }
.cal-day.selected.today .day-num { color: #fff; }
.day-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #2f7d4f;
  margin-top: 2px;
}
.cal-day.selected .day-dot { background: #fff; }

.cal-menu {
  position: fixed;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  padding: 8px;
  z-index: 1000;
  min-width: 140px;
}
.cal-menu-item {
  display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 8px;
  &:active { background: #f5f7f5; }
}
.cal-menu-icon { font-size: 16px; }
.cal-menu-text { font-size: 14px; color: #333; }

/* 周视图 */
.week-view {
  background: #fff; border-radius: 12px; margin-bottom: 16px;
  border: 1px solid #e8ece9; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  overflow: hidden;
}
.week-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-bottom: 1px solid #f0f0f0;
}
.week-arrow { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #2f7d4f; border-radius: 50%; font-weight: 600;
  &:active { background: #f5f7f5; } }
.week-title { font-size: 15px; font-weight: 600; color: #1a1a2e; flex: 1; text-align: center; }
.week-download-btn {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 12px; border-radius: 16px;
  background: rgba(47,125,79,0.08); border: 1px solid rgba(47,125,79,0.15);
  white-space: nowrap; cursor: pointer;
  &:active { background: rgba(47,125,79,0.15); }
  .download-icon { font-size: 14px; }
  .download-text { font-size: 12px; color: #2f7d4f; font-weight: 500; }
}

/* 周视图主体容器 */
.week-container {
  display: flex; flex-direction: row;
}

/* 左侧固定时间轴容器 */
.week-timeline-container {
  width: 50px; flex-shrink: 0; background: #fafafa;
  border-right: 1px solid #f0f0f0; display: flex; flex-direction: column;
}
.week-timeline-header {
  height: 60px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  border-bottom: 2px solid #f0f0f0; font-size: 11px; color: #999; font-weight: 500;
}
.week-timeline-scroll {
  flex: 1; width: 100%;
}
.week-timeline {
  width: 50px;
}
/* 手机端：时间轴收窄 */
@media (max-width: 767px) {
  .week-timeline-container {
    width: 36px;
  }
  .week-timeline {
    width: 36px;
  }
  .week-timeline-header {
    font-size: 10px;
  }
  .time-label {
    font-size: 9px; padding-right: 3px;
  }
}

/* 右侧日期区域 */
.week-dates-container {
  flex: 1; overflow: hidden;
}
.week-dates-hscroll {
  overflow-x: auto; overflow-y: hidden;
}
.week-dates-table { display: flex; flex-direction: column; }
/* 桌面端：表格居中，右侧不留白 */
@media (min-width: 768px) {
  .week-container {
    justify-content: center;
  }
  .week-dates-container {
    flex: 0 0 auto;
  }
}

/* 日期头行 */
.week-days-header {
  display: flex; background: #fff; border-bottom: 2px solid #f0f0f0;
  height: 60px;
}
.week-day-header {
  flex-shrink: 0; text-align: center;
  border-right: 1px solid #f0f0f0;
  height: 60px; display: flex; flex-direction: column; align-items: center; justify-content: center;
  &:last-child { border-right: none; }
  &.today {
    .week-day-num { color: #2f7d4f; font-weight: 700; }
    .week-day-name { color: #2f7d4f; }
    background: rgba(47,125,79,0.08); border-radius: 8px;
    margin: 2px; border: 1px solid rgba(47,125,79,0.2);
  }
  &.weekend { background: rgba(255,248,220,0.3); .week-day-name, .week-day-num { color: #8b7355; } }
}
.week-day-name { display: block; font-size: 11px; color: #999; margin-bottom: 2px; }
.week-day-num { font-size: 18px; color: #1a1a2e; font-weight: 600; line-height: 1; }
.week-day-dot { width: 8px; height: 8px; border-radius: 50%; background: #2f7d4f; margin-top: 3px; }

/* 格子体纵向滚动 */
.week-dates-scroll {
  flex: 1;
}

/* 时间标签 */
.time-label {
  height: 72px; display: flex; align-items: flex-start; justify-content: flex-end;
  padding-right: 6px; padding-top: 2px; font-size: 10px; color: #999; font-weight: 500;
  box-sizing: border-box; border-bottom: 1px solid #f5f5f5;
}
.week-grid { display: flex; }
.week-column { flex-shrink: 0; border-right: 1px solid #f0f0f0; position: relative;
  &:last-child { border-right: none; }
  &.weekend { background: rgba(255,248,220,0.1); }
}
.week-cell {
  height: 72px; border-bottom: 1px solid #f5f5f5;
  &:last-child { border-bottom: none; }
  &:nth-child(odd) { background: rgba(248,250,248,0.5); }
}
.week-task {
  background: #e8f5e9; border-radius: 6px; padding: 3px 5px;
  cursor: pointer; box-shadow: 0 1px 3px rgba(47,125,79,0.2);
  overflow: hidden; display: flex; flex-direction: column;
  &:active { filter: brightness(0.93); }
  &.scrolled { overflow-y: auto; -webkit-overflow-scrolling: touch; }
  &.completed { background: #f0f0f0; box-shadow: none; opacity: 0.7; }
  &.subject-ds { background: #e3f2fd; .week-task-content { color: #1565c0; } }
  &.subject-os { background: #f3e5f5; .week-task-content { color: #7b1fa2; } }
  &.subject-cn { background: #e0f7fa; .week-task-content { color: #00838f; } }
  &.subject-co { background: #fff3e0; .week-task-content { color: #e65100; } }
  &.subject-en { background: #fce4ec; .week-task-content { color: #c62828; } }
  &.subject-pol { background: #f1f8e9; .week-task-content { color: #558b2f; } }
  &.subject-math { background: #ede7f6; .week-task-content { color: #4527a0; } }
  &.subject-db { background: #e8f5e9; .week-task-content { color: #2e7d32; } }
  &.subject-uml { background: #fff8e1; .week-task-content { color: #f57f17; } }
  &.subject-algo { background: #e1f5fe; .week-task-content { color: #01579b; } }
  &.subject-c { background: #fbe9e7; .week-task-content { color: #bf360c; } }
  &.subject-default { background: #e8f5e9; .week-task-content { color: #2f7d4f; } }
}
.task-importance-dot {
  width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 4px;
  &.importance-red { background: #ef5350; box-shadow: 0 0 4px rgba(239,83,80,0.6); }
  &.importance-blue { background: #42a5f5; box-shadow: 0 0 4px rgba(66,165,245,0.6); }
  &.importance-orange { background: #ff9800; box-shadow: 0 0 4px rgba(255,152,0,0.6); }
  &.importance-gray { background: #9e9e9e; }
}
.week-task-content {
  font-size: 12px; color: #2f7d4f;
  white-space: normal; word-break: break-word; overflow-wrap: break-word;
  font-weight: 500; line-height: 1.4;
}
.week-task-duration { font-size: 10px; color: #999; margin-top: 2px; }
.week-task-time { font-size: 10px; color: #2f7d4f; font-weight: 500; margin-right: 4px; }
.week-task-actions { display: flex; gap: 4px; margin-top: 4px; width: 100%; }
.wta-btn { font-size: 11px; padding: 2px 8px; border-radius: 6px; background: rgba(0,0,0,0.08); color: #555;
  &.danger { color: #c62828; background: rgba(198,40,40,0.1); } }

.week-tip-bar {
  padding: 4px 0 8px; text-align: center; margin: 0;
}
.week-tip-text { font-size: 11px; color: #999; }

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
.task-importance-tag { font-size: 11px; padding: 2px 8px; border-radius: 8px; font-weight: 500; white-space: nowrap;
  &.importance-red { background: #ffebee; color: #c62828; }
  &.importance-blue { background: #e3f2fd; color: #1565c0; }
  &.importance-orange { background: #fff3e0; color: #e65100; }
  &.importance-gray { background: #f5f5f5; color: #616161; }
}
.task-repeat-tag { font-size: 12px; color: #e65100; background: #fff3e0; padding: 2px 8px; border-radius: 8px; font-weight: 500; }
.task-duration, .task-actual, .task-time { font-size: 12px; color: #999; }
.task-time { color: #2f7d4f; font-weight: 500; }
.task-pomodoro { flex-shrink: 0; .pomodoro-icon { font-size: 24px; } }
.task-reflection {
  flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%;
  background: rgba(47,125,79,0.08); display: flex; align-items: center; justify-content: center;
  .reflection-icon { font-size: 16px; color: #2f7d4f; }
  &:active { background: rgba(47,125,79,0.15); }
}
.task-delete { flex-shrink: 0; padding: 4px 8px; .delete-icon { font-size: 18px; color: #c62828; } }

.empty { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .empty-icon { font-size: 48px; margin-bottom: 12px; } .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; } .empty-hint { font-size: 13px; color: #999; text-align: center; } }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 24px; }
.modal-content { background: #fff; border-radius: 20px; width: 100%; max-width: 440px; max-height: 75vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-header-actions { display: flex; align-items: center; gap: 8px; }
.modal-ai-btn { font-size: 13px; color: #6b4ce6; padding: 4px 10px; background: #f3f0ff; border-radius: 14px; font-weight: 500; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.delete-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #c62828; background: #ffebee; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: #2f7d4f; font-weight: 600; }
.form-group { margin-bottom: 16px; &.half { flex: 1; } }
.form-row { display: flex; gap: 12px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; &:focus-within { border-color: #2f7d4f; } }
.picker-wrapper { display: flex; align-items: center; justify-content: space-between; }
.picker-value { font-size: 15px; color: #1a1a2e; flex: 1; &.placeholder { color: #999; } }
.picker-arrow { font-size: 14px; color: #999; margin-left: 8px; }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 60px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.form-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.form-label-row .form-label { margin-bottom: 0; }
.form-manage-link {
  font-size: 12px; color: $accent; padding: 2px 8px; border-radius: 8px;
  background: rgba(47,125,79,0.06); font-weight: 500;
  &:active { background: rgba(47,125,79,0.15); }
}
.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-item { padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; display: flex; align-items: center; gap: 4px; &.active { background: #2f7d4f; color: #fff; } &.subject-add { background: #fff; border: 1.5px dashed #d0d5d2; color: #2f7d4f; } }
.type-row { display: flex; gap: 8px; }
.type-item { flex: 1; padding: 10px; text-align: center; border-radius: 10px; font-size: 13px; color: #65746d; background: #f5f7f5; &.active { background: #2f7d4f; color: #fff; } }

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

.add-mode-tabs {
  display: flex; gap: 10px; margin-bottom: 20px;
}
.add-mode-tab {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 12px; border-radius: 12px; background: #f5f7f5;
  .tab-icon { font-size: 20px; }
  .tab-text { font-size: 13px; color: #666; }
  &.active {
    background: linear-gradient(135deg, #2f7d4f, #3d9960);
    .tab-text { color: #fff; font-weight: 600; }
  }
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

.picker-value {
  height: 44px; line-height: 44px; color: #333; font-size: 14px;
}

.importance-item {
  display: flex; align-items: center; gap: 6px;
  .imp-dot {
    width: 8px; height: 8px; border-radius: 50%;
  }
  .imp-red { background: #ff4d4f; }
  .imp-blue { background: #1890ff; }
  .imp-orange { background: #fa8c16; }
  .imp-gray { background: #bfbfbf; }
}

.bottom-space { height: 100px; }

.focus-records-section {
  margin: 16px 0;
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.focus-records-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}
.focus-records-title { font-size: 16px; font-weight: 600; color: #333; }
.focus-records-count { font-size: 12px; color: #999; }
.focus-record-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f8f8f8;
  &:last-child { border-bottom: none; }
}
.focus-record-icon {
  width: 36px; height: 36px; border-radius: 50%;
  background: #fff3e0; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.focus-record-emoji { font-size: 18px; }
.focus-record-body { flex: 1; min-width: 0; }
.focus-record-task {
  font-size: 14px; color: #333; font-weight: 500;
  display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.focus-record-meta { font-size: 12px; color: #999; margin-top: 2px; }
.focus-record-duration {
  font-size: 14px; font-weight: 600; color: #ef5350;
  flex-shrink: 0;
}

/* 复制任务选择弹窗 */
.modal-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 300;
  display: flex; align-items: flex-end;
}
.modal-sheet {
  background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-width: 520px; margin: 0 auto;
  max-height: 75vh; display: flex; flex-direction: column;
  animation: cpUp 0.25s ease;
}
@keyframes cpUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.modal-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 22px; border-bottom: 1px solid #f0f0f0;
}
.modal-sheet .modal-title { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.modal-sheet .modal-x {
  width: 30px; height: 30px; border-radius: 50%; background: #f5f7f5;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; color: #999;
}
.modal-sheet .modal-body { padding: 16px 22px; flex: 1; overflow-y: auto; }
.copy-search-wrap { margin-bottom: 12px; }
.copy-search-input {
  width: 100%; padding: 12px 14px; border: 1.5px solid #e8ece9; border-radius: 12px;
  background: #fafafa; font-size: 14px; color: #1a1a2e; box-sizing: border-box;
  height: 44px;
}
.copy-search-input:focus { border-color: #2f7d4f; }
.copy-target-hint {
  font-size: 12px; color: #888; background: #f5f7f5; padding: 8px 12px;
  border-radius: 10px; margin-bottom: 12px;
}
.copy-target-date { color: #2f7d4f; font-weight: 600; }
.copy-target-time { color: #2f7d4f; font-weight: 600; margin-left: 4px; }
.copy-list { display: flex; flex-direction: column; gap: 8px; }
.copy-item {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px; background: #fafafa; border-radius: 12px; border: 1px solid #e8ece9;
  &:active { background: #e8f0eb; border-color: #2f7d4f; }
}
.copy-item-body { flex: 1; min-width: 0; }
.copy-item-content { display: block; font-size: 14px; color: #1a1a2e; font-weight: 500; }
.copy-item-meta { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px; }
.copy-item-subj { font-size: 11px; padding: 2px 8px; background: #e8f5e9; color: #2f7d4f; border-radius: 8px; }
.copy-item-chap { font-size: 11px; padding: 2px 8px; background: #f3f0ff; color: #6b4ce6; border-radius: 8px; }
.copy-item-dur { font-size: 11px; color: #999; }
.copy-item-date { font-size: 11px; color: #bbb; }
.copy-item-arrow { font-size: 20px; color: #ccc; flex-shrink: 0; }
.copy-empty { text-align: center; padding: 30px 12px; }
.copy-empty-text { font-size: 13px; color: #999; }
</style>