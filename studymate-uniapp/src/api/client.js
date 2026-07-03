/** API client for the FastAPI backend. */

const BASE_URL = 'http://localhost:8000/api'

function getToken() {
  return uni.getStorageSync('studymate_token') || ''
}

function setToken(token) {
  uni.setStorageSync('studymate_token', token)
}

function clearToken() {
  uni.removeStorageSync('studymate_token')
}

async function request(url, options = {}) {
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

export async function getCards(planId) {
  return request(`/cards?plan_id=${planId}`)
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