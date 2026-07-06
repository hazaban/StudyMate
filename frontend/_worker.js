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
