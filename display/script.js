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
    const next = Array.isArray(events) ? events[0] : null;
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
  const res = await fetch('config.json');
  const config = await res.json();
  await applyConfig(config);
}

window.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'gigdash-config') {
    applyConfig(event.data.config);
  }
});

init();
