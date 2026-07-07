<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">计划总览</text>
      <view class="edit-btn" @click="editPlan">
        <text class="edit-icon">✎</text>
      </view>
    </view>

    <!-- 切换计划 -->
    <view class="switch-section" v-if="planStore.plans.length > 1">
      <view class="switch-trigger" @click="showPlanSwitcher = !showPlanSwitcher">
        <text class="switch-label">📋 切换计划</text>
        <view class="switch-current">
          <text class="switch-current-name">{{ planStore.currentPlan?.exam_name }}</text>
          <text class="switch-arrow" :class="{ open: showPlanSwitcher }">▾</text>
        </view>
      </view>
      <view class="switch-panel" v-if="showPlanSwitcher">
        <view class="switch-plan-item" :class="{ active: planStore.currentPlan?.id === p.id }"
          v-for="p in planStore.plans" :key="p.id" @click="switchToPlan(p)">
          <view class="switch-plan-info">
            <text class="switch-plan-name">{{ p.exam_name }}</text>
            <text class="switch-plan-meta">{{ p.exam_date }}</text>
          </view>
          <text class="switch-plan-check" v-if="planStore.currentPlan?.id === p.id">✓</text>
        </view>
      </view>
    </view>

    <view class="plan-card" v-if="planStore.currentPlan">
      <view class="plan-header">
        <text class="plan-name">{{ planStore.currentPlan.exam_name }}</text>
        <text class="plan-status">进行中</text>
      </view>

      <view class="plan-info">
        <view class="info-item">
          <text class="info-icon">📅</text>
          <view class="info-content">
            <text class="info-label">考试日期</text>
            <text class="info-value">{{ planStore.currentPlan.exam_date }}</text>
          </view>
        </view>
        <view class="info-item">
          <text class="info-icon">⏱</text>
          <view class="info-content">
            <text class="info-label">每日学习</text>
            <text class="info-value">{{ planStore.currentPlan.daily_study_time }}分钟</text>
          </view>
        </view>
        <view class="info-item">
          <text class="info-icon">📊</text>
          <view class="info-content">
            <text class="info-label">剩余天数</text>
            <text class="info-value highlight">{{ daysRemaining }}天</text>
          </view>
        </view>
      </view>

      <!-- 备考进度甘特图 -->
      <view class="gantt-section" v-if="subjects.length > 0">
        <view class="section-header">
          <text class="section-title">甘特图绘制</text>
          <view class="gantt-toggle">
            <view class="toggle-opt" :class="{active:ganttMode==='plan'}" @click="ganttMode='plan'">仅计划</view>
            <view class="toggle-opt" :class="{active:ganttMode==='actual'}" @click="ganttMode='actual'">仅实际</view>
            <view class="toggle-opt" :class="{active:ganttMode==='both'}" @click="ganttMode='both'">对比</view>
          </view>
          <text class="gantt-hint-text">点击条编辑日期，电脑端体验更佳</text>
        </view>

        <view class="gantt-wrapper" v-if="ganttDayColumns.length > 0 && allChapters.length > 0">
          <view class="gantt-chart" :style="{ minWidth: ganttDayColumns.length * 32 + 130 + 'px' }">
            <view class="gantt-axis">
              <view class="gantt-label-col gantt-label-wide">科目 / 章节</view>
              <view class="gantt-date-row">
                <view class="gantt-date-col" v-for="(d, di) in ganttDayColumns" :key="di"
                  :class="{ today: d.isToday, 'week-start': d.isWeekStart }">
                  <text class="gantt-date-num">{{ d.day }}</text>
                  <text class="gantt-date-label" v-if="d.showMonth">{{ d.month }}月</text>
                </view>
              </view>
            </view>

            <view class="gantt-chapter-row" v-for="(ch, ci) in allChapters" :key="ci"
              :class="{ 'subject-first': ch.isFirstInSubject }">
              <view class="gantt-label-col gantt-label-wide">
                <text class="gantt-subj-name" v-if="ch.isFirstInSubject">{{ ch.subjectName }}</text>
                <text class="gantt-chapter-name">{{ ch.name || '未命名' }}</text>
              </view>
              <view class="gantt-bars-row" :class="'mode-'+ganttMode">
                <view class="gantt-subrow" v-if="ganttMode==='plan' || ganttMode==='both'">
                  <text class="gantt-row-tag plan-tag" v-if="ganttMode==='both'">计划</text>
                  <view class="gantt-bar gantt-bar-planned"
                    v-if="ch.planLeft !== null"
                    :style="{ left: ch.planLeft + '%', width: Math.max(ch.planWidth, 1) + '%', background: ch.color }"
                    @click="editChapterDate(ch)">
                    <text class="gantt-bar-label">{{ ch.plannedLabel }}</text>
                  </view>
                  <view class="gantt-bar gantt-bar-placeholder" v-else @click="editChapterDate(ch)">
                    <text class="gantt-bar-ph">未设置计划</text>
                  </view>
                </view>
                <view class="gantt-subrow" v-if="ganttMode==='actual' || ganttMode==='both'">
                  <text class="gantt-row-tag actual-tag" v-if="ganttMode==='both'">实际</text>
                  <view class="gantt-bar gantt-bar-actual"
                    v-if="ch.actualLeft !== null"
                    :style="{ left: ch.actualLeft + '%', width: Math.max(ch.actualWidth, 1) + '%' }"
                    @click="editChapterDate(ch)">
                    <text class="gantt-bar-label">{{ ch.actualLabel }}</text>
                  </view>
                  <view class="gantt-bar gantt-bar-placeholder" v-else @click="editChapterDate(ch)">
                    <text class="gantt-bar-ph">未设置实际</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="gantt-empty" v-else>
          <text class="gantt-empty-text">请先在下方科目中添加章节并设置计划日期</text>
        </view>
      </view>

      <!-- 科目列表 -->
      <view class="subjects-section" v-if="subjects.length > 0">
        <view class="section-header">
          <text class="section-title">📚 科目章节</text>
          <view class="add-subject-btn" @click="startAddSubject">+ 添加科目</view>
        </view>
        <view class="subject-list">
          <view class="subject-card" v-for="(subj, idx) in subjects" :key="idx" @click="editSubjectPhase(idx)">
            <view class="subject-header">
              <text class="subject-name">{{ subj.name }}</text>
              <text class="subject-score" v-if="subj.target_score">目标: {{ subj.target_score }}分</text>
            </view>
            <view class="subject-chapters" v-if="subj.chapters && subj.chapters.length > 0">
              <view class="chapter-tags">
                <view class="chapter-tag" v-for="(ch, ci) in subj.chapters" :key="ci">
                  {{ ch.name }}({{ ch.duration || 30 }}分钟/天)
                </view>
              </view>
            </view>
            <view class="subject-actions">
              <text class="action-link" @click.stop="editSubjectPhase(idx)">编辑章节</text>
              <text class="action-link apply-link" @click.stop="applyChaptersToTasks(idx)"
                v-if="subj.chapters && subj.chapters.length > 0">应用到今日任务</text>
            </view>
          </view>
        </view>
      </view>

      <view class="action-buttons">
        <view class="action-btn primary" @click="goToTaskBoard">
          <text class="btn-icon">📋</text>
          <text class="btn-text">今日任务</text>
        </view>
        <view class="action-btn danger" @click="deletePlan">
          <text class="btn-icon">🗑</text>
          <text class="btn-text">删除计划</text>
        </view>
      </view>
    </view>

    <!-- 科目章节编辑弹窗 -->
    <view class="modal-overlay" v-if="showSubjectModal" @click.self="showSubjectModal = false">
      <view class="modal-content chapter-modal">
        <view class="modal-header">
          <text class="modal-title">编辑「{{ editingSubject?.name }}」章节</text>
          <text class="modal-hint">💡 章节的"分钟/天"值会被"应用到今日任务"使用</text>
          <view class="modal-close" @click="showSubjectModal = false">✕</view>
        </view>
        <view class="modal-body">
          <view class="chapter-list">
            <view class="chapter-item" v-for="(ch, ci) in editingChapters" :key="ci">
              <view class="ch-top-row">
                <input class="ch-name" v-model="ch.name" placeholder="章节名" />
                <view class="ch-dur-wrap">
                  <text class="ch-dur-label">分钟/天</text>
                  <input class="ch-dur" v-model.number="ch.duration" type="number" placeholder="30" />
                </view>
                <view class="ch-remove" @click="editingChapters.splice(ci, 1)">✕</view>
              </view>
              <view class="ch-dates-row">
                <view class="ch-date-block planned">
                  <text class="ch-date-tag">📋 计划</text>
                  <picker mode="date" :value="ch.planned_start" @change="onChapterDateChange($event, ch, 'planned_start')">
                    <view class="ch-picker"><text class="ch-picker-text">{{ ch.planned_start || '开始日期' }}</text></view>
                  </picker>
                  <text class="ch-date-arrow">→</text>
                  <picker mode="date" :value="ch.planned_end" @change="onChapterDateChange($event, ch, 'planned_end')">
                    <view class="ch-picker"><text class="ch-picker-text">{{ ch.planned_end || '结束日期' }}</text></view>
                  </picker>
                </view>
                <view class="ch-date-block actual">
                  <text class="ch-date-tag">✅ 实际</text>
                  <picker mode="date" :value="ch.actual_start" @change="onChapterDateChange($event, ch, 'actual_start')">
                    <view class="ch-picker"><text class="ch-picker-text">{{ ch.actual_start || '开始日期' }}</text></view>
                  </picker>
                  <text class="ch-date-arrow">→</text>
                  <picker mode="date" :value="ch.actual_end" @change="onChapterDateChange($event, ch, 'actual_end')">
                    <view class="ch-picker"><text class="ch-picker-text">{{ ch.actual_end || '结束日期' }}</text></view>
                  </picker>
                </view>
              </view>
            </view>
          </view>
          <view class="add-chapter-btn" @click="editingChapters.push({ name:'', duration:30, planned_start:'', planned_end:'', actual_start:'', actual_end:'' })">+ 添加章节</view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showSubjectModal = false">取消</view>
          <view class="submit-btn" @click="saveSubjectPhase">保存</view>
        </view>
      </view>
    </view>

    <!-- 添加科目弹窗 -->
    <view class="modal-overlay" v-if="showAddSubject" @click="showAddSubject = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">添加科目</text>
          <view class="modal-close" @click="showAddSubject = false">✕</view>
        </view>
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">科目名称</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="newSubject.name" placeholder="如：高等数学" />
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">目标分数（选填）</text>
            <view class="input-wrapper">
              <input class="input-field" v-model="newSubject.target_score" type="number" placeholder="选填" />
            </view>
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showAddSubject = false">取消</view>
          <view class="submit-btn" @click="confirmAddSubject">确认添加</view>
        </view>
      </view>
    </view>

    <view class="modal-overlay" v-if="showEmptyState">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">📋</text>
          <view class="modal-close" @click="showEmptyState = false">✕</view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import { dateUtil } from '@/utils/date'
