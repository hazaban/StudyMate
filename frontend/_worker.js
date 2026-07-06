/**
 * Cloudflare Pages Advanced Mode Worker.
 *
 * All /api/* requests are proxied through Cloudflare's backbone to the Vercel
 * backend, bypassing IP blocks that affect mobile carriers.
 * All other requests are served as static assets (SPA).
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Proxy API calls to the Vercel backend via Cloudflare backbone
    if (url.pathname.startsWith('/api/')) {
      // AI代理：通过Cloudflare边缘节点直连国内智谱API
      if (url.pathname.startsWith('/api/ai-proxy/')) {
        const GLM_PATH = url.pathname.replace('/api/ai-proxy', '');
        const GLM_URL = `https://open.bigmodel.cn/api/paas/v4${GLM_PATH}${url.search}`;

        const proxyHeaders = new Headers(request.headers);
        proxyHeaders.set('Host', 'open.bigmodel.cn');

        const proxyInit = {
          method: request.method,
          headers: proxyHeaders,
          redirect: 'follow',
        };
        if (request.method !== 'GET' && request.method !== 'HEAD') {
          proxyInit.body = await request.arrayBuffer();
        }

        try {
          const proxyResp = await fetch(GLM_URL, proxyInit);
          const respHeaders = new Headers(proxyResp.headers);
          respHeaders.set('Access-Control-Allow-Origin', '*');
          return new Response(proxyResp.body, {
            status: proxyResp.status,
            statusText: proxyResp.statusText,
            headers: respHeaders,
          });
        } catch (err) {
          return new Response(
            JSON.stringify({ error: 'GLM unreachable via Cloudflare proxy' }),
            { status: 502, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
          );
        }
      }

      // 普通API：转发到 Vercel 后端
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
        resHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
        resHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: resHeaders,
        });
      } catch (err) {
        return new Response(
          JSON.stringify({ detail: 'Backend unreachable — please try again later.' }),
          {
            status: 502,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          }
        );
      }
    }

    // Let Cloudflare serve static files (SPA)
    return env.ASSETS.fetch(request);
  },
};
