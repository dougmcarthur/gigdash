// Cloudflare Pages Function backing the single hosted GigDash config.
//
// GET  /api/config  -> returns the current config (public; the display and
//                      the Pi read this). Falls back to the bundled
//                      config.json default when nothing has been saved yet.
// PUT  /api/config  -> saves the config to KV. Requires the editor token in
//                      an "Authorization: Bearer <token>" header, compared
//                      against the EDITOR_TOKEN secret.
//
// Bindings expected on the Pages project:
//   - KV namespace bound as GIGDASH_CONFIG
//   - Secret EDITOR_TOKEN (the edit password)

const KEY = 'config';

function cors(extra = {}) {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    ...extra,
  };
}

const json = (extra = {}) => cors({ 'Content-Type': 'application/json', ...extra });

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: cors() });
}

export async function onRequestGet({ env, request }) {
  const stored = env.GIGDASH_CONFIG ? await env.GIGDASH_CONFIG.get(KEY) : null;
  if (stored) {
    return new Response(stored, { headers: json({ 'Cache-Control': 'no-store' }) });
  }
  // Nothing saved yet — serve the bundled default so first load still works.
  try {
    const def = await fetch(new URL('/config.json', request.url));
    if (def.ok) {
      return new Response(await def.text(), { headers: json({ 'Cache-Control': 'no-store' }) });
    }
  } catch (_) {
    // fall through
  }
  return new Response('{"slides":[]}', { headers: json({ 'Cache-Control': 'no-store' }) });
}

export async function onRequestPut({ env, request }) {
  const expected = env.EDITOR_TOKEN;
  const provided = (request.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
  if (!expected || provided !== expected) {
    return new Response(JSON.stringify({ error: 'unauthorized' }), { status: 401, headers: json() });
  }
  if (!env.GIGDASH_CONFIG) {
    return new Response(JSON.stringify({ error: 'storage not configured' }), { status: 500, headers: json() });
  }
  const text = await request.text();
  try {
    JSON.parse(text); // reject anything that isn't valid JSON
  } catch (_) {
    return new Response(JSON.stringify({ error: 'invalid json' }), { status: 400, headers: json() });
  }
  await env.GIGDASH_CONFIG.put(KEY, text);
  return new Response(JSON.stringify({ ok: true }), { headers: json() });
}