import * as api from '@/api/client'

const planStore = usePlanStore()
const userStore = useUserStore()

const showSubjectModal = ref(false)
const showAddSubject = ref(false)
const showPlanSwitcher = ref(false)
const showPhaseModal = ref(false)
const showEmptyState = ref(false)
const editingSubjectIndex = ref(-1)
const editingChapters = ref([])
const editingPhases = ref([])
const editingPhaseSubject = ref('')
const editingPhaseSubjIdx = ref(-1)
const newSubject = ref({ name: '', target_score: '' })
const allTasks = ref([])
const editDateModal = ref(false)
const ganttMode = ref('both')

const editingSubject = computed(() => {
  if (editingSubjectIndex.value >= 0) return subjects.value[editingSubjectIndex.value]
  return null
})

const subjects = computed(() => {
  const s = planStore.currentPlan?.subjects || []
  // 如果subjects为空但target_scores有数据，自动从target_scores生成
  if (s.length === 0) {
    const scores = planStore.currentPlan?.target_scores || {}
    const keys = Object.keys(scores)
    if (keys.length > 0) {
      return keys.map(name => ({
        name,
        target_score: String(scores[name] || ''),
        chapters: [],
        phases: []
      }))
    }
  }
  return s
})

const totalWeeks = computed(() => {
  if (!planStore.currentPlan) return 0
  const start = new Date(planStore.currentPlan.created_at || Date.now())
  const end = new Date(planStore.currentPlan.exam_date)
  const diffDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
  return Math.max(1, Math.ceil(diffDays / 7))
})

