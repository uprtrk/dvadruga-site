/* ДВА ДРУГА — shared site behaviour: language, mobile nav, navbar.
   Loaded synchronously as the first element of <body> so the saved
   language is applied before any content paints (no flash of Russian). */
(function () {
  'use strict';

  var LANGS = { ru: '', en: 'english', sr: 'serbian' };

  function readLang() {
    try {
      var l = localStorage.getItem('preferredLanguage');
      return LANGS.hasOwnProperty(l) ? l : 'ru';
    } catch (e) { return 'ru'; }
  }

  function applyLang(lang) {
    var body = document.body;
    body.classList.remove('english', 'serbian');
    if (LANGS[lang]) body.classList.add(LANGS[lang]);
    document.documentElement.lang = lang;
  }

  function syncButtons(lang) {
    document.querySelectorAll('.lang-btn-nav').forEach(function (b) {
      b.classList.toggle('active', b.textContent.trim().toLowerCase() === lang);
    });
  }

  window.switchLanguage = function (lang) {
    if (!LANGS.hasOwnProperty(lang)) lang = 'ru';
    applyLang(lang);
    syncButtons(lang);
    try { localStorage.setItem('preferredLanguage', lang); } catch (e) {}
  };

  window.toggleMobileNav = function () {
    var nav = document.getElementById('mobileNav');
    var btn = document.getElementById('hamburgerBtn') || document.getElementById('hamburger');
    if (!nav) return;
    var open = nav.classList.toggle('open');
    if (btn) btn.classList.toggle('open', open);
    document.body.style.overflow = open ? 'hidden' : '';
  };

  var initial = readLang();
  applyLang(initial);

  document.addEventListener('DOMContentLoaded', function () {
    syncButtons(initial);
    var navbar = document.getElementById('navbar');
    if (navbar) {
      var onScroll = function () { navbar.classList.toggle('scrolled', window.scrollY > 50); };
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }
  });
})();
