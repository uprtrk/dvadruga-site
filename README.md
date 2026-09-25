# Dva Druga — yacht cleaning in Montenegro

Multilingual website for a yacht cleaning and detailing service in the Bay of Kotor (Herceg Novi, Kotor, Tivat).

**Live:** https://2druga.netlify.app

![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![Netlify](https://img.shields.io/badge/Netlify-00C7B7?logo=netlify&logoColor=white)

<table>
  <tr>
    <td width="72%"><img src="docs/desktop.jpg" alt="Desktop"></td>
    <td width="28%"><img src="docs/mobile.jpg" alt="Mobile"></td>
  </tr>
</table>

## Highlights

- **Three languages (RU / EN / SR)** with a switcher in the navbar, no framework and no build step.
- **8 pages:** home, services, pricing, about, contact, plus a landing page for each city (local SEO).
- **SEO:** unique title / description / OpenGraph / canonical per page, `LocalBusiness` JSON-LD with prices and service areas, `sitemap.xml`, `robots.txt`.
- **Performance:** images moved out of inline base64 into files, which cut total HTML from ~1.8 MB to ~0.3 MB.
- **Progressive enhancement:** scroll reveals and count-up counters in a small `enhance.js`, respecting `prefers-reduced-motion`.
- **Conversion:** WhatsApp / Telegram / phone contacts on every page.

## Run

Static site: open `index.html`, or serve the folder:

```bash
python -m http.server 8000
```

---

**По-русски:** сайт сервиса мойки и ухода за яхтами в Боке Которской. Чистый HTML/CSS/JS, три языка, отдельные страницы под каждый город, SEO-разметка LocalBusiness, деплой на Netlify.

Автор: Telegram [@uprtrk](https://t.me/uprtrk)
