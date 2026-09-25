/* ДВА ДРУГА — progressive UX enhancements
   Safe by design: if this script does not run, all content stays visible.
   Respects prefers-reduced-motion. No external dependencies. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Scroll reveal ---------- */
  if (!reduceMotion) {
    var style = document.createElement('style');
    style.textContent =
      '.rv{opacity:0;transform:translateY(26px);' +
      'transition:opacity .7s cubic-bezier(.2,.7,.2,1),transform .7s cubic-bezier(.2,.7,.2,1);will-change:opacity,transform}' +
      '.rv.in{opacity:1;transform:none}';
    document.head.appendChild(style);

    var revealSel = [
      '.service-card-new', '.price-card-new', '.location-card-new',
      '.marina-card', '.adv-item', '.about-stat', '.stat-box',
      '.process-step', '.contact-card', '.section-header',
      '.about-text', '.hero-image-wrap', '.band-quote'
    ].join(',');

    var els = Array.prototype.slice.call(document.querySelectorAll(revealSel));
    els.forEach(function (el, i) {
      el.classList.add('rv');
      el.style.transitionDelay = (Math.min(i % 6, 5) * 70) + 'ms';
    });

    if (!('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('in'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
      els.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---------- Count-up for stat numbers ---------- */
  function animateCount(el) {
    var txt = el.textContent.trim();
    var m = txt.match(/^([^\d]*)(\d+(?:[.,]\d+)?)(.*)$/);
    if (!m) return;
    var pre = m[1], target = parseFloat(m[2].replace(',', '.')), suf = m[3];
    var decimals = (m[2].indexOf('.') > -1 || m[2].indexOf(',') > -1) ? 1 : 0;
    if (reduceMotion) { return; }
    var dur = 1100, start = null;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var cur = (target * eased).toFixed(decimals);
      el.textContent = pre + cur + suf;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = pre + m[2] + suf;
    }
    requestAnimationFrame(step);
  }

  var numSel = '.stat-item h3,.about-stat .as-num,.stat-box .num,.floating-card h3';
  var nums = Array.prototype.slice.call(document.querySelectorAll(numSel));
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io2 = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { animateCount(e.target); io2.unobserve(e.target); }
      });
    }, { threshold: 0.5 });
    nums.forEach(function (el) { io2.observe(el); });
  }
})();
