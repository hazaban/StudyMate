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
- plan: 生成完整学习计划（含阶段划分、每周目标）
- task: 把自然语言拆成结构化任务
- syllabus: 分析教材目录（支持图片或文字目录）
- review: 学习复盘总结
- chat: 一般对话

**输出格式**：必须返回合法JSON（不含markdown标记）：
{
  "summary": "对用户的自然语言回复",
  "tool": "plan|task|syllabus|review|chat",
  "data": { ... }
}

**各工具data格式**：
- plan: {"phases":[{name,description,duration_days,focus:[],daily_schedule}],"weekly_goals":[],"review_strategy":"","subjects":[{name,target_score,chapters:[{name,daily_duration,estimated_days}]}]}
- task: {"tasks":[{content,subject,chapter,duration,type,date,start_hour,repeat_type,selected}]}
  ⚠️ duration必须是整数分钟（2小时=120，半小时=30），type必须是"new_study"/"review"/"mistake"，repeat_type必须是"none"
- syllabus: {"subject":"","chapters":[{name,daily_duration,estimated_days}],"total_days":N,"suggestion":""}
- review: {"summary":"","highlights":[],"improvements":[],"tomorrow_focus":[],"mood_suggestion":""}
- chat: {}

**═══ 引导式规划协议 ═══**

当用户表达"制定学习计划/帮我规划/备考"等意图时，**不要**直接 tool=plan，而是按以下4个阶段逐步引导：

阶段标记：在 summary 末尾附上「◆1/4 基本信息」格式的标记，前端据此显示进度条。

**阶段1 — 基本信息**
summary: 友好问候 + 询问3个问题（考试名称、考试日期、每天能学几小时）
标记: ◆1/4 基本信息
用户回答后 → 进入阶段2。用户说"跳过/不知道"→ 用默认值进入阶段2。

**阶段2 — 科目设置**
summary: 确认上一阶段收集的信息 + 询问有哪些科目及各科目标分数（如"数学 130"）
标记: ◆2/4 科目设置
用户回答后 → 解析科目列表，进入阶段3。用户说"跳过/没有"→ 科目留空进入阶段3。

**阶段3 — 章节确认**
先问用户："需要为每个科目设置具体章节吗？输入具体章节可以帮你生成更精准的计划，也可以说"跳过"。
标记: ◆3/4 章节确认

- 用户说"跳过/不需要/不用了" → 直接进入阶段4
- 用户说"好的/需要/可以" → 逐科目询问（一次只问一个科目）：
    "【数据结构】有哪些章节？（如：数组、链表、栈、树、图）"
    标记: ◆3/4 数据结构(1/N)
  用户回答 → 记录该科目章节，继续下一个科目
  用户说"这个跳过" → 该科目章节留空，继续下一个
  用户说"剩下的都跳过" → 剩余科目全部留空，进入阶段4
  所有科目问完后 → 进入阶段4

**阶段4 — 汇总生成**
整理前3阶段收集的所有信息，一次性调用 tool=plan 生成完整计划。
data 中必须包含 subjects 数组，每个科目含 name、target_score、chapters。
summary: 总结收集到的信息 + 提示用户可以点击"确认应用此计划"写入数据库。
标记: ◆4/4 汇总生成

**重要**：
- 阶段标记只在 tool=chat 或 tool=plan 时附加（tool=task/syllabus 时不加）
- 用户在中途插入其他请求（如"先帮我加个任务"）→ 正常处理，但处理完后在对话结尾询问"继续制定计划吗？"
- 如果对话历史中已有足够信息，可自动跳过已完成阶段

