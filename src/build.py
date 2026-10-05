"""Static site generator for ДВА ДРУГА.

Writes every page in three languages:  RU -> <out>/,  EN -> <out>/en/,  SR -> <out>/sr/
Usage:  python src/build.py [out_dir]      (default: v2)
All texts live in this file; edit here and re-run.
"""
import os, re, shutil, sys, json, hashlib
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, sys.argv[1] if len(sys.argv) > 1 else 'v2')
SITE = 'https://2druga.netlify.app'
PHONE, PHONE_H = '38267551020', '+382 67 551 020'
TG, MAIL = 'uprtrk', '2drugamonte@gmail.com'
LANGS = ['ru', 'en', 'sr']
# GoatCounter site code (free, no cookies): register at goatcounter.com, put the code here, e.g. 'dvadruga'.
ANALYTICS = ''
IMAGES = ['hero-yacht.jpg', 'bay-view.jpg', 'bay-wide.jpg', 'city-hercegnovi.jpg', 'city-kotor.jpg',
          'city-tivat.jpg', 'cover.png', 'logo.png', 'svc-hull.jpg', 'svc-interior.jpg',
          'svc-marina.jpg', 'svc-teak.jpg', 'yacht-side.jpg']

L = 'ru'  # current language during rendering
VER = {}  # content hashes for cache-busting: image stem -> hash, 'style.css'/'site.js' -> hash


def short_hash(path):
    with open(path, 'rb') as fh:
        return hashlib.md5(fh.read()).hexdigest()[:8]


def _(ru, en, sr):
    return {'ru': ru, 'en': en, 'sr': sr}[L]


def pre():  # path prefix from current page to site root
    return '' if L == 'ru' else '../'


def url(slug, lang=None):
    lang = lang or L
    base = '' if lang == 'ru' else lang + '/'
    return base + ('' if slug == 'index' else slug + '.html')


def href(slug):  # link from current page to another page in the same language
    return slug + '.html' if slug != 'index' else './'


def img(name):
    return pre() + 'img/' + name


def bg(name):
    # marks an element for a background photo; the matching CSS (with paths relative to this page)
    # is injected into <head> by with_bg_css(), small WebP on phones and large on wider screens
    return os.path.splitext(name)[0]


def with_bg_css(html):
    stems = sorted(set(re.findall(r'data-bg="([^"]+)"', html)))
    if not stems:
        return html
    small = ''.join(f'[data-bg="{s}"]{{background-image:url("{pre()}img/{s}-s.{VER[s]}.webp")!important}}' for s in stems)
    large = ''.join(f'[data-bg="{s}"]{{background-image:url("{pre()}img/{s}-l.{VER[s]}.webp")!important}}' for s in stems)
    return html.replace('</head>', f'<style>{small}@media (min-width:700px){{{large}}}</style>\n</head>', 1)


def wa(text=None):
    return 'https://wa.me/' + PHONE + ('?text=' + quote(text) if text else '')


# ------------------------------------------------------------------ nav data
def pages_main():
    return [('services', _('Услуги', 'Services', 'Usluge')),
            ('pricing', _('Цены', 'Prices', 'Cene')),
            ('zones', _('Зоны', 'Areas', 'Zone')),
            ('about', _('О нас', 'About', 'O nama')),
            ('contact', _('Контакты', 'Contact', 'Kontakt'))]


def cities():
    return [('herceg-novi', _('Херцег-Нови', 'Herceg Novi', 'Herceg Novi')),
            ('kotor', _('Котор', 'Kotor', 'Kotor')),
            ('tivat', _('Тиват', 'Tivat', 'Tivat'))]


def lang_links(slug):
    out = []
    for lg in LANGS:
        target = pre() + url(slug, lg)
        if target == '':
            target = './'
        cls = ' class="on" aria-current="true"' if lg == L else ''
        out.append(f'<a href="{target}" hreflang="{lg}"{cls}>{lg.upper()}</a>')
    return '<div class="lang">' + ''.join(out) + '</div>'


WA_SVG = ('<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.39-1.47-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.08-.13-.28-.2-.58-.35m-5.42 7.4h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88"/></svg>')

# small original motorboat, side view
BOAT = ('<div class="boat" aria-hidden="true"><svg viewBox="0 0 54 30"><path d="M2 19h48l-5 8H9z" fill="#fff"/>'
        '<path d="M14 19l4-7h16l6 7z" fill="#fff"/><path d="M20 13.5h5v4h-5zM27 13.5h5l2.5 4H27z" fill="#0B3A42"/>'
        '<path d="M24 12V6" stroke="#fff" stroke-width="1.6"/></svg></div>')


def sea(fill):
    # one wave period = 240px; path drawn over 2 periods of the 200%-wide svg so translateX(-50%) loops
    d = 'M0 14 ' + ' '.join(f'Q{60+240*i} 2 {120+240*i} 14 T{240+240*i} 14' for i in range(12)) + ' V30 H0Z'
    return (f'<div class="sea">{BOAT}<svg class="w" viewBox="0 0 2880 30" preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="{d}" fill="{fill}"/></svg></div>')


# ------------------------------------------------------------------ layout
def analytics():
    if not ANALYTICS:
        return ''
    return f'<script data-goatcounter="https://{ANALYTICS}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'


LOGO_MARK = ('<svg class="mark" viewBox="0 0 32 20" aria-hidden="true"><path d="M1 12h28l-3.5 6H5z" fill="currentColor"/>'
             '<path d="M8.5 12l2.5-5h9l3.5 5z" fill="currentColor"/><path d="M0 19.2q4-2 8 0t8 0 8 0 8 0" stroke="currentColor" stroke-width="1.2" fill="none"/></svg>')

def head(slug, title, desc, image=None, jsonld=''):
    image = image or f'og-{L}.jpg'
    alts = ''.join(f'<link rel="alternate" hreflang="{lg}" href="{SITE}/{url(slug, lg)}">' for lg in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}/{url(slug, "ru")}">'
    full = f'{title} | {_("Два Друга", "Dva Druga", "Dva Druga")}'
    return f'''<!DOCTYPE html>
<html lang="{L}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}/{url(slug)}">
{alts}
<meta property="og:type" content="website"><meta property="og:title" content="{full}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}/{url(slug)}"><meta property="og:image" content="{SITE}/img/{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B3A42">
<link rel="icon" href="{pre()}favicon.svg" type="image/svg+xml">
<link rel="preload" href="{pre()}fonts/onest-{'cyrillic' if L == 'ru' else 'latin'}.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre()}style.css?v={VER['style.css']}">
{jsonld}
{analytics()}
</head>
<body>
'''


def header(slug, over=False):
    links = ''.join(f'<a href="{href(s)}"{" class=\"on\"" if s == slug or (s == "zones" and slug in ("herceg-novi","kotor","tivat")) else ""}>{n}</a>'
                    for s, n in pages_main())
    menu_main = ''.join(f'<a href="{href(s)}"{" class=\"on\"" if s == slug else ""}>{n}</a>'
                        for s, n in [('index', _('Главная', 'Home', 'Početna'))] + pages_main())
    menu_city = ''.join(f'<a href="{href(s)}">{n}</a>' for s, n in cities())
    return f'''<header class="nav{' over' if over else ''}"><div class="wrap in">
  <a class="logo" href="{href('index')}">{LOGO_MARK}{_('Два Друга', 'Dva Druga', 'Dva Druga')}</a>
  <nav class="links" aria-label="{_('Основное меню', 'Main menu', 'Glavni meni')}">{links}</nav>
  {lang_links(slug)}
  <button class="burger" type="button" aria-controls="menu" aria-expanded="false" aria-label="{_('Открыть меню', 'Open menu', 'Otvori meni')}"><i></i><span>{_('Меню', 'Menu', 'Meni')}</span></button>
</div></header>
<div class="menu" id="menu" aria-hidden="true" role="dialog" aria-label="{_('Меню', 'Menu', 'Meni')}"><div class="wrap" style="display:flex;flex-direction:column;min-height:100%">
  <div class="top"><span class="logo">{LOGO_MARK}{_('Два Друга', 'Dva Druga', 'Dva Druga')}</span><button class="close" type="button">{_('Закрыть', 'Close', 'Zatvori')} <i>×</i></button></div>
  <div class="cols">
    <div class="col big">{menu_main}</div>
    <div class="col small"><p class="h4">{_('Где работаем', 'Where we work', 'Gde radimo')}</p>{menu_city}</div>
    <div class="col small"><p class="h4">{_('Связаться', 'Get in touch', 'Kontakt')}</p>
      <a href="{wa()}">WhatsApp</a><a href="https://t.me/{TG}">Telegram</a><a href="tel:+{PHONE}">{PHONE_H}</a><a href="mailto:{MAIL}">{MAIL}</a></div>
  </div>
  <div class="bottom">{lang_links(slug)}<span style="opacity:.6">{_('Каждый день сезона, 08:00–20:00', 'Every day of the season, 08:00–20:00', 'Svaki dan sezone, 08:00–20:00')}</span></div>
</div></div>
'''


def contact_block(title=None):
    title = title or _('Пришлите фото яхты — назовём цену', 'Send us a photo of your yacht — we’ll quote a price', 'Pošaljite fotografiju jahte — reći ćemo vam cenu')
    return f'''<section class="contact"><div class="wrap">
  <h2>{title}</h2>
  <div class="ways">
    <a href="{wa()}"><span>WhatsApp</span>{PHONE_H}</a>
    <a href="https://t.me/{TG}"><span>Telegram</span>@{TG}</a>
    <a href="mailto:{MAIL}"><span>Email</span>{MAIL}</a>
  </div>
  <p class="hours">{_('Каждый день сезона, 08:00–20:00 · Херцег-Нови, Черногория', 'Every day of the season, 08:00–20:00 · Herceg Novi, Montenegro', 'Svaki dan sezone, 08:00–20:00 · Herceg Novi, Crna Gora')}</p>
</div></section>
'''


