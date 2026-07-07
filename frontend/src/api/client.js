/** API client for the FastAPI backend. */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

function getToken() {
  return uni.getStorageSync('studymate_token') || ''
}

function setToken(token) {
  uni.setStorageSync('studymate_token', token)
}

function clearToken() {
  uni.removeStorageSync('studymate_token')
}

export async function request(url, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers
  }

  const res = await uni.request({
    url: `${BASE_URL}${url}`,
    method: options.method || 'GET',
    data: options.data,
    header: headers,
    timeout: options.timeout || 60000
  })

  if (res.statusCode >= 200 && res.statusCode < 300) {
    return res.data
  }

  const msg = res.data?.detail || '请求失败'
  throw new Error(msg)
}

// ==================== Auth ====================

export async function register(email, password, nickname) {
  const data = await request('/auth/register', {
    method: 'POST',
    data: { email, password, nickname }
  })
  setToken(data.access_token)
  return data
}

export async function login(email, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    data: { email, password }
  })
  setToken(data.access_token)
  return data
}

export async function getMe() {
  return request('/auth/me')
}

export async function updateMe(data) {
  return request('/auth/me', { method: 'PUT', data })
}

export function logout() {
  clearToken()
}

// ==================== Plans ====================

export async function createPlan(data) {
  return request('/plans', { method: 'POST', data })
}

export async function getPlans() {
  return request('/plans')
}

export async function getPlan(id) {
  return request(`/plans/${id}`)
}

export async function updatePlan(id, data) {
  return request(`/plans/${id}`, { method: 'PUT', data })
}

export async function deletePlan(id) {
  return request(`/plans/${id}`, { method: 'DELETE' })
}

/** 直接调用 CF Worker AI 端点（绕过 Vercel 超时限制） */
async function aiRequest(url, body) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await uni.request({
    url: `/api/ai${url}`,
    method: 'POST',
    data: body,
    header: headers,
    timeout: 30000
  })

  if (res.statusCode >= 200 && res.statusCode < 300) {
    return res.data
  }
  throw new Error(res.data?.error || res.data?.detail || 'AI请求失败')
}

export async function aiGeneratePlan(data) {
  const today = new Date().toISOString().split('T')[0]
  const prompt = `请根据以下信息生成一份详细的备考计划：

考试名称：${data.exam_name || data.description || '未知考试'}
考试日期：${data.exam_date || '未指定'}
目标分数：${JSON.stringify(data.target_scores || {})}
每日学习时间：${data.daily_study_time || 480}分钟
薄弱点：${(data.weak_points || []).join('、') || '无'}
补充描述：${data.description || ''}

请生成包含阶段划分（每阶段名称、时长、重点科目、每日安排）、每周目标、复习策略的完整计划。返回JSON格式。`
  return aiRequest('/generate-plan', { prompt, temperature: 0.3 })
}

// ==================== Tasks ====================

export async function createTask(data) {
  return request('/tasks', { method: 'POST', data })
}

export async function getTasks(planId, date) {
  const params = date ? `plan_id=${planId}&date=${date}` : `plan_id=${planId}`
  return request(`/tasks?${params}`)
}

export async function getTask(id) {
  return request(`/tasks/${id}`)
}

export async function updateTask(id, data) {
  return request(`/tasks/${id}`, { method: 'PUT', data })
}

export async function deleteTask(id) {
  return request(`/tasks/${id}`, { method: 'DELETE' })
}

export async function completeTask(id, taskDate) {
  let url = `/tasks/${id}/complete`
  if (taskDate) url += `?task_date=${taskDate}`
  return request(url, { method: 'POST' })
}

export async function uncompleteTask(id, taskDate) {
  let url = `/tasks/${id}/uncomplete`
  if (taskDate) url += `?task_date=${taskDate}`
  return request(url, { method: 'POST' })
}

export async function aiGenerateTasks(data) {
  return request('/tasks/ai/generate', { method: 'POST', data })
}

