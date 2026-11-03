/* Glass Player — personal CORS proxy (Cloudflare Worker, free tier is plenty).
 *
 * Why: some providers block browsers (CORS) or block http streams on https pages.
 * Your own proxy fetches the stream server-side and re-serves it with CORS headers,
 * so the web player can play it. It also hides your real IP from the provider.
 *
 * Deploy (2 minutes, no tools needed):
 *   1. dash.cloudflare.com → Workers & Pages → Create → Worker → name it e.g. "gp-proxy"
 *   2. Replace the worker code with this file's content → Deploy.
 *   3. Your proxy URL is:  https://gp-proxy.<your-subdomain>.workers.dev/?url=
 *   4. Point Glass Player at it (one time, in the browser where you use the player):
 *        DevTools → Console →  localStorage.setItem('gp-proxy', JSON.stringify('https://gp-proxy.<your-subdomain>.workers.dev/?url='))
 *      The player then tries YOUR proxy first, before the public ones.
 *
 * Only http/https targets are allowed; the proxy is for your own use.
 */
export default {
  async fetch(request) {
    const target = new URL(request.url).searchParams.get('url');
    if (!target) return new Response('Glass Player proxy — use ?url=<stream url>', { status: 200 });
    let url;
    try { url = new URL(target); } catch { return new Response('bad url', { status: 400 }); }
    if (!/^https?:$/.test(url.protocol)) return new Response('only http/https', { status: 400 });

    const headers = new Headers(request.headers);
    headers.delete('host');
    headers.delete('referer');            // don't leak where the player is hosted
    headers.set('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36');

    let upstream;
    try {
      upstream = await fetch(url.toString(), { method: request.method, headers, redirect: 'follow' });
    } catch (e) {
      return new Response('upstream failed: ' + e.message, { status: 502 });
    }

    const out = new Headers(upstream.headers);
    out.set('Access-Control-Allow-Origin', '*');
    out.set('Access-Control-Expose-Headers', '*');
    return new Response(upstream.body, { status: upstream.status, headers: out });
  },
};