def footer():
    main = ''.join(f'<a href="{href(s)}">{n}</a>' for s, n in pages_main())
    city = ''.join(f'<a href="{href(s)}">{n}</a>' for s, n in cities())
    return f'''<footer><div class="wrap">
  <div class="cols">
    <div><p class="h4">{_('Два Друга', 'Dva Druga', 'Dva Druga')}</p><p>{_('Мойка и уход за яхтами в Которском заливе. Нас двое, мы живём в Херцег-Нови.', 'Yacht washing and care in the Bay of Kotor. Two of us, based in Herceg Novi.', 'Pranje i nega jahti u Kotorskom zalivu. Nas dvojica, iz Herceg Novog.')}</p></div>
    <div><p class="h4">{_('Страницы', 'Pages', 'Stranice')}</p>{main}</div>
    <div><p class="h4">{_('Зоны', 'Areas', 'Zone')}</p>{city}</div>
    <div><p class="h4">{_('Связь', 'Contact', 'Kontakt')}</p><a href="{wa()}">WhatsApp</a><a href="https://t.me/{TG}">Telegram</a><a href="tel:+{PHONE}">{PHONE_H}</a><a href="mailto:{MAIL}">Email</a></div>
  </div>
  <p class="copy">© 2026 {_('Два Друга — мойка яхт в Черногории', 'Dva Druga — yacht cleaning in Montenegro', 'Dva Druga — pranje jahti u Crnoj Gori')}</p>
</div></footer>
<a class="fab" href="{wa(_('Здравствуйте! Хочу узнать про мойку яхты.', 'Hello! I’d like to ask about yacht cleaning.', 'Zdravo! Zanima me pranje jahte.'))}" aria-label="WhatsApp">{WA_SVG}</a>
<script src="{pre()}site.js?v={VER['site.js']}" defer></script>
</body>
</html>
'''


def page_hero(slug, photo, kicker, title, lead, crumbs=None):
    cr = ''
    if crumbs:
        cr = '<div class="crumbs"><a href="' + href('index') + '">' + _('Главная', 'Home', 'Početna') + '</a>' + \
             ''.join(f' / <a href="{href(s)}">{n}</a>' for s, n in crumbs) + '</div>'
    return f'''<section class="phero"><div class="wrap grid">
  <div>{cr}<div class="lbl">{kicker}</div><h1>{title}</h1><p>{lead}</p></div>
  <div class="ph" data-bg="{bg(photo)}" role="img" aria-label="{title}"></div>
</div>{sea('#F7F5F0')}</section>
'''


# ------------------------------------------------------------------ shared content blocks
def services_data():
    return [
        ('hull', 'svc-hull.jpg', _('Корпус', 'Hull', 'Trup'), _('Мойка корпуса', 'Hull wash', 'Pranje trupa'),
         _('Морской шампунь с нейтральным pH и мягкие щётки. Смываем соль, водоросли и налёт, не трогая гелькоут и антикоррозийное покрытие.',
           'pH-neutral marine shampoo and soft brushes. We remove salt, algae and deposits without harming the gelcoat or anti-corrosion coating.',
           'Morski šampon neutralnog pH i meke četke. Uklanjamo so, alge i naslage bez oštećenja gelcoata i antikorozivnog premaza.'),
         [_('Предварительный осмотр корпуса', 'Initial hull inspection', 'Početni pregled trupa'),
          _('Нанесение морского шампуня', 'Marine shampoo application', 'Nanošenje morskog šampona'),
          _('Мягкие щётки — без царапин', 'Soft brushes — scratch-free', 'Meke četke — bez ogrebotina'),
          _('Ополаскивание пресной водой', 'Fresh water rinse', 'Ispiranje slatkom vodom'),
          _('Протирка насухо замшей', 'Chamois dry finish', 'Sušenje jelenskom kožom')]),
        ('interior', 'svc-interior.jpg', _('Салон', 'Interior', 'Unutrašnjost'), _('Уборка внутри', 'Interior cleaning', 'Čišćenje unutrašnjosti'),
         _('Каюты, салон, камбуз и санузлы. Убираем без химии. Цена зависит от того, насколько загрязнён салон, — согласуем её заранее, можно по фото.',
           'Cabins, saloon, galley and heads, cleaned without chemicals. The price depends on how dirty the interior is — we agree it upfront, a photo is enough.',
           'Kabine, salon, kuhinja i sanitarni čvorovi, bez hemije. Cena zavisi od toga koliko je unutrašnjost zaprljana — dogovaramo je unapred, dovoljna je fotografija.'),
         [_('Пылесос и мытьё полов', 'Vacuuming and floor washing', 'Usisavanje i pranje podova'),
          _('Чистка всех поверхностей', 'All surfaces cleaned', 'Čišćenje svih površina'),
          _('Иллюминаторы изнутри', 'Portholes from inside', 'Iluminatori iznutra'),
          _('Санузлы и камбуз', 'Heads and galley', 'WC i kuhinja'),
          _('Устранение запахов', 'Odour removal', 'Uklanjanje mirisa')]),
        ('polish', 'svc-teak.jpg', _('Защита', 'Protection', 'Zaštita'), _('Полировка и защита', 'Polishing & protection', 'Poliranje i zaštita'),
         _('Машинная полировка гелькоута профессиональными пастами, затем защитный воск или жидкое стекло. Держится весь сезон.',
           'Machine polishing of the gelcoat with professional compounds, then protective wax or liquid glass. Lasts the whole season.',
           'Mašinsko poliranje gelcoata profesionalnim pastama, zatim zaštitni vosak ili tečno staklo. Traje celu sezonu.'),
         [_('Оценка состояния покрытия', 'Coating assessment', 'Procena stanja premaza'),
          _('Орбитальная машинная полировка', 'Orbital machine polishing', 'Orbitalno mašinsko poliranje'),
          _('Воск или жидкое стекло', 'Wax or liquid glass', 'Vosak ili tečno staklo'),
          _('Полировка нержавейки', 'Stainless steel polishing', 'Poliranje nerđajućeg čelika'),
          _('Финальный осмотр', 'Final inspection', 'Završni pregled')]),
    ]


# Prices agreed 2026-09-25. Columns: up to 10 m, 10-15 m (x1.5), 15-20 m (x2); over 20 m is quoted from a photo.
PRICE_TABLE = {60: [60, 90, 120], 90: [90, 135, 180], 165: [165, 250, 330]}
# Travel supplement from the Herceg Novi base (Kamenari-Lepetane ferry both ways + fuel + time).
TRAVEL = {'hn': 0, 'tivat': 15, 'kotor': 20}


def size_labels():
    return [_('до 10 м', 'up to 10 m', 'do 10 m'), _('10–15 м', '10–15 m', '10–15 m'),
            _('15–20 м', '15–20 m', '15–20 m'), _('больше 20 м', 'over 20 m', 'preko 20 m')]


def size_table():
    pk = packages()
    head_ = ''.join(f'<th>{n}</th>' for p, n, *_r in pk)
    rows = ''
    for i, lab in enumerate(size_labels()):
        if i < 3:
            cells = ''.join(f'<td>{PRICE_TABLE[p][i]} €</td>' for p, *_r in pk)
        else:
            cells = f'<td colspan="3">{_("по фото — назовём точную цену", "from a photo — we quote an exact price", "po fotografiji — navodimo tačnu cenu")}</td>'
        rows += f'<tr><th scope="row">{lab}</th>{cells}</tr>'
    return (f'<div class="ptable-wrap"><table class="ptable"><caption>{_("Цена по длине яхты", "Price by yacht length", "Cena po dužini jahte")}</caption>'
            f'<thead><tr><th>{_("Длина", "Length", "Dužina")}</th>{head_}</tr></thead><tbody>{rows}</tbody></table></div>')


def packages():
    return [
        (60, _('Базовый', 'Basic', 'Osnovni'), False,
         _('Регулярная мойка корпуса в течение сезона.', 'Regular hull wash through the season.', 'Redovno pranje trupa tokom sezone.'),
         [_('Мойка корпуса', 'Hull wash', 'Pranje trupa'), _('Ополаскивание пресной водой', 'Fresh water rinse', 'Ispiranje slatkom vodom'),
          _('Протирка насухо', 'Dry finish', 'Sušenje'), _('Фотоотчёт владельцу', 'Photo report to the owner', 'Foto izveštaj vlasniku')]),
        (90, _('Комплексный', 'Complete', 'Kompletni'), True,
         _('Корпус и салон за один выезд. Если салон сильно загрязнён, цену согласуем заранее.', 'Hull and interior in one visit. If the interior is heavily soiled, we agree the price upfront.', 'Trup i unutrašnjost u jednom dolasku. Ako je unutrašnjost jako zaprljana, cenu dogovaramo unapred.'),
         [_('Всё из базового', 'Everything in Basic', 'Sve iz Osnovnog'), _('Полная уборка салона', 'Full interior clean', 'Kompletno čišćenje unutrašnjosti'),
          _('Иллюминаторы изнутри', 'Portholes from inside', 'Iluminatori iznutra'), _('Фотоотчёт владельцу', 'Photo report to the owner', 'Foto izveštaj vlasniku')]),
        (165, _('Премиум', 'Premium', 'Premium'), False,
         _('Полный уход с полировкой и защитой на весь сезон.', 'Full care with polishing and season-long protection.', 'Kompletna nega sa poliranjem i zaštitom za celu sezonu.'),
         [_('Всё из комплексного', 'Everything in Complete', 'Sve iz Kompletnog'), _('Машинная полировка корпуса', 'Machine hull polishing', 'Mašinsko poliranje trupa'),
          _('Воск или жидкое стекло', 'Wax or liquid glass', 'Vosak ili tečno staklo'), _('Полировка нержавейки', 'Stainless steel polishing', 'Poliranje nerđajućeg čelika')]),
    ]


def price_cards():
    out = []
    for price, name, main, desc, items in packages():
        msg = _(f'Здравствуйте! Хочу заказать пакет «{name}» ({price} €).', f'Hello! I’d like to book the “{name}” package (€{price}).', f'Zdravo! Želim da naručim paket „{name}” ({price} €).')
        badge = f' <em>{_("берут чаще всего", "most popular", "najčešće biraju")}</em>' if main else ''
        lis = ''.join(f'<li>{i}</li>' for i in items)
        out.append(f'''<div class="card{' main' if main else ''}"><div class="name">{name}{badge}</div><div class="amt">{price} €</div>
      <p class="desc">{desc}</p><ul class="checks">{lis}</ul>
      <a class="b wa" href="{wa(msg)}">{_('Заказать в WhatsApp', 'Book via WhatsApp', 'Naruči preko WhatsApp-a')}</a></div>''')
    return '<div class="cards">' + ''.join(out) + '</div>'


