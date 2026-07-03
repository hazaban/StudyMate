/** API client for the FastAPI backend. */

const BASE_URL = '/api'

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
    timeout: options.timeout || 30000
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
  return request(`/tasks?plan_id=${planId}&date=${date}`)
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

export async function completeTask(id) {
  return request(`/tasks/${id}/complete`, { method: 'POST' })
}

export async function aiGenerateTasks(data) {
  return request('/tasks/ai/generate', { method: 'POST', data })
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

export async function harvestPlant(plantId) {
  return request(`/farm/plants/${plantId}/harvest`, { method: 'POST' })
}

export async function fertilizePlant(plantId) {
  return request(`/farm/plants/${plantId}/fertilize`, { method: 'POST' })
}

export async function ensureCrop(planId, subject) {
  return request(`/farm/ensure-crop?plan_id=${planId}&subject=${encodeURIComponent(subject)}`, { method: 'POST' })
}

// ==================== AI ====================

export async function aiDailyReview(planId, date) {
  return request(`/ai/review?plan_id=${planId}&task_date=${date}`, { method: 'POST' })
}

export async function aiAnalyzeSyllabus(imageBase64, subject) {
  return request('/ai/analyze-syllabus', { method: 'POST', data: { image_base64: imageBase64, subject } })
}

export async function aiAnalyzeSubjectPhase(description, subject) {
  return request('/ai/analyze-subject-phase', { method: 'POST', data: { description, subject } })
}

// ==================== Upload ====================

export async function getSTSCredential() {
  return request('/upload/sts')
}

export async function presignUpload(filename) {
  return request(`/upload/presign?filename=${encodeURIComponent(filename)}`, { method: 'POST' })
}

// ==================== Export ====================

function buildExportUrl(type, format, params) {
  let url = `/export/${type}/${format}?plan_id=${params.planId}`
  if (params.subject) url += `&subject=${encodeURIComponent(params.subject)}`
  if (params.tag) url += `&tag=${encodeURIComponent(params.tag)}`
  if (params.mastery_level) url += `&mastery_level=${params.mastery_level}`
  if (params.difficulty) url += `&difficulty=${params.difficulty}`
  if (params.mastered !== undefined && params.mastered !== null) url += `&mastered=${params.mastered}`
  if (params.min_errors) url += `&min_errors=${params.min_errors}`
  if (params.questions_only) url += `&questions_only=true`
  return url
}

export async function getExportTags(planId, type, subject) {
  let url = `/export/tags?plan_id=${planId}&type=${type}`
  if (subject) url += `&subject=${encodeURIComponent(subject)}`
  return request(url)
}

export function getExportUrl(type, format, params) {
  const token = getToken()
  const url = buildExportUrl(type, format, params)
  // For H5: return full URL with token as query param for download
  return `${BASE_URL}${url}&token=${encodeURIComponent(token)}`
}

export async function downloadExport(type, format, params) {
  const url = buildExportUrl(type, format, params)
  const token = getToken()
  // #ifdef H5
  // For H5: use window.open to trigger download
  const fullUrl = `${BASE_URL}${url}`
  // Create a temporary link element to download with auth header
  const response = await fetch(fullUrl, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('导出失败')
  const blob = await response.blob()
  const downloadUrl = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = downloadUrl
  const ext = format === 'excel' ? 'xlsx' : format
  a.download = `${type === 'cards' ? 'knowledge_cards' : 'mistakes'}.${ext}`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(downloadUrl)
  // #endif
  // #ifndef H5
  // For non-H5: use uni.downloadFile
  return new Promise((resolve, reject) => {
    uni.downloadFile({
      url: `${window.location.origin}${BASE_URL}${url}`,
      header: { Authorization: `Bearer ${token}` },
      success: (res) => resolve(res),
      fail: (err) => reject(err)
    })
  })
  // #endif
}