const currentWeek = computed(() => {
  if (!planStore.currentPlan) return 1
  const start = new Date(planStore.currentPlan.created_at || Date.now())
  const now = new Date()
  const diffDays = Math.ceil((now - start) / (1000 * 60 * 60 * 24))
  return Math.max(1, Math.min(totalWeeks.value, Math.ceil(diffDays / 7)))
})

const daysRemaining = computed(() => {
  if (!planStore.currentPlan) return 0
  return dateUtil.getDaysBetween(dateUtil.today(), planStore.currentPlan.exam_date)
})

function getSubjectColor(idx) {
  const colors = ['#4caf50', '#2196f3', '#ff9800', '#9c27b0', '#00bcd4', '#e91e63', '#8bc34a', '#673ab7']
  return colors[idx % colors.length]
}

function parseDate(s) { if (!s) return null; const d = new Date(s); return isNaN(d.getTime()) ? null : d }

// 甘特图日期列
const ganttDayColumns = computed(() => {
  const cols = []
  let minDate = null, maxDate = null
  subjects.value.forEach(s => (s.chapters||[]).forEach(ch => {
    const ps = parseDate(ch.planned_start), pe = parseDate(ch.planned_end)
    const as_ = parseDate(ch.actual_start), ae = parseDate(ch.actual_end)
    ;[ps, pe, as_, ae].forEach(d => {
      if (d) { if (!minDate || d < minDate) minDate = d; if (!maxDate || d > maxDate) maxDate = d }
    })
  }))
  if (!minDate) minDate = new Date(); if (!maxDate) maxDate = new Date(minDate.getTime() + 30*86400000)
  if (maxDate - minDate < 7*86400000) { maxDate = new Date(minDate.getTime() + 30*86400000) }
  if (maxDate - minDate > 365*86400000) { maxDate = new Date(minDate.getTime() + 365*86400000) }

  const d = new Date(minDate)
  const todayStr = new Date().toISOString().split('T')[0]
  while (d <= maxDate) {
    const ds = d.toISOString().split('T')[0]
    cols.push({
      date: ds, day: d.getDate(), month: d.getMonth() + 1,
      isToday: ds === todayStr,
      isWeekStart: d.getDay() === 1,
      showMonth: d.getDate() === 1 || d.getDay() === 1
    })
    d.setDate(d.getDate() + 1)
  }
  return cols
})