def price_notes():
    return f'''<div class="fine">
    <div><b>{_('Яхта длиннее 10 м', 'Yacht over 10 m', 'Jahta duža od 10 m')}</b>{_('10–15 м — ×1,5 к цене пакета, 15–20 м — ×2. Больше 20 м считаем по фото.', '10–15 m: ×1.5 the package price, 15–20 m: ×2. Over 20 m we quote from a photo.', '10–15 m: ×1,5 cene paketa, 15–20 m: ×2. Preko 20 m računamo po fotografiji.')}</div>
    <div><b>{_('Выезд', 'Travel', 'Dolazak')}</b>{_('Херцег-Нови — без доплаты. Тиват +15 €, Котор +20 €.', 'Herceg Novi: no supplement. Tivat +€15, Kotor +€20.', 'Herceg Novi — bez doplate. Tivat +15 €, Kotor +20 €.')}</div>
    <div><b>{_('Абонемент на сезон', 'Season subscription', 'Pretplata za sezonu')}</b>{_('Скидка, фиксированный график, приоритетный выезд.', 'A discount, a fixed schedule and priority visits.', 'Popust, fiksni raspored i prioritetni dolazak.')}</div>
  </div>'''


def steps():
    items = [
        (_('Пишете нам', 'You message us', 'Pišete nam'), _('WhatsApp, Telegram или звонок. Укажите марину и размер яхты, можно прислать фото.', 'WhatsApp, Telegram or a call. Tell us the marina and yacht size; a photo helps.', 'WhatsApp, Telegram ili poziv. Navedite marinu i veličinu jahte, može i fotografija.')),
        (_('Называем цену', 'We quote a price', 'Navodimo cenu'), _('Точную, до начала работы. Договариваемся о времени.', 'An exact price before we start. We agree on a time.', 'Tačnu, pre početka rada. Dogovaramo vreme.')),
        (_('Приезжаем', 'We come over', 'Dolazimo'), _('В день заявки, со своим оборудованием. Обычно работа занимает 2–4 часа.', 'The same day, with our own equipment. The job usually takes 2–4 hours.', 'Na dan zahteva, sa svojom opremom. Posao obično traje 2–4 sata.')),
        (_('Фотоотчёт', 'Photo report', 'Foto izveštaj'), _('Присылаем фото результата. Замечания устраняем бесплатно.', 'We send photos of the result. Any remarks are fixed at no charge.', 'Šaljemo fotografije rezultata. Primedbe otklanjamo besplatno.')),
    ]
    return '<div class="steps">' + ''.join(f'<div><h3>{h}</h3><p>{p}</p></div>' for h, p in items) + '</div>'


def city_cards():
    data = [('herceg-novi', 'city-hercegnovi.jpg', _('Portonovi, Igalo, Зеленика, Кумбор', 'Portonovi, Igalo, Zelenika, Kumbor', 'Portonovi, Igalo, Zelenika, Kumbor'), True),
            ('kotor', 'city-kotor.jpg', _('Kotor Marina, Доброта, Прчань', 'Kotor Marina, Dobrota, Prčanj', 'Kotor Marina, Dobrota, Prčanj'), False),
            ('tivat', 'city-tivat.jpg', _('Porto Montenegro, Tivat Marina, Калиман', 'Porto Montenegro, Tivat Marina, Kaliman', 'Porto Montenegro, Tivat Marina, Kaliman'), False)]
    names = dict(cities())
    out = []
    for slug, photo, sub, base in data:
        tag = f'<span class="tag">{_("наша база", "our base", "naša baza")}</span><br>' if base else ''
        out.append(f'<a class="city" href="{href(slug)}" data-bg="{bg(photo)}"><div>{tag}<h3>{names[slug]}</h3><p>{sub}</p>'
                   f'<span class="go">{_("Подробнее", "Learn more", "Saznajte više")} →</span></div></a>')
    return '<div class="cities">' + ''.join(out) + '</div>'


def faq(items):
    return '<div class="faq">' + ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items) + '</div>'


def faq_general():
    return [
        (_('Нужно ли мне быть на борту?', 'Do I need to be on board?', 'Da li moram da budem na brodu?'),
         _('Нет. Договариваемся о доступе к яхте, после работы присылаем фотоотчёт — видно, что сделано, даже если вас не было рядом.', 'No. We agree on access to the yacht and send a photo report afterwards, so you can see the result even if you weren’t there.', 'Ne. Dogovorimo pristup jahti, a posle rada šaljemo foto izveštaj — vidite šta je urađeno i ako niste bili tu.')),
        (_('Как быстро вы приедете?', 'How soon can you come?', 'Koliko brzo dolazite?'),
         _('Обычно в день заявки. Работаем каждый день сезона с 08:00 до 20:00.', 'Usually the same day you book. We work every day of the season, 08:00–20:00.', 'Obično na dan zahteva. Radimo svaki dan sezone od 08:00 do 20:00.')),
        (_('Какие средства вы используете?', 'What products do you use?', 'Koja sredstva koristite?'),
         _('Специальные морские: pH-нейтральные шампуни, мягкие щётки, профессиональные полировальные пасты и защитные воски. Они безопасны для гелькоута и антикоррозийных покрытий.', 'Marine-specific ones: pH-neutral shampoos, soft brushes, professional polishing compounds and protective waxes, all safe for gelcoat and anti-corrosion coatings.', 'Specijalna morska: pH-neutralni šamponi, meke četke, profesionalne paste za poliranje i zaštitni voskovi, bezbedni za gelcoat i antikorozivne premaze.')),
        (_('Моя яхта длиннее 10 метров. Сколько это стоит?', 'My yacht is over 10 metres. What does it cost?', 'Moja jahta je duža od 10 metara. Koliko košta?'),
         _('10–15 м — цена пакета ×1,5, 15–20 м — ×2 (таблица на странице цен). Яхты длиннее 20 м считаем индивидуально: пришлите фото и длину.', '10–15 m costs 1.5× the package price, 15–20 m costs 2× (see the table on the prices page). Over 20 m we price individually — send a photo and the length.', '10–15 m košta 1,5× cenu paketa, 15–20 m 2× (tabela na stranici cena). Preko 20 m računamo individualno — pošaljite fotografiju i dužinu.')),
        (_('Что если мне что-то не понравится?', 'What if I’m not happy with something?', 'Šta ako mi se nešto ne dopadne?'),
         _('Напишите нам — замечания устраняем бесплатно.', 'Just tell us — we fix any remarks at no extra charge.', 'Javite nam — primedbe otklanjamo besplatno.')),
        (_('Есть ли абонемент на сезон?', 'Do you offer a season subscription?', 'Da li imate pretplatu za sezonu?'),
         _('Да. Договариваемся о фиксированном графике на весь сезон — это дешевле разовых заказов, и выезд у вас в приоритете.', 'Yes. We agree on a fixed schedule for the season — it costs less than one-off bookings and you get priority visits.', 'Da. Dogovaramo fiksni raspored za celu sezonu — jeftinije je od pojedinačnih narudžbi i imate prioritet.')),
        (_('Сколько стоит уборка салона отдельно?', 'How much is interior cleaning on its own?', 'Koliko košta samo čišćenje unutrašnjosti?'),
         _('Зависит от того, насколько загрязнён салон. Пришлите фото — согласуем цену заранее. Убираем без химии.', 'It depends on how dirty the interior is. Send us a photo and we’ll agree the price upfront. We clean without chemicals.', 'Zavisi od toga koliko je unutrašnjost zaprljana. Pošaljite fotografiju — cenu dogovaramo unapred. Čistimo bez hemije.')),
    ]


def jsonld_business():
    data = {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": SITE + "/#business",
            "name": "Dva Druga", "alternateName": "ДВА ДРУГА",
            "description": _('Мойка, уборка и полировка яхт в Которском заливе — Херцег-Нови, Котор, Тиват.', 'Yacht washing, cleaning and polishing in the Bay of Kotor — Herceg Novi, Kotor, Tivat.', 'Pranje, čišćenje i poliranje jahti u Kotorskom zalivu — Herceg Novi, Kotor, Tivat.'),
            "url": SITE + "/", "logo": SITE + "/img/logo.png", "image": SITE + "/img/cover.png",
            "telephone": PHONE_H, "email": MAIL, "priceRange": "60€–330€", "currenciesAccepted": "EUR",
            "address": {"@type": "PostalAddress", "addressLocality": "Herceg Novi", "addressRegion": "Boka Kotorska", "addressCountry": "ME"},
            "geo": {"@type": "GeoCoordinates", "latitude": 42.4531, "longitude": 18.5375},
            "areaServed": [{"@type": "City", "name": n} for n in ("Herceg Novi", "Kotor", "Tivat")],
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "08:00", "closes": "20:00"}],
            "makesOffer": [{"@type": "Offer", "name": n, "price": str(p), "priceCurrency": "EUR"} for p, n, *_r in packages()],
            "sameAs": [wa(), "https://t.me/" + TG]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


