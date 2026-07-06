<template>
  <view class="page" @click="closeCalMenu">
    <view class="header">
      <view class="header-top">
        <view class="header-left">
          <view class="view-toggle">
            <view class="toggle-btn" :class="{ active: viewMode === 'today' }" @click="switchView('today')">今日</view>
            <view class="toggle-btn" :class="{ active: viewMode === 'week' }" @click="switchView('week')">周视图</view>
            <view class="toggle-btn" :class="{ active: viewMode === 'month' }" @click="switchView('month')">月视图</view>
          </view>
          <text class="title">{{ headerTitle }}</text>
          <text class="date">{{ currentDate }}</text>
        </view>
        <view class="header-actions">
          <view class="quadrant-switch" @click="toggleQuadrant">
            <view class="switch-track" :class="{ active: enableQuadrant }">
              <view class="switch-thumb"></view>
            </view>
            <text class="switch-label">四象限</text>
          </view>
          <view class="quadrant-entry-btn" v-if="enableQuadrant" @click="goToQuadrant">
            <text class="quadrant-entry-icon">◻️</text>
          </view>
          <view class="add-btn" @click="openManualAdd">
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
            'has-task': taskDates.has(day.dateStr)
          }"
          @click="selectDate(day.dateStr)"
          @contextmenu.prevent="handleCalRightClick(day.dateStr, $event)"
          @touchstart="onCalTouchStart(day.dateStr)"
          @touchend="onCalTouchEnd"
          @mousedown="onCalMouseDown(day.dateStr, $event)"
          @mouseup="onCalMouseUp"
          @mouseleave="onCalMouseUp">
          <text class="day-num">{{ day.day }}</text>
          <view class="day-dot" v-if="taskDates.has(day.dateStr)"></view>
        </view>
      </view>
    </view>

    <view class="cal-menu" v-if="showCalMenu" :style="{ left: calMenuX + 'px', top: calMenuY + 'px' }" @click.stop>
      <view class="cal-menu-item" @click="addTaskFromCal">
        <text class="cal-menu-icon">+</text>
        <text class="cal-menu-text">添加任务</text>
      </view>
    </view>

    <view class="week-view" v-if="viewMode === 'week'">
      <view class="week-header">
        <view class="week-arrow" @click="switchWeek(-1)">‹</view>
        <text class="week-title">{{ weekTitle }}</text>
        <view class="week-arrow" @click="switchWeek(1)">›</view>
      </view>
      <view class="week-days-header">
        <view class="week-timeline-header"></view>
        <view class="week-day-header" v-for="(day, idx) in weekDays" :key="idx" :class="{ today: day.isToday, weekend: day.isWeekend }">
          <text class="week-day-name">{{ day.dayName }}</text>
          <text class="week-day-num">{{ day.day }}</text>
          <view class="week-day-dot" v-if="taskDates.has(day.dateStr)"></view>
        </view>
      </view>
      <view class="week-scroll">
        <view class="week-body">
          <view class="week-timeline">
            <view class="time-label" v-for="hour in timelineHours" :key="hour">
              <text>{{ hour }}:00</text>
            </view>
          </view>
          <view class="week-grid">
          <view class="week-column" v-for="(day, colIdx) in weekDays" :key="colIdx" :data-col="colIdx" :class="{ weekend: day.isWeekend }">
            <view
              class="week-cell"
              v-for="(hour, hourIdx) in timelineHours"
              :key="hourIdx"
              :data-hour="hour"
              :data-date="day.dateStr"
              :class="{ expanded: expandedCell === day.dateStr + '-' + hour }"
              @click.stop="onWeekCellClick(day.dateStr, hour)"
              @contextmenu.prevent="handleWeekCellRightClick(day.dateStr, hour, $event)"
              @touchstart="onWeekCellTouchStart(day.dateStr, hour)"
              @touchmove="onWeekCellTouchCancel"
              @touchend.prevent="onWeekCellTouchEnd"
              @mousedown="onWeekCellMouseDown(day.dateStr, hour)"
              @mouseup="onWeekCellMouseUp">
              <view class="week-task" v-for="task in getTasksAt(day.dateStr, hour)" :key="task.id" :class="{ completed: task.status === 'completed', [getSubjectClass(task.subject)]: true }">
                <view class="task-importance-dot" :class="getImportanceClass(task.importance)" v-if="task.importance && enableQuadrant"></view>
                <text class="week-task-content">{{ task.content }}</text>
                <text class="week-task-duration">{{ task.duration }}min</text>
              </view>
            </view>
          </view>
        </view>
        </view><!-- .week-body -->
        <view class="current-time-line" v-if="viewMode === 'week'" :style="currentTimeLineStyle"></view>
        <view class="week-hint">
          <text class="week-hint-text">点击任务查看详情，长按格子编辑/添加任务</text>
        </view>
      </view>
    </view>

    <!-- 周视图右键菜单 -->
    <view class="cal-menu" v-if="showWeekMenu" :style="{ left: weekMenuX + 'px', top: weekMenuY + 'px' }" @click.stop>
      <view class="cal-menu-item" @click="addTaskFromWeekCell(weekCellDate, weekCellHour)">
        <text class="cal-menu-icon">+</text>
        <text class="cal-menu-text">添加任务</text>
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
            <view class="task-importance-tag" :class="getImportanceClass(task.importance)" v-if="task.importance && enableQuadrant">{{ getImportanceLabel(task.importance) }}</view>
            <text class="task-repeat-tag" v-if="task.repeat_type && task.repeat_type !== 'none'">{{ getRepeatLabel(task.repeat_type) }}</text>
            <text class="task-duration">预计: {{ task.duration }}分钟</text>
            <text class="task-actual" v-if="task.actual_duration > 0">实际: {{ task.actual_duration }}分钟</text>
          </view>
        </view>
        <view class="task-pomodoro" @click="startPomodoro(task)">
          <text class="pomodoro-icon">🍅</text>
        </view>
      </view>
    </view>

    <view class="empty" v-if="viewMode !== 'week' && filteredTasks.length === 0">
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无任务</text>
      <text class="empty-hint">点击上方「添加任务」按钮手动创建任务</text>
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

    <view class="modal-overlay" v-if="showAddForm || editingTask" @click="closeForm">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingTask ? '编辑任务' : '添加任务' }}</text>
          <view class="modal-header-actions">
            <text class="modal-ai-btn" v-if="!editingTask && addMode === 'manual'" @click="addMode = 'ai'">🤖 AI添加</text>
            <text class="modal-ai-btn" v-if="!editingTask && addMode === 'ai'" @click="addMode = 'manual'">✏️ 手动输入</text>
            <view class="modal-close" @click="closeForm">✕</view>
          </view>
        </view>
        <scroll-view scroll-y class="modal-body">

          <view v-if="addMode === 'ai' && !editingTask" class="ai-section">
            <view class="ai-hint-box">
              <text class="ai-hint-title">粘贴文字计划，AI自动生成任务</text>
              <text class="ai-hint-desc">例如：明天上午9点复习数学第三章，下午2点做英语阅读</text>
            </view>
            <textarea class="ai-textarea-large" v-model="aiParseInput" placeholder="请粘贴您的文字计划..." />
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

          <view v-if="addMode === 'manual' || editingTask">
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
              <view class="input-wrapper" v-if="showSubjectInput" style="margin-top: 10px;">
                <input class="input-field" v-model="customSubject" placeholder="输入自定义科目..." @confirm="addCustomSubject" />
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
                <text class="form-label">开始时间</text>
                <view class="input-wrapper">
                  <picker mode="selector" :range="hourOptions" @change="onStartHourChange">
                    <view class="picker-value">{{ form.start_hour }}:00</view>
                  </picker>
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

            <view class="form-group" v-if="editingTask">
              <text class="form-label">实际用时（系统根据番茄钟自动记录）</text>
              <view class="input-wrapper">
                <input class="input-field" v-model="form.actual_duration" type="number" placeholder="0" />
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="closeForm">取消</view>
          <view class="submit-btn" @click="submitForm">{{ editingTask ? '保存' : '添加' }}</view>
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
          <view class="manage-item" v-for="s in subjectOptions" :key="s">
            <view class="manage-item-left">
              <text class="manage-item-name">{{ s }}</text>
              <text class="manage-item-badge" v-if="!customSubjectOptions.includes(s)">预设</text>
              <text class="manage-item-badge manage-custom-badge" v-else>自定义</text>
            </view>
            <view
              class="manage-item-del"
              v-if="customSubjectOptions.includes(s)"
              @click="removeSubjectFromManager(s)"
            >删除</view>
          </view>
          <view class="manage-add-row">
            <input
              class="manage-add-input"
              v-model="manageNewSubject"
              placeholder="输入新科目名称"
              @confirm="addManageSubject"
            />
            <view class="manage-add-btn" @click="addManageSubject">添加</view>
          </view>
        </view>
      </view>
    </view>

    <view class="manage-overlay" v-if="showAIParseModal" @click="showAIParseModal = false">
      <view class="manage-dialog ai-dialog" @click.stop>
        <view class="manage-dialog-top">
          <text class="manage-dialog-title">🤖 AI解析文字计划</text>
          <view class="manage-dialog-close" @click="showAIParseModal = false">✕</view>
        </view>
        <view class="manage-dialog-body">
          <view class="ai-hint">
            <text class="ai-hint-text">粘贴您的文字计划，AI会自动解析并生成任务列表</text>
            <text class="ai-hint-example">例如："明天上午9点复习数学第三章，下午2点做英语阅读"</text>
          </view>
          <textarea class="ai-textarea" v-model="aiParseInput" placeholder="请粘贴您的文字计划..." />
          <view class="ai-parse-btn-large" @click="parseWithAI">
            <text class="ai-icon">🔍</text>
            <text class="ai-text">开始解析</text>
          </view>
          <view class="ai-result" v-if="aiParseResult.length > 0">
            <text class="ai-result-title">解析结果</text>
            <view class="ai-task-item" v-for="(task, idx) in aiParseResult" :key="idx">
              <view class="ai-task-checkbox" :class="{ checked: task.selected }" @click="task.selected = !task.selected"></view>
              <view class="ai-task-info">
                <text class="ai-task-content">{{ task.content }}</text>
                <text class="ai-task-meta">{{ task.subject }} · {{ task.date }} · {{ task.duration }}分钟</text>
              </view>
            </view>
            <view class="ai-add-all-btn" @click="addParsedTasks">添加选中任务</view>
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useTaskStore } from '@/stores/task'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import { useFarmStore } from '@/stores/farm'
import { getFocusRecords } from '@/api/client'

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
let weekCellTouchTimer = null

