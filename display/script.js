// GigDash audience display: renders a config-driven card carousel and
// applies logo/card animation variants. Config comes from config.json by
// default, but can be overridden live via postMessage (used by the editor
// preview) or query-string params (used for variant previews).

const params = new URLSearchParams(location.search);
const LOGO_VARIANTS = ['sheen', 'breathe', 'glow', 'none'];
const CARD_VARIANTS = ['pulse', 'ring', 'sparkle', 'border', 'none'];

let rotateTimer = null;
let current = 0;
const gigCache = new Map();

async function fetchNextGig({ artistName, appId }) {
  if (!artistName || !appId) return null;
  const cacheKey = `${artistName}::${appId}`;
  if (gigCache.has(cacheKey)) return gigCache.get(cacheKey);
  try {
    const url = `https://rest.bandsintown.com/artists/${encodeURIComponent(artistName)}/events?app_id=${appId}`;
    const res = await fetch(url);
    const events = await res.json();
    const list = Array.isArray(events) ? events : [];
    // Skip a show happening today — that's the gig being played right now,
    // not an upcoming one worth advertising. Bandsintown datetimes are the
    // venue's local wall-clock time, so compare local calendar dates.
    const now = new Date();
    const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    const next = list.find((ev) => ev.datetime && ev.datetime.slice(0, 10) !== todayStr) || null;
    const gig = next
      ? {
          date: new Date(next.datetime).toLocaleDateString(undefined, {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
          }),
          venue: next.venue?.name || '',
          location: [next.venue?.city, next.venue?.region].filter(Boolean).join(', '),
          url: next.url || '',
        }
      : null;
    gigCache.set(cacheKey, gig);
    return gig;
  } catch (err) {
    console.error('Bandsintown fetch failed', err);
    gigCache.set(cacheKey, null);
    return null;
  }
}

function sparkles() {
  return `<span class="sparkle sparkle-1"></span><span class="sparkle sparkle-2"></span>` +
         `<span class="sparkle sparkle-3"></span><span class="sparkle sparkle-4"></span>`;
}

function cardInner(slide) {
  if (slide.type === 'next-gig') {
    const gig = slide._gig;
    return `
      <p class="card-eyebrow">${slide.caption || 'Next Show'}</p>
      <p class="gig-date">${gig.date}</p>
      <p class="gig-venue">${gig.venue}</p>
      <p class="gig-location">${gig.location}</p>
      ${sparkles()}
    `;
  }
  return `
    <img class="card-image" src="${slide.image}" alt="${slide.alt || slide.caption || ''}">
    <p class="card-caption">${slide.caption || ''}</p>
    ${sparkles()}
  `;
}

function renderSlides(slides) {
  const carousel = document.querySelector('.card-carousel');
  carousel.innerHTML = '';
  current = 0;
  slides.forEach((slide, i) => {
    const el = document.createElement(slide.url && slide.type !== 'next-gig' ? 'a' : 'div');
    el.className = 'carousel-card' + (i === 0 ? ' is-active' : '');
    if (el.tagName === 'A') {
      el.href = slide.url;
      el.setAttribute('aria-label', slide.caption || '');
    }
    const face = document.createElement('div');
    face.className = 'card-face' + (slide.type === 'next-gig' ? ' card-face-text' : '');
    face.innerHTML = cardInner(slide);
    el.appendChild(face);
    carousel.appendChild(el);
  });
}

function rotate() {
  const cards = document.querySelectorAll('.carousel-card');
  if (cards.length < 2) return;
  cards[current].classList.remove('is-active');
  current = (current + 1) % cards.length;
  cards[current].classList.add('is-active');
}