# ------------------------------------------------------------------ pages
def page_index():
    s = 'index'
    svc_rows = ''
    for sid, photo, lbl, title, text, items in services_data():
        chips = ''.join(f'<span>{i}</span>' for i in items[:4])
        svc_rows += f'''<div class="svc"><div class="ph" data-bg="{bg(photo)}" role="img" aria-label="{title}"></div><div class="tx">
    <div class="lbl">{lbl}</div><h2>{title}</h2><p>{text}</p><div class="chips">{chips}</div>
    <a class="more" href="{href('services')}#{sid}">{_('Подробнее об услуге', 'More about this service', 'Više o usluzi')} →</a></div></div>
'''
    return head(s, _('Мойка яхт в Херцег-Нови, Которе и Тивате', 'Yacht cleaning in Herceg Novi, Kotor and Tivat', 'Pranje jahti u Herceg Novom, Kotoru i Tivtu'),
                _('Мойка корпуса, уборка салона и полировка яхт в Которском заливе. Приедем в день заявки, фотоотчёт после работы. От 60 €.',
                  'Hull washing, interior cleaning and polishing for yachts in the Bay of Kotor. Same-day visits, photo report after every job. From €60.',
                  'Pranje trupa, čišćenje unutrašnjosti i poliranje jahti u Kotorskom zalivu. Dolazimo istog dana, foto izveštaj posle rada. Od 60 €.'),
                jsonld=jsonld_business()) + header(s, over=True) + f'''
<section class="hero" data-bg="{bg('hero-yacht.jpg')}"><div class="wrap">
  <div class="hero-body">
    <h1>{_('Моем яхты в Которском заливе', 'Yacht cleaning in the Bay of Kotor', 'Peremo jahte u Kotorskom zalivu')}</h1>
    <div><p>{_('Приедем в день заявки. Цену скажем до начала работы, фотоотчёт пришлём после.', 'We come the day you call. You get the price before we start and a photo report when we finish.', 'Dolazimo na dan zahteva. Cenu kažemo pre početka, foto izveštaj šaljemo posle.')}</p>
      <div class="btns" style="margin-top:22px"><a class="b light" href="{wa()}">WhatsApp</a><a class="b ghost" href="https://t.me/{TG}">Telegram</a><a class="b ghost" href="tel:+{PHONE}">{_('Позвонить', 'Call', 'Pozovite')}</a></div></div>
  </div>
  <div class="strip"><span>{_('от 60 € за мойку корпуса', 'from €60 for a hull wash', 'od 60 € za pranje trupa')}</span><span>{_('Херцег-Нови · Котор · Тиват', 'Herceg Novi · Kotor · Tivat', 'Herceg Novi · Kotor · Tivat')}</span><span>{_('Каждый день, 08:00–20:00', 'Every day, 08:00–20:00', 'Svaki dan, 08:00–20:00')}</span></div>
</div>{sea('#F7F5F0')}</section>

<section class="sec intro"><div class="wrap"><p>{_('Нас двое, мы живём в Херцег-Нови.', 'There are two of us, and we live in Herceg Novi.', 'Nas je dvojica i živimo u Herceg Novom.')} <span>{_('Никаких субподрядчиков и колл-центров — на каждую яхту приезжаем сами, со своим оборудованием и морскими средствами.', 'No subcontractors, no call centre — we come to every yacht ourselves, with our own equipment and marine-grade products.', 'Bez podizvođača i kol-centara — na svaku jahtu dolazimo lično, sa svojom opremom i morskim sredstvima.')}</span></p></div></section>

<div id="services">
{svc_rows}</div>

<section class="sec sand" id="prices"><div class="wrap">
  <div class="lbl">{_('Цены', 'Prices', 'Cene')}</div>
  <h2 class="h2">{_('Три пакета для яхт до 10 метров', 'Three packages for yachts up to 10 m', 'Tri paketa za jahte do 10 metara')}</h2>
  <p class="sub">{_('Цену фиксируем до начала — после работы сумма не меняется.', 'The price is fixed before we start and doesn’t change afterwards.', 'Cenu fiksiramo pre početka — posle rada se ne menja.')}</p>
  {price_cards()}
  {price_notes()}
  <p style="margin-top:30px"><a class="more" href="{href('pricing')}#calc">{_('Рассчитать стоимость для своей яхты', 'Estimate the price for your yacht', 'Izračunajte cenu za svoju jahtu')} →</a></p>
</div></section>

<section class="sec"><div class="wrap">
  <div class="lbl">{_('Как это работает', 'How it works', 'Kako funkcioniše')}</div>
  <h2 class="h2">{_('От сообщения до чистой яхты — обычно в тот же день', 'From message to clean yacht — usually the same day', 'Od poruke do čiste jahte — obično istog dana')}</h2>
  {steps()}
</div></section>

<section class="sec sand"><div class="wrap">
  <div class="lbl">{_('Где работаем', 'Where we work', 'Gde radimo')}</div>
  <h2 class="h2">{_('Весь Которский залив', 'The whole Bay of Kotor', 'Ceo Kotorski zaliv')}</h2>
  <p class="sub">{_('База в Херцег-Нови, в Котор и Тиват выезжаем каждый день.', 'Based in Herceg Novi, with daily trips to Kotor and Tivat.', 'Baza u Herceg Novom, u Kotor i Tivat dolazimo svakog dana.')}</p>
  {city_cards()}
</div></section>

<section class="sec"><div class="wrap split">
  <div class="ph" data-bg="{bg('yacht-side.jpg')}" role="img" aria-label="{_('Яхта на якоре', 'Yacht at anchor', 'Jahta na sidru')}"></div>
  <div>
    <div class="lbl">{_('О нас', 'About us', 'O nama')}</div>
    <h2 class="h2">{_('Два друга, одно дело', 'Two friends, one job', 'Dva prijatelja, jedan posao')}</h2>
    <p>{_('Несколько лет назад мы начали мыть яхты знакомых — просто потому что умеем делать это хорошо. Потом появились постоянные клиенты, потом нас начали находить сами.', 'A few years ago we started washing yachts for friends — simply because we’re good at it. Regular clients followed, and then people started finding us on their own.', 'Pre nekoliko godina počeli smo da peremo jahte poznanicima — jednostavno zato što to radimo dobro. Zatim su došli stalni klijenti, a onda su nas ljudi počeli sami pronalaziti.')}</p>
    <div class="stats"><div><b>3+</b><span>{_('года в Которском заливе', 'years in the Bay of Kotor', 'godine u Kotorskom zalivu')}</span></div><div><b>7/7</b><span>{_('без выходных в сезон', 'no days off in season', 'bez slobodnih dana u sezoni')}</span></div></div>
    <a class="more" href="{href('about')}">{_('Подробнее о нас', 'More about us', 'Više o nama')} →</a>
  </div>
</div></section>
''' + contact_block() + footer()


def page_services():
    s = 'services'
    rows = ''
    for sid, photo, lbl, title, text, items in services_data():
        lis = ''.join(f'<li>{i}</li>' for i in items)
        rows += f'''<div class="svc" id="{sid}"><div class="ph" data-bg="{bg(photo)}" role="img" aria-label="{title}"></div><div class="tx">
    <div class="lbl">{lbl}</div><h2>{title}</h2><p>{text}</p><ul class="checks">{lis}</ul>
    <div class="btns"><a class="b dark" href="{href('pricing')}">{_('Смотреть цены', 'See prices', 'Pogledajte cene')}</a></div></div></div>
'''
    extras = [
        (_('Тенты и парусина', 'Covers and canvas', 'Tende i cerade'), _('Чистка чехлов, тентов и биминей — аккуратно, без деформации материала.', 'Cleaning of covers, canopies and biminis — carefully, without deforming the fabric.', 'Čišćenje navlaka, tendi i biminija — pažljivo, bez deformacije materijala.')),
        (_('Абонемент на сезон', 'Season subscription', 'Pretplata za sezonu'), _('Фиксированный график на весь сезон. Удобнее и выгоднее разовых заказов.', 'A fixed schedule for the whole season. More convenient and better value than one-off bookings.', 'Fiksni raspored za celu sezonu. Praktičnije i povoljnije od pojedinačnih narudžbi.')),
        (_('Подготовка к продаже', 'Pre-sale preparation', 'Priprema za prodaju'), _('Приводим яхту в товарный вид перед показом покупателям — снаружи и внутри.', 'We get the yacht looking its best before viewings — inside and out.', 'Dovodimo jahtu u najbolji izgled pre pokazivanja kupcima — spolja i iznutra.')),
    ]
    boxes = ''.join(f'<div class="box"><h3>{h}</h3><p>{p}</p></div>' for h, p in extras)
    return head(s, _('Услуги', 'Services', 'Usluge'),
                _('Мойка корпуса, уборка салона, полировка и защита яхт. Тенты, абонемент на сезон, подготовка к продаже.', 'Hull washing, interior cleaning, polishing and protection. Covers, season subscriptions, pre-sale preparation.', 'Pranje trupa, čišćenje unutrašnjosti, poliranje i zaštita jahti. Tende, sezonska pretplata, priprema za prodaju.')) \
        + header(s) + page_hero(s, 'deck-work.jpg', _('Услуги', 'Services', 'Usluge'),
                                _('Что мы делаем', 'What we do', 'Šta radimo'),
                                _('Профессиональный уход за яхтой морскими средствами и оборудованием. Работаем аккуратно и соблюдаем правила марин.', 'Professional yacht care with marine-grade products and equipment. We work carefully and follow marina rules.', 'Profesionalna nega jahte morskim sredstvima i opremom. Radimo pažljivo i poštujemo pravila marina.'),
                                crumbs=[]) + f'''
{rows}
<section class="sec sand"><div class="wrap">
  <div class="lbl">{_('Дополнительно', 'Also', 'Dodatno')}</div>
  <h2 class="h2">{_('Ещё можем помочь с этим', 'We can also help with', 'Možemo pomoći i sa ovim')}</h2>
  <div class="grid3">{boxes}</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="lbl">{_('Порядок работы', 'How it works', 'Redosled rada')}</div>
  <h2 class="h2">{_('Как проходит заказ', 'How a booking works', 'Kako izgleda narudžbina')}</h2>
  {steps()}
</div></section>
<section class="sec sand"><div class="wrap">
  <div class="lbl">FAQ</div><h2 class="h2">{_('Частые вопросы', 'Frequently asked questions', 'Česta pitanja')}</h2>
  {faq(faq_general())}
</div></section>
''' + contact_block() + footer()