export async function aiParsePlan(data) {
  const today = new Date().toISOString().split('T')[0]
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0]
  const prompt = `当前日期：${today}，明天：${tomorrow}

用户输入的自然语言计划：
${data.text}

请把以上文字拆成结构化的任务列表。每个任务必须包含：
- content: 20字以内的简洁摘要（不能照搬原文）
- subject: 科目名
- chapter: 章节名（提到了就提取，没提填空字符串""）
- duration: 分钟数整数（默认30）
- type: "new_study"/"review"/"mistake"
- date: YYYY-MM-DD（明天=${tomorrow}，今天或无时间词=${today}）
- start_hour: 0-23整数（默认9）
- repeat_type: "none"
- selected: true

返回JSON格式：{"tasks": [{"content":"...","subject":"...","chapter":"...","duration":30,"type":"new_study","date":"${today}","start_hour":9,"repeat_type":"none","selected":true}]}`
  return aiRequest('/parse-tasks', { prompt, temperature: 0.1 })
}

export async function aiChat(data) {
  return request('/ai/chat', { method: 'POST', data })
}

export async function aiParseTask(data) {
  return request('/ai/parse-task', { method: 'POST', data })
}

// ==================== Cards ====================

export async function createCard(data) {
  return request('/cards', { method: 'POST', data })
}

export async function getCards(planId, subject, tag, pending) {
  let url = `/cards?plan_id=${planId}`
  if (subject) url += `&subject=${encodeURIComponent(subject)}`
  if (tag) url += `&tag=${encodeURIComponent(tag)}`
  if (pending) url += `&pending=1`
  return request(url)
}

export async function getPendingCards(planId) {
  return request(`/cards/pending?plan_id=${planId}`)
}

export async function getCard(id) {
  return request(`/cards/${id}`)
}

export async function updateCard(id, data) {
  return request(`/cards/${id}`, { method: 'PUT', data })
}

export async function deleteCard(id) {
  return request(`/cards/${id}`, { method: 'DELETE' })
}

export async function reviewCard(id, masteryLevel) {
  return request(`/cards/${id}/review?mastery_level=${masteryLevel}`, { method: 'POST' })
}

export async function getCardSubjects(planId) {
  return request(`/cards/subjects?plan_id=${planId}`)
}

export async function getCardTagsBySubject(planId, subject) {
  let url = `/cards/tags/by-subject?plan_id=${planId}`
  if (subject) url += `&subject=${encodeURIComponent(subject)}`
  return request(url)
}

export async function exportCards(planId, subject, tag) {
  let url = `/cards/export?plan_id=${planId}`
  if (subject) url += `&subject=${encodeURIComponent(subject)}`
  if (tag) url += `&tag=${encodeURIComponent(tag)}`
  return request(url)
}

export async function aiAnalyzeSubjectPhase(description, subject) {
  return request('/ai/syllabus', { method: 'POST', data: { description, subject, image: '' } })
}

export async function aiAnalyzeSyllabus(imageBase64, subject) {
  return request('/ai/syllabus', { method: 'POST', data: { image: imageBase64, subject, description: '' } })
}

export async function aiGenerateCards(content, subject) {
  return request('/cards/ai/generate', {
    method: 'POST',
    data: { content, subject }
  })
}

// ==================== Mistakes ====================

export async function createMistake(data) {
  return request('/mistakes', { method: 'POST', data })
}

export async function getMistakes(planId, subject, tag, pending) {
  let url = `/mistakes?plan_id=${planId}`
  if (subject) url += `&subject=${encodeURIComponent(subject)}`
  if (tag) url += `&tag=${encodeURIComponent(tag)}`
  if (pending) url += `&pending=1`
  return request(url)
}

export async function getMistake(id) {
  return request(`/mistakes/${id}`)
}

export async function updateMistake(id, data) {
  return request(`/mistakes/${id}`, { method: 'PUT', data })
}

export async function deleteMistake(id) {
  return request(`/mistakes/${id}`, { method: 'DELETE' })
}

export async function markMistakeMastered(id) {
  return request(`/mistakes/${id}/master`, { method: 'POST' })
}

export async function retryMistake(id) {
  return request(`/mistakes/${id}/retry`, { method: 'POST' })
}

export async function reviewMistake(id, correct) {
  return request(`/mistakes/${id}/review?correct=${correct}`, { method: 'POST' })
}

export async function getMistakeSubjects(planId) {
  return request(`/mistakes/subjects?plan_id=${planId}`)
}