// 所有科目章节展平为甘特图行，计算位置百分比
const allChapters = computed(() => {
  const cols = ganttDayColumns.value
  if (cols.length === 0) return []
  const totalDays = cols.length

  const rows = []
  subjects.value.forEach((subj, si) => {
    (subj.chapters||[]).forEach((ch, ci) => {
      const ps = parseDate(ch.planned_start)
      const pe = parseDate(ch.planned_end)
      const as_ = parseDate(ch.actual_start)
      const ae = parseDate(ch.actual_end)

      let planLeft = null, planWidth = null, actualLeft = null, actualWidth = null
      let plannedLabel = '', actualLabel = ''

      if (ps && pe) {
        const startIdx = Math.max(0, Math.round((ps - parseDate(cols[0].date)) / 86400000))
        const endIdx = Math.min(totalDays - 1, Math.round((pe - parseDate(cols[0].date)) / 86400000))
        planLeft = (startIdx / totalDays) * 100
        planWidth = ((endIdx - startIdx + 1) / totalDays) * 100
        const diffDays = Math.round((pe - ps)/86400000)+1
        plannedLabel = diffDays + '天 计划'
      }
      if (as_ && ae) {
        const startIdx = Math.max(0, Math.round((as_ - parseDate(cols[0].date)) / 86400000))
        const endIdx = Math.min(totalDays - 1, Math.round((ae - parseDate(cols[0].date)) / 86400000))
        actualLeft = (startIdx / totalDays) * 100
        actualWidth = ((endIdx - startIdx + 1) / totalDays) * 100
        const diffDays = Math.round((ae - as_)/86400000)+1
        actualLabel = diffDays + '天 实际'
      }

      rows.push({
        ...ch, subjectName: subj.name, subjectIndex: si, chapterIndex: ci,
        isFirstInSubject: ci === 0, color: getSubjectColor(si),
        planLeft, planWidth, plannedLabel, actualLeft, actualWidth, actualLabel
      })
    })
  })
  return rows
})