const allSubjects = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']
const subjectOptions = ref([...allSubjects])
const customSubjectOptions = ref([])
const showManageSubjects = ref(false)
const manageNewSubject = ref('')
const showAIParseModal = ref(false)
const aiParseInput = ref('')
const aiParseResult = ref([])
const addMode = ref('manual')
const hourOptions = Array.from({ length: 18 }, (_, i) => String(i + 6))

// 章节下拉选项：从当前计划科目中提取
const availableChapters = computed(() => {
  const planSubjects = planStore.currentPlan?.subjects || []
  // 找到当前选中科目的章节列表
  const currentSubj = planSubjects.find(s => s.name === form.value.subject)
  if (!currentSubj || !currentSubj.chapters || currentSubj.chapters.length === 0) return []
  return currentSubj.chapters.map(c => c.name || '').filter(Boolean)
})

function onChapterChange(e) {
  const idx = e.detail.value
  if (availableChapters.value[idx]) {
    form.value.chapter = availableChapters.value[idx]
    // 如果有章节时长，自动填入预计时间
    const planSubjects = planStore.currentPlan?.subjects || []
    const currentSubj = planSubjects.find(s => s.name === form.value.subject)
    if (currentSubj?.chapters?.[idx]?.duration) {
      form.value.duration = currentSubj.chapters[idx].duration
    }
  }
}