export async function getMistakeTagsBySubject(planId, subject) {
  let url = `/mistakes/tags/by-subject?plan_id=${planId}`
  if (subject) url += `&subject=${encodeURIComponent(subject)}`
  return request(url)
}

export async function exportMistakes(planId, subject, tag, difficulty) {
  let url = `/mistakes/export?plan_id=${planId}`
  if (subject) url += `&subject=${encodeURIComponent(subject)}`
  if (tag) url += `&tag=${encodeURIComponent(tag)}`
  if (difficulty) url += `&difficulty=${encodeURIComponent(difficulty)}`
  return request(url)
}

// ==================== Subjects ====================

export async function getUserSubjects() {
  return request('/subjects')
}

export async function addUserSubject(name) {
  return request('/subjects', { method: 'POST', data: { name } })
}

export async function removeUserSubject(name) {
  return request(`/subjects/${encodeURIComponent(name)}`, { method: 'DELETE' })
}

// ==================== Farm ====================

export async function getFarm(planId) {
  return request(`/farm?plan_id=${planId}`)
}

export async function plantSeed(data) {
  return request('/farm/plants', { method: 'POST', data })
}

export async function waterPlant(plantId) {
  return request(`/farm/plants/${plantId}/water`, { method: 'POST' })
}

export async function fertilizePlant(plantId) {
  return request(`/farm/plants/${plantId}/fertilize`, { method: 'POST' })
}

export async function harvestPlant(plantId) {
  return request(`/farm/plants/${plantId}/harvest`, { method: 'POST' })
}

export async function ensureCrop(planId, subject) {
  return request(`/farm/ensure-crop?plan_id=${planId}&subject=${encodeURIComponent(subject)}`)
}

// ==================== Focus Records (番茄钟) ====================

export async function createFocusRecord(data) {
  return request('/focus', { method: 'POST', data })
}

export async function getFocusRecords(planId, startDate, endDate, subject) {
  let url = `/focus?plan_id=${planId}`
  if (startDate) url += `&start_date=${startDate}`
  if (endDate) url += `&end_date=${endDate}`
  if (subject) url += `&subject=${encodeURIComponent(subject)}`
  return request(url)
}

export async function getFocusStats(planId, startDate, endDate) {
  let url = `/focus/stats?plan_id=${planId}`
  if (startDate) url += `&start_date=${startDate}`
  if (endDate) url += `&end_date=${endDate}`
  return request(url)
}

export async function getFocusSubjectStats(planId, startDate, endDate) {
  let url = `/focus/stats/subject?plan_id=${planId}`
  if (startDate) url += `&start_date=${startDate}`
  if (endDate) url += `&end_date=${endDate}`
  return request(url)
}

export async function getFocusDailyStats(planId, startDate, endDate) {
  let url = `/focus/stats/daily?plan_id=${planId}`
  if (startDate) url += `&start_date=${startDate}`
  if (endDate) url += `&end_date=${endDate}`
  return request(url)
}

export async function getFocusWeeklyStats(planId, startDate, endDate) {
  let url = `/focus/stats/weekly?plan_id=${planId}`
  if (startDate) url += `&start_date=${startDate}`
  if (endDate) url += `&end_date=${endDate}`
  return request(url)
}

export async function getFocusMonthlyStats(planId, startDate, endDate) {
  let url = `/focus/stats/monthly?plan_id=${planId}`
  if (startDate) url += `&start_date=${startDate}`
  if (endDate) url += `&end_date=${endDate}`
  return request(url)
}

export async function updateFocusRecord(id, data) {
  return request(`/focus/${id}`, { method: 'PUT', data })
}

export async function deleteFocusRecord(id) {
  return request(`/focus/${id}`, { method: 'DELETE' })
}

// ==================== AI ====================

export async function aiDailyReview(planId, date) {
  return request(`/ai/review?plan_id=${planId}&task_date=${date}`, { method: 'POST' })
}

// ==================== Upload ====================

export async function getSTSCredential() {
  return request('/upload/sts')
}

export async function presignUpload(filename) {
  return request(`/upload/presign?filename=${encodeURIComponent(filename)}`, { method: 'POST' })
}