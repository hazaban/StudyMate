/**
 * Cloudflare Pages Advanced Mode Worker.
 *
 * /api/ai/*  → Worker 直接调用智谱 GLM（绕过 Vercel 超时限制）
 * /api/*     → 代理到 Vercel 后端（数据库 CRUD）
 * 其他       → 静态文件（SPA）
 */
// GLM_API_KEY 从 Cloudflare Pages 环境变量中读取（Settings → Environment Variables）
const GLM_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions';

const CHAT_SYSTEM = `你是 StudyMate 学习星球的 AI 备考规划助手。你拥有多种能力：

**能力**：
- plan: 生成学习计划、备考规划、时间安排
- task: 把自然语言拆成结构化任务（提取科目/章节/时长/类型/日期/开始时间）
- syllabus: 分析教材目录图片，提取章节结构（用户需上传图片）
- review: 根据学习数据做每日复盘总结
- chat: 一般对话、问候、咨询

**工作方式**：
1. 友好自然地与用户对话
2. 识别用户意图，决定是否需要调用工具
3. 如果用户输入中包含图片（image_url），评估是否为教材目录

**输出格式**：必须返回合法JSON（不含markdown标记）：
{
  "summary": "对用户的自然语言回复（1-3句话）",
  "tool": "plan|task|syllabus|review|chat",
  "data": { ... 工具返回的结构化数据 }
}

**各工具data格式**：
- plan: {"phases":[{name,description,duration_days,focus:[],daily_schedule}],"weekly_goals":[],"review_strategy":""}
- task: {"tasks":[{content,subject,chapter,duration,type,date,start_hour,repeat_type,selected}]}
- syllabus: {"subject":"","chapters":[{name,daily_duration,estimated_days}],"total_days":N,"suggestion":""}
- review: {"summary":"","highlights":[],"improvements":[],"tomorrow_focus":[],"mood_suggestion":""}
- chat: {}

**重要规则**：
- summary 必须始终先给出自然语言回答
- 如果用户只是聊天(hello/你好/谢谢) → tool=chat, data={}
- 如果用户提到考试+时间安排 → tool=plan
- 如果用户描述具体学习任务(明天复习XX/下午做XX) → tool=task
- 如果用户上传图片且问目录/章节 → tool=syllabus
- 如果用户问"今天学了什么/复盘" → tool=review
- data 字段在 chat 意图下可以为 null`;

async function callGLM(apiKey, messages, model, temperature) {
  if (!apiKey) throw new Error('GLM_API_KEY 未配置，请在 Cloudflare Pages 环境变量中设置');
  const resp = await fetch(GLM_URL, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: model || 'glm-4.5-air',
      messages,
      temperature: temperature ?? 0.3,
      max_tokens: 2048,
    }),
  });
  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(`GLM returned ${resp.status}: ${errText.substring(0, 200)}`);
  }
  const data = await resp.json();
  return data.choices[0].message.content;
}

function extractJSON(text) {
  let cleaned = (text || '').trim()
    .replace(/```json\s*/gi, '').replace(/```\s*/gi, '').trim();
  const m = cleaned.match(/\{[\s\S]*\}/);
  if (m) cleaned = m[0];
  try { return JSON.parse(cleaned); } catch (e) { return { summary: cleaned, tool: 'chat', data: null }; }
}