def page_pricing():
    s = 'pricing'
    pk = packages()
    pkg_opts = ''.join(f'<label><input type="radio" name="pkg" value="{p}"{" checked" if main else ""}><span>{n}</span></label>' for p, n, main, *_r in pk)
    len_opts = ''.join(f'<label><input type="radio" name="len" value="{i}"{" checked" if i == 0 else ""}><span>{lab}</span></label>' for i, lab in enumerate(size_labels()))
    prices_json = json.dumps({str(k): v for k, v in PRICE_TABLE.items()})
    travel_json = json.dumps(TRAVEL)
    calc = f'''<form class="calc" id="calc" onsubmit="return false"
    data-hello="{_('Здравствуйте! Хочу заказать:', 'Hello! I’d like to book:', 'Zdravo! Želim da naručim:')}"
    data-prices='{prices_json}' data-travel='{travel_json}'
    data-individual="{_('Индивидуально', 'On request', 'Individualno')}"
    data-note-big="{_('Для яхт длиннее 20 м цену считаем по фото — пришлите его в WhatsApp.', 'For yachts over 20 m we price from a photo — send it via WhatsApp.', 'Za jahte duže od 20 m cenu računamo po fotografiji — pošaljite je preko WhatsApp-a.')}"
    data-note-trip="{_('Пакет {p} € + выезд {t} €.', 'Package €{p} + travel €{t}.', 'Paket {p} € + dolazak {t} €.')}"
    data-note-other="{_('Плюс доплата за выезд — назовём её сразу, она зависит от места.', 'Plus a travel supplement, which depends on the spot — we’ll tell you upfront.', 'Plus putni dodatak koji zavisi od mesta — navodimo ga unapred.')}"
    data-note-ok="{_('Цена окончательная — фиксируем её до начала работы.', 'This is the final price, fixed before we start.', 'Ovo je konačna cena, fiksirana pre početka rada.')}"
    data-total="{_('Итого', 'Total', 'Ukupno')}">
  <fieldset><legend>{_('Пакет', 'Package', 'Paket')}</legend><div class="opts">{pkg_opts}</div></fieldset>
  <fieldset><legend>{_('Длина яхты', 'Yacht length', 'Dužina jahte')}</legend><div class="opts">{len_opts}</div></fieldset>
  <fieldset><legend>{_('Где стоит яхта', 'Where is the yacht', 'Gde je jahta')}</legend><div class="opts">
    <label><input type="radio" name="place" value="hn" checked><span>{_('Херцег-Нови', 'Herceg Novi', 'Herceg Novi')}</span></label>
    <label><input type="radio" name="place" value="tivat"><span>{_('Тиват', 'Tivat', 'Tivat')}</span></label>
    <label><input type="radio" name="place" value="kotor"><span>{_('Котор, Доброта, Прчань', 'Kotor, Dobrota, Prčanj', 'Kotor, Dobrota, Prčanj')}</span></label>
    <label><input type="radio" name="place" value="other"><span>{_('Другое место залива', 'Elsewhere in the bay', 'Drugo mesto u zalivu')}</span></label></div></fieldset>
  <div class="result" aria-live="polite"><div class="lbl" style="margin:0">{_('Стоимость', 'Price', 'Cena')}</div><div class="sum">90 €</div><p class="note"></p>
    <div><a class="b wa" href="{wa()}">{_('Отправить заявку в WhatsApp', 'Send request via WhatsApp', 'Pošaljite zahtev preko WhatsApp-a')}</a></div></div>
</form>'''
    pfaq = [faq_general()[3], faq_general()[6], faq_general()[5],
            (_('Сколько стоит выезд в Котор или Тиват?', 'How much is the trip to Kotor or Tivat?', 'Koliko košta dolazak u Kotor ili Tivat?'),
             _('Тиват — +15 €, Котор, Доброта и Прчань — +20 €. В Херцег-Нови доплаты нет. Для других мест залива называем сумму сразу, до начала работы.', 'Tivat is +€15; Kotor, Dobrota and Prčanj are +€20. No supplement in Herceg Novi. For other spots in the bay we tell you the amount upfront.', 'Tivat +15 €, Kotor, Dobrota i Prčanj +20 €. U Herceg Novom nema doplate. Za ostala mesta u zalivu iznos navodimo unapred.')),
            (_('Может ли цена измениться после работы?', 'Can the price change after the job?', 'Da li se cena može promeniti posle rada?'),
             _('Нет. Цену фиксируем до начала, и после работы сумма не меняется.', 'No. We fix the price before we start and it doesn’t change afterwards.', 'Ne. Cenu fiksiramo pre početka i posle rada se ne menja.'))]
    return head(s, _('Цены', 'Prices', 'Cene'),
                _('Цены на мойку яхт: базовый 60 €, комплексный 90 €, премиум 165 €. Калькулятор стоимости, без скрытых платежей.', 'Yacht cleaning prices: Basic €60, Complete €90, Premium €165. Price calculator, no hidden fees.', 'Cene pranja jahti: osnovni 60 €, kompletni 90 €, premium 165 €. Kalkulator cene, bez skrivenih troškova.')) \
        + header(s) + page_hero(s, 'marina-masts.jpg', _('Цены', 'Prices', 'Cene'),
                                _('Честные цены без сюрпризов', 'Fair prices, no surprises', 'Poštene cene bez iznenađenja'),
                                _('Три пакета для яхт до 10 метров. Стоимость фиксируем до начала работы — после сумма не меняется.', 'Three packages for yachts up to 10 m. The price is fixed before we start and doesn’t change.', 'Tri paketa za jahte do 10 metara. Cenu fiksiramo pre početka rada i ne menja se.'),
                                crumbs=[]) + f'''
<section class="sec"><div class="wrap">
  <div class="lbl">{_('Пакеты', 'Packages', 'Paketi')}</div>
  <h2 class="h2">{_('Выберите пакет', 'Choose a package', 'Izaberite paket')}</h2>
  {price_cards()}
  {size_table()}
  {price_notes()}
</div></section>
<section class="sec sand" id="calc-sec"><div class="wrap">
  <div class="lbl">{_('Калькулятор', 'Calculator', 'Kalkulator')}</div>
  <h2 class="h2">{_('Сколько будет стоить у вас', 'What it will cost for you', 'Koliko će koštati kod vas')}</h2>
  <p class="sub">{_('Выберите параметры — покажем цену и соберём заявку для WhatsApp.', 'Pick your options — we’ll show the price and prepare a WhatsApp request.', 'Izaberite opcije — prikazaćemo cenu i pripremiti zahtev za WhatsApp.')}</p>
  {calc}
</div></section>
<section class="sec"><div class="wrap">
  <div class="lbl">FAQ</div><h2 class="h2">{_('Вопросы о ценах', 'Questions about prices', 'Pitanja o cenama')}</h2>
  {faq(pfaq)}
</div></section>
''' + contact_block() + footer()


