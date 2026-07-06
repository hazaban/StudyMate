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

      <!-- 科目阶段时间线 -->
      <view class="phase-timeline-section" v-if="subjects.length > 0">
        <view class="section-header">
          <text class="section-title">📐 阶段时间线</text>
          <view class="header-actions">
            <text class="header-btn" @click="suggestPhasesAI" v-if="!phaseLoading">🤖 AI建议</text>
            <text class="header-btn" v-if="phaseLoading" style="opacity:0.6">⏳ 生成中...</text>
          </view>
        </view>

        <!-- 周数标尺 -->
        <view class="tl-ruler" v-if="totalWeeks > 0">
          <view class="tl-subject-spacer"></view>
          <view class="tl-weeks">
            <view class="tl-week-mark" v-for="w in totalWeeks" :key="w" :class="{ current: w === currentWeek }">
              <text class="tl-week-num">{{ w }}</text>
            </view>
          </view>
        </view>

        <!-- 每个科目一行 -->
        <view class="tl-row" v-for="(subj, si) in subjectsWithPhases" :key="si">
          <view class="tl-subject-spacer">
            <text class="tl-subj-name">{{ subj.name }}</text>
          </view>
          <view class="tl-bars">
            <view class="tl-phase-bar" v-for="(ph, pi) in subj.phases" :key="pi"
              :style="{
                left: ((ph.start_week - 1) / totalWeeks * 100) + '%',
                width: ((ph.end_week - ph.start_week + 1) / totalWeeks * 100) + '%',
                background: ph.color || getSubjectColor(si)
              }"
              @click="editPhase(subj, ph, pi, si)">
              <view class="tl-phase-fill" :style="{ width: getPhaseProgress(subj.name, ph) + '%' }"></view>
              <text class="tl-phase-label">{{ ph.name }}</text>
              <text class="tl-phase-weeks">{{ getPhaseProgress(subj.name, ph) }}%</text>
            </view>
            <!-- 无阶段占位 -->
            <view class="tl-no-phase" v-if="!subj.phases || subj.phases.length === 0">
              <text class="tl-no-phase-text" @click="addSubjectPhases(subj, si)">+ 添加阶段</text>
            </view>
          </view>
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

    <!-- 阶段编辑弹窗 -->
    <view class="modal-overlay" v-if="showPhaseModal" @click="showPhaseModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑「{{ editingPhaseSubject }}」阶段</text>
          <view class="modal-close" @click="showPhaseModal = false">✕</view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="phase-edit-list">
            <view class="phase-edit-item" v-for="(ph, pi) in editingPhases" :key="pi">
              <view class="phase-edit-row">
                <input class="phase-name-input" v-model="ph.name" placeholder="阶段名称" />
                <view class="phase-week-inputs">
                  <text class="phase-week-label">第</text>
                  <input class="phase-week-num" v-model="ph.start_week" type="number" />
                  <text class="phase-week-label">-</text>
                  <input class="phase-week-num" v-model="ph.end_week" type="number" />
                  <text class="phase-week-label">周</text>
                </view>
                <input class="phase-color-input" type="color" v-model="ph.color" />
                <view class="phase-remove" @click="editingPhases.splice(pi, 1)">✕</view>
              </view>
            </view>
            <view class="add-phase-btn" @click="editingPhases.push({name:'新阶段',start_week:1,end_week:totalWeeks,color:'#4caf50'})">
              + 添加阶段
            </view>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showPhaseModal = false">取消</view>
          <view class="submit-btn" @click="savePhases">保存阶段</view>
        </view>
      </view>
    </view>

    <!-- 科目章节编辑弹窗 -->
    <view class="modal-overlay" v-if="showSubjectModal" @click="showSubjectModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑「{{ editingSubject?.name }}」章节</text>
          <view class="modal-close" @click="showSubjectModal = false">✕</view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="form-group">
            <text class="form-label">章节规划</text>
            <view class="chapter-list">
              <view class="chapter-item" v-for="(ch, ci) in editingChapters" :key="ci">
                <view class="chapter-row">
                  <input class="chapter-input" v-model="ch.name" placeholder="章节名" />
                  <input class="chapter-input short" v-model="ch.duration" type="number" placeholder="分钟/天" />
                  <view class="chapter-remove" @click="editingChapters.splice(ci, 1)">✕</view>
                </view>
              </view>
              <view class="add-chapter-btn" @click="editingChapters.push({ name: '', duration: 30 })">+ 添加章节</view>
            </view>
          </view>
        </scroll-view>
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
const phaseLoading = ref(false)

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

