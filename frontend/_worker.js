/**
 * Cloudflare Pages Advanced Mode Worker.
 *
 * - /api/ai/* → Worker 直接调智谱 GLM，绕过 Vercel 超时限制
 * - /api/*    → 代理到 Vercel 后端（数据库 CRUD）
 * - 其他      → 静态文件（SPA）
 */
const GLM_KEY = 'ca8557521ff444d2b511fc1c45026e9d.h3wmWjhZyvfWhOiU';
const GLM_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions';

const SYSTEM_PROMPT = `你是 StudyMate 学习星球的 AI 备考助手。你是专业、耐心、有洞察力的学习导师。
输出格式要求：严格返回 JSON，不要包含 markdown 代码块标记，不要有额外解释。`;

async function callGLM(messages, model, temperature) {
  const resp = await fetch(GLM_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GLM_KEY}`,
      'Content-Type': 'application/json',
    },
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

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // ── AI 调用：Worker 直接调 GLM ──
    if (url.pathname.startsWith('/api/ai/')) {
      // 只允许 POST
      if (request.method !== 'POST') {
        return new Response(JSON.stringify({ error: 'Method Not Allowed' }), {
          status: 405,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }

      try {
        const body = await request.json();
        const route = url.pathname;

        let model = 'glm-4.5-air';
        let messages = [];

        if (route === '/api/ai/generate-plan') {
          // 生成学习计划
          messages = [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: body.prompt },
          ];
        } else if (route === '/api/ai/generate-tasks') {
          // 生成每日任务
          messages = [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: body.prompt },
          ];
        } else if (route === '/api/ai/generate-cards') {
          // 生成知识卡片
          messages = [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: body.prompt },
          ];
        } else if (route === '/api/ai/generate-review') {
          // 每日复盘
          messages = [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: body.prompt },
          ];
        } else if (route === '/api/ai/parse-tasks') {
          // 解析文字计划为结构化任务
          model = 'glm-4.5-air';
          messages = [
            { role: 'system', content: '你是 Strict JSON 输出器。只输出合法 JSON，不要任何解释。' },
            { role: 'user', content: body.prompt },
          ];
        } else if (route === '/api/ai/analyze-syllabus') {
          // 图片识别章节
          model = 'glm-4.1v-thinking-flashx';
          messages = body.messages || [
            { role: 'user', content: [{ type: 'image_url', image_url: { url: body.image } }, { type: 'text', text: body.prompt }] },
          ];
        } else {
          return new Response(JSON.stringify({ error: `Unknown AI route: ${route}` }), {
            status: 404,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          });
        }

        const result = await callGLM(messages, model, body.temperature);
        let data;
        try {
          // Try to parse as JSON
          const cleaned = result.replace(/```(?:json)?\s*\n?/g, '').trim();
          data = JSON.parse(cleaned);
        } catch (e) {
          // Return raw text if not valid JSON
          data = { text: result };
        }

        return new Response(JSON.stringify(data), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      } catch (err) {
        return new Response(
          JSON.stringify({ error: err.message || 'AI service unavailable' }),
          { status: 502, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
        );
      }
    }

    // ── 普通 API：转发到 Vercel 后端 ──
    if (url.pathname.startsWith('/api/')) {
      const BACKEND = 'https://server-ten-eosin-90.vercel.app';
      const backendUrl = `${BACKEND}${url.pathname}${url.search}`;

      const headers = new Headers(request.headers);
      headers.delete('host');

      const init = {
        method: request.method,
        headers,
        redirect: 'follow',
      };
      if (request.method !== 'GET' && request.method !== 'HEAD') {
        init.body = await request.arrayBuffer();
      }

      try {
        const response = await fetch(backendUrl, init);
        const resHeaders = new Headers(response.headers);
        resHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: resHeaders,
        });
      } catch (err) {
        return new Response(
          JSON.stringify({ detail: 'Backend unreachable — please try again later.' }),
          { status: 502, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
        );
      }
    }

    // ── 静态文件 ──
    return env.ASSETS.fetch(request);
  },
};
