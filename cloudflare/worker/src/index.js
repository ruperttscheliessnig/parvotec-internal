/**
 * Parvotec Private Content Worker
 *
 * Architecture:
 *   Browser → Cloudflare Access (auth) → this Worker → R2 bucket → HTML
 *
 * Cloudflare Access has already verified the user before this Worker runs.
 * The CF-Access-Authenticated-User-Email header can be trusted.
 * We use HTMLRewriter to strip gate.js (no longer needed server-side).
 */

const CONTENT_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.json': 'application/json',
  '.webp': 'image/webp',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.svg':  'image/svg+xml',
  '.pdf':  'application/pdf',
};

// Strips gate.js script tags from HTML served from R2.
// Cloudflare Access handles auth — client-side gate is redundant.
class GateJsRemover {
  element(el) { el.remove(); }
}

function contentType(path) {
  const ext = path.substring(path.lastIndexOf('.'));
  return CONTENT_TYPES[ext] ?? 'application/octet-stream';
}

function r2Key(pathname) {
  // Strip /private/ prefix if routed via that path
  let key = pathname.startsWith('/private/')
    ? pathname.slice('/private/'.length)
    : pathname.replace(/^\//, '');

  // Default index
  if (key === '' || key.endsWith('/')) key += 'index.html';
  return key;
}

function securityHeaders(isHtml) {
  const h = new Headers({
    'X-Content-Type-Options':  'nosniff',
    'X-Frame-Options':         'SAMEORIGIN',
    'Referrer-Policy':         'same-origin',
    'Cache-Control':           'private, no-store, no-cache',
    'X-Robots-Tag':            'noindex, nofollow',
  });
  if (isHtml) {
    h.set('Content-Security-Policy',
      "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:;");
  }
  return h;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const key = r2Key(url.pathname);

    // Only GET/HEAD allowed
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    // Who is the authenticated user? (informational, Access already verified)
    const userEmail = request.headers.get('CF-Access-Authenticated-User-Email') ?? 'unknown';

    let object;
    try {
      object = await env.PRIVATE.get(key);
    } catch (err) {
      console.error(`R2 error for key "${key}":`, err.message);
      return new Response('Internal Server Error', { status: 500 });
    }

    if (!object) {
      return new Response(`Not found: ${key}`, { status: 404 });
    }

    const isHtml = key.endsWith('.html');
    const headers = securityHeaders(isHtml);
    headers.set('Content-Type', contentType(key));
    headers.set('ETag', object.httpEtag);
    headers.set('X-Authenticated-User', userEmail); // visible in DevTools, not to JS

    object.writeHttpMetadata(headers);

    if (request.method === 'HEAD') {
      return new Response(null, { headers });
    }

    const response = new Response(object.body, { headers });

    // Strip client-side gate.js — auth is now Cloudflare Access
    if (isHtml) {
      return new HTMLRewriter()
        .on('script[src*="gate.js"]', new GateJsRemover())
        .on('script[src*="gate-"]',   new GateJsRemover())
        .transform(response);
    }

    return response;
  },
};