const STRICT_JSON_SYSTEM = '你是 Strict JSON 输出器。只输出合法 JSON，不含 markdown 标记，不含额外解释。';
const PLAN_SYSTEM = '你是 StudyMate 学习星球的备考规划导师。专业、耐心、有洞察力。输出严格JSON。';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const glmKey = env.GLM_API_KEY || '';

    // ── AI 代理（透传）──
    if (url.pathname.startsWith('/api/ai-proxy/')) {
      if (request.method !== 'POST') {
        return new Response(JSON.stringify({ error: 'Method Not Allowed' }), {
          status: 405, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }
      if (!glmKey) {
        return new Response(JSON.stringify({ error: 'GLM_API_KEY not configured' }), {
          status: 500, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }
      try {
        const body = await request.json();
        const resp = await fetch(GLM_URL, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${glmKey}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: body.model || 'glm-4.5-air',
            messages: body.messages,
            temperature: body.temperature ?? 0.7,
            max_tokens: body.max_tokens ?? 2048,
          }),
        });
        if (!resp.ok) {
          const errText = await resp.text();
          return new Response(JSON.stringify({ error: `GLM ${resp.status}: ${errText.substring(0, 200)}` }), {
            status: resp.status, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          });
        }
        const data = await resp.json();
        return new Response(JSON.stringify(data), {
          status: 200, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 502, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }
    }

    // ── AI 调用：Worker 直连 GLM ──
    if (url.pathname.startsWith('/api/ai/')) {
      if (request.method !== 'POST') {
        return new Response(JSON.stringify({ error: 'Method Not Allowed' }), {
          status: 405, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }
      try {
        const body = await request.json();
        const route = url.pathname;
        let model = 'glm-4.5-air';
        let messages = [];

        // ── 统一对话接口 ──
        if (route === '/api/ai/chat') {
          const today = new Date().toISOString().split('T')[0];
          const history = body.history || [];
          messages = [
            { role: 'system', content: CHAT_SYSTEM + `\n当前日期: ${today}` },
            ...history,
            { role: 'user', content: body.prompt || body.text || '你好' },
          ];
          const raw = await callGLM(glmKey, messages, model, 0.3);
          const data = extractJSON(raw);
          return new Response(JSON.stringify(data), {
            status: 200, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          });
        }

        // ── 计划生成 ──
        if (route === '/api/ai/generate-plan') {
          messages = [
            { role: 'system', content: PLAN_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        // ── 任务生成 ──
        else if (route === '/api/ai/generate-tasks') {
          messages = [
            { role: 'system', content: PLAN_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        // ── 卡片生成 ──
        else if (route === '/api/ai/generate-cards') {
          messages = [
            { role: 'system', content: PLAN_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        // ── 每日复盘 ──
        else if (route === '/api/ai/generate-review') {
          messages = [
            { role: 'system', content: PLAN_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        // ── 解析任务 ──
        else if (route === '/api/ai/parse-tasks') {
          messages = [
            { role: 'system', content: STRICT_JSON_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        // ── 识别教材 ──
        else if (route === '/api/ai/analyze-syllabus') {
          model = 'glm-4.1v-thinking-flashx';
          messages = body.messages || [
            { role: 'user', content: [{ type: 'image_url', image_url: { url: body.image } }, { type: 'text', text: body.prompt }] },
          ];
        }
        else {
          return new Response(JSON.stringify({ error: `Unknown AI route: ${route}` }), {
            status: 404, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          });
        }

        const rawResult = await callGLM(glmKey, messages, model, body.temperature);
        const data = extractJSON(rawResult);
        return new Response(JSON.stringify(data), {
          status: 200, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message || 'AI service unavailable' }), {
          status: 502, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }
    }

    // ── 普通 API：转发到 Vercel ──
    if (url.pathname.startsWith('/api/')) {
      const BACKEND = 'https://server-ten-eosin-90.vercel.app';
      const backendUrl = `${BACKEND}${url.pathname}${url.search}`;
      const headers = new Headers(request.headers);
      headers.delete('host');
      const init = { method: request.method, headers, redirect: 'follow' };
      if (request.method !== 'GET' && request.method !== 'HEAD') {
        init.body = await request.arrayBuffer();
      }
      try {
        const response = await fetch(backendUrl, init);
        const resHeaders = new Headers(response.headers);
        resHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(response.body, { status: response.status, statusText: response.statusText, headers: resHeaders });
      } catch (err) {
        return new Response(JSON.stringify({ detail: 'Backend unreachable' }), {
          status: 502, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }
    }

    return env.ASSETS.fetch(request);
  },
};