**其他规则**：
- 纯粹问候/咨询 → tool=chat
- 具体学习安排描述 → tool=task
- 目录/章节/框架/图片 → tool=syllabus
- 复盘/总结 → tool=review`;

async function callGLM(apiKey, messages, model, temperature, maxTokens = 2048) {
  if (!apiKey) throw new Error('GLM_API_KEY 未配置，请在 Cloudflare Pages 环境变量中设置');
  const resp = await fetch(GLM_URL, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: model || 'glm-4.5-air',
      messages,
      temperature: temperature ?? 0.3,
      max_tokens: maxTokens,
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
        let maxTokens = 2048;

        // ── 统一对话接口 ──
        if (route === '/api/ai/chat') {
          const today = new Date().toISOString().split('T')[0];
          const history = body.history || [];
          messages = [
            { role: 'system', content: CHAT_SYSTEM + `\n当前日期: ${today}` },
            ...history,
            { role: 'user', content: body.prompt || body.text || '你好' },
          ];
          maxTokens = 4096; // plan 生成需要更多 token 空间
          const raw = await callGLM(glmKey, messages, model, 0.3, maxTokens);
          const data = extractJSON(raw);
          return new Response(JSON.stringify(data), {
            status: 200, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          });
        }

        // ── 计划生成 ──
        if (route === '/api/ai/generate-plan') {
          maxTokens = 3072; // 计划生成需要更多token输出
          messages = [
            { role: 'system', content: PLAN_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        else if (route === '/api/ai/generate-tasks') {
          maxTokens = 2048;
          messages = [
            { role: 'system', content: PLAN_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        else if (route === '/api/ai/generate-cards') {
          maxTokens = 1024;
          messages = [
            { role: 'system', content: PLAN_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        else if (route === '/api/ai/generate-review') {
          maxTokens = 1024;
          messages = [
            { role: 'system', content: PLAN_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        else if (route === '/api/ai/parse-tasks') {
          maxTokens = 1024;
          messages = [
            { role: 'system', content: STRICT_JSON_SYSTEM },
            { role: 'user', content: body.prompt },
          ];
        }
        // ── 任务解析（TaskFormModal AI添加 调用，单数路由）──
        else if (route === '/api/ai/parse-task') {
          const today = new Date().toISOString().split('T')[0];
          const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];
          const text = body.text || '';
          const image = body.image || '';
          const prompt = `当前日期：${today}，明天：${tomorrow}

用户输入：
${text}

请把以上文字拆成结构化任务列表。每个任务必须包含：
- content: 20字以内的简洁摘要
- subject: 科目名
- chapter: 章节名（提到了就提取，没提填空字符串""）
- duration: 分钟数整数，**用户说"小时"必须换算成分钟**（如"2小时"=120，"1.5小时"=90，"半小时"=30，没提则默认30）
- type: "new_study"/"review"/"mistake"
- date: YYYY-MM-DD（明天=${tomorrow}，今天或无时间词=${today}）
- start_hour: 0-23整数（默认9，**上午=8-12，下午=13-17，晚上=18-22**）
- repeat_type: "none"
- selected: true

返回JSON：{"tasks":[{"content":"复习二叉树","subject":"数据结构","chapter":"二叉树","duration":45,"type":"review","date":"${today}","start_hour":9,"repeat_type":"none","selected":true}]}`;

          if (image) {
            model = 'glm-4.1v-thinking-flashx';
            maxTokens = 2048;
            messages = [
              { role: 'system', content: STRICT_JSON_SYSTEM },
              { role: 'user', content: [
                { type: 'image_url', image_url: { url: image } },
                { type: 'text', text: prompt }
              ]}
            ];
          } else {
            maxTokens = 1024;
            messages = [
              { role: 'system', content: STRICT_JSON_SYSTEM },
              { role: 'user', content: prompt }
            ];
          }
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

        const rawResult = await callGLM(glmKey, messages, model, body.temperature, maxTokens);
        let data = extractJSON(rawResult);

        // 格式归一化：确保输出匹配前端预期格式
        if (route === '/api/ai/parse-tasks' || route === '/api/ai/parse-task') {
          if (!data.tasks) {
            // GLM 返回了单个对象或非标准格式 → 包裹为 tasks 数组
            if (Array.isArray(data)) {
              data = { tasks: data };
            } else if (data.content || data.title) {
              data = { tasks: [data] };
            } else {
              data = { tasks: [] };
            }
          }
        } else if (route === '/api/ai/generate-plan' || route === '/api/ai/generate-tasks') {
          if (!data.phases && !data.tasks && data.text) {
            // GLM 返回纯文本 → 包裹
            data = route.includes('plan') ? { phases: [], overview: data.text } : { tasks: [], summary: data.text };
          }
        } else if (route === '/api/ai/generate-cards') {
          if (!data.cards) data = { cards: Array.isArray(data) ? data : [] };
        }
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
