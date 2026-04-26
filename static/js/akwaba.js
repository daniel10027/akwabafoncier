// AkwabaFoncier — Main JS

document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss alerts after 5s
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s, transform 0.5s';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 500);
    }, 5000);
  });

  // Active nav link
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-nav a').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });

  // Number formatting for stats
  document.querySelectorAll('.stat-value').forEach(el => {
    const n = parseInt(el.textContent.replace(/\D/g, ''));
    if (!isNaN(n) && n > 999) {
      animateCount(el, n);
    }
  });

});

function animateCount(el, target) {
  const original = el.textContent;
  let current = 0;
  const duration = 1200;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(timer);
      el.textContent = original;
      return;
    }
    el.textContent = Math.floor(current).toLocaleString();
  }, 16);
}

// Confirm dangerous actions
function confirmAction(msg) {
  return confirm(msg || 'Êtes-vous sûr de vouloir effectuer cette action ?');
}

// Copy to clipboard
function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = '✓ Copié';
    btn.style.color = 'var(--green)';
    setTimeout(() => { btn.textContent = orig; btn.style.color = ''; }, 2000);
  });
}

// Mobile sidebar toggle
function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}

// Form validation
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', function (e) {
    const required = form.querySelectorAll('[required]');
    let valid = true;
    required.forEach(el => {
      if (!el.value.trim()) {
        el.style.borderColor = 'var(--red)';
        valid = false;
        el.addEventListener('input', () => el.style.borderColor = '', { once: true });
      }
    });
    if (!valid) {
      e.preventDefault();
      const first = form.querySelector('[required]:invalid, [required][style*="red"]');
      if (first) first.focus();
    }
  });
});
