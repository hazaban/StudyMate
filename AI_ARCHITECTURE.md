# StudyMate AI 架构说明书

> 最后更新：2026-07-07 | 模型：智谱 GLM-4.5-Air / GLM-4.1V-Thinking-FlashX

---

## 目录

- [总体架构](#总体架构)
- [AI 入口（3个）](#ai-入口3个)
- [核心链路](#核心链路)
- [_worker.js 详解](#_workerjs-详解)
- [前端 API 层](#前端-api-层)
- [AI 规划页面](#ai-规划页面)
- [后端 AI 服务（备用）](#后端-ai-服务备用)
- [会话记忆管理](#会话记忆管理)
- [模型选型对照](#模型选型对照)
- [故障排错](#故障排错)
- [环境变量配置](#环境变量配置)

---

## 总体架构

```
用户浏览器
    │
    ▼
Cloudflare Pages（studymate-5w0.pages.dev）
    │
    ├── /api/ai/*   →  _worker.js 直连智谱 GLM（主要路径，绕过 Vercel 超时）
    │                   Cloudflare 边缘节点 → open.bigmodel.cn
    │
    └── /api/*      →  Vercel Serverless（backend/）
                        FastAPI + SQLAlchemy → Supabase PostgreSQL
```

**关键决策**：AI 调用走 Cloudflare Worker 而非 Vercel，因为：
- Vercel Hobby 计划限制 10 秒函数超时
- Vercel 美国机房 → 智谱中国延迟太高
- Cloudflare 边缘节点直连国内，延迟 < 1s

---

## AI 入口（3个）

### 1. AI 智能规划（ai-plan.vue）

**路径**：前端 → `POST /api/ai/chat` → Worker → GLM

**用途**：统一对话入口。用户输入自然语言，GLM 自动识别意图并调用对应工具。

```
用户："帮我规划考研408，还有120天"
  → GLM 识别 intent=plan
  → 返回 {summary: "我来帮你制定...", tool: "plan", data: {...}}
  → 前端展示计划卡片，用户点"确认应用此计划"写入数据库
```

**功能**：
- ☰ 侧边栏：历史会话列表（localStorage 存储，最多 20 条）
- 📷 上传图片：自动转 base64，传给 GLM-4.1V 识别教材目录
- 快速入口卡片：规划计划/添加任务/分析目录/每日复盘
- 统一输入框 + 图片预览

### 2. AI 添加任务（TaskFormModal.vue）

**路径**：前端 → `POST /api/ai/parse-tasks` → Worker → GLM

**触发**：任务看板 → "+" → 弹窗右上角 "🤖 AI添加"

**流程**：
```
用户："明天上午9点复习数据结构二叉树45分钟"
  → 前端构造提示词（含当前日期/明天日期/格式要求）
  → Worker 调用 GLM，temperature=0.1
  → GLM 返回 {"tasks": [{content:"复习二叉树",subject:"数据结构",...}]}
  → 用户勾选确认 → addParsedTasks() → api.createTask() → PostgreSQL
```

### 3. AI 生成计划（ai-plan.vue → confirmPlan）

**路径**：前端 → `POST /api/ai/generate-plan` → Worker → GLM

**触发**：在 AI 规划页面描述考试目标，GLM 返回计划后点确认

---

## 核心链路

### 链路 1：添加任务（AI 解析）

```
TaskFormModal.vue "🤖 AI添加"
  │  输入文字："明天复习数据结构"
  ▼
client.js: aiParsePlan({text})
  │  构造 prompt（含日期/格式要求）
  ▼
POST /api/ai/parse-tasks  →  _worker.js
  │  temperature=0.1, max_tokens=1024
  ▼
GLM-4.5-Air (open.bigmodel.cn)
  ▼  返回: {"tasks":[{content,subject,chapter,duration,type,date,start_hour,selected}]}
_worker.js extractJSON + 格式归一化
  ▼  返回给前端
TaskFormModal.vue: parseWithAI()
  │  展示任务列表供用户勾选
  ▼
addParsedTasks() → taskStore.createTask() → POST /api/tasks → PostgreSQL
```

### 链路 2：AI 规划对话

```
ai-plan.vue: sendMessage()
  │  输入 + 最近6轮对话 history
  ▼
POST /api/ai/chat  →  _worker.js
  │  history 拼接在 messages 数组中
  ▼
GLM-4.5-Air
  ▼  返回: {summary: "自然语言回复", tool: "plan|task|chat", data: {...}}
前端展示卡片
  │  用户点 "确认添加任务" / "确认写入计划"
  ▼
confirmTasks() / confirmPlan() → api.createTask() / planStore.createPlan() → PostgreSQL
```

### 链路 3：教材目录识别

```
ai-plan.vue: chooseImage() → 拍照/选图 → canvas 转 base64
  │
POST /api/ai/analyze-syllabus  →  _worker.js
  │  model: glm-4.1v-thinking-flashx
  │  messages: [{role:"user",content:[{image_url},{text}]}]
  ▼
GLM-4.1V → 返回: {subject, chapters:[], total_days, suggestion}
  │
前端展示章节列表 → confirmSyllabus() → 按章节批量 createTask() → PostgreSQL
```

---

## _worker.js 详解

**位置**：`frontend/_worker.js`

**职责**：Cloudflare Pages 的 Advanced Mode Worker，拦截所有 `/api/*` 请求

### AI 路由清单

| 路由 | 模型 | max_tokens | System Prompt | 用途 |
|------|------|-----------|---------------|------|
| `/api/ai/chat` | glm-4.5-air | 2048 | CHAT_SYSTEM（含能力描述+输出格式） | 统一对话，意图识别 |
| `/api/ai/generate-plan` | glm-4.5-air | 3072 | PLAN_SYSTEM | 生成学习计划 |
| `/api/ai/generate-tasks` | glm-4.5-air | 2048 | PLAN_SYSTEM | 生成每日任务 |
| `/api/ai/generate-cards` | glm-4.5-air | 1024 | PLAN_SYSTEM | 生成知识卡片 |
| `/api/ai/generate-review` | glm-4.5-air | 1024 | PLAN_SYSTEM | 每日复盘 |
| `/api/ai/parse-tasks` | glm-4.5-air | 1024 | STRICT_JSON_SYSTEM | 文字→结构化任务 |
| `/api/ai/analyze-syllabus` | glm-4.1v-thinking-flashx | 2048 | — | 图片→章节结构 |

### 格式归一化（extractJSON + 后处理）

```js
// 1. 剥离 markdown 代码块 (```json ... ```)
// 2. 正则提取第一个 { ... } 
// 3. JSON.parse
// 4. 按路由做格式补全：
//    parse-tasks: 确保返回 {tasks:[...]}，单个对象自动包裹
//    generate-plan: 无 phases 时包裹为 {phases:[],overview:text}
//    generate-cards: 保证 {cards:[...]}
```

### 环境变量

| 变量 | 来源 | 用途 |
|------|------|------|
| `GLM_API_KEY` | Cloudflare Dashboard → Settings → Variables | 智谱 API 密钥 |

---

## 前端 API 层

**位置**：`frontend/src/api/client.js`

### AI 请求函数

| 函数 | 调用的 Worker 路由 | 超时 | 特点 |
|------|-------------------|------|------|
| `aiChat(data)` | `/api/ai/chat` | 60s | 支持 `history` 对话上下文 |
| `aiGeneratePlan(data)` | `/api/ai/generate-plan` | 60s | 自动构造 prompt |
| `aiParsePlan(data)` | `/api/ai/parse-tasks` | 60s | 自动注入日期+格式要求 |
| `aiGenerateTasks(data)` | `/api/tasks/ai/generate` (Vercel) | 60s | 走 Vercel 旧路径 |

### aiRequest() 通用函数

```js
async function aiRequest(url, body) {
  const res = await uni.request({
    url: `/api/ai${url}`,    // → Cloudflare Worker
    method: 'POST',
    data: body,
    timeout: 60000            // 60秒，计划生成可能需要较长时间
  })
  if (res.statusCode >= 200 && res.statusCode < 300) return res.data
  throw new Error(res.data?.error || 'AI请求失败')
}
```

> ⚠️ `aiChat` 调用的是 `request('/ai/chat', ...)` 走 **Vercel 路径**，未使用 `aiRequest`。需要改成 `aiRequest('/chat', ...)` 才能走 Worker 快路径。

---

## AI 规划页面

**位置**：`frontend/src/pages/plan/ai-plan.vue`

### 页面结构

```
┌──────────────────────────────┐
│ ← AI 智能规划            ☰  │  头部（返回/标题/侧边栏开关）
├──────────────────────────────┤
│ 🤖 你好！我是AI学习规划助手  │
│ 👤 我要考研408               │  对话区（scroll-view）
│ 🤖 我来为你制定备考计划...   │
│  [阶段卡片] [确认应用]       │
├──────────────────────────────┤
│ 💡 试试这些：                │
│ ┌────────┐ ┌────────┐       │  快速入口卡片（首次对话时显示）
│ │规划计划│ │添加任务│       │
│ └────────┘ └────────┘       │
│ ┌────────┐ ┌────────┐       │
│ │分析目录│ │每日复盘│       │
│ └────────┘ └────────┘       │
├──────────────────────────────┤
│ [📷] 输入需求...        [➤] │  输入区（含图片上传按钮）
└──────────────────────────────┘

☰ 点击展开侧边栏:
┌─────────────┐
│ 历史会话     │
│ ├ 考研408规划│
│ │  7/7/2026 │
│ ├ 软考备考  │
│ │  7/5/2026 │
│             │
│ + 新会话    │
└─────────────┘
```

### 关键函数

| 函数 | 触发 | 作用 |
|------|------|------|
| `sendMessage()` | 输入框回车/发按钮 | 构造 history + 调 `aiChat()` |
| `chooseImage()` | 📷按钮 | 拍照/选图→canvas转base64 |
| `confirmTasks(tasks)` | 点击"确认添加任务" | 批量 createTask() |
| `confirmPlan(data)` | 点击"确认应用此计划" | planStore.createPlan() |
| `confirmSyllabus(data)` | 点击"确认写入计划" | 批量 createTask()（按章节展开） |
| `saveCurrentConversation()` | 新会话/加载会话时 | 将当前对话存入 localStorage |
| `loadConversation(idx)` | 点击侧边栏条目 | 从 localStorage 恢复对话 |
| `startNewConversation()` | "+ 新会话"按钮 | 保存当前→清空→新建 |

---

## 后端 AI 服务（备用）

**位置**：`backend/services/ai_service.py`

> ⚠️ 当前生产环境 AI 调用主要通过 Cloudflare Worker 完成。后端的 `ai_service.py` 仅在 Vercel 环境内通过 `/api/ai-proxy/` 转发到 Worker 时使用，或作为本地开发的备用路径。

### 函数清单

| 函数 | 模型 | 用途 |
|------|------|------|
| `_call_glm(messages, model, temperature)` | glm-4.5-air | OpenAI 兼容协议调用 GLM |
| `generate_study_plan(params)` | glm-4.5-air | 生成学习计划 |
| `generate_daily_tasks(params)` | glm-4.5-air | 生成每日任务 |
| `generate_flash_cards(content, subject)` | glm-4.5-air | 生成知识卡片 |
| `parse_task_text(text, plan_id)` | glm-4.5-air | 文字→结构化任务 |
| `generate_daily_review(...)` | glm-4.5-air | 每日复盘 |
| `analyze_syllabus_image(data_url, subject, desc)` | glm-4.1v | 图片→章节结构 |
| `generate_subject_phases(plan_info)` | glm-4.5-air | 科目阶段建议 |

### System Prompts

- `SYSTEM_PROMPT_TASK_PARSE`：严格的 JSON 输出器
- `SYSTEM_PROMPT_PLAN`：备考规划导师
- `SYSTEM_PROMPT_SYLLABUS`：教材目录分析专家
- `SYSTEM_PROMPT_PLAN_AGENT`：多工具 Agent（plan/task/syllabus/review/search）
- `SYSTEM_PROMPT_DEFAULT`：通用助手

---

## 会话记忆管理

### 上下文策略

**滑动窗口**：保留最近 6 轮对话作为上下文，超出部分丢弃。

```
发送第7轮消息时:
  history = [user[1], assistant[1], user[2], assistant[2], ..., user[6], assistant[6]]
```

**实现位置**：`ai-plan.vue: sendMessage()`

```js
const history = []
const ru = userMessages.value.slice(-7, -1)   // 前6条用户消息
const ra = messages.value.filter(m => m.type !== 'intro' && m.type !== 'error').slice(-6)  // 前6条AI回复
for (let i = 0; i < Math.max(ru.length, ra.length); i++) {
  if (ru[i]) history.push({ role: 'user', content: ru[i].text })
  if (ra[i]) history.push({ role: 'assistant', content: ra[i].text || '' })
}
```

### 持久化存储

- **存储位置**：浏览器 localStorage，Key: `studymate_ai_conversations`
- **格式**：JSON 数组，每项包含 `{title, date, messages[], userMessages[]}`
- **容量**：最多 20 条历史会话
- **生命周期**：持久化，除非用户清除浏览器数据

### 内存状态

| 变量 | 类型 | 说明 |
|------|------|------|
| `messages` | `ref([])` | AI 回复消息列表 |
| `userMessages` | `ref([])` | 用户发送消息列表 |
| `conversationList` | `ref([])` | localStorage 中的历史会话列表 |
| `showSidebar` | `ref(false)` | 侧边栏开关 |

---

## 模型选型对照

| 场景 | 模型 | 原因 |
|------|------|------|
| 统一对话（chat） | `glm-4.5-air` | 性价比高、快，适合多意图识别 |
| 生成学习计划 | `glm-4.5-air` | 需要长文本输出，max_tokens=3072 |
| 解析任务 | `glm-4.5-air` | 需要精确 JSON，temperature=0.1 |
| 生成卡片 | `glm-4.5-air` | 标准文本生成，max_tokens=1024 |
| 每日复盘 | `glm-4.5-air` | 结构化总结，max_tokens=1024 |
| 识别教材图片 | `glm-4.1v-thinking-flashx` | 多模态视觉模型，便宜极速 |

| 参数 | 默认值 | 可配置 |
|------|-------|--------|
| temperature（对话） | 0.3 | ✅ body.temperature |
| temperature（解析） | 0.1 | ✅ body.temperature |
| max_tokens | 1024-3072（按路由） | ✅ callGLM 第5参数 |
| timeout（前端） | 60000ms | `client.js:106` |
| timeout（后端） | 15000ms | `ai_service.py:105` |

---

## 故障排错

### 问题 1：AI 返回 "GLM_API_KEY 未配置"

**原因**：Cloudflare Pages 环境变量未设置或未部署

**修复**：
1. Cloudflare Dashboard → `studymate-5w0` → Settings → Variables
2. 添加 `GLM_API_KEY` = 你的智谱 API Key
3. Deployments → 最新一条 → Retry deployment

### 问题 2：返回 mock 假数据

**原因**：Vercel 超时或 GLM 连接失败 → 走了 mock 降级

**修复**：检查 Worker 是否生效（浏览器 F12 → Network → 看 AI 请求是否 200），确认走的是 `/api/ai/*` 而非 Vercel

### 问题 3：计划生成太慢（>30s）

**原因**：GLM-4.5-Air 生成长文本本身就慢

**缓解**：
- 已设置 max_tokens=3072 平衡速度
- 前端超时 60s
- 可考虑换 `glm-4-flash` 极速模型

### 问题 4：解析任务返回空数组

**原因**：GLM 返回格式不符合预期（如单个对象而非数组）

**修复**：`_worker.js` 已实现格式归一化——单个对象自动包裹为 `{tasks: [obj]}`

### 问题 5：侧边栏点开空白

**原因**：`loadConversationList()` 未在 `onMounted` 中调用

**修复**：已修复，`onMounted` 中调用 `loadConversationList()`

---

## 环境变量配置

### Cloudflare Pages（_worker.js）

| 变量 | 用途 | 如何设置 |
|------|------|---------|
| `GLM_API_KEY` | 智谱 AI 调用凭证 | Dashboard → Settings → Variables |

### Vercel 后端（backend/config.py）

| 变量 | 默认值 | 用途 |
|------|-------|------|
| `GLM_API_KEY` | — | 智谱 API Key（备用路径） |
| `GLM_BASE_URL` | `https://studymate-5w0.pages.dev/api/ai-proxy` | 生产环境走 CF 代理 |
| `GLM_TEXT_MODEL` | `glm-4.5-air` | 文本模型 |
| `GLM_VISION_MODEL` | `glm-4.1v-thinking-flashx` | 视觉模型 |

### 智谱 API

- 申请地址：https://open.bigmodel.cn/
- API 端点：`https://open.bigmodel.cn/api/paas/v4/chat/completions`
- 协议：OpenAI 兼容（Bearer Token）

---

## 测试方法

### 命令行动测试

```bash
# 测试 AI 对话（替换为你的域名）
curl -X POST https://studymate-5w0.pages.dev/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"text":"你好","history":[]}'

# 测试任务解析
curl -X POST https://studymate-5w0.pages.dev/api/ai/parse-tasks \
  -H "Content-Type: application/json" \
  -d '{"prompt":"当前日期:2026-07-07\n用户输入:明天复习数据结构\n返回JSON"}' 
```

### 前端测试路径

1. 登录 → 任务看板 → "+" → "🤖 AI添加" → 输入文字 → "开始解析"
2. 登录 → AI 智能规划（从个人中心进入）→ 输入需求 → 查看回复 → 确认应用