// 科目切换时清空章节（如果不是同一科目）
watch(() => form.value.subject, () => {
  form.value.chapter = ''
})

async function loadTaskSubjects() {
  try { const res = await api.getUserSubjects(); const saved = res.subjects || []; customSubjectOptions.value = saved.filter(s => !allSubjects.includes(s)); subjectOptions.value = [...allSubjects]; saved.forEach(s => { if (!subjectOptions.value.includes(s)) subjectOptions.value.push(s) }) } catch (e) { /* offline */ }
}
function addCustomSubject() {
  const name = customSubject.value.trim()
  if (!name) return
  if (!subjectOptions.value.includes(name)) { subjectOptions.value.push(name) }
  if (!customSubjectOptions.value.includes(name)) { customSubjectOptions.value.push(name); api.addUserSubject(name).catch(()=>{}) }
  form.value.subject = name; customSubject.value = ''; showSubjectInput.value = false
}
function addManageSubject() {
  const name = manageNewSubject.value.trim()
  if (!name) return
  if (!subjectOptions.value.includes(name)) { subjectOptions.value.push(name) }
  if (!customSubjectOptions.value.includes(name)) { customSubjectOptions.value.push(name); api.addUserSubject(name).catch(()=>{}) }
  manageNewSubject.value = ''
}
function removeSubjectFromManager(name) {
  uni.showModal({ title: '删除科目', content: `确定要删除「${name}」吗？`, success: (res) => {
    if (res.confirm) {
      customSubjectOptions.value = customSubjectOptions.value.filter(s => s !== name)
      subjectOptions.value = subjectOptions.value.filter(s => s !== name)
      api.removeUserSubject(name).catch(()=>{})
      if (form.value.subject === name) form.value.subject = subjectOptions.value[0] || ''
    }
  }})
}