async function applyConfig(config) {
  const logo = LOGO_VARIANTS.includes(params.get('logo')) ? params.get('logo') : config.logoAnimation || 'sheen';
  const card = CARD_VARIANTS.includes(params.get('qr')) ? params.get('qr') : config.cardAnimation || 'border';
  document.body.dataset.logo = logo;
  document.body.dataset.qr = card;

  const qrWidth = parseFloat(params.get('qrWidth'));
  if (!isNaN(qrWidth) && qrWidth >= 0) {
    document.body.style.setProperty('--qr-border-width', `${qrWidth}px`);
  } else if (config.qrBorderWidth != null) {
    document.body.style.setProperty('--qr-border-width', `${config.qrBorderWidth}px`);
  }

  // Resolve next-gig slides, dropping any with no upcoming event (e.g.
  // offline, or nothing booked) so the carousel never shows a dead slide.
  const resolved = [];
  for (const slide of config.slides || []) {
    if (slide.type === 'next-gig') {
      const gig = await fetchNextGig(slide.bandsintown || {});
      if (gig) resolved.push({ ...slide, _gig: gig });
    } else {
      resolved.push(slide);
    }
  }

  renderSlides(resolved);

  if (rotateTimer) clearInterval(rotateTimer);
  if (params.get('carousel') !== 'off' && resolved.length > 1) {
    rotateTimer = setInterval(rotate, config.carouselIntervalMs || 18000);
  }
}

async function init() {
  try {
    const res = await fetch('config.json');
    const config = await res.json();
    await applyConfig(config);
  } catch (err) {
    console.error('Failed to load config.json', err);
    document.querySelector('.card-carousel').innerHTML =
      '<div class="carousel-card is-active"><div class="card-face card-face-text">' +
      '<p class="card-eyebrow">Config error</p>' +
      '<p class="gig-venue">Could not load config.json</p>' +
      '</div></div>';
  }
}

window.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'gigdash-config') {
    applyConfig(event.data.config);
  }
});

// Fullscreen toggle. On desktop and Android the Fullscreen API drops the
// browser chrome directly. On iPad, Safari exposes no Fullscreen API for
// arbitrary elements, so the button is hidden there and the standalone
// "Add to Home Screen" launch (see the manifest + apple meta tags) is the
// way to run chrome-free.
function setupFullscreen() {
  const btn = document.querySelector('.fullscreen-toggle');
  if (!btn) return;

  const el = document.documentElement;
  const request =
    el.requestFullscreen || el.webkitRequestFullscreen || el.webkitRequestFullScreen;
  const exit = document.exitFullscreen || document.webkitExitFullscreen;
  const fsElement = () => document.fullscreenElement || document.webkitFullscreenElement;

  // Already running standalone (launched from the Home Screen) — there's no
  // chrome to escape, so the control would be noise.
  const standalone =
    window.matchMedia('(display-mode: fullscreen)').matches ||
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true;

  // Embedded (e.g. the editor's preview iframe): no chrome of our own to
  // toggle, and cross-frame fullscreen is blocked anyway.
  const embedded = window.self !== window.top;

  if (!request || standalone || embedded) return;

  btn.hidden = false;

  btn.addEventListener('click', () => {
    if (fsElement()) {
      if (exit) exit.call(document);
    } else {
      const p = request.call(el);
      if (p && typeof p.catch === 'function') {
        p.catch((err) => console.error('Fullscreen request failed', err));
      }
    }
  });

  const sync = () => document.body.classList.toggle('is-fullscreen', !!fsElement());
  document.addEventListener('fullscreenchange', sync);
  document.addEventListener('webkitfullscreenchange', sync);
}

// Screen Wake Lock: keep the display awake for unattended kiosk use
// (iPadOS Safari 16.4+, plus desktop Chrome/Edge). The OS releases the lock
// whenever the page is hidden — screen off, app switch, tab change — so we
// re-acquire it every time the page becomes visible again. This is a backup
// to the device's own Auto-Lock: Never setting, not a replacement for it.
function setupWakeLock() {
  if (!('wakeLock' in navigator)) return;

  let sentinel = null;

  const acquire = async () => {
    if (document.visibilityState !== 'visible') return;
    try {
      sentinel = await navigator.wakeLock.request('screen');
      sentinel.addEventListener('release', () => { sentinel = null; });
    } catch (err) {
      // Rejected e.g. on low battery or when not user-visible; harmless.
      console.error('Wake lock request failed', err);
    }
  };

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && !sentinel) acquire();
  });

  acquire();
}

setupFullscreen();
setupWakeLock();
init();
