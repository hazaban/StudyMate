/**
 * Cloudflare Pages Function — API proxy to Vercel backend.
 *
 * All /api/* requests are proxied through Cloudflare's backbone network
 * to the Vercel serverless backend, bypassing potential IP blocks on
 * mobile carriers.
 */
export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  // Target backend
  const BACKEND = 'https://server-ten-eosin-90.vercel.app';
  const backendUrl = `${BACKEND}${url.pathname}${url.search}`;

  // Forward the request — preserve method, headers, and body
  const headers = new Headers(request.headers);
  // Let Cloudflare set the Host header correctly
  headers.delete('host');

  const init = {
    method: request.method,
    headers,
    redirect: 'follow',
  };

  // Only attach a body for methods that support it
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = await request.arrayBuffer();
  }

  try {
    const response = await fetch(backendUrl, init);

    // Build the proxied response
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
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      }
    );
  }
}
