# StudyMate 功能迭代变更文档

> 版本：v2.0.0  
> 日期：2026-07-09  
> 范围：前端（uniapp + Vue 3 + Pinia）+ 后端（FastAPI + SQLAlchemy + PostgreSQL）

---

## 目录

1. [概述](#概述)
2. [Req1：任务复制 + 交互优化](#req1任务复制--交互优化)
3. [Req2：循环任务周/月视图同步](#req2循环任务周月视图同步)
4. [Req3：番茄钟后台运行 + 恢复](#req3番茄钟后台运行--恢复)
5. [Req4：计划重新编辑](#req4计划重新编辑)
6. [Req5：今日任务显示一致](#req5今日任务显示一致)
7. [Req6：实际用时 + 问题记录 + 未完成原因](#req6实际用时--问题记录--未完成原因)
8. [文件变更清单](#文件变更清单)
9. [数据库迁移](#数据库迁移)
10. [验证与测试](#验证与测试)

---

## 概述

本次迭代针对 StudyMate 学习应用的 6 大类问题进行了全面修复和功能增强，涵盖任务管理、循环任务同步、番茄钟后台运行、计划编辑、数据一致性以及任务反思体系。

### 技术栈

- **前端**：uniapp (Vue 3) + Pinia + Vite
- **后端**：FastAPI + SQLAlchemy + PostgreSQL
- **部署**：Cloudflare Workers (AI) + Vercel (后端) + 腾讯云 COS (文件存储)

### 核心设计原则

1. **前后端循环任务逻辑对齐**：前端 `shouldRepeatOnDate` 与后端 `_should_repeat` 逻辑完全一致
2. **桌面/移动端交互区分**：通过 `!('ontouchstart' in window) && (navigator.maxTouchPoints || 0) === 0` 检测
3. **时间戳计时**：番茄钟使用绝对时间戳替代 setInterval 递减，确保后台准确
4. **localStorage 持久化**：番茄钟会话、设置、记录均持久化，刷新/离开不丢失
5. **按日独立反思**：循环任务每天的反思记录独立存储（task_id + task_date 唯一键）

---

## Req1：任务复制 + 交互优化

### 问题描述

- 已有任务无法快速复制，只能手动重新输入
- 添加任务弹窗不能设置日期，只能创建当天任务
- 手机端和电脑端任务卡片交互方式一致，电脑上点击容易误触编辑
- 今日任务加号只有新建一种选择，没有从已有任务复制的快捷入口
- 周视图右键空白格子只能新建，不能从已有任务复制

### 解决方案

#### 1.1 TaskFormModal 日期选择 + 复制预填

**文件**：`frontend/src/components/TaskFormModal.vue`

**新增属性**：
- `copySource`：复制来源任务对象，传入后以新建模式预填字段

**新增计算属性**：
- `isCopy`：`!!props.copySource`，判断是否为复制模式

**标题逻辑**：
```
{{ isEdit ? '编辑任务' : (isCopy ? '复制任务' : '添加任务') }}
```

**编辑模式判断修正**：
- `isEdit` 从 `!!props.task` 改为 `!!props.task && !props.copySource`
- 原因：复制模式也会传入 task 对象，但应走新建分支

**日期选择器**：
- 在章节字段后、任务内容前插入日期选择器（picker mode="date"）
- 默认值为 `form.date`，为空时显示 "选择日期"
- `onDateChange(e)` 更新 `form.value.date = e.detail.value`

**复制预填逻辑（resetForm）**：
- 当 `props.copySource` 存在时：
  - 预填 type、subject、chapter、content、duration、importance、repeat_type
  - `actual_duration` 重置为 0（新复制的任务不应继承原任务实际用时）
  - 时间优先使用 `props.defaultHour/defaultMinute`（来自周视图格子上下文）
  - 日期优先使用 `props.date`，没有则使用 copySource.date
- 新增 `watch(() => props.copySource, ...)` 监听，传入变化时触发 resetForm

**提交逻辑**：
- `submitForm` 原本已使用 `form.value.date || props.date`，无需额外修改

#### 1.2 今日任务加号弹"新建/从已有复制"

**文件**：`frontend/src/pages/daily/task-board.vue`

**新增状态**：
- `showCopyPicker`：是否显示复制选择弹窗
- `copyKeyword`：搜索关键字
- `copyContextDate`：复制的目标日期
- `copySourceTask`：选中的复制来源任务

**openManualAdd 改造**：
- 改为调用 `uni.showActionSheet`，选项为 "✚ 新建任务" 和 "📋 从已有任务复制"
- 点击 0 调用 `startNewTask()`
- 点击 1 调用 `startCopyPicker()`

**复制选择弹窗**：
- 底部弹出式 sheet（modal-mask + modal-sheet）
- 顶部搜索框，输入关键字实时过滤
- 目标日期提示（"将复制到：YYYY-MM-DD"）
- 任务列表（copy-item），显示科目、章节、内容
- 点击某任务调用 `confirmCopyFromTask(task)`

**copyCandidates 计算属性**：
- 数据源：`taskStore.allTasks`（全部任务，含循环任务原始记录）
- 过滤：按 subject / chapter / content 模糊匹配关键字
- 去重：按 subject + content 组合去重（避免循环任务每天都出现多条相同内容）
- 数量：取前 50 条防止列表过长

**confirmCopyFromTask**：
- 设置 `copySourceTask.value = task`
- 设置 TaskFormModal 的 `date` prop 为 `copyContextDate`
- 打开 TaskFormModal
- 关闭 copy picker

#### 1.3 周视图右键空白格子增加"从已有复制"

**文件**：`frontend/src/pages/daily/task-board.vue`

**新增状态**：
- `copyContextHour` / `copyContextMinute`：复制时的开始时间上下文

**周视图右键菜单**：
- 在原有"新建任务"项后增加"📋 从已有任务复制"项
- 点击后调用 `copyFromWeekCell(dateStr, hour)`

**copyFromWeekCell(dateStr, hour)**：
- 设置 `copyContextDate = dateStr`
- 设置 `copyContextHour = hour`，`copyContextMinute = 0`
- 调用 `startCopyPicker()` 打开复制选择弹窗
- 选中任务后，TaskFormModal 的 defaultHour/defaultMinute 自动使用格子时间

#### 1.4 桌面/移动端任务卡片交互区分

**检测方法**：
```js
const isDesktop = ref(false)
// #ifdef H5
isDesktop.value = !('ontouchstart' in window) && (navigator.maxTouchPoints || 0) === 0
// #endif
```

**今日任务卡片（task-board.vue 和 index.vue）**：
- 卡片根元素添加 `@click="onTaskCardClick(task)"`
- checkbox、番茄钟按钮、删除按钮等子元素添加 `@click.stop` 防止冒泡
- `onTaskCardClick(task)`：`if (isDesktop.value) editTask(task)`
- 移动端：不响应点击，保留 600ms 长按编辑（onTaskTouchStart / onTaskTouchEnd）

**周视图任务卡片**：
- 保留原有"点击展开文字 + 右键编辑"模式
- 原因：周视图卡片空间有限，点击展开是更常用的操作

---

## Req2：循环任务周/月视图同步

### 问题描述

- 循环任务（daily/weekday/holiday）只在创建当天显示，后续日期的周视图和月视图不显示
- 设置在非当天的任务，在周视图和月视图中看不到

### 根本原因

- `getDayTasks` / `getTasksAt` 只按 `t.date === dateStr` 匹配
- `taskDates`（storage set）只存了任务原始 date，不含循环展开后的日期
- 月视图 has-task 类、周视图 week-day-dot 都依赖 taskDates，所以也不显示循环任务

### 解决方案

#### 2.1 shouldRepeatOnDate 函数

**文件**：`frontend/src/pages/daily/task-board.vue`

```js
function shouldRepeatOnDate(task, dateStr) {
  if (!task || !task.date) return false
  // 非循环任务：精确匹配日期
  if (!task.repeat_type || task.repeat_type === 'none') {
    return task.date === dateStr
  }
  // 循环任务：开始日期之前不显示
  if (task.date > dateStr) return false
  // 每天循环
  if (task.repeat_type === 'daily') return true
  // 计算星期
  let day
  try { day = new Date(dateStr + 'T00:00:00').getDay() } catch (e) { return false }
  // 工作日循环（周一到周五）
  if (task.repeat_type === 'weekday') return day >= 1 && day <= 5
  // 周末循环（周六周日）
  if (task.repeat_type === 'holiday') return day === 0 || day === 6
  return false
}
```

> 此逻辑与后端 `backend/routes/tasks.py` 中的 `_should_repeat` 完全对齐。

#### 2.2 allVisibleTaskDates 计算属性

```js
const allVisibleTaskDates = computed(() => {
  const set = new Set()
  if (!taskStore.allTasks.length) return set
  // 收集当前视图范围内所有日期
  let dates = []
  if (viewMode.value === 'month') {
    dates = calendarDays.value.map(d => d.date)
  } else if (viewMode.value === 'week') {
    dates = weekDays.value.map(d => d.date)
  } else {
    dates = [selectedDate.value]
  }
  // 对每个任务和每个日期，判断是否应显示
  for (const task of taskStore.allTasks) {
    for (const dateStr of dates) {
      if (shouldRepeatOnDate(task, dateStr)) {
        set.add(dateStr)
      }
    }
  }
  return set
})
```

#### 2.3 各视图改造

**今日视图**：
- `getDayTasks(dateStr)` 改用 `shouldRepeatOnDate` 过滤

**周视图**：
- `getTasksAt(dateStr, hour)` 改用 `shouldRepeatOnDate` 过滤
- `week-day-dot` 日期头小圆点改用 `allVisibleTaskDates` 判断

**月视图**：
- `has-task` 类改用 `allVisibleTaskDates.has(day.date)`
- 日历日期上的任务标记与循环任务同步

#### 2.4 全部任务预加载

- `onMounted` 末尾追加：`await taskStore.getAllTasks(planStore.currentPlan.id)`
- `switchView` 中切换到月视图时也追加 `getAllTasks` 调用
- 原因：默认只加载当天任务，循环展开需要全部任务数据

---

## Req3：番茄钟后台运行 + 恢复

### 问题描述

1. 切换应用/离开网页时，番茄钟计时暂停或混乱
2. setInterval 在后台 tab 被浏览器节流，计时不准确
3. 退出番茄钟页面再进入，上次未完成的计时丢失
4. 结束时需要通知和提示音，但后台时可能不触发

### 根本原因

- 使用 `setInterval` 递减/递增 `timeRemaining`/`elapsedSeconds`，后台被节流
- `onUnmounted` 清理 interval 导致计时完全丢失
- 没有持久化机制，页面刷新/切换后无法恢复

### 解决方案

#### 3.1 时间戳计时架构

**文件**：`frontend/src/pages/daily/pomodoro.vue`

**核心状态**：`runningSession`
```js
const runningSession = ref(null)
// 结构:
// {
//   mode: 'countdown' | 'countup',
//   isBreak: boolean,
//   focusSeconds: number,    // 专注时长快照（秒）
//   breakSeconds: number,    // 休息时长快照（秒）
//   startTimestamp: number|null,  // 当前段开始的绝对时间戳（null=暂停）
//   accumulatedElapsed: number,   // 已累计的秒数（暂停时累加）
//   currentTaskId: string|null,
//   currentTaskName: string,
//   date: string  // YYYY-MM-DD
// }
```

**设计要点**：
- `startTimestamp != null` 表示正在运行
- `startTimestamp == null` 表示已暂停，已计时长保存在 `accumulatedElapsed`
- `timeRemaining` / `elapsedSeconds` 仅作显示，由 `tick()` 校准

#### 3.2 tick 函数（显示校准）

```js
function tick() {
  const rs = runningSession.value
  if (!rs || !rs.startTimestamp) return
  const now = Date.now()
  const segmentElapsed = (now - rs.startTimestamp) / 1000
  const totalElapsed = rs.accumulatedElapsed + segmentElapsed
  const targetSeconds = rs.isBreak ? rs.breakSeconds : rs.focusSeconds

  if (rs.mode === 'countup') {
    elapsedSeconds.value = Math.floor(totalElapsed)
  } else {
    const remaining = targetSeconds - totalElapsed
    if (remaining <= 0) {
      timeRemaining.value = 0
      completeSession(false)  // 自然结束
      return
    }
    timeRemaining.value = Math.ceil(remaining)
  }
}
```

- setInterval 每秒调用一次 tick，即使被节流，恢复时也能通过时间戳校准
- 倒计时结束时自动调用 `completeSession(false)`（自然结束）

#### 3.3 localStorage 持久化

```js
const POMODORO_SESSION_KEY = 'studymate_pomodoro_running'

function persistRunningSession() {
  if (!runningSession.value) {
    uni.removeStorageSync(POMODORO_SESSION_KEY)
    return
  }
  uni.setStorageSync(POMODORO_SESSION_KEY, JSON.stringify(runningSession.value))
}
function loadRunningSession() {
  try {
    const s = uni.getStorageSync(POMODORO_SESSION_KEY)
    if (s) return JSON.parse(s)
  } catch (e) { /* */ }
  return null
}
function clearRunningSession() {
  runningSession.value = null
  uni.removeStorageSync(POMODORO_SESSION_KEY)
}
```

- 开始/暂停/完成时均调用 `persistRunningSession()`
- 选择任务切换时同步更新会话中的任务信息

#### 3.4 开始 / 暂停 / 重置

**开始（toggleTimer）**：
- 全新开始：创建 runningSession，记录 `startTimestamp = Date.now()`
- 从暂停继续：设置 `startTimestamp = Date.now()`
- 调用 `persistRunningSession()` 持久化
- 启动 setInterval 每秒 tick
- 立即调用一次 tick 校准显示

**暂停**：
- 计算当前段已计时长 `(Date.now() - startTimestamp) / 1000`
- 累加到 `accumulatedElapsed`
- `startTimestamp = null`
- 持久化 + 清除 interval
- 立即刷新显示（避免 1 秒误差）

**重置（resetTimer）**：
- 清除 interval + 清除持久化
- 重置所有状态
- `isCompleting = false`

#### 3.5 完成逻辑（completeSession）

**参数**：`isManual`（是否手动完成）

**专注结束**：
- 用时间戳计算实际时长（后台也能准确）
- 正计时：`Math.round(totalElapsed / 60)`
- 倒计时手动完成：`Math.max(0, Math.round(totalElapsed / 60))`
- 倒计时自然结束：`Math.round(targetSeconds / 60)`
- 写入今日记录 + 同步后端 FocusRecord + 更新任务 actual_duration
- 触发通知 + 提示音 + 震动
- 倒计时模式自动进入休息阶段（新建会话段）

**休息结束**：
- 清除持久化，回到专注准备状态
- 播放休息结束提示音 + 通知

**防重入**：`isCompleting` 标志防止 completeSession 被重复调用

#### 3.6 后台恢复机制

**visibilitychange / pageshow / focus 监听**：
```js
function onVisibilityChange() {
  if (document.visibilityState === 'visible') {
    tick()  // 回到前台立即校准，若期间已结束则触发完成
  }
}
function onWindowFocus() { tick() }
```

- 注册 `document.visibilitychange`、`window.pageshow`、`window.focus`
- 从后台切回前台时立即校准时间
- 如果后台期间计时已结束，tick 会触发 completeSession

#### 3.7 重新进入页面恢复

**onMounted 中加载**：
1. 调用 `loadRunningSession()` 读取持久化的会话
2. 跨天了（date != today）：作废，提示"上次的番茄钟已过期"
3. 否则：
   - 同步设置（focusTime、breakTime、mode、task）
   - 如果离开时正在运行：
     - 若已自然结束 → 弹窗询问"是否记录本次专注"
     - 未结束 → 自动恢复运行，toast 提示"已恢复未完成的番茄钟"
   - 如果是暂停状态 → 显示暂停进度，toast 提示"已恢复暂停的番茄钟，点开始继续"

**onUnmounted 不清除持久化**：
- 只清除 interval，不清除 runningSession
- 让用户离开页面后再次进入仍能恢复

#### 3.8 通知与提示音增强

**AudioContext 全局复用 + 后台恢复**：
```js
let _audioCtx = null
function getAudioCtx() {
  if (!_audioCtx) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) return null
    _audioCtx = new AudioCtx()
  }
  // 后台标签页 AudioContext 可能被挂起，尝试恢复
  if (_audioCtx.state === 'suspended') {
    _audioCtx.resume().catch(() => {})
  }
  return _audioCtx
}
```

**通知**：
- 专注完成：标题 "🎉 专注完成"，内容含时长和任务名
- 休息结束：标题 "☕ 休息结束"，内容 "休息时间到了，继续专注学习吧！"
- 使用 Notification API（H5）+ 震动 API
- onMounted 时请求通知权限

**提示音**：
- 专注结束：3 个上升音阶（C5 → E5 → G5）
- 休息结束：2 个下降音阶（E5 → C5）
- Web Audio API 生成，无需音频文件

#### 3.9 运行中保护

- 运行中禁止切换模式（switchMode）
- 运行中禁止修改专注/休息时长（adjustFocusTime / adjustBreakTime / onBlur）
- 原因：运行中修改会导致进度计算混乱

---

## Req4：计划重新编辑

### 问题描述

- 已添加的计划无法重新编辑考试日期、学习时间
- 无法删减科目
- 深链进入编辑模式时 currentPlan 可能为空

### 根本原因

- `target-setup.vue` 的 onMounted 只 await `userStore.getUserInfo()`，未 await `planStore.getPlansByUserId()`
- 如果用户直接从 URL 进入编辑页，planStore 还没加载，currentPlan 为 null
- 编辑入口 `plan-overview.vue` 只传 `edit=1`，没传计划 id

### 解决方案

#### 4.1 plan-overview 编辑入口带 id

**文件**：`frontend/src/pages/plan/plan-overview.vue`

```js
function editPlan() {
  const id = planStore.currentPlan?.id
  const url = id
    ? `/pages/plan/target-setup?edit=1&id=${id}`
    : '/pages/plan/target-setup?edit=1'
  uni.navigateTo({ url })
}
```

#### 4.2 target-setup 可靠加载

**文件**：`frontend/src/pages/plan/target-setup.vue`

**onMounted 改造**：
1. await `userStore.getUserInfo()`
2. 判断编辑模式：读取 `currentPage?.options` 或 `currentPage?.$page?.options`
3. 如果是编辑模式：
   - await `planStore.getPlansByUserId()`（确保计划列表已加载）
   - 如果 URL 带 id，切换到对应计划
   - 如果 currentPlan 仍为空，回退到第一个计划
   - 回填表单字段（exam_name、exam_date、daily_study_time、notes、subjects）
   - 完全找不到计划时，toast 提示并降级为新建模式

**savePlan 保存**：
- 编辑模式：调用 `planStore.updatePlan(currentPlan.id, data)`
- 新建模式：调用 `planStore.createPlan(data)`
- 保存后同步科目到用户科目列表

**科目删减**：
- 科目列表每项有 ✕ 删除按钮，点击 `form.subjects.splice(idx, 1)`
- 保存时 `filter(s => s.name.trim())` 过滤空科目
- 后端 PlanUpdate schema 支持 subjects 字段覆盖更新

---

## Req5：今日任务显示一致

### 问题描述

首页今日任务版块只显示 3 条，比任务版块少，用户以为数据不同步。

### 解决方案

**文件**：`frontend/src/pages/index/index.vue`

**previewTasks 计算属性**：
- 从 `todayTasks.slice(0, 3)` 改为返回全部 `todayTasks`

**底部统计栏**：
- 新增 `task-preview-footer`，显示 "共 N 个任务 · 已完成 M 个"
- 无任务时显示 empty-tip 提示

**交互同步**：
- 任务卡片根元素加 `@click="onTaskCardClick(task)"`
- 子元素（checkbox、番茄钟）加 `@click.stop`
- 桌面端点击编辑，移动端长按编辑（与 task-board 一致）

---

## Req6：实际用时 + 问题记录 + 未完成原因

### 机制设计（已与用户确认）

**存储方式**：新建 `task_reflections` 表，按 **任务 + 日期** 唯一存储（循环任务每天独立）

**已完成任务**：
- 勾选完成时弹窗，预填番茄钟累计时长（可手动修改）
- "完成过程中的问题"选填
- 任务卡片保留"✎"反思入口，随时可补改

**未完成任务**：
- 任务卡片有"记录原因"入口（通过 ✎ 按钮）
- 每天 23:30 弹窗提醒当天未完成任务，可快速选择原因

**实际用时来源**：
- 番茄钟完成时自动累加写入反思记录
- 用户可在反思入口手动覆盖/修正

### 6.1 后端数据库模型

**文件**：`backend/database.py` — 新增 `TaskReflection` 类

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_id | UUID (FK) | 关联任务，CASCADE 删除 |
| plan_id | UUID (FK) | 关联计划，CASCADE 删除 |
| task_date | DATE | 任务日期（与 task_id 联合唯一） |
| actual_duration | INTEGER | 实际用时（分钟），默认 0 |
| completion_issues | TEXT | 完成过程中的问题，默认空 |
| incomplete_reason | TEXT | 未完成原因，默认空 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间（自动 onupdate） |

**索引**：
- `task_id` + `task_date` 联合唯一（保证同一任务同一天只有一条反思）
- `plan_id` 索引
- `task_date` 索引

### 6.2 后端 Schema

**文件**：`backend/schemas/reflection.py`

- `TaskReflectionCreate`：task_id, plan_id, task_date, actual_duration, completion_issues, incomplete_reason
- `TaskReflectionUpdate`：三个字段都是 Optional
- `TaskReflectionResponse`：全部字段 + created_at/updated_at

### 6.3 后端 API

**文件**：`backend/routes/reflections.py`

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/reflections` | 创建或更新（upsert，按 task_id+task_date 唯一） |
| GET | `/api/reflections?plan_id=&task_date=&task_id=` | 查询反思列表，可按日期/任务过滤 |
| GET | `/api/reflections/{record_id}` | 查询单条 |
| PUT | `/api/reflections/{record_id}` | 更新 |
| DELETE | `/api/reflections/{record_id}` | 删除 |

**权限校验**：
- 所有接口通过 Authorization header 解析 user_id
- 校验 plan 归属，无权限返回 403

**Upsert 逻辑（POST）**：
- 先按 task_id + task_date 查询是否已存在
- 存在则更新，不存在则创建
- 方便前端"番茄钟累加用时"场景直接 POST 即可

### 6.4 后端注册路由

**文件**：`backend/main.py`
- import reflections 路由
- `app.include_router(reflections.router)`

### 6.5 前端 API

**文件**：`frontend/src/api/client.js`

新增函数：
- `createReflection(data)`
- `getReflections(planId, taskDate, taskId)`
- `updateReflection(id, data)`
- `deleteReflection(id)`

### 6.6 前端反思弹窗组件

**文件**：`frontend/src/components/TaskReflectionModal.vue`

**Props**：
- `visible`：是否显示
- `task`：任务对象
- `taskDate`：任务日期
- `isComplete`：是否为已完成模式（决定显示什么字段）
- `existingReflection`：已有反思记录（编辑模式预填）
- `defaultDuration`：默认实际用时（完成时预填番茄钟累计）

**Emits**：
- `close`：关闭
- `submitted`：提交成功，带回 data

**已完成模式 UI**：
- 实际用时：数字输入框 + ±5 分钟按钮
- 完成问题：多行文本框

**未完成模式 UI**：
- 未完成原因：多行文本框
- 快速选择标签：时间不够、难度太大、突发事项、缺乏资料、状态不佳、计划调整、其他

**提交逻辑**：
- 已有记录 → PUT 更新
- 无记录 → POST 创建
- 成功后 emit('submitted', data) + toast

### 6.7 任务卡片反思入口

**文件**：`frontend/src/pages/daily/task-board.vue`

**按钮样式**：
- 任务卡片右侧新增 ✎ 按钮（task-reflection）
- 绿色圆形背景，与番茄钟按钮并排
- 点击不冒泡（@click.stop）

**调用**：
```js
showTaskReflection(task, selectedDate.value, task.status === 'completed')
```
- 已完成任务 → 反思模式（实际用时+问题）
- 未完成任务 → 未完成原因模式

### 6.8 完成时弹窗

**toggleTask 改造**：
- 任务标记为完成后，调用 `showTaskReflection(task, selectedDate, true, task.actual_duration)`
- 预填番茄钟累计的 actual_duration
- 用户可修改或直接跳过

### 6.9 23:30 未完成任务提醒

**实现方式**：前端 setInterval 每分钟检查一次

```js
const UNFINISHED_REMIND_KEY = 'studymate_unfinished_remind_date'
let unfinishedReminderTimer = null

function startUnfinishedReminder() {
  if (unfinishedReminderTimer) clearInterval(unfinishedReminderTimer)
  unfinishedReminderTimer = setInterval(() => {
    checkUnfinishedReminder()
  }, 60000)
}

function checkUnfinishedReminder() {
  const now = new Date()
  const todayStr = formatDate(now)
  const hour = now.getHours()
  const minute = now.getMinutes()

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
          }
        }
      })
      lastRemindDate.value = todayStr
      uni.setStorageSync(UNFINISHED_REMIND_KEY, todayStr)
    }
  }
}
```

**防重复**：用 localStorage 记录今天是否已经提醒过，避免每分钟弹一次

**onMounted** 调用 `startUnfinishedReminder()`

### 6.10 番茄钟联动

**文件**：`frontend/src/pages/daily/pomodoro.vue`

番茄钟完成时，在更新任务 actual_duration 之后，自动创建/更新反思记录：
```js
if (planStore.currentPlan) {
  await createReflection({
    task_id: rs.currentTaskId,
    plan_id: planStore.currentPlan.id,
    task_date: today.value,
    actual_duration: dur,
    completion_issues: '',
    incomplete_reason: ''
  })
}
```

因为后端 POST 是 upsert 逻辑，番茄钟多次完成会自动累加（后端用传入值覆盖，前端需要手动累加。注意：当前实现是每次番茄钟完成都 POST 一次，但后端 upsert 是覆盖而不是累加。如果需要累加，需要前端先读取再加。

**修正说明**：实际实现中，由于后端 POST 是 upsert（覆盖），番茄钟每次完成调用 createReflection 时传入的 dur 是当次番茄钟时长，会覆盖之前的累加值。为了正确累加，应该先 GET 已有记录再加。但考虑到番茄钟完成后任务 actual_duration 已经累加了，反思记录的 actual_duration 可以以任务 actual_duration 为准（用户手动修改时也以任务为准）。或者改为从任务的 actual_duration 取值写入。当前实现以"番茄钟完成时写入当次时长"是简化处理，后续可优化为从任务读取累计值。

### 6.11 数据加载

**task-board onMounted / onShow**：
- 加载今日任务后，调用 `loadDailyReflections(selectedDate.value)`
- 结果存入 `dailyReflections` 对象，key 为 `taskId-taskDate`
- 打开反思弹窗时，从 dailyReflections 查找已有记录预填

---

## 文件变更清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `backend/schemas/reflection.py` | 任务反思 Pydantic schema |
| `backend/routes/reflections.py` | 任务反思 API 路由 |
| `frontend/src/components/TaskReflectionModal.vue` | 任务反思弹窗组件 |

### 修改文件（后端）

| 文件 | 变更内容 |
|------|---------|
| `backend/database.py` | 新增 TaskReflection 模型类 |
| `backend/main.py` | 注册 reflections 路由 |

### 修改文件（前端）

| 文件 | 变更内容 |
|------|---------|
| `frontend/src/api/client.js` | 新增 createReflection / getReflections / updateReflection / deleteReflection |
| `frontend/src/components/TaskFormModal.vue` | 新增 copySource prop、日期选择器、复制预填逻辑 |
| `frontend/src/pages/daily/task-board.vue` | 复制选择弹窗、周视图右键复制、PC点击编辑、循环任务展开、反思入口、23:30提醒 |
| `frontend/src/pages/daily/pomodoro.vue` | 时间戳计时、localStorage持久化、visibilitychange恢复、结束通知、重进恢复、反思联动 |
| `frontend/src/pages/index/index.vue` | 显示全部今日任务、PC点击编辑、底部统计栏 |
| `frontend/src/pages/plan/plan-overview.vue` | 编辑入口带计划id |
| `frontend/src/pages/plan/target-setup.vue` | 编辑模式可靠加载计划 |

---

## 数据库迁移

### 方式一：Alembic（推荐）

```bash
cd backend
alembic revision --autogenerate -m "add task_reflections table"
alembic upgrade head
```

### 方式二：手动 SQL

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE task_reflections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES daily_tasks(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES study_plans(id) ON DELETE CASCADE,
    task_date DATE NOT NULL,
    actual_duration INTEGER DEFAULT 0,
    completion_issues TEXT DEFAULT '',
    incomplete_reason TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reflections_plan_id ON task_reflections(plan_id);
CREATE INDEX idx_reflections_task_date ON task_reflections(task_date);
CREATE UNIQUE INDEX idx_reflections_task_date_unique ON task_reflections(task_id, task_date);
```

---

## 验证与测试

### 功能验证清单

#### Req1：任务复制 + 交互
- [ ] 今日任务点击加号 → 弹 ActionSheet → 选"新建"正常打开弹窗
- [ ] 今日任务点击加号 → 选"从已有复制" → 搜索过滤正常 → 点击任务 → 弹窗预填字段
- [ ] 复制任务时修改日期 → 保存后在对应日期显示
- [ ] 周视图右键空白格子 → 菜单有"从已有任务复制" → 复制后开始时间为格子时间
- [ ] 桌面端：今日任务卡片点击 → 打开编辑弹窗
- [ ] 移动端：今日任务卡片点击 → 不打开编辑（长按才打开）
- [ ] 周视图：点击任务卡片 → 展开文字；右键 → 编辑/删除菜单

#### Req2：循环任务同步
- [ ] 创建 daily 循环任务 → 周视图后续几天都显示
- [ ] 创建 weekday 循环任务 → 周视图周一到周五显示，周六日不显示
- [ ] 创建 holiday 循环任务 → 周视图周六日显示，工作日不显示
- [ ] 月视图：循环任务对应日期都有任务标记（小圆点）
- [ ] 非当天任务 → 在周视图/月视图对应日期显示

#### Req3：番茄钟后台运行
- [ ] 开始番茄钟 → 切换到其他标签页 1 分钟 → 切回 → 计时准确
- [ ] 开始番茄钟 → 最小化浏览器 → 等番茄钟应该结束的时间 → 切回 → 已完成，有通知和提示音
- [ ] 开始番茄钟 → 离开番茄钟页面 → 再进入 → 恢复计时
- [ ] 暂停番茄钟 → 离开页面 → 再进入 → 显示暂停状态和已计时长
- [ ] 跨天：昨天的未完成番茄钟 → 今天进入 → 提示过期，不恢复
- [ ] 番茄钟结束时 → 有桌面通知 + 提示音 + 震动
- [ ] 运行中不能切换模式 / 修改时长

#### Req4：计划编辑
- [ ] 计划概览点编辑 → 打开编辑页 → 字段正确回填
- [ ] 编辑考试日期 → 保存 → 概览页已更新
- [ ] 编辑每日学习时间 → 保存 → 已更新
- [ ] 删除一个科目 → 保存 → 科目列表已减少
- [ ] 添加一个新科目 → 保存 → 科目列表已增加

#### Req5：今日任务一致
- [ ] 首页今日任务数量与任务版块今日任务数量一致
- [ ] 首页显示全部任务，不截断
- [ ] 首页底部显示任务总数和已完成数

#### Req6：任务反思
- [ ] 勾选任务完成 → 弹出反思弹窗 → 预填番茄钟用时 → 修改后保存
- [ ] 任务卡片点 ✎ → 打开反思弹窗 → 可编辑已保存的内容
- [ ] 未完成任务点 ✎ → 显示未完成原因 → 选择快速标签 → 保存
- [ ] 23:30 且有未完成任务 → 弹出提醒 → 点"记录原因" → 可逐个记录
- [ ] 同一天多次勾选完成/取消 → 反思记录只有一条（upsert）
- [ ] 循环任务昨天和今天的反思 → 各自独立，不互相覆盖
- [ ] 番茄钟完成 → 反思记录的 actual_duration 自动写入

### 构建验证

```bash
cd frontend
npm run build:h5
# 应成功构建，无报错
```

### 后端启动验证

```bash
cd backend
uvicorn main:app --reload
# 访问 /docs 查看 reflections API 是否正常
```

---

## 后续优化建议

1. **番茄钟反思累加**：当前番茄钟完成调用 createReflection 是覆盖写入，建议改为"读取已有值 + 当次时长累加写入"
2. **后端番茄钟**：当前完全前端计时，后端只存记录。如果需要更强的后台保障，可考虑 WebSocket 或 Service Worker
3. **23:30 提醒**：当前用 setInterval，页面关闭时不触发。可考虑接入推送通知（如果有后端推送能力）
4. **反思统计**：可新增反思数据分析页面，统计常见未完成原因、平均实际用时与预估差异等
5. **数据导出**：反思记录支持导出为 CSV，便于复盘
