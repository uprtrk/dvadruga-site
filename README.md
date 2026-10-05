# Dva Druga — yacht cleaning in Montenegro

Multilingual website for a yacht cleaning and detailing service in the Bay of Kotor (Herceg Novi, Kotor, Tivat).

**Live:** https://2druga.netlify.app

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![Puppeteer](https://img.shields.io/badge/Puppeteer-40B5A4?logo=puppeteer&logoColor=white)
![Netlify](https://img.shields.io/badge/Netlify-00C7B7?logo=netlify&logoColor=white)

<table>
  <tr>
    <td width="72%"><img src="docs/desktop.jpg" alt="Desktop"></td>
    <td width="28%"><img src="docs/mobile.jpg" alt="Mobile"></td>
  </tr>
</table>

## Highlights

- **Static site generator in one Python file** (`src/build.py`): all texts live there, one run writes 27 pages.
- **Three languages with real URLs:** RU at `/`, EN at `/en/`, SR at `/sr/`, with `hreflang` links between them.
- **Price calculator:** package × yacht length × location, the total goes straight into a prefilled WhatsApp message.
- **Local SEO:** a landing page per city plus a service-zones page, per-page title / description / OpenGraph / canonical, `LocalBusiness` JSON-LD, `sitemap.xml`.
- **Performance:** self-hosted Onest font split by subset, responsive image thumbnails generated with Pillow, content-hash cache busting, long-lived cache headers (`_headers`).
- **Browser tests** (`tests/site-test.js`, Puppeteer): menu, calculator math for every tier, order form, link crawl over all pages, no horizontal overflow at 360 px, no console errors.

## Structure

```
src/        generator, styles, script, fonts, extra photos
v2/         generated site (this is what Netlify publishes)
tests/      Puppeteer browser tests
*.jpg/png   source photos used by the generator
```

## Build and test

```bash
pip install pillow
python src/build.py              # writes v2/

python -m http.server 8080       # in the project folder
cd tests && npm install && npm test
```

Deploy: `v2/` is uploaded to Netlify as-is (`netlify.toml` → `publish = "v2"`).

---

**По-русски:** сайт сервиса мойки и ухода за яхтами в Боке Которской. Генератор на Python собирает 27 страниц на трёх языках (RU / EN / SR), калькулятор цены с отправкой заявки в WhatsApp, отдельные страницы под каждый город, SEO-разметка LocalBusiness, браузерные тесты на Puppeteer, деплой на Netlify.

Автор: Telegram [@uprtrk](https://t.me/uprtrk)