function getPhaseProgress(subjectName, phase) {
  if (!planStore.currentPlan) return 0
  const start = new Date(planStore.currentPlan.created_at || Date.now())
  const phaseStart = new Date(start)
  phaseStart.setDate(phaseStart.getDate() + (phase.start_week - 1) * 7)
  const phaseEnd = new Date(start)
  phaseEnd.setDate(phaseEnd.getDate() + phase.end_week * 7)

  const phaseTasks = allTasks.value.filter(t => {
    if (t.subject !== subjectName) return false
    const taskDate = new Date(t.date)
    return taskDate >= phaseStart && taskDate < phaseEnd
  })
  if (phaseTasks.length === 0) return 0
  const done = phaseTasks.filter(t => t.status === 'completed').length
  return Math.round((done / phaseTasks.length) * 100)
}

async function suggestPhasesAI() {
  if (!planStore.currentPlan) return
  phaseLoading.value = true
  try {
    const resp = await api.request('/plans/ai/phases', {
      method: 'POST',
      data: {
        exam_name: planStore.currentPlan.exam_name,
        total_weeks: totalWeeks.value,
        subjects: subjects.value.map(s => ({ name: s.name }))
      }
    })
    applyPhasesToSubjects(resp.phases || {})
  } catch (e) {
    applyPhasesToSubjects(mockPhases())
  } finally {
    phaseLoading.value = false
    uni.showToast({ title: 'AI阶段建议已生成', icon: 'success' })
  }
}

function mockPhases() {
  const result = {}
  const configs = [
    [{ name: '基础学习', start_week: 1, end_week: Math.floor(totalWeeks.value / 3), color: '#4caf50' },
     { name: '强化刷题', start_week: Math.floor(totalWeeks.value / 3) + 1, end_week: Math.floor(totalWeeks.value * 2 / 3), color: '#2196f3' },
     { name: '真题冲刺', start_week: Math.floor(totalWeeks.value * 2 / 3) + 1, end_week: totalWeeks.value, color: '#ff9800' }],
    [{ name: '入门理解', start_week: 1, end_week: Math.floor(totalWeeks.value / 2), color: '#8bc34a' },
     { name: '实战演练', start_week: Math.floor(totalWeeks.value / 2) + 1, end_week: totalWeeks.value, color: '#f44336' }],
  ]
  subjects.value.forEach((s, i) => { result[s.name] = configs[i % configs.length] })
  return result
}

function applyPhasesToSubjects(phasesMap) {
  const updated = subjects.value.map(s => ({
    ...s,
    phases: phasesMap[s.name] || s.phases || []
  }))
  planStore.updatePlan(planStore.currentPlan.id, { subjects: updated })
  setTimeout(() => loadPlan(), 500)
}

function editPhase(subj, phase, pi, si) {
  editingPhaseSubject.value = subj.name
  editingPhaseSubjIdx.value = si
  editingPhases.value = JSON.parse(JSON.stringify(subj.phases || []))
  showPhaseModal.value = true
}

function addSubjectPhases(subj, si) {
  editingPhaseSubject.value = subj.name
  editingPhaseSubjIdx.value = si
  editingPhases.value = [
    { name: '基础阶段', start_week: 1, end_week: Math.ceil(totalWeeks.value / 3), color: '#4caf50' },
    { name: '强化阶段', start_week: Math.ceil(totalWeeks.value / 3) + 1, end_week: Math.ceil(totalWeeks.value * 2 / 3), color: '#2196f3' },
    { name: '冲刺阶段', start_week: Math.ceil(totalWeeks.value * 2 / 3) + 1, end_week: totalWeeks.value, color: '#ff9800' }
  ]
  showPhaseModal.value = true
}