def city_data(slug):
    if slug == 'herceg-novi':
        return dict(photo='hn-town.jpg', map='Herceg+Novi,+Montenegro',
            kicker=_('Наша база', 'Our base', 'Naša baza'),
            lead=_('Херцег-Нови — наша постоянная база. Работаем здесь каждый день, знаем каждую марину и приезжаем в день заявки.', 'Herceg Novi is our home base. We work here every day, know every marina and come the same day you call.', 'Herceg Novi je naša stalna baza. Radimo ovde svaki dan, poznajemo svaku marinu i dolazimo na dan zahteva.'),
            about=[_('Бухта Херцег-Нови — одно из самых живописных мест Которского залива. Здесь несколько марин совершенно разного характера: от люксового Portonovi до камерного Igalo. На всех работаем с одинаковым вниманием к деталям.', 'The Herceg Novi bay is one of the most scenic parts of the Bay of Kotor, with marinas of very different character — from luxurious Portonovi to intimate Igalo. We work across all of them with the same attention to detail.', 'Zaliv Herceg Novog jedno je od najlepših mesta Kotorskog zaliva, sa marinama potpuno različitog karaktera — od luksuznog Portonovija do intimnog Igala. U svima radimo sa istom pažnjom prema detaljima.'),
                   _('Соль, водоросли и яркое солнце быстро пачкают поверхности яхты. Регулярный уход продлевает жизнь покрытий и сохраняет вид судна весь сезон.', 'Salt, algae and strong sun quickly foul yacht surfaces. Regular care extends coating life and keeps the vessel looking good all season.', 'So, alge i jako sunce brzo prljaju površine jahte. Redovna nega produžava vek premaza i čuva izgled plovila cele sezone.')],
            marinas=[('Marina Portonovi', _('Марина премиум-класса с развитой инфраструктурой и причалами для яхт любого размера. Высокий трафик — нужен регулярный уход.', 'A premium marina with full infrastructure and berths for yachts of any size. Busy traffic means regular care matters.', 'Premium marina sa razvijenom infrastrukturom i vezovima za jahte svih veličina. Veliki promet zahteva redovno održavanje.'),
                      [_('Приедем в день заявки', 'Same-day visits', 'Dolazak na dan zahteva'), _('Яхты от 8 до 40+ метров', 'Yachts from 8 to 40+ m', 'Jahte od 8 do 40+ m')]),
                     ('Igalo', _('Камерная марина в тихом районе. Удобное место для регулярного обслуживания по абонементу.', 'An intimate marina in a quiet area — ideal for regular subscription service.', 'Intimna marina u mirnom kraju — idealna za redovno održavanje po pretplati.'),
                      [_('Скидки по абонементу', 'Subscription discounts', 'Popusti uz pretplatu'), _('Малые и средние яхты', 'Small and mid-size yachts', 'Male i srednje jahte')]),
                     (_('Зеленика, Мелине, Кумбор', 'Zelenika, Meljine, Kumbor', 'Zelenika, Meljine, Kumbor'), _('Яхты на якорных стоянках и в небольших бухтах вдоль берега. Время согласуем индивидуально.', 'Yachts at anchor and in small coves along the shore. Timing agreed individually.', 'Jahte na sidrištima i u malim uvalama duž obale. Termin dogovaramo individualno.'),
                      [_('Работа на якорных стоянках', 'Service at anchor', 'Rad na sidrištu'), _('Индивидуальная цена', 'Individual pricing', 'Individualna cena')])],
            specifics=[(_('Мы здесь живём', 'We live here', 'Ovde živimo'), _('Оборудование хранится здесь, мы живём здесь. Поэтому приезжаем быстро и без доплаты за выезд.', 'Our equipment is here and so are we — so we arrive quickly and with no travel supplement.', 'Oprema je ovde, i mi smo ovde — zato dolazimo brzo i bez putnog dodatka.')),
                       (_('Цены ниже', 'Lower prices', 'Niže cene'), _('Транспорт не закладываем в стоимость — здесь дешевле, чем выезд в Котор или Тиват.', 'No travel costs are added, so it’s cheaper here than in Kotor or Tivat.', 'Troškovi puta nisu uračunati — ovde je jeftinije nego u Kotoru ili Tivtu.')),
                       (_('Морские средства', 'Marine products', 'Morska sredstva'), _('Мягкие щётки, pH-нейтральные шампуни, пасты и воски, безопасные для антикоррозийных покрытий.', 'Soft brushes, pH-neutral shampoos, compounds and waxes safe for anti-corrosion coatings.', 'Meke četke, pH-neutralni šamponi, paste i voskovi bezbedni za antikorozivne premaze.'))])
    if slug == 'kotor':
        return dict(photo='bay-perast.jpg', map='Kotor,+Montenegro',
            kicker=_('Выезд из Херцег-Нови', 'Visits from Herceg Novi', 'Dolazak iz Herceg Novog'),
            lead=_('Старый Котор окружён одним из самых красивых заливов Средиземноморья. Обслуживаем яхты у стен старого города и в тихих бухтах Доброты.', 'Historic Kotor sits in one of the most beautiful bays of the Mediterranean. We service yachts by the old town walls and in the quiet coves of Dobrota.', 'Istorijski Kotor okružen je jednim od najlepših zaliva Mediterana. Servisiramo jahte uz zidine starog grada i u mirnim uvalama Dobrote.'),
            about=[_('Которский залив — место особой красоты и множества яхт. Глубокие тихие воды, богатые солью и планктоном, ускоряют обрастание корпуса, поэтому регулярный уход здесь особенно важен.', 'The Bay of Kotor is beautiful and busy with yachts. Its deep, calm waters, rich in salt and plankton, speed up hull fouling — so regular care matters here.', 'Kotorski zaliv je mesto izuzetne lepote i mnogo jahti. Duboke, mirne vode bogate solju i planktonom ubrzavaju obrastanje trupa, pa je redovna nega ovde posebno važna.'),
                   _('Приезжаем из нашей базы в Херцег-Нови в день заявки. Доплата за выезд — 20 €.', 'We come from our Herceg Novi base on the day you book. The travel supplement is €20.', 'Dolazimo iz naše baze u Herceg Novom na dan zahteva. Putni dodatak je 20 €.')],
            marinas=[('Kotor Marina', _('Прямо у стен Старого города. Небольшая, но очень загруженная в сезон марина — яхты здесь всегда на виду.', 'Right by the Old Town walls. Small but very busy in season — yachts here are always on show.', 'Odmah uz zidine Starog grada. Mala, ali veoma popunjena u sezoni — jahte su ovde uvek na vidiku.'),
                      [_('По предварительной записи', 'By appointment', 'Po prethodnom dogovoru'), _('Яхты любого класса', 'Yachts of any class', 'Jahte svih klasa')]),
                     (_('Доброта', 'Dobrota', 'Dobrota'), _('Тихий посёлок в 2 км от Котора. Частные причалы и небольшие стоянки, где ценят уединение.', 'A quiet village 2 km from Kotor, with private berths and small anchorages valued for their privacy.', 'Mirno mesto 2 km od Kotora, sa privatnim vezovima i malim sidrištima gde se ceni privatnost.'),
                      [_('Частные причалы', 'Private berths', 'Privatni vezovi'), _('Гибкий график', 'Flexible schedule', 'Fleksibilan raspored')]),
                     (_('Прчань, Столив, Ораховац', 'Prčanj, Stoliv, Orahovac', 'Prčanj, Stoliv, Orahovac'), _('Вся береговая линия от Котора до Тивата — выезжаем по договорённости.', 'The whole shoreline from Kotor to Tivat — visits by arrangement.', 'Cela obala od Kotora do Tivta — dolazak po dogovoru.'),
                      [_('Согласованный день', 'Agreed day', 'Dogovoreni dan'), _('Индивидуальная цена', 'Individual pricing', 'Individualna cena')])],
            specifics=[(_('Закрытая бухта', 'Sheltered bay', 'Zatvoren zaliv'), _('Вода прогревается быстрее, водоросли растут активнее. Советуем обслуживание чаще обычного.', 'The water warms faster and algae grow quicker. We recommend more frequent service.', 'Voda se brže greje i alge brže rastu. Preporučujemo češće održavanje.')),
                       (_('Всегда на виду', 'Always on show', 'Uvek na vidiku'), _('Яхты у стен старого города видят все. Ухоженный вид — это и уважение к месту.', 'Yachts by the old town walls are seen by everyone. A well-kept boat is also a sign of respect for the place.', 'Jahte uz zidine starog grada svi vide. Uredan izgled je i znak poštovanja prema mestu.')),
                       (_('Без подготовки', 'No preparation', 'Bez pripreme'), _('Привозим всё оборудование с собой — от вас ничего не требуется.', 'We bring all the equipment — nothing is needed from you.', 'Donosimo svu opremu — od vas nije potrebno ništa.'))])
    return dict(photo='tivat-marina.jpg', map='Porto+Montenegro,+Tivat',
        kicker=_('Выезд из Херцег-Нови', 'Visits from Herceg Novi', 'Dolazak iz Herceg Novog'),
        lead=_('Тиват — морская столица Черногории и дом Porto Montenegro, одного из самых известных яхтенных портов Адриатики.', 'Tivat is Montenegro’s maritime capital and home to Porto Montenegro, one of the best-known yacht ports on the Adriatic.', 'Tivat je pomorska prestonica Crne Gore i dom Porto Montenegra, jedne od najpoznatijih jahting luka na Jadranu.'),
        about=[_('Porto Montenegro принимает суперяхты и крупные моторные яхты со всей Европы. Владельцы здесь особенно требовательны — и мы работаем на этом уровне.', 'Porto Montenegro welcomes superyachts and large motor yachts from all over Europe. Owners here expect a lot — and we work to that standard.', 'Porto Montenegro prima superjahte i velike motorne jahte iz cele Evrope. Vlasnici ovde imaju visoke zahteve — i mi radimo na tom nivou.'),
               _('Приезжаем в день заявки. Доплата за выезд — 15 €, она входит в цену, которую мы фиксируем при согласовании.', 'We come on the day you book. The travel supplement is €15, included in the price we fix when you confirm.', 'Dolazimo na dan zahteva. Putni dodatak je 15 € i ulazi u cenu koju fiksiramo pri potvrdi.')],
        marinas=[('Porto Montenegro', _('Главная марина региона, принимает суперяхты до 250 метров. Высокие стандарты и соответствующие ожидания от сервиса.', 'The region’s flagship marina, taking superyachts up to 250 m. High standards and high service expectations.', 'Vodeća marina regiona, prima superjahte do 250 m. Visoki standardi i očekivanja od servisa.'),
                  [_('Все классы, включая суперяхты', 'All classes incl. superyachts', 'Sve klase, uključujući superjahte'), _('Строго по правилам марины', 'Strictly by marina rules', 'Strogo po pravilima marine')]),
                 ('Tivat Marina', _('Городская марина в центре Тивата. Популярна у владельцев парусных и моторных яхт среднего класса.', 'The town marina in central Tivat, popular with owners of mid-size sailing and motor yachts.', 'Gradska marina u centru Tivta, popularna kod vlasnika jedrilica i motornih jahti srednje klase.'),
                  [_('Яхты до 30 м', 'Yachts up to 30 m', 'Jahte do 30 m'), _('Скидки по абонементу', 'Subscription discounts', 'Popusti uz pretplatu')]),
                 (_('Калиман и стоянки', 'Kaliman and anchorages', 'Kaliman i sidrišta'), _('Небольшие марины и якорные стоянки вокруг Тивата. По предварительной договорённости.', 'Small marinas and anchorages around Tivat, by prior arrangement.', 'Male marine i sidrišta oko Tivta, po prethodnom dogovoru.'),
                  [_('Якорные стоянки и частные причалы', 'Anchorages and private berths', 'Sidrišta i privatni vezovi'), _('Индивидуальная цена', 'Individual pricing', 'Individualna cena')])],
        specifics=[(_('Уровень Porto Montenegro', 'Porto Montenegro standard', 'Nivo Porto Montenegra'), _('Здесь привыкли к премиальному сервису — соответствуем по материалам и культуре работы.', 'Owners here are used to premium service — we match it in materials and conduct.', 'Ovde su navikli na premium servis — odgovaramo mu materijalima i kulturom rada.')),
                   (_('Крупные суда', 'Large vessels', 'Velika plovila'), _('Мойка суперяхты — это другая организация работы и оборудование. Есть опыт с судами от 8 до 45+ метров.', 'Washing a superyacht takes a different workflow and equipment. We have experience with vessels from 8 to 45+ m.', 'Pranje superjahte traži drugačiju organizaciju i opremu. Imamo iskustvo sa plovilima od 8 do 45+ m.')),
                   (_('Абонемент', 'Subscription', 'Pretplata'), _('Для яхт, которые стоят в Тивате весь сезон, — обслуживание по графику, дешевле разовых визитов.', 'For yachts based in Tivat all season — scheduled service that costs less than one-off visits.', 'Za jahte koje su u Tivtu celu sezonu — održavanje po rasporedu, jeftinije od pojedinačnih dolazaka.'))])


def map_embed(q):
    return f'<div class="map"><iframe src="https://maps.google.com/maps?q={q}&z=13&output=embed&hl={"sr-Latn" if L == "sr" else L}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Map"></iframe></div>'


def page_city(slug):
    d = city_data(slug)
    name = dict(cities())[slug]
    about = ''.join(f'<p>{p}</p>' for p in d['about'])
    marinas = ''.join(f'<div class="box"><h3>{n}</h3><p>{t}</p><ul class="checks">{"".join(f"<li>{i}</li>" for i in lis)}</ul></div>' for n, t, lis in d['marinas'])
    spec = ''.join(f'<div class="box"><h3>{h}</h3><p>{p}</p></div>' for h, p in d['specifics'])
    title_book = _(f'Записаться на мойку — {name}', f'Book a wash in {name}', f'Zakažite pranje — {name}')
    return head(slug, _(f'Мойка яхт — {name}', f'Yacht cleaning in {name}', f'Pranje jahti — {name}'), d['lead'], image='cover.png') \
        + header(slug) + page_hero(slug, d['photo'], d['kicker'], name, d['lead'], crumbs=[('zones', _('Зоны', 'Areas', 'Zone'))]) + f'''
<section class="sec"><div class="wrap split">
  <div><div class="lbl">{_('О работе здесь', 'Working here', 'O radu ovde')}</div><h2 class="h2">{_(f'Мойка яхт: {name}', f'Yacht care in {name}', f'Nega jahti: {name}')}</h2>{about}
    <div class="stats"><div><b>{_('В день заявки', 'Same day', 'Istog dana')}</b><span>{_('приезжаем к яхте', 'we come to your yacht', 'dolazimo do jahte')}</span></div><div><b>{_('от 60 €', 'from €60', 'od 60 €')}</b><span>{_('мойка корпуса', 'hull wash', 'pranje trupa')}</span></div></div>
  </div>
  {map_embed(d['map'])}
</div></section>
<section class="sec sand"><div class="wrap">
  <div class="lbl">{_('Марины и стоянки', 'Marinas and anchorages', 'Marine i sidrišta')}</div>
  <h2 class="h2">{_('Где работаем', 'Where we work', 'Gde radimo')}</h2>
  <div class="grid3">{marinas}</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="lbl">{_('Особенности', 'Local specifics', 'Specifičnosti')}</div>
  <h2 class="h2">{_('Что важно знать', 'Good to know', 'Važno je znati')}</h2>
  <div class="grid3">{spec}</div>
</div></section>
<section class="sec sand"><div class="wrap">
  <div class="lbl">{_('Порядок работы', 'How it works', 'Redosled rada')}</div>
  <h2 class="h2">{_('Как проходит заказ', 'How a booking works', 'Kako izgleda narudžbina')}</h2>
  {steps()}
</div></section>
''' + contact_block(title_book) + footer()