const defaultForm = {
  subject: '数据结构',
  chapter: '',
  content: '',
  duration: 25,
  actual_duration: 0,
  type: 'new_study',
  repeat_type: 'none',
  importance: '',
  start_hour: 9
}

const form = ref({ ...defaultForm })

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
  return formatDateLabel(new Date(selectedDate.value))
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
  const CELL_H = 60
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

function getTasksAt(dateStr, hour) {
  return taskStore.weekTasks.filter(t => t.date === dateStr && t.start_hour === hour)
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
  }
  if (planStore.currentPlan && viewMode.value === 'week') {
    await taskStore.getAllTasks(planStore.currentPlan.id)
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
    type: task.type,
    repeat_type: task.repeat_type || 'none',
    importance: task.importance || ''
  }
  showAddForm.value = false
}

function openManualAdd() {
  addMode.value = 'manual'
  showAddForm.value = true
}

function openAIAdd() {
  addMode.value = 'ai'
  showAddForm.value = true
}

function closeForm() {
  showAddForm.value = false
  editingTask.value = null
  form.value = { ...defaultForm }
  addMode.value = 'manual'
  aiParseInput.value = ''
  aiParseResult.value = []
}

function onStartHourChange(e) {
  form.value.start_hour = parseInt(hourOptions[e.detail.value])
}

const allSelected = computed(() => {
  if (aiParseResult.value.length === 0) return false
  return aiParseResult.value.every(t => t.selected)
})

function toggleSelectAll() {
  const target = !allSelected.value
  aiParseResult.value.forEach(t => {
    t.selected = target
  })
}