let ganttClickTimer = null
function editChapterDate(ch) {
  const subj = subjects.value.find(s => s.name === ch.subjectName)
  if (!subj) return
  editingSubjectIndex.value = subjects.value.indexOf(subj)
  editingChapters.value = JSON.parse(JSON.stringify(subj.chapters || []))
  showSubjectModal.value = true
}

async function loadTasks() {
  if (!planStore.currentPlan) return
  try { const tasks = await api.getTasks(planStore.currentPlan.id); allTasks.value = tasks || [] }
  catch (e) { allTasks.value = [] }
}

async function loadPlan() {
  if (!planStore.currentPlan) return
  await planStore.getPlansByUserId(userStore.user.id)
  await loadTasks()
}

function switchToPlan(plan) { planStore.switchPlan(plan.id); showPlanSwitcher.value = false; loadTasks() }
function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) { uni.navigateBack() } else { uni.switchTab({ url: '/pages/profile/profile' }) }
}
function editPlan() { uni.navigateTo({ url: '/pages/plan/target-setup?edit=1' }) }
function goToTaskBoard() { uni.switchTab({ url: '/pages/daily/task-board' }) }

function startAddSubject() { newSubject.value = { name: '', target_score: '' }; showAddSubject.value = true }
async function confirmAddSubject() {
  if (!newSubject.value.name.trim()) return
  const updated = [...subjects.value, { name: newSubject.value.name.trim(), target_score: newSubject.value.target_score || '', chapters: [], phases: [] }]
  await planStore.updatePlan(planStore.currentPlan.id, { subjects: updated })
  showAddSubject.value = false
}

function editSubjectPhase(idx) {
  editingSubjectIndex.value = idx
  editingChapters.value = JSON.parse(JSON.stringify((subjects.value[idx] || {}).chapters || []))
  showSubjectModal.value = true
}

async function saveSubjectPhase() {
  const updated = [...subjects.value]
  updated[editingSubjectIndex.value] = { ...updated[editingSubjectIndex.value], chapters: editingChapters.value }
  await planStore.updatePlan(planStore.currentPlan.id, { subjects: updated })
  showSubjectModal.value = false
  uni.showToast({ title: '保存成功', icon: 'success' })
}

function onChapterDateChange(e, chapter, field) {
  chapter[field] = e.detail.value
}

async function applyChaptersToTasks(subjIdx) {
  const subj = subjects.value[subjIdx]
  if (!subj?.chapters?.length) { uni.showToast({ title: '该科目没有章节', icon: 'none' }); return }
  uni.showModal({
    title: '添加到今日任务',
    content: `将「${subj.name}」的 ${subj.chapters.length} 个章节添加到今日任务？`,
    success: async (res) => {
      if (!res.confirm) return
      uni.showLoading({ title: '添加中...' })
      const today = new Date().toISOString().split('T')[0]
      let added = 0
      for (const ch of subj.chapters) {
        try { await api.createTask({ plan_id: planStore.currentPlan.id, date: today, type: 'new_study', subject: subj.name, content: ch.name, duration: ch.duration || 30, status: 'pending' }); added++ }
        catch (e) { /* skip */ }
      }
      uni.hideLoading()
      uni.showToast({ title: `已添加 ${added} 个任务`, icon: 'success' })
    }
  })
}