def page_zones():
    s = 'zones'
    return head(s, _('Где мы работаем', 'Where we work', 'Gde radimo'),
                _('Мойка яхт по всему Которскому заливу: Херцег-Нови, Котор, Тиват и якорные стоянки.', 'Yacht cleaning across the Bay of Kotor: Herceg Novi, Kotor, Tivat and anchorages.', 'Pranje jahti u celom Kotorskom zalivu: Herceg Novi, Kotor, Tivat i sidrišta.')) \
        + header(s) + page_hero(s, 'bay-perast.jpg', _('Зоны', 'Areas', 'Zone'), _('Весь Которский залив', 'The whole Bay of Kotor', 'Ceo Kotorski zaliv'),
                                _('База в Херцег-Нови. В Котор, Тиват и к якорным стоянкам залива выезжаем каждый день — в день заявки.', 'Based in Herceg Novi, with same-day visits to Kotor, Tivat and anchorages around the bay.', 'Baza u Herceg Novom. U Kotor, Tivat i do sidrišta u zalivu dolazimo svaki dan — na dan zahteva.'),
                                crumbs=[]) + f'''
<section class="sec"><div class="wrap">
  <div class="lbl">{_('Города', 'Towns', 'Gradovi')}</div>
  <h2 class="h2">{_('Выберите свою зону', 'Choose your area', 'Izaberite svoju zonu')}</h2>
  {city_cards()}
</div></section>
<section class="sec sand"><div class="wrap">
  <div class="lbl">{_('Карта', 'Map', 'Mapa')}</div>
  <h2 class="h2">{_('Бока Которская', 'Boka Kotorska', 'Boka Kotorska')}</h2>
  <p class="sub">{_('Херцег-Нови — без доплаты. Выезд в Тиват +15 €, в Котор +20 €.', 'Herceg Novi: no supplement. Tivat +€15, Kotor +€20.', 'Herceg Novi — bez doplate. Tivat +15 €, Kotor +20 €.')}</p>
  {map_embed('Boka+Kotorska,+Montenegro').replace('z=13', 'z=11')}
</div></section>
''' + contact_block() + footer()


def page_about():
    s = 'about'
    principles = [
        (_('Честно о цене', 'Honest pricing', 'Pošteno o ceni'), _('Называем точную стоимость до начала работы. Никаких «выяснилось по ходу» и доплат после.', 'We quote the exact price before we start. No “it turned out to be more” and no extras afterwards.', 'Navodimo tačnu cenu pre početka rada. Bez „ispostavilo se” i bez doplata posle.')),
        (_('Фотоотчёт каждый раз', 'Photo report every time', 'Foto izveštaj svaki put'), _('Фотографируем результат и отправляем владельцу. Вы видите, что сделано, даже если вас не было на борту.', 'We photograph the result and send it to the owner, so you see what was done even if you weren’t on board.', 'Fotografišemo rezultat i šaljemo vlasniku — vidite šta je urađeno i ako niste bili na brodu.')),
        (_('Своё оборудование', 'Our own equipment', 'Sopstvena oprema'), _('Только проверенные морские средства и профессиональное оборудование, подходящее для яхтенных покрытий.', 'Only proven marine products and professional equipment suited to yacht coatings.', 'Samo proverena morska sredstva i profesionalna oprema pogodna za premaze jahti.')),
    ]
    boxes = ''.join(f'<div class="box"><h3>{h}</h3><p>{p}</p></div>' for h, p in principles)
    return head(s, _('О нас', 'About us', 'O nama'),
                _('Два друга из Херцег-Нови, которые моют яхты по всему Которскому заливу. Честные цены, фотоотчёт, своё оборудование.', 'Two friends from Herceg Novi washing yachts across the Bay of Kotor. Honest prices, photo reports, our own equipment.', 'Dva prijatelja iz Herceg Novog koji peru jahte u celom Kotorskom zalivu. Poštene cene, foto izveštaj, sopstvena oprema.')) \
        + header(s) + page_hero(s, 'deck-bow.jpg', _('О нас', 'About us', 'O nama'), _('Два друга', 'Two friends', 'Dva prijatelja'),
                                _('Мы не агентство и не компания с колл-центром. Мы — двое людей, которые живут здесь, любят море и делают свою работу на совесть.', 'We’re not an agency or a company with a call centre. We’re two people who live here, love the sea and take pride in our work.', 'Nismo agencija niti kompanija sa kol-centrom. Nas dvojica živimo ovde, volimo more i savesno radimo svoj posao.'),
                                crumbs=[]) + f'''
<section class="sec"><div class="wrap split">
  <div>
    <div class="lbl">{_('История', 'Our story', 'Priča')}</div>
    <h2 class="h2">{_('Как всё началось', 'How it started', 'Kako je sve počelo')}</h2>
    <p>{_('Несколько лет назад мы начали мыть яхты знакомых — просто потому что умеем делать это хорошо и нам нравится результат. Первые клиенты пришли по рекомендации, потом появились постоянные, потом нас начали находить сами.', 'A few years ago we started washing yachts for people we knew — simply because we do it well and enjoy the result. The first clients came by word of mouth, then regulars followed, then people started finding us on their own.', 'Pre nekoliko godina počeli smo da peremo jahte poznanicima — jednostavno zato što to radimo dobro i volimo rezultat. Prvi klijenti su došli preko preporuka, zatim stalni, a onda su nas ljudi počeli sami pronalaziti.')}</p>
    <p>{_('Сегодня мы обслуживаем яхты по всему Которскому заливу — от Херцег-Нови до Тивата. Наёмных сотрудников, которых мы не знаем лично, у нас нет. Приезжаем сами.', 'Today we look after yachts across the Bay of Kotor, from Herceg Novi to Tivat. We have no hired staff we don’t personally know. We come ourselves.', 'Danas održavamo jahte u celom Kotorskom zalivu, od Herceg Novog do Tivta. Nemamo zaposlene koje lično ne poznajemo. Dolazimo sami.')}</p>
  </div>
  <div class="stats" style="margin:0">
    <div><b>3+</b><span>{_('года в Которском заливе', 'years in the Bay of Kotor', 'godine u Kotorskom zalivu')}</span></div>
    <div><b>3</b><span>{_('города: Херцег-Нови, Котор, Тиват', 'towns: Herceg Novi, Kotor, Tivat', 'grada: Herceg Novi, Kotor, Tivat')}</span></div>
    <div><b>7/7</b><span>{_('без выходных весь сезон', 'no days off all season', 'bez slobodnih dana cele sezone')}</span></div>
    <div><b>2</b><span>{_('человека — сами приезжаем на каждый заказ', 'people — we come to every job ourselves', 'čoveka — lično dolazimo na svaki posao')}</span></div>
  </div>
</div></section>
<section class="sec sand"><div class="wrap">
  <div class="lbl">{_('Принципы', 'Principles', 'Principi')}</div>
  <h2 class="h2">{_('Как мы работаем', 'How we work', 'Kako radimo')}</h2>
  <div class="grid3">{boxes}</div>
</div></section>
''' + contact_block(_('Познакомимся поближе?', 'Let’s get acquainted', 'Da se upoznamo?')) + footer()


