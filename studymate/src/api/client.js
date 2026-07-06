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

export async function aiGeneratePlan(data) {
  return request('/plans/ai/generate', { method: 'POST', data })
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
  return request('/tasks/ai/parse-plan', { method: 'POST', data })
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