async function deletePlan() {
  if (!planStore.currentPlan) return
  uni.showModal({
    title: '删除计划',
    content: '确定删除这个学习计划吗？',
    success: async (res) => {
      if (!res.confirm) return
      await planStore.deletePlan(planStore.currentPlan.id)
      uni.showToast({ title: '删除成功', icon: 'success' })
      setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 1000)
    }
  })
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn && userStore.user) {
    await planStore.getPlansByUserId(userStore.user.id)
    await loadTasks()
  }
})
</script>

<style lang="scss" scoped>
.header { display: flex; align-items: center; justify-content: space-between; padding: 60px 20px 20px;
  .back-btn, .edit-btn { width: 40px; height: 40px; background: $bg2; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    .back-icon, .edit-icon { font-size: 20px; color: $ink; } }
  .page-title { font-size: 20px; font-weight: 600; color: $ink; } }

.switch-section { margin-bottom: 16px; }
.switch-trigger { display: flex; align-items: center; justify-content: space-between; background: $bg2; border-radius: 16px; padding: 14px 18px; border: 1px solid $rule; &:active { background: $soft; } }
.switch-label { font-size: 13px; color: $muted; font-weight: 500; }
.switch-current { display: flex; align-items: center; gap: 6px; }
.switch-current-name { font-size: 14px; color: $accent; font-weight: 600; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.switch-arrow { font-size: 16px; color: $muted; transition: transform 0.2s; &.open { transform: rotate(180deg); } }
.switch-panel { background: $bg2; border-radius: 0 0 16px 16px; border: 1px solid $rule; border-top: none; overflow: hidden; animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
.switch-plan-item { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-top: 1px solid $rule; &:active { background: $soft; } &.active { background: rgba(47,125,79,0.06); } }
.switch-plan-info { flex: 1; min-width: 0; }
.switch-plan-name { display: block; font-size: 14px; color: $ink; font-weight: 500; }
.switch-plan-meta { display: block; font-size: 11px; color: $muted; margin-top: 2px; }
.switch-plan-check { width: 22px; height: 22px; border-radius: 50%; background: $accent; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; margin-left: 10px; }

.plan-card { background: $bg2; border-radius: 20px; padding: 24px; border: 1px solid $rule; }
.plan-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
  .plan-name { font-size: 24px; font-weight: 700; color: $ink; }
  .plan-status { font-size: 12px; padding: 4px 12px; background: $soft; color: $accent; border-radius: 20px; } }
.plan-info { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.info-item { display: flex; align-items: center; gap: 12px;
  .info-icon { font-size: 20px; }
  .info-content { flex: 1;
    .info-label { display: block; font-size: 12px; color: $muted; }
    .info-value { display: block; font-size: 16px; color: $ink; font-weight: 500; &.highlight { color: $accent; font-size: 18px; font-weight: 700; } } } }

/* 甘特图 - 建议电脑端查看 */
.gantt-section {
  margin-bottom: 20px; background: #fff; border-radius: 16px; padding: 20px;
  border: 1px solid #e8ece9; box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  min-height: 200px;
}
.gantt-wrapper {
  width: 100%; max-height: 400px; overflow: auto;
  -webkit-overflow-scrolling: touch;
  border: 1px solid #f0f0f0; border-radius: 8px;
}
.gantt-chart { min-width: 800px; }
.gantt-axis { display: flex; align-items: flex-end; border-bottom: 2px solid #e0e0e0; padding-bottom: 6px; position: sticky; top: 0; left: 0; background: #fff; z-index: 5; }
.gantt-date-row { flex: 1; display: flex; overflow: hidden; }
.gantt-date-col { min-width: 32px; text-align: center; padding: 4px 0;
  &.today { background: rgba(244,67,54,0.08); .gantt-date-num { color: #f44336; font-weight: 700; } }
  &.week-start { border-left: 1px solid #ddd; }
}
.gantt-date-num { display: block; font-size: 11px; color: #999; }
.gantt-date-label { display: block; font-size: 9px; color: #bbb; margin-top: 1px; }

.gantt-chapter-row { display: flex; align-items: stretch; border-bottom: 1px solid #f0f0f0; min-height: 48px;
  &.subject-first { border-top: 2px solid #ddd; }
}
.gantt-hint-text { font-size: 12px; color: #999; }
.gantt-label-col { flex-shrink: 0; width: 120px; padding: 6px 8px; display: flex; flex-direction: column; justify-content: center; overflow: hidden;
  &.gantt-label-wide { width: 120px; }
}
.gantt-subj-name { font-size: 12px; color: #1a1a2e; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gantt-chapter-name { font-size: 11px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gantt-bars-row { flex: 1; display: flex; flex-direction: column;
  &.mode-plan, &.mode-actual { background: #f8f9f8; }
}
.gantt-subrow { flex: 1; position: relative; min-height: 26px; display: flex; align-items: center; padding-left: 4px; }
.gantt-row-tag { font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin-right: 4px; flex-shrink: 0; }
.plan-tag { background: rgba(76,175,80,0.12); color: #2f7d4f; }
.actual-tag { background: rgba(244,67,54,0.1); color: #c62828; }

.gantt-bar {
  position: absolute; top: 3px; bottom: 3px; border-radius: 8px;
  display: flex; align-items: center; padding: 0 8px; cursor: pointer; overflow: hidden;
  min-width: 16px; transition: filter 0.15s;
  &:active { filter: brightness(0.88); }
}
.gantt-bar-planned { box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.gantt-bar-actual { background: #f44336; box-shadow: 0 1px 4px rgba(244,67,54,0.2); }
.gantt-bar-placeholder { position: absolute; left: 0; right: 0; top: 3px; bottom: 3px; display: flex; align-items: center; padding-left: 8px; cursor: pointer; }
.gantt-bar-label { font-size: 11px; color: #fff; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gantt-bar-ph { font-size: 10px; color: #ccc; }

/* 切换按钮 */
.gantt-toggle { display: flex; background: #f0f0f0; border-radius: 10px; padding: 2px; gap: 2px; }
.toggle-opt { padding: 4px 12px; border-radius: 8px; font-size: 12px; color: #888; font-weight: 500; transition: all 0.2s;
  &.active { background: #fff; color: #1a1a2e; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
}
.gantt-bar-weeks { display: none; }

.gantt-empty { padding: 40px; text-align: center; }
.gantt-empty-text { font-size: 14px; color: #999; line-height: 1.6; }
.gantt-hint { text-align: center; padding: 8px; font-size: 11px; color: #bbb; }

/* 阶段编辑弹窗 */
.phase-edit-list { display: flex; flex-direction: column; gap: 10px; }
.phase-edit-item { background: #f5f7f5; border-radius: 10px; padding: 10px; }
.phase-edit-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.phase-name-input { flex: 1; min-width: 80px; padding: 12px 14px; border: 1.5px solid #d0d5d2; border-radius: 10px; font-size: 16px; background: #fff;
  :deep(.uni-input-input) { font-size: 16px; } }
.phase-week-inputs { display: flex; align-items: center; gap: 4px; }
.phase-week-label { font-size: 13px; color: #999; }
.phase-week-num { width: 48px; padding: 10px 6px; border: 1.5px solid #d0d5d2; border-radius: 8px; font-size: 15px; text-align: center; background: #fff; }
.phase-color-input { width: 30px; height: 30px; border: none; border-radius: 6px; cursor: pointer; padding: 0; }
.phase-remove { font-size: 16px; color: #ef5350; padding: 4px; }
.add-phase-btn { padding: 10px; text-align: center; border: 1.5px dashed #d0d5d2; border-radius: 10px; font-size: 14px; color: $accent; }

/* 科目章节 */
.subjects-section { margin-bottom: 20px;
  .section-title { font-size: 14px; color: $muted; }
  .add-subject-btn { font-size: 13px; color: $accent; } }
.subject-list { display: flex; flex-direction: column; gap: 10px; }
.subject-card { background: $soft; border-radius: 12px; padding: 14px;
  .subject-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
  .subject-name { font-size: 15px; font-weight: 600; color: $ink; }
  .subject-score { font-size: 12px; color: $accent; }
  .chapter-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
  .chapter-tag { font-size: 12px; padding: 6px 10px; background: $bg2; border-radius: 8px; color: $ink; }
  .subject-actions { margin-top: 8px; display: flex; gap: 12px; }
  .action-link { font-size: 12px; color: $accent; }
  .apply-link { color: #ef5350; font-weight: 500; } }

/* 按钮 */
.action-buttons { display: flex; gap: 12px; margin-top: 20px; }
.action-btn { flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 14px; border-radius: 12px;
  &.primary { background: $accent; .btn-icon, .btn-text { color: #fff; } }
  &.danger { background: #ffebee; .btn-icon, .btn-text { color: #c62828; } }
  .btn-icon { font-size: 16px; } .btn-text { font-size: 15px; font-weight: 500; } }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-content { background: #fff; border-radius: 20px; width: 100%; max-width: 520px; max-height: 80vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch; position: relative; z-index: 1; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: $accent; font-weight: 600; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
/* 章节编辑弹窗 */
.modal-hint { font-size: 11px; color: #888; margin-left: 8px; flex: 1; }
.chapter-modal { max-width: 500px; }
.chapter-list { display: flex; flex-direction: column; gap: 12px; }
.chapter-item {
  background: #fff; border: 1.5px solid #e8ece9; border-radius: 16px; padding: 18px; margin-bottom: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.ch-top-row { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.ch-name { flex: 1; padding: 12px 14px; border: 1.5px solid #d0d5d2; border-radius: 12px; font-size: 16px; background: #fff; color: #1a1a2e; min-width: 0; :deep(.uni-input-input) { height: 24px; line-height: 24px; } :deep(.uni-input-wrapper) { min-height: 24px; }
  &:active, &:focus { border-color: $accent; } }
.ch-dur-wrap { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.ch-dur-label { font-size: 12px; color: #888; white-space: nowrap; }
.ch-dur { width: 56px; padding: 12px 6px; border: 1.5px solid #d0d5d2; border-radius: 12px; font-size: 16px; background: #fff; color: #1a1a2e; text-align: center; :deep(.uni-input-input) { height: 24px; line-height: 24px; } :deep(.uni-input-wrapper) { min-height: 24px; }
  &:focus { border-color: $accent; } }
.ch-remove { font-size: 22px; color: #ef5350; padding: 6px 4px; flex-shrink: 0; cursor: pointer; }

.ch-dates-row { display: flex; flex-direction: column; gap: 8px; }
.ch-date-block { display: flex; align-items: center; gap: 4px; }
.ch-date-tag { font-size: 13px; font-weight: 600; min-width: 44px; white-space: nowrap;
  .ch-date-block.planned & { color: #2f7d4f; }
  .ch-date-block.actual & { color: #c62828; }
}
.ch-date-arrow { font-size: 14px; color: #ccc; flex-shrink: 0; }
.ch-picker {
  flex: 1; padding: 10px 6px; border: 1.5px solid #d0d5d2; border-radius: 10px;
  font-size: 14px; background: #fafafa; color: #1a1a2e; text-align: center; min-width: 72px;
  overflow: hidden; position: relative;
}
.ch-picker-text {
  position: relative; z-index: 1; background: inherit;
  display: block; width: 100%; text-align: center;
}

.add-chapter-btn { padding: 16px; text-align: center; border: 2px dashed #d0d5d2; border-radius: 14px; font-size: 16px; color: $accent; font-weight: 500; margin-top: 10px; }

.bottom-space { height: 60px; }
</style>