/**
 * script.js - Water Quality AI Frontend Logic
 * Handles: particles, navbar scroll, scroll reveal, tooltips, interactions
 */

'use strict';

// ===========================================================
// 1. FLOATING PARTICLES GENERATOR
// ===========================================================
(function generateParticles() {
  const container = document.getElementById('particles');
  if (!container) return;

  const count = 25;
  for (let i = 0; i < count; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';

    // Random properties
    const size = Math.random() * 3 + 1;
    const left = Math.random() * 100;
    const duration = Math.random() * 15 + 10;
    const delay = Math.random() * 15;
    const opacity = Math.random() * 0.5 + 0.1;

    // Random colors: primary blue or purple
    const colors = ['#00d4ff', '#7c3aed', '#06ffa0', '#3b82f6'];
    const color = colors[Math.floor(Math.random() * colors.length)];

    particle.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${left}%;
      background: ${color};
      animation-duration: ${duration}s;
      animation-delay: -${delay}s;
      opacity: ${opacity};
    `;

    container.appendChild(particle);
  }
})();

// ===========================================================
// 2. NAVBAR SCROLL EFFECT
// ===========================================================
(function initNavbar() {
  const navbar = document.getElementById('mainNavbar');
  if (!navbar) return;

  let ticking = false;

  window.addEventListener('scroll', function () {
    if (!ticking) {
      requestAnimationFrame(function () {
        if (window.scrollY > 50) {
          navbar.classList.add('scrolled');
        } else {
          navbar.classList.remove('scrolled');
        }
        ticking = false;
      });
      ticking = true;
    }
  });
})();

// ===========================================================
// 3. SCROLL REVEAL ANIMATION
// ===========================================================
(function initScrollReveal() {
  const revealElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  if (revealElements.length === 0) return;

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          // Optionally unobserve after reveal
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: '0px 0px -60px 0px'
    }
  );

  revealElements.forEach(function (el) {
    observer.observe(el);
  });
})();

// ===========================================================
// 4. BOOTSTRAP TOOLTIPS INITIALIZATION
// ===========================================================
(function initTooltips() {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipTriggerList.forEach(function (el) {
    new bootstrap.Tooltip(el, {
      trigger: 'hover focus',
      boundary: 'window'
    });
  });
})();

// ===========================================================
// 5. NUMBER COUNTER ANIMATION (for stat cards)
// ===========================================================
function animateCounter(element, target, duration, suffix) {
  const start = 0;
  const startTime = performance.now();
  const isFloat = target % 1 !== 0;

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Easing: ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = start + (target - start) * eased;

    element.textContent = (isFloat ? current.toFixed(1) : Math.floor(current)).toLocaleString() + suffix;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = (isFloat ? target.toFixed(1) : target).toLocaleString() + suffix;
    }
  }

  requestAnimationFrame(update);
}

// Trigger counter animation when stat cards enter viewport
(function initCounters() {
  const statNumbers = document.querySelectorAll('.stat-number, .metric-value');
  if (statNumbers.length === 0) return;

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const el = entry.target;
          const text = el.textContent.trim();
          // Extract number and suffix
          const match = text.match(/^([0-9,\.]+)(.*)$/);
          if (match) {
            const num = parseFloat(match[1].replace(/,/g, ''));
            const suffix = match[2] || '';
            if (!isNaN(num) && num > 0) {
              animateCounter(el, num, 1500, suffix);
            }
          }
          observer.unobserve(el);
        }
      });
    },
    { threshold: 0.5 }
  );

  statNumbers.forEach(function (el) {
    observer.observe(el);
  });
})();

// ===========================================================
// 6. FORM INTERACTION ENHANCEMENTS
// ===========================================================
(function initFormEnhancements() {
  // Add focus visual feedback to param cards
  document.querySelectorAll('.form-control-custom').forEach(function (input) {
    input.addEventListener('focus', function () {
      this.closest('.param-card')?.classList.add('focused');
    });
    input.addEventListener('blur', function () {
      this.closest('.param-card')?.classList.remove('focused');
    });

    // Real-time validation feedback
    input.addEventListener('input', function () {
      const val = parseFloat(this.value);
      const min = parseFloat(this.getAttribute('min'));
      const max = parseFloat(this.getAttribute('max'));
      const card = this.closest('.param-card');

      if (this.value === '') {
        card?.classList.remove('has-error', 'has-success');
      } else if (isNaN(val) || val < min || val > max) {
        card?.classList.add('has-error');
        card?.classList.remove('has-success');
      } else {
        card?.classList.remove('has-error');
        card?.classList.add('has-success');
      }
    });
  });

  // Add has-success CSS if not already defined
  const style = document.createElement('style');
  style.textContent = `
    .param-card.has-success {
      border-color: rgba(34, 197, 94, 0.4) !important;
      background: rgba(34, 197, 94, 0.03) !important;
    }
    .param-card.focused {
      border-color: rgba(0, 212, 255, 0.5) !important;
    }
  `;
  document.head.appendChild(style);
})();

// ===========================================================
// 7. SMOOTH ANCHOR SCROLL
// ===========================================================
document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ===========================================================
// 8. AUTO-DISMISS FLASH MESSAGES
// ===========================================================
(function autoDismissAlerts() {
  const alerts = document.querySelectorAll('.alert-glass');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease, max-height 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(function () {
        alert.style.display = 'none';
      }, 500);
    }, 5000); // Auto-dismiss after 5 seconds
  });
})();

// ===========================================================
// 9. RESULT PAGE - ANIMATED CONFIDENCE BAR
// ===========================================================
(function animateResultBars() {
  // Trigger confidence bar animation
  const confBar = document.getElementById('confBar');
  if (confBar) {
    const targetWidth = confBar.style.width;
    confBar.style.width = '0%';
    setTimeout(function () {
      confBar.style.transition = 'width 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
      confBar.style.width = targetWidth;
    }, 400);
  }
})();

// ===========================================================
// 10. COPY TO CLIPBOARD (for API info)
// ===========================================================
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(function () {
    showToast('Disalin ke clipboard!', 'success');
  }).catch(function () {
    // Fallback
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    showToast('Disalin!', 'success');
  });
}

// ===========================================================
// 11. SIMPLE TOAST NOTIFICATION
// ===========================================================
function showToast(message, type) {
  type = type || 'info';
  const colors = {
    success: 'rgba(34,197,94,0.15)',
    danger: 'rgba(239,68,68,0.15)',
    info: 'rgba(0,212,255,0.15)',
    warning: 'rgba(245,158,11,0.15)'
  };
  const borderColors = {
    success: 'rgba(34,197,94,0.4)',
    danger: 'rgba(239,68,68,0.4)',
    info: 'rgba(0,212,255,0.4)',
    warning: 'rgba(245,158,11,0.4)'
  };

  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: ${colors[type]};
    border: 1px solid ${borderColors[type]};
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 0.875rem;
    font-weight: 600;
    color: #f0f4ff;
    backdrop-filter: blur(20px);
    z-index: 9999;
    animation: toastIn 0.3s ease;
    font-family: 'Inter', sans-serif;
  `;
  toast.textContent = message;

  // Add animation keyframes
  if (!document.getElementById('toastStyle')) {
    const s = document.createElement('style');
    s.id = 'toastStyle';
    s.textContent = `
      @keyframes toastIn { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
      @keyframes toastOut { from { opacity:1; transform:translateY(0); } to { opacity:0; transform:translateY(20px); } }
    `;
    document.head.appendChild(s);
  }

  document.body.appendChild(toast);
  setTimeout(function () {
    toast.style.animation = 'toastOut 0.3s ease forwards';
    setTimeout(function () { document.body.removeChild(toast); }, 300);
  }, 3000);
}

// ===========================================================
// 12. PAGE LOAD COMPLETE
// ===========================================================
window.addEventListener('load', function () {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.4s ease';
  setTimeout(function () {
    document.body.style.opacity = '1';
  }, 10);
});

console.log('%c Water Quality AI ', 'background:#00d4ff;color:#060918;font-weight:900;font-size:14px;padding:4px 8px;border-radius:4px;');
console.log('%c Built with Flask + Scikit-Learn + Bootstrap 5', 'color:#94a3b8;font-size:12px;');
