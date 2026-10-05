const puppeteer = require('puppeteer-core');
/* Browser tests for the built site (v2/).
   Run:  1) python -m http.server 8080   (in the project folder)
         2) cd tests && npm install && node site-test.js
   Override the address with  BASE=http://localhost:8080/v2/ node site-test.js
   Uses the locally installed Google Chrome (CHROME env var to change the path). */
const BASE = process.env.BASE || 'http://localhost:8080/v2/';
const results = [];
const ok = (name, cond, extra = '') => results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  | ' + extra : ''}`);

(async () => {
  const browser = await puppeteer.launch({ executablePath: process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: 'new' });
  const page = await browser.newPage();
  const consoleErrors = [];
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push(page.url() + ' :: ' + m.text()); });
  page.on('pageerror', e => consoleErrors.push(page.url() + ' :: ' + e.message));

  // ---------- menu ----------
  await page.setViewport({ width: 390, height: 800, isMobile: true, hasTouch: true });
  await page.goto(BASE, { waitUntil: 'networkidle2' });
  await page.click('.burger');
  let st = await page.evaluate(() => ({ open: document.getElementById('menu').classList.contains('open'), lock: document.body.classList.contains('lock'), exp: document.querySelector('.burger').getAttribute('aria-expanded') }));
  ok('menu opens on burger', st.open && st.lock && st.exp === 'true', JSON.stringify(st));
  await page.keyboard.press('Escape');
  st = await page.evaluate(() => ({ open: document.getElementById('menu').classList.contains('open'), lock: document.body.classList.contains('lock') }));
  ok('menu closes on Escape, scroll unlocked', !st.open && !st.lock, JSON.stringify(st));
  await page.click('.burger');
  await new Promise(r => setTimeout(r, 350)); // let the .25s fade-in finish, as a real tap would
  await page.click('.menu .close');
  st = await page.evaluate(() => document.getElementById('menu').classList.contains('open'));
  ok('menu closes on close button', !st);

  // ---------- header over hero ----------
  const before = await page.evaluate(() => document.querySelector('.nav').classList.contains('solid'));
  await page.evaluate(() => window.scrollTo(0, 600));
  await new Promise(r => setTimeout(r, 200));
  const after = await page.evaluate(() => document.querySelector('.nav').classList.contains('solid'));
  ok('header turns solid after scroll', !before && after, `before=${before} after=${after}`);

  // ---------- calculator ----------
  await page.goto(BASE + 'pricing.html', { waitUntil: 'networkidle2' });
  const read = () => page.evaluate(() => ({ sum: document.querySelector('#calc .sum').textContent, note: document.querySelector('#calc .note').textContent, href: decodeURIComponent(document.querySelector('#calc .b.wa').href) }));
  const pick = async (name, value) => { await page.click(`input[name="${name}"][value="${value}"] + span`); return read(); };
  let c = await read();
  ok('calc default: Complete, up to 10 m, Herceg Novi = 90 €', c.sum === '90 €' && /окончательная/.test(c.note), JSON.stringify(c));
  c = await pick('pkg', '165');
  ok('calc Premium = 165 €', c.sum === '165 €', c.sum);
  c = await pick('place', 'kotor');
  ok('calc Kotor adds +20 € = 185 €', c.sum === '185 €' && /165 € \+ выезд 20 €/.test(c.note), c.sum + ' / ' + c.note);
  c = await pick('place', 'tivat');
  ok('calc Tivat adds +15 € = 180 €', c.sum === '180 €', c.sum);
  c = await pick('len', '1');
  ok('calc 10-15 m Premium Tivat = 250 + 15 = 265 €', c.sum === '265 €', c.sum);
  ok('calc message has total', /Итого: 265 €/.test(c.href) && /10–15 м/.test(c.href) && /Тиват/.test(c.href), c.href.slice(0, 180));
  c = await pick('len', '2');
  ok('calc 15-20 m Premium Tivat = 330 + 15 = 345 €', c.sum === '345 €', c.sum);
  c = await pick('pkg', '60');
  ok('calc 15-20 m Basic Tivat = 120 + 15 = 135 €', c.sum === '135 €', c.sum);
  c = await pick('place', 'other');
  ok('calc elsewhere: base price + "depends on spot" note, total marked "+ ?"', c.sum === '120 €' && /зависит от места/.test(c.note) && /Итого: 120 € \+ \?/.test(c.href), c.sum + ' / ' + c.note);
  c = await pick('len', '3');
  ok('calc over 20 m = individual, no price in message', c.sum === 'Индивидуально' && /по фото/.test(c.note) && !/Итого/.test(c.href) && !/\d+ €/.test(c.href), JSON.stringify(c));

  // ---------- price table ----------
  const table = await page.evaluate(() => [...document.querySelectorAll('.ptable tbody tr')].map(r => [...r.children].map(td => td.textContent.trim())));
  ok('price table matches agreed tiers', JSON.stringify(table.slice(0, 3)) === JSON.stringify([['до 10 м', '60 €', '90 €', '165 €'], ['10–15 м', '90 €', '135 €', '250 €'], ['15–20 м', '120 €', '180 €', '330 €']]), JSON.stringify(table));

  // ---------- request form ----------
  await page.goto(BASE + 'contact.html', { waitUntil: 'networkidle2' });
  await page.evaluate(() => { window.__opened = []; window.open = (u) => { window.__opened.push(u); return null; }; });
  await page.type('#request input[data-k="Длина"]', '12');
  await page.click('#request button[type="submit"]');
  let opened = await page.evaluate(() => window.__opened.map(decodeURIComponent));
  ok('form opens WhatsApp once', opened.length === 1, String(opened.length));
  const msg = opened[0] || '';
  ok('form message has hello, place, package, length', /Заявка с сайта/.test(msg) && /Место: Херцег-Нови/.test(msg) && /Пакет: Базовый/.test(msg) && /Длина: 12/.test(msg), msg.replace(/\n/g, ' / '));
  ok('form skips empty optional fields', !/Марина:|Комментарий:|Дата:/.test(msg));

  // ---------- crawl: links, overflow, console ----------
  const seen = new Set(), queue = [BASE], broken = [], overflow = [];
  await page.setViewport({ width: 360, height: 740, isMobile: true, hasTouch: true });
  while (queue.length) {
    const url = queue.shift();
    if (seen.has(url)) continue;
    seen.add(url);
    const resp = await page.goto(url, { waitUntil: 'networkidle2' }).catch(e => null);
    if (!resp || resp.status() >= 400) { broken.push(url + ' -> ' + (resp ? resp.status() : 'ERR')); continue; }
    const info = await page.evaluate(() => ({
      over: document.documentElement.scrollWidth - window.innerWidth,
      links: [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.startsWith(location.origin + '/v2/')),
      imgs: [...document.querySelectorAll('[data-bg]')].map(e => getComputedStyle(e).backgroundImage),
    }));
    if (info.over > 1) overflow.push(`${url} (+${info.over}px)`);
    for (const bgi of info.imgs) if (!bgi || bgi === 'none') broken.push(url + ' -> element with data-bg has no background');
    for (const l of info.links) { const u = l.split('#')[0]; if (!seen.has(u)) queue.push(u); }
  }
  // make sure the photos actually decode (not just referenced)
  const imgFail = [];
  for (const u of [...seen].filter(u => /\/(en|sr)\/|v2\/$/.test(u)).slice(0, 3)) {
    await page.goto(u, { waitUntil: 'networkidle0' });
    const bad = await page.evaluate(async () => {
      const urls = [...document.querySelectorAll('[data-bg]')].map(e => getComputedStyle(e).backgroundImage.slice(5, -2));
      const res = await Promise.all(urls.map(src => new Promise(r => { const i = new Image(); i.onload = () => r(null); i.onerror = () => r(src); i.src = src; })));
      return res.filter(Boolean);
    });
    imgFail.push(...bad);
  }
  ok(`crawl: ${seen.size} pages, no broken links/pages`, broken.length === 0, broken.slice(0, 5).join(' ; '));
  ok('no horizontal overflow at 360px', overflow.length === 0, overflow.slice(0, 5).join(' ; '));
  ok('all background photos decode', imgFail.length === 0, imgFail.slice(0, 3).join(' ; '));
  ok('no console errors', consoleErrors.filter(e => !/maps|google|gstatic/i.test(e)).length === 0, consoleErrors.slice(0, 4).join(' ; '));

  await browser.close();
  console.log(results.join('\n'));
})().catch(e => { console.error('TEST CRASH', e); process.exit(1); });