def page_contact():
    s = 'contact'
    city_opts = ''.join(f'<option>{n}</option>' for _s, n in cities()) + f'<option>{_("Другое место залива", "Elsewhere in the bay", "Drugo mesto u zalivu")}</option>'
    pkg_opts = ''.join(f'<option>{n} · {p} €</option>' for p, n, *_r in packages()) + f'<option>{_("Пока не знаю — посоветуйте", "Not sure yet — please advise", "Ne znam još — posavetujte me")}</option>'
    form = f'''<form class="form" id="request" data-hello="{_('Здравствуйте! Заявка с сайта:', 'Hello! Request from the website:', 'Zdravo! Zahtev sa sajta:')}">
  <div class="row2">
    <label>{_('Где стоит яхта', 'Where is the yacht', 'Gde je jahta')}<select data-k="{_('Место', 'Location', 'Mesto')}">{city_opts}</select></label>
    <label>{_('Марина или стоянка', 'Marina or berth', 'Marina ili vez')} <small>{_('необязательно', 'optional', 'nije obavezno')}</small><input data-k="{_('Марина', 'Marina', 'Marina')}" placeholder="Portonovi, Kotor Marina…"></label>
  </div>
  <div class="row2">
    <label>{_('Что нужно', 'What you need', 'Šta vam treba')}<select data-k="{_('Пакет', 'Package', 'Paket')}">{pkg_opts}</select></label>
    <label>{_('Длина яхты, м', 'Yacht length, m', 'Dužina jahte, m')} <small>{_('необязательно', 'optional', 'nije obavezno')}</small><input data-k="{_('Длина', 'Length', 'Dužina')}" inputmode="decimal" placeholder="9"></label>
  </div>
  <label>{_('Удобная дата', 'Preferred date', 'Željeni datum')} <small>{_('необязательно', 'optional', 'nije obavezno')}</small><input type="date" data-k="{_('Дата', 'Date', 'Datum')}"></label>
  <label>{_('Комментарий', 'Comment', 'Komentar')} <small>{_('необязательно', 'optional', 'nije obavezno')}</small><textarea data-k="{_('Комментарий', 'Comment', 'Komentar')}"></textarea></label>
  <div><button class="b wa" type="submit">{_('Отправить в WhatsApp', 'Send via WhatsApp', 'Pošaljite preko WhatsApp-a')}</button></div>
  <small style="color:var(--muted)">{_('Откроется WhatsApp с готовым сообщением — останется нажать «отправить».', 'WhatsApp opens with the message ready — just tap send.', 'Otvoriće se WhatsApp sa spremnom porukom — samo pritisnite „pošalji”.')}</small>
</form>'''
    return head(s, _('Контакты', 'Contact', 'Kontakt'),
                _(f'Связаться с Два Друга: WhatsApp {PHONE_H}, Telegram @{TG}, email. Мойка яхт в Херцег-Нови, Которе, Тивате.', f'Contact Dva Druga: WhatsApp {PHONE_H}, Telegram @{TG}, email. Yacht cleaning in Herceg Novi, Kotor, Tivat.', f'Kontakt Dva Druga: WhatsApp {PHONE_H}, Telegram @{TG}, email. Pranje jahti u Herceg Novom, Kotoru, Tivtu.')) \
        + header(s) + page_hero(s, 'deck-clean.jpg', _('Контакты', 'Contact', 'Kontakt'), _('Напишите нам', 'Get in touch', 'Pišite nam'),
                                _('Отвечаем в течение нескольких минут. Можно сразу прислать фото яхты — так мы точнее назовём цену.', 'We reply within minutes. Send a photo of the yacht right away and we can quote more precisely.', 'Odgovaramo za nekoliko minuta. Odmah pošaljite fotografiju jahte — tako ćemo tačnije reći cenu.'),
                                crumbs=[]) + f'''
<section class="sec"><div class="wrap">
  <div class="grid3" style="margin-top:0">
    <a class="box" href="{wa()}"><div class="lbl">WhatsApp</div><h3>{PHONE_H}</h3><p>{_('Самый быстрый способ. Можно прислать фото.', 'The fastest way. Photos welcome.', 'Najbrži način. Može i fotografija.')}</p></a>
    <a class="box" href="https://t.me/{TG}"><div class="lbl">Telegram</div><h3>@{TG}</h3><p>{_('Если вам удобнее Telegram.', 'If you prefer Telegram.', 'Ako vam je Telegram zgodniji.')}</p></a>
    <a class="box" href="tel:+{PHONE}"><div class="lbl">{_('Телефон', 'Phone', 'Telefon')}</div><h3>{PHONE_H}</h3><p>{_('Каждый день сезона, 08:00–20:00.', 'Every day of the season, 08:00–20:00.', 'Svaki dan sezone, 08:00–20:00.')}</p></a>
  </div>
  <p style="margin-top:18px;color:var(--muted)">Email: <a href="mailto:{MAIL}" style="color:var(--ink);border-bottom:1px solid">{MAIL}</a> — {_('для подробных запросов и абонемента, отвечаем в тот же день.', 'for detailed requests and subscriptions; we reply the same day.', 'za detaljne upite i pretplatu, odgovaramo istog dana.')}</p>
</div></section>
<section class="sec sand"><div class="wrap">
  <div class="lbl">{_('Быстрая заявка', 'Quick request', 'Brzi zahtev')}</div>
  <h2 class="h2">{_('Заполните — отправим в WhatsApp', 'Fill in — we’ll send it via WhatsApp', 'Popunite — poslaćemo preko WhatsApp-a')}</h2>
  <p class="sub">{_('Никаких регистраций. Форма просто собирает сообщение, вы отправляете его сами.', 'No sign-up. The form just prepares a message and you send it yourself.', 'Bez registracije. Forma samo priprema poruku, a vi je šaljete.')}</p>
  {form}
</div></section>
<section class="sec"><div class="wrap">
  <div class="lbl">{_('Где мы', 'Where we are', 'Gde smo')}</div>
  <h2 class="h2">{_('Херцег-Нови и весь залив', 'Herceg Novi and the whole bay', 'Herceg Novi i ceo zaliv')}</h2>
  {map_embed('Herceg+Novi,+Montenegro').replace('z=13', 'z=11')}
</div></section>
''' + footer()


def page_404():
    return head('index', _('Страница не найдена', 'Page not found', 'Stranica nije pronađena'),
                _('Такой страницы нет.', 'This page does not exist.', 'Ova stranica ne postoji.')).replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"') \
        + header('index') + f'''
<section class="phero" style="padding-bottom:110px"><div class="wrap">
  <div class="lbl">404</div>
  <h1>{_('Кажется, эта страница уплыла', 'Looks like this page has sailed away', 'Izgleda da je ova stranica otplovila')}</h1>
  <p style="margin-bottom:26px">{_('Такой страницы нет. Вернитесь на главную или сразу напишите нам.', 'This page doesn’t exist. Head back home or just message us.', 'Ova stranica ne postoji. Vratite se na početnu ili nam odmah pišite.')}</p>
  <div class="btns"><a class="b dark" href="/">{_('На главную', 'Home', 'Početna')}</a><a class="b wa" href="{wa()}">WhatsApp</a></div>
  <p style="margin-top:26px;font-size:14px"><a class="more" href="/en/">English</a> &nbsp; <a class="more" href="/sr/">Srpski</a></p>
</div>{sea('#082A30')}</section>
''' + footer()


FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#0B3A42"/><path d="M5 19h22l-3 5H8z" fill="#fff"/><path d="M11 19l2.5-5h7l3 5z" fill="#fff"/></svg>'''


def make_og_images():
    """1200x630 link-preview images (WhatsApp/Telegram/Facebook), one per language."""
    global L
    from PIL import Image, ImageDraw, ImageFont
    font_path = os.path.join(ROOT, 'src', 'fonts', 'Onest.ttf')

    def font(size, weight):
        f = ImageFont.truetype(font_path, size)
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
        return f

    base = Image.open(os.path.join(ROOT, 'hero-yacht.jpg')).convert('RGB')
    w, h = base.size
    crop_h = int(w * 630 / 1200)
    base = base.crop((0, (h - crop_h) // 2, w, (h - crop_h) // 2 + crop_h)).resize((1200, 630), Image.LANCZOS)
    shade = Image.new('RGB', base.size, (5, 25, 30))
    base = Image.blend(base, shade, 0.45)
    for L in LANGS:
        im = base.copy()
        d = ImageDraw.Draw(im)
        d.text((64, 56), _('ДВА ДРУГА', 'DVA DRUGA', 'DVA DRUGA'), font=font(34, 700), fill='white')
        title = _('Мойка яхт\nв Которском заливе', 'Yacht cleaning\nin the Bay of Kotor', 'Pranje jahti\nu Kotorskom zalivu')
        d.multiline_text((64, 300), title, font=font(76, 650), fill='white', spacing=6)
        d.text((64, 540), _('Херцег-Нови · Котор · Тиват  —  от 60 €', 'Herceg Novi · Kotor · Tivat  —  from €60', 'Herceg Novi · Kotor · Tivat  —  od 60 €'), font=font(30, 450), fill=(235, 240, 240))
        im.save(os.path.join(OUT, 'img', f'og-{L}.jpg'), 'JPEG', quality=82, optimize=True)
    L = 'ru'


def write_file(path, text):
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


def build():
    global L
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'img'))
    from PIL import Image
    extra = os.listdir(os.path.join(ROOT, 'src', 'img')) if os.path.isdir(os.path.join(ROOT, 'src', 'img')) else []
    for f in IMAGES + extra:
        src = os.path.join(ROOT, 'src', 'img', f) if os.path.exists(os.path.join(ROOT, 'src', 'img', f)) else os.path.join(ROOT, f)
        if f.lower().endswith(('.png', '.txt')):
            shutil.copy2(src, os.path.join(OUT, 'img', f))  # logo/cover for schema.org, credits
        if f.lower().endswith(('.jpg', '.jpeg')):
            stem = os.path.splitext(f)[0]
            VER[stem] = short_hash(src)
            im = Image.open(src).convert('RGB')
            for suffix, w, q in (('s', 800, 72), ('l', 1600, 76)):
                c = im.copy(); c.thumbnail((w, w * 2))
                c.save(os.path.join(OUT, 'img', f'{stem}-{suffix}.{VER[stem]}.webp'), 'WEBP', quality=q, method=6)
    shutil.copy2(os.path.join(ROOT, 'src', 'style.css'), OUT)
    VER['style.css'] = short_hash(os.path.join(ROOT, 'src', 'style.css'))
    VER['site.js'] = short_hash(os.path.join(ROOT, 'src', 'site.js'))
    shutil.copy2(os.path.join(ROOT, 'src', 'site.js'), OUT)
    os.makedirs(os.path.join(OUT, 'fonts'))
    for f in os.listdir(os.path.join(ROOT, 'src', 'fonts')):
        if f.endswith(('.woff2', '.txt')):
            shutil.copy2(os.path.join(ROOT, 'src', 'fonts', f), os.path.join(OUT, 'fonts', f))
    write_file(os.path.join(OUT, 'favicon.svg'), FAVICON)
    pages = {'index': page_index, 'services': page_services, 'pricing': page_pricing, 'zones': page_zones,
             'about': page_about, 'contact': page_contact,
             'herceg-novi': lambda: page_city('herceg-novi'), 'kotor': lambda: page_city('kotor'), 'tivat': lambda: page_city('tivat')}
    make_og_images()
    count = 0
    for L in LANGS:
        d = OUT if L == 'ru' else os.path.join(OUT, L)
        os.makedirs(d, exist_ok=True)
        for slug, fn in pages.items():
            write_file(os.path.join(d, slug + '.html'), with_bg_css(fn()))
            count += 1
    L = 'ru'
    import re as _re  # 404 is served at any URL depth, so every local link must be root-absolute
    html404 = with_bg_css(page_404())
    html404 = _re.sub(r'(href|src)="(?!https?:|mailto:|tel:|/|#)(\./)?([^"]*)"', lambda m: f'{m.group(1)}="/{m.group(3)}"', html404)
    write_file(os.path.join(OUT, '404.html'), html404)
    write_file(os.path.join(OUT, '_headers'), 
        # versioned files (content hash in the name or ?v=) never change, so they can be cached for a year
        '/img/*.webp\n  Cache-Control: public, max-age=31536000, immutable\n'
        '/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n'
        '/style.css\n  Cache-Control: public, max-age=31536000, immutable\n'
        '/site.js\n  Cache-Control: public, max-age=31536000, immutable\n'
        '/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
    # sitemap + robots
    urls = ''.join(f'<url><loc>{SITE}/{url(s, lg)}</loc>' + ''.join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{SITE}/{url(s, a)}"/>' for a in LANGS) + '</url>'
                   for lg in LANGS for s in pages)
    write_file(os.path.join(OUT, 'sitemap.xml'), 
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + '</urlset>')
    write_file(os.path.join(OUT, 'robots.txt'), f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    g = os.path.join(ROOT, 'googleee91df9c1536dabf.html')
    if os.path.exists(g):
        shutil.copy2(g, OUT)
    print(f'built {count} pages into {OUT}')


if __name__ == '__main__':
    build()
