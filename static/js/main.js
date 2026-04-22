// ── Navbar scroll effect ─────────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 10);
});

// ── Mobile menu ────────────────────────────────────────────────────────
document.getElementById('hamburger')?.addEventListener('click', () => {
  document.querySelector('.nav-links').classList.toggle('open');
});

// ── Toast helper ────────────────────────────────────────────────────────
function showToast(msg, icon = 'fa-check-circle') {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast'; t.className = 'toast';
    document.body.appendChild(t);
  }
  t.innerHTML = `<i class="fas ${icon} toast-icon"></i><span>${msg}</span>`;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

// ── Animate progress bars ────────────────────────────────────────────────
function animateBars() {
  document.querySelectorAll('.progress-fill[data-width]').forEach(el => {
    setTimeout(() => { el.style.width = el.dataset.width + '%'; }, 100);
  });
}

// ── Chart.js global defaults ─────────────────────────────────────────────
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#8fa38f';
  Chart.defaults.borderColor = '#2a3f2a';
  Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
  Chart.defaults.font.size = 11;
}

// ── API helper ───────────────────────────────────────────────────────────
async function apiPost(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}

// ── Number counter animation ─────────────────────────────────────────────
function animateCount(el, target, duration = 800, decimals = 2) {
  const start = Date.now();
  const tick = () => {
    const p = Math.min((Date.now() - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = (target * ease).toFixed(decimals);
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

