/* ─── Toast System ─────────────────────────────────── */
const Toast = (() => {
  let container;

  function getContainer() {
    if (!container) {
      container = document.getElementById('toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
      }
    }
    return container;
  }

  function show(message, type = 'info', duration = 3500) {
    const c = getContainer();
    const icons = {
      success: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
      error:   `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
      info:    `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`,
    };

    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = `
      <div class="toast-icon">${icons[type] || icons.info}</div>
      <span style="flex:1;font-weight:500">${message}</span>
    `;
    c.appendChild(el);

    setTimeout(() => {
      el.classList.add('exiting');
      el.addEventListener('animationend', () => el.remove(), { once: true });
    }, duration);
  }

  return { show, success: (m, d) => show(m, 'success', d), error: (m, d) => show(m, 'error', d), info: (m, d) => show(m, 'info', d) };
})();

/* ─── Scroll Animations (Intersection Observer) ────── */
function initScrollAnimations() {
  const targets = document.querySelectorAll('.anim-target');
  if (!targets.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const anim = el.dataset.anim || 'anim-fade-up';
        const delay = el.dataset.delay || '0';
        el.style.animationDelay = delay + 's';
        el.classList.add(anim);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  targets.forEach(el => observer.observe(el));
}

/* ─── Navbar Scroll Effect ─────────────────────────── */
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 30);
  }, { passive: true });
}

/* ─── Mobile Menu ──────────────────────────────────── */
function initMobileMenu() {
  const toggle = document.getElementById('menu-toggle');
  const menu   = document.getElementById('mobile-menu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!toggle.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove('open');
    }
  });
}

/* ─── Typing Animation ─────────────────────────────── */
function initTypingAnimation(elementId, words, speed = { type: 100, delete: 55, pause: 1800 }) {
  const el = document.getElementById(elementId);
  if (!el) return;

  let wordIdx = 0, charIdx = 0, isDeleting = false;

  function tick() {
    const word = words[wordIdx];
    if (isDeleting) {
      el.textContent = word.substring(0, charIdx - 1);
      charIdx--;
      if (charIdx === 0) {
        isDeleting = false;
        wordIdx = (wordIdx + 1) % words.length;
        setTimeout(tick, 400);
        return;
      }
    } else {
      el.textContent = word.substring(0, charIdx + 1);
      charIdx++;
      if (charIdx === word.length) {
        isDeleting = true;
        setTimeout(tick, speed.pause);
        return;
      }
    }
    setTimeout(tick, isDeleting ? speed.delete : speed.type);
  }

  setTimeout(tick, 700);
}

/* ─── Copy to Clipboard ────────────────────────────── */
async function copyToClipboard(text, btn) {
  try {
    await navigator.clipboard.writeText(text);
    const orig = btn.innerHTML;
    btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!`;
    btn.style.color = '#4ade80';
    setTimeout(() => { btn.innerHTML = orig; btn.style.color = ''; }, 2000);
    Toast.success('Summary copied to clipboard!');
  } catch {
    Toast.error('Failed to copy — please copy manually.');
  }
}

/* ─── Download as .txt ─────────────────────────────── */
function downloadText(text, filename = 'summary.txt') {
  const blob = new Blob([text], { type: 'text/plain' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  Toast.success('Summary downloaded as summary.txt');
}

/* ─── Init on DOMContentLoaded ─────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initScrollAnimations();
  initNavbar();
  initMobileMenu();
});

window.Toast        = Toast;
window.copyToClipboard  = copyToClipboard;
window.downloadText     = downloadText;
window.initTypingAnimation = initTypingAnimation;