function goToQuadrant() {
  uni.navigateTo({ url: '/pages/daily/quadrant' })
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
        date: selectedDate.value,
        type: form.value.type,
        subject: form.value.subject,
        chapter: form.value.chapter,
        content: form.value.content,
        duration: parseInt(form.value.duration) || 25,
        repeat_type: form.value.repeat_type,
        importance: form.value.importance,
        start_hour: form.value.start_hour || 9
      })
      taskDates.value.add(selectedDate.value)
      saveTaskDatesToStorage()
      generateCalendar()
    }
    if (planStore.currentPlan) {
      await taskStore.getAllTasks(planStore.currentPlan.id)
      if (viewMode.value === 'today') {
        await taskStore.getTasksByDate(planStore.currentPlan.id, selectedDate.value)
      }
    }
    closeForm()
    uni.showToast({ title: editingTask.value ? '已更新' : '已添加', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
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
  showAddForm.value = true
  form.value.date = calSelectedDate.value
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
  showAddForm.value = true
  form.value.date = dateStr
  form.value.start_hour = hour
  form.value.duration = 60
}

// === 单元格交互：点击展开任务详情，长按编辑/添加 ===
let weekCellDownTime = 0
let weekCellDidLong = false
let weekCellDownDate = ''
let weekCellDownHour = 0
let weekCellMouseTimer = null

function onWeekCellTouchStart(dateStr, hour) {
  weekCellDidLong = false
  weekCellDownDate = dateStr
  weekCellDownHour = hour
  weekCellDownTime = Date.now()
  clearTimeout(weekCellTouchTimer)
  weekCellTouchTimer = setTimeout(() => {
    weekCellDidLong = true
    const tasksAtCell = getTasksAt(dateStr, hour)
    if (tasksAtCell.length > 0) {
      // 有任务：直接编辑第一个
      editTask(tasksAtCell[0])
    } else {
      // 无任务：弹右键菜单
      weekCellDate.value = dateStr
      weekCellHour.value = hour
      showWeekMenu.value = true
      weekMenuX.value = 100
      weekMenuY.value = 200
    }
  }, 300)
}

function onWeekCellTouchCancel() {
  // 滑动时取消长按，防止误触
  clearTimeout(weekCellTouchTimer)
  weekCellDidLong = false
}

function onWeekCellTouchEnd() {
  clearTimeout(weekCellTouchTimer)
  // 重置长按标记，恢复短按功能
  setTimeout(() => { weekCellDidLong = false }, 50)
}

function onWeekCellMouseDown(dateStr, hour) {
  weekCellDidLong = false
  weekCellDownDate = dateStr
  weekCellDownHour = hour
  weekCellDownTime = Date.now()
  clearTimeout(weekCellMouseTimer)
  weekCellMouseTimer = setTimeout(() => {
    weekCellDidLong = true
    const tasksAtCell = getTasksAt(dateStr, hour)
    if (tasksAtCell.length > 0) {
      editTask(tasksAtCell[0])
    } else {
      weekCellDate.value = dateStr
      weekCellHour.value = hour
      handleWeekCellRightClick(dateStr, hour, { clientX: 200, clientY: 300 })
    }
  }, 300)
}

function onWeekCellMouseUp() {
  clearTimeout(weekCellMouseTimer)
}

function closeWeekMenu() {
  showWeekMenu.value = false
}

function confirmDeleteTask(task) {
  uni.showModal({
    title: '删除任务',
    content: `确定要删除「${task.content}」吗？`,
    success: (res) => {
      if (res.confirm) {
        taskStore.deleteTask(task.id)
        uni.showToast({ title: '已删除', icon: 'success' })
        loadTasks()
      }
    }
  })
}

async function parseWithAI() {
  if (!aiParseInput.value.trim()) {
    uni.showToast({ title: '请输入文字计划', icon: 'none' })
    return
  }

  uni.showLoading({ title: 'AI解析中...' })
  try {
    const result = await api.aiParsePlan({
      text: aiParseInput.value.trim(),
      plan_id: planStore.currentPlan?.id
    })
    aiParseResult.value = (result.tasks || []).map(t => ({
      ...t,
      selected: true
    }))
  } catch (e) {
    uni.showToast({ title: 'AI服务暂不可用', icon: 'none' })
    aiParseResult.value = mockParsePlan(aiParseInput.value.trim())
  } finally {
    uni.hideLoading()
  }
}

function mockParsePlan(text) {
  const subjects = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']
  const today = new Date()
  const result = []
  
  const lines = text.split(/[,，。；;、\n]/).filter(l => l.trim())
  lines.forEach(line => {
    const lineTrim = line.trim()
    if (!lineTrim) return
    
    let subject = '数据结构'
    for (const s of subjects) {
      if (lineTrim.includes(s)) {
        subject = s
        break
      }
    }
    
    let date = formatDate(today)
    if (lineTrim.includes('明天') || lineTrim.includes('明日')) {
      const tmr = new Date(today)
      tmr.setDate(tmr.getDate() + 1)
      date = formatDate(tmr)
    } else if (lineTrim.includes('后天')) {
      const day = new Date(today)
      day.setDate(day.getDate() + 2)
      date = formatDate(day)
    }
    
    const durationMatch = lineTrim.match(/(\d+)\s*分钟|(\d+)\s*小时|(\d+)\s*min/)
    let duration = 30
    if (durationMatch) {
      const num = parseInt(durationMatch[1] || durationMatch[2] || durationMatch[3])
      if (lineTrim.includes('小时')) {
        duration = num * 60
      } else {
        duration = num
      }
    }
    
    result.push({
      content: lineTrim,
      subject,
      date,
      duration,
      selected: true
    })
  })
  
  return result.slice(0, 10)
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
        date: task.date,
        type: 'new_study',
        subject: task.subject,
        content: task.content,
        duration: task.duration,
        repeat_type: 'none'
      })
      taskDates.value.add(task.date)
      added++
    } catch (e) { /* skip */ }
  }
  uni.hideLoading()
  saveTaskDatesToStorage()
  generateCalendar()
  showAIParseModal.value = false
  aiParseInput.value = ''
  aiParseResult.value = []
  uni.showToast({ title: `已添加 ${added} 个任务`, icon: 'success' })
}

