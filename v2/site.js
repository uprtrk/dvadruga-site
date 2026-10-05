/* ДВА ДРУГА — menu, header, price calculator, request form. No dependencies. */
(function () {
  'use strict';

  /* ---- header: solid background once the hero is scrolled past ---- */
  var nav = document.querySelector('.nav.over');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('solid', window.scrollY > 40); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---- full-screen menu ---- */
  var menu = document.getElementById('menu');
  var opener = document.querySelector('.burger');
  function setMenu(open) {
    if (!menu) return;
    menu.classList.toggle('open', open);
    menu.setAttribute('aria-hidden', open ? 'false' : 'true');
    if (opener) opener.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.classList.toggle('lock', open);
    if (open) { var c = menu.querySelector('.close'); if (c) c.focus(); }
    else if (opener) opener.focus();
  }
  if (opener) opener.addEventListener('click', function () { setMenu(true); });
  if (menu) {
    menu.querySelector('.close').addEventListener('click', function () { setMenu(false); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('open')) setMenu(false);
    });
  }

  /* ---- analytics: count clicks on contact links (GoatCounter, only if enabled in build.py) ---- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a || !window.goatcounter || !window.goatcounter.count) return;
    var h = a.getAttribute('href'), kind = /wa\.me/.test(h) ? 'whatsapp' : /t\.me/.test(h) ? 'telegram' : /^tel:/.test(h) ? 'phone' : /^mailto:/.test(h) ? 'email' : '';
    if (kind) window.goatcounter.count({ path: 'click-' + kind, title: location.pathname, event: true });
  });

  var PHONE = '38267551020';
  function waLink(text) { return 'https://wa.me/' + PHONE + '?text=' + encodeURIComponent(text); }
  function checkedLabel(form, name) {
    var el = form.querySelector('input[name="' + name + '"]:checked');
    return el ? el.parentNode.querySelector('span').textContent.trim() : '';
  }

  /* ---- price calculator (prices and travel supplements come from build.py via data-*) ---- */
  var calc = document.getElementById('calc');
  if (calc) {
    var d = calc.dataset, prices = JSON.parse(d.prices), travel = JSON.parse(d.travel);
    var sum = calc.querySelector('.sum'), note = calc.querySelector('.note'), btn = calc.querySelector('.b.wa');
    var val = function (name) { return calc.querySelector('input[name="' + name + '"]:checked').value; };
    var update = function () {
      var tier = +val('len'), place = val('place');
      var base = prices[val('pkg')][tier];            // undefined for "over 20 m"
      var trip = travel.hasOwnProperty(place) ? travel[place] : null;  // null for "elsewhere in the bay"
      var notes = [], total = null;
      if (base === undefined) {
        sum.textContent = d.individual;
        notes.push(d.noteBig);
        if (trip === null) notes.push(d.noteOther);
      } else {
        total = base + (trip || 0);
        sum.textContent = total + ' €';
        if (trip) notes.push(d.noteTrip.replace('{p}', base).replace('{t}', trip));
        if (trip === null) notes.push(d.noteOther); else notes.push(d.noteOk);
      }
      note.textContent = notes.join(' ');
      var msg = d.hello + ' ' + [checkedLabel(calc, 'pkg'), checkedLabel(calc, 'len'), checkedLabel(calc, 'place')].join(', ') + '.';
      if (total !== null) msg += ' ' + d.total + ': ' + total + ' €' + (trip === null ? ' + ?' : '') + '.';
      btn.href = waLink(msg);
    };
    calc.addEventListener('change', update);
    update();
  }

  /* ---- request form -> WhatsApp ---- */
  var form = document.getElementById('request');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = form.dataset, lines = [d.hello];
      form.querySelectorAll('[data-k]').forEach(function (f) {
        var v = f.tagName === 'SELECT' ? f.options[f.selectedIndex].text : f.value.trim();
        if (v) lines.push(f.dataset.k + ': ' + v);
      });
      window.open(waLink(lines.join('\n')), '_blank', 'noopener');
    });
  }
})();