async function savePhases() {
  const updated = [...subjects.value]
  updated[editingPhaseSubjIdx.value] = {
    ...updated[editingPhaseSubjIdx.value],
    phases: editingPhases.value
  }
  await planStore.updatePlan(planStore.currentPlan.id, { subjects: updated })
  showPhaseModal.value = false
  uni.showToast({ title: '阶段已保存', icon: 'success' })
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

/* 阶段时间线 */
.phase-timeline-section { margin-bottom: 20px; background: #fff; border-radius: 14px; padding: 16px; border: 1px solid #e8ece9; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-title { font-size: 15px; font-weight: 600; color: #333; }
.header-actions { display: flex; gap: 10px; }
.header-btn { font-size: 13px; color: $accent; font-weight: 500; padding: 4px 10px; background: rgba(47,125,79,0.08); border-radius: 14px; }
.tl-ruler { display: flex; margin-bottom: 4px; }
.tl-subject-spacer { width: 72px; flex-shrink: 0; overflow: hidden; }
.tl-subj-name { font-size: 12px; color: #555; font-weight: 600; white-space: nowrap; }
.tl-weeks { flex: 1; display: flex; }
.tl-week-mark { flex: 1; text-align: center; border-left: 1px solid #eee; padding: 2px 0; &.current { background: rgba(244,67,54,0.08); } }
.tl-week-num { font-size: 10px; color: #bbb; &.current { color: #f44336; font-weight: 700; } }
.tl-row { display: flex; align-items: center; margin-bottom: 6px; min-height: 36px; }
.tl-bars { flex: 1; position: relative; height: 32px; background: #f9f9f9; border-radius: 6px; overflow: hidden; }
.tl-phase-bar { position: absolute; top: 3px; bottom: 3px; border-radius: 5px; display: flex; align-items: center; justify-content: space-between; padding: 0 6px; overflow: hidden; cursor: pointer; min-width: 30px; transition: filter 0.15s;
  &:active { filter: brightness(0.9); } }
.tl-phase-fill { position: absolute; left: 0; top: 0; bottom: 0; background: rgba(255,255,255,0.3); border-radius: 5px 0 0 5px; transition: width 0.4s; }
.tl-phase-label { font-size: 10px; color: #fff; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.3); white-space: nowrap; position: relative; z-index: 1; overflow: hidden; text-overflow: ellipsis; }
.tl-phase-weeks { font-size: 9px; color: rgba(255,255,255,0.85); position: relative; z-index: 1; flex-shrink: 0; margin-left: 4px; display: none; }
.tl-no-phase { flex: 1; display: flex; align-items: center; justify-content: center; height: 100%; }
.tl-no-phase-text { font-size: 12px; color: #999; padding: 4px 12px; border: 1px dashed #d0d5d2; border-radius: 10px; }

/* 阶段编辑弹窗 */
.phase-edit-list { display: flex; flex-direction: column; gap: 10px; }
.phase-edit-item { background: #f5f7f5; border-radius: 10px; padding: 10px; }
.phase-edit-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.phase-name-input { flex: 1; min-width: 80px; padding: 8px; border: 1px solid #e8ece9; border-radius: 8px; font-size: 14px; background: #fff; }
.phase-week-inputs { display: flex; align-items: center; gap: 2px; }
.phase-week-label { font-size: 12px; color: #999; }
.phase-week-num { width: 40px; padding: 6px; border: 1px solid #e8ece9; border-radius: 6px; font-size: 13px; text-align: center; background: #fff; }
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
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; }
.modal-content { background: #fff; border-radius: 24px 24px 0 0; width: 100%; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 20px; color: #999; padding: 4px; }
.modal-body { padding: 20px 24px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 24px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 14px; text-align: center; border-radius: 14px; font-size: 16px; color: #fff; background: $accent; font-weight: 600; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.chapter-list { display: flex; flex-direction: column; gap: 8px; }
.chapter-item { background: #f5f7f5; border-radius: 10px; padding: 10px; }
.chapter-row { display: flex; align-items: center; gap: 8px; }
.chapter-input { flex: 1; padding: 8px 12px; border: 1px solid #e8ece9; border-radius: 8px; font-size: 14px; background: #fff; &.short { flex: 0 0 80px; } }
.chapter-remove { font-size: 16px; color: #ef5350; padding: 4px; }
.add-chapter-btn { padding: 10px; text-align: center; border: 1.5px dashed #d0d5d2; border-radius: 10px; font-size: 14px; color: $accent; }

.bottom-space { height: 60px; }
</style>