async function switchView(mode) {
  if (viewMode.value === mode) return
  viewMode.value = mode
  if (mode === 'month') {
    loadTaskDates()
    generateCalendar()
    await loadTasks()
  } else if (mode === 'week') {
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
    const records = await getFocusRecords(planStore.currentPlan.id, selectedDate.value, selectedDate.value)
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
    }
  }
})

onShow(async () => {
  if (planStore.currentPlan && userStore.isLoggedIn) {
    await loadTasks()
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
  padding: 60px 0 20px;
  background: linear-gradient(135deg, var(--color-header-green-start, #2f7d4f) 0%, var(--color-header-green-end, #3d9a62) 100%);
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

.view-toggle {
  display: inline-flex;
  background: rgba(255,255,255,0.2);
  border-radius: 20px;
  padding: 3px;
  margin-bottom: 10px;
  gap: 2px;
}
.toggle-btn {
  padding: 5px 14px;
  border-radius: 17px;
  font-size: 12px;
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

.header-actions {
  display: flex; gap: 8px; align-items: center;
}

.quadrant-switch {
  display: flex; align-items: center; gap: 6px;
  .switch-track {
    width: 36px; height: 20px; border-radius: 10px; background: rgba(255,255,255,0.3); transition: all 0.3s; position: relative;
    &.active { background: #fff; }
    .switch-thumb {
      width: 16px; height: 16px; border-radius: 50%; background: #fff; position: absolute; top: 2px; left: 2px; transition: all 0.3s;
    }
    &.active .switch-thumb { left: 18px; background: #2f7d4f; }
  }
  .switch-label { font-size: 12px; color: rgba(255,255,255,0.85); }
}
.quadrant-entry-btn {
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(255,255,255,0.25); border: 1px solid rgba(255,255,255,0.35);
  display: flex; align-items: center; justify-content: center;
  &:active { background: rgba(255,255,255,0.4); transform: scale(0.92); }
}
.quadrant-entry-icon { font-size: 14px; }

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

.week-view {
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid #e8ece9;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  overflow: hidden;
}
.week-header {
  display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid #f0f0f0;
}
.week-arrow {
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #2f7d4f; border-radius: 50%; font-weight: 600;
  &:active { background: #f5f7f5; }
}
.week-title { font-size: 15px; font-weight: 600; color: #1a1a2e; }
.week-days-header {
  display: flex; background: #fff; position: sticky; top: 0; z-index: 10;
  border-bottom: 2px solid #f0f0f0; overflow: hidden;
}
.week-timeline-header {
  width: 40px; flex-shrink: 0; background: #fafafa; border-right: 1px solid #f0f0f0;
  display: flex; align-items: center; justify-content: center;
}
.week-day-header {
  flex: 1; min-width: 0; text-align: center; padding: 10px 2px; position: relative;
  border-right: 1px solid #f0f0f0;
  &:last-child { border-right: none; }
  &.today {
    .week-day-num { color: #2f7d4f; font-weight: 700; }
    .week-day-name { color: #2f7d4f; }
    background: rgba(47,125,79,0.08);
    border-radius: 8px;
    margin: 2px;
    border: 1px solid rgba(47,125,79,0.2);
  }
  &.weekend {
    background: rgba(255,248,220,0.3);
    .week-day-name, .week-day-num { color: #8b7355; }
  }
  &:active { background: rgba(47,125,79,0.06); }
}
.week-day-name { display: block; font-size: 11px; color: #999; margin-bottom: 3px; }
.week-day-num { font-size: 18px; color: #1a1a2e; font-weight: 600; }
.week-day-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #2f7d4f; margin: 4px auto 0;
  box-shadow: 0 0 4px rgba(47,125,79,0.4);
}
.week-scroll {
  height: 500px; overflow-y: auto; overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}
.week-body {
  display: flex; flex-direction: row;
}
.week-timeline {
  width: 40px; flex-shrink: 0; background: #fafafa; border-right: 1px solid #f0f0f0;
}
.time-label {
  height: 64px; display: flex; align-items: flex-start; justify-content: center;
  padding-top: 4px; font-size: 10px; color: #999; font-weight: 500;
}
.week-grid {
  flex: 1; display: flex; min-width: 0;
}
.week-column {
  flex: 1; min-width: 0; border-right: 1px solid #f0f0f0;
  &:last-child { border-right: none; }
  &.weekend { background: rgba(255,248,220,0.1); }
}
.week-cell {
  min-height: 64px; border-bottom: 1px solid #f5f5f5; position: relative; padding: 2px;
  overflow: hidden; transition: min-height 0.2s;
  &:nth-child(odd) { background: rgba(248,250,248,0.5); }
  &.expanded {
    min-height: auto; height: auto; overflow: visible; background: rgba(47,125,79,0.04);
    z-index: 3; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    .week-task { white-space: normal; }
    .week-task-content { -webkit-line-clamp: unset; display: block; }
  }
}
.week-task {
  background: #e8f5e9; border-radius: 6px; padding: 3px 4px;
  margin-bottom: 1px; cursor: pointer; box-shadow: 0 1px 2px rgba(47,125,79,0.12);
  &:active { transform: scale(0.98); }
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
  font-size: 11px; color: #2f7d4f;
  white-space: normal; word-break: break-all; overflow: hidden;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  font-weight: 500; line-height: 1.3;
}
.week-task-duration { font-size: 9px; color: #999; }
.week-task-actions { display: flex; gap: 4px; margin-top: 4px; width: 100%; }
.wta-btn { font-size: 11px; padding: 2px 8px; border-radius: 6px; background: rgba(0,0,0,0.08); color: #555;
  &.danger { color: #c62828; background: rgba(198,40,40,0.1); } }

.week-hint {
  position: absolute;
  bottom: 12px; left: 50%;
  transform: translateX(-50%);
  padding: 6px 12px;
  background: rgba(0,0,0,0.55);
  border-radius: 12px;
  pointer-events: none;
}
.week-hint-text { font-size: 11px; color: #fff; }

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
.task-duration, .task-actual { font-size: 12px; color: #999; }
.task-pomodoro { flex-shrink: 0; .pomodoro-icon { font-size: 24px; } }

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
.manage-item-badge {
  font-size: 10px; padding: 2px 8px; border-radius: 10px;
  background: #edf7ee; color: #2f7d4f;
}
.manage-custom-badge { background: #fff3e0; color: #e65100; }
.manage-item-del {
  font-size: 12px; padding: 5px 12px; border-radius: 8px;
  background: #ffebee; color: #c62828; font-weight: 500;
  &:active { background: #ffcdd2; }
}
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
  .ai-hint-title { display: block; font-size: 14px; font-weight: 600; color: #333; margin-bottom: 4px; }
  .ai-hint-desc { font-size: 12px; color: #888; }
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
</style>