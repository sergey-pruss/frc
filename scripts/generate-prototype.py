#!/usr/bin/env python3
"""Generate static shop prototype pages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PRODUCTS = [
    {
        "slug": "futbolka-oranzhevaya",
        "title": "Футболка «Оранжевая линия»",
        "cat": "futbolki",
        "cat_label": "Футболки",
        "price": 3990,
        "old": 4590,
        "tag": "Новинка",
        "img": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800&q=80",
        "desc": "Плотный хлопок, прямой крой. На груди — стилизованная графика с отсылкой к архитектуре центра. Рыбный текст для демонстрации карточки.",
    },
    {
        "slug": "futbolka-belaya",
        "title": "Футболка «Белый фасад»",
        "cat": "futbolki",
        "cat_label": "Футболки",
        "price": 3490,
        "old": None,
        "tag": "Хит",
        "img": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?auto=format&fit=crop&w=800&q=80",
        "desc": "Базовая модель для повседневных образов. Минималистичный принт, мягкая ткань, универсальный размерный ряд.",
    },
    {
        "slug": "svitshot-klassika",
        "title": "Свитшот «Классика»",
        "cat": "svitshoty",
        "cat_label": "Свитшоты",
        "price": 5990,
        "old": None,
        "tag": "Коллекция",
        "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=800&q=80",
        "desc": "Утеплённый флис внутри, объёмная вышивка на груди. Подходит для прохладной погоды и городских прогулок.",
    },
    {
        "slug": "svitshot-premium",
        "title": "Свитшот «Премиум капсула»",
        "cat": "svitshoty",
        "cat_label": "Свитшоты",
        "price": 6490,
        "old": 7200,
        "tag": "−10%",
        "img": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=800&q=80",
        "desc": "Оверсайз, плотный материал, контрастные манжеты. Демо-описание для согласования блока характеристик.",
    },
    {
        "slug": "kepka-simvol",
        "title": "Кепка «Символ»",
        "cat": "kepki",
        "cat_label": "Кепки",
        "price": 2490,
        "old": None,
        "tag": "Аксессуар",
        "img": "https://images.unsplash.com/photo-1588856142877-1aae7062c88f?auto=format&fit=crop&w=800&q=80",
        "desc": "Регулируемый ремешок, вышивка спереди. Лёгкий акцент к любому образу из каталога.",
    },
    {
        "slug": "kurtka-veter",
        "title": "Куртка «Ветер с севера»",
        "cat": "kurtki",
        "cat_label": "Куртки",
        "price": 12990,
        "old": None,
        "tag": "Премиум",
        "img": "https://images.unsplash.com/photo-1544022613-e87ca75a784a?auto=format&fit=crop&w=800&q=80",
        "desc": "Ветрозащитная ткань, капюшон, утеплённая подкладка. Прототип верхней одежды для витрины.",
    },
]


def fmt_price(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f") + " ₽"


def shell(depth: int, title: str, body: str) -> str:
    root = "../" * depth
    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — Универмаг «Россия»</title>
    <meta name="description" content="Прототип интернет-магазина мерча Национального центра «Россия».">
    <meta name="robots" content="noindex, nofollow">
    <link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="{root}assets/shop.css">
  </head>
  <body>
    <div data-site-header></motion>
    <main>
{body}
    </main>
    <div data-site-footer></motion>
    <script src="{root}assets/site.js" data-depth="{depth}"></script>
  </body>
</html>
""".replace("<motion", "<div").replace("</motion>", "</div>")


def card(p: dict, depth: int) -> str:
    root = "../" * depth
    old = f'<span class="price-old">{fmt_price(p["old"])}</span>' if p["old"] else ""
    return f"""
        <article class="product-card">
          <a href="{root}product/{p['slug']}/">
            <div class="product-thumb">
              <span class="product-tag">{p['tag']}</span>
              <img src="{p['img']}" alt="{p['title']}" loading="lazy" width="400" height="500">
            </div>
            <div class="product-body">
              <h3>{p['title']}</h3>
              <p>{p['desc'][:72]}…</p>
              <motion class="price-row">
                <span class="price">{fmt_price(p['price'])}</span>
                {old}
              </motion>
            </div>
          </a>
        </article>""".replace("<motion", "<div").replace("</motion>", "</div>")


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("wrote", rel)


def main() -> None:
    grid_home = "\n".join(card(p, 0) for p in PRODUCTS[:8])
    home = shell(
        0,
        "Главная",
        f"""
      <section class="hero-shop">
        <div class="wrap hero-grid">
          <div class="hero-copy">
            <div class="hero-badges">
              <span class="pill">Официальный мерч</span>
              <span class="pill">Доставка по России</span>
              <span class="pill">Коллекция Russia Capsule</span>
            </div>
            <h1>Одежда и мерч Национального центра «Россия»</h1>
            <p>Демо-витрина для согласования структуры каталога, карточек и сервисных страниц. Все тексты и цены — рыбные заглушки.</p>
            <div style="display:flex;flex-wrap:wrap;gap:12px;">
              <a class="btn btn-primary" href="catalog/">Смотреть каталог</a>
              <a class="btn btn-secondary" href="collections/russia-capsule/">Russia Capsule</a>
            </div>
          </div>
          <div class="hero-visual" aria-hidden="true"></div>
        </div>
      </section>
      <section class="section">
        <div class="wrap">
          <div class="section-head">
            <h2>Новинки сезона</h2>
            <p>Подборка для прототипа: сетка карточек, цены, бейджи и переход в товар.</p>
          </div>
          <div class="product-grid">{grid_home}
          </div>
        </div>
      </section>
      <section class="section">
        <div class="wrap collection-banner">
          <div class="visual" aria-hidden="true"></div>
          <div class="copy">
            <h3>Russia Capsule</h3>
            <p>Капсульная линейка с акцентом на символику и архитектурные мотивы. Здесь будет отдельная посадочная коллекции с историей и lookbook.</p>
            <a class="btn btn-primary" href="collections/russia-capsule/">Открыть коллекцию</a>
          </div>
        </div>
      </section>
      <section class="section">
        <div class="wrap trust-row">
          <div class="trust-card"><strong>Доставка по РФ</strong>Курьер, ПВЗ и почта — условия на демо-странице.</div>
          <motion class="trust-card"><strong>Официальный магазин</strong>Брендовая связка с Национальным центром «Россия».</div>
          <div class="trust-card"><strong>Примерка и возврат</strong>Блок FAQ и возвратов для SEO и доверия.</div>
          <div class="trust-card"><strong>Подарочные карты</strong>Отдельный сценарий в структуре каталога.</div>
        </div>
      </section>""".replace("<motion", "<div").replace("</motion>", "</motion>").replace("</motion>", "</motion>"),
    )
    home = home.replace("</motion>", "</div>").replace("<motion", "<div")
    write("index.html", home)

    cats = [
        ("futbolki", "Футболки", "Базовый слой каталога: футболки с принтом и без."),
        ("svitshoty", "Свитшоты", "Тёплый сегмент: свитшоты и худи в одной ветке прототипа."),
        ("kepki", "Кепки", "Аксессуары с низким чеком — хороший вход в корзину."),
        ("kurtki", "Куртки", "Верхняя одежда с расширенной карточкой и таблицей размеров."),
    ]
    for slug, label, intro in cats:
        items = [p for p in PRODUCTS if p["cat"] == slug]
        chips = "\n".join(
            f'<a href="../{c}/" class="{"is-active" if c == slug else ""}">{l}</a>'
            for c, l, _ in cats
        )
        grid = "\n".join(card(p, 2) for p in items) or "<p>Товары появятся после уточнения ассортимента.</p>"
        body = f"""
      <div class="wrap">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../">Каталог</a> / <span>{label}</span></nav>
        <h1>{label}</h1>
        <p class="page-intro">{intro} Рыбный intro-текст 300–600 знаков будет здесь в продакшене.</p>
        <div class="category-chips">{chips}</div>
        <div class="filters-bar">
          <div>Фильтры: размер · цвет · цена <span style="color:var(--muted)">(демо)</span></motion>
          <select aria-label="Сортировка"><option>По популярности</option><option>Сначала новые</option><option>Цена ↑</option></select>
        </div>
        <div class="product-grid">{grid}</div>
      </div>"""
        body = body.replace("<motion", "<div").replace("</motion>", "</div>")
        write(f"catalog/{slug}/index.html", shell(2, label, body))

    catalog_grid = "\n".join(card(p, 1) for p in PRODUCTS)
    write(
        "catalog/index.html",
        shell(
            1,
            "Каталог",
            f"""
      <div class="wrap">
        <nav class="breadcrumbs"><a href="../">Главная</a> / <span>Каталог</span></nav>
        <h1>Каталог</h1>
        <p class="page-intro">Разводящая страница ассортимента: категории, новинки и фильтры. В прототипе — 6 демо-товаров.</p>
        <div class="category-chips">
          <a class="is-active" href="./">Все</a>
          <a href="futbolki/">Футболки</a>
          <a href="svitshoty/">Свитшоты</a>
          <a href="kepki/">Кепки</a>
          <a href="kurtki/">Куртки</a>
        </div>
        <div class="product-grid">{catalog_grid}</motion>
      </div>""".replace("<motion", "<motion").replace("</motion>", "</motion>").replace("<motion", "<div").replace("</motion>", "</motion>"),
        ),
    )

    # fix catalog index
    text = (ROOT / "catalog/index.html").read_text()
    write("catalog/index.html", text.replace("</motion>", "</div>").replace("<motion", "<div"))

    for p in PRODUCTS:
        if p["slug"] not in ("futbolka-oranzhevaya", "svitshot-klassika", "kurtka-veter"):
            continue
        thumbs = [p["img"], p["img"], p["img"], p["img"]]
        thumb_html = "".join(
            f'<button type="button" class="{"is-active" if i == 0 else ""}"><img src="{u}" alt=""></button>'
            for i, u in enumerate(thumbs)
        )
        body = f"""
      <div class="wrap">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../../catalog/">Каталог</a> / <a href="../../catalog/{p['cat']}/">{p['cat_label']}</a> / <span>{p['title']}</span></nav>
        <div class="product-page">
          <div>
            <div class="gallery-main"><img src="{p['img']}" alt="{p['title']}"></div>
            <div class="gallery-thumbs">{thumb_html}</div>
          </div>
          <div class="product-info">
            <p class="pill" style="display:inline-block;">{p['tag']}</p>
            <h1>{p['title']}</h1>
            <p class="lead-price">{fmt_price(p['price'])}</p>
            <p>{p['desc']} Дополнительный рыбный текст про посадку, состав 80% хлопок / 20% полиэстер и уход при 30°.</p>
            <p><strong>Размер</strong></p>
            <div class="size-grid">
              <button type="button">S</button><button type="button" class="is-active">M</button><button type="button">L</button><button type="button">XL</button>
            </div>
            <div style="display:flex;gap:12px;flex-wrap:wrap;">
              <button class="btn btn-primary" type="button" data-demo-cart>В корзину</button>
              <a class="btn btn-secondary" href="../../delivery/">Доставка и возврат</a>
            </div>
            <ul class="spec-list">
              <li><span>Коллекция</span><span>Russia Capsule</span></li>
              <li><span>Артикул</span><span>DEMO-{p['slug'][:6].upper()}</span></li>
              <li><span>Наличие</span><span>В наличии (рыба)</span></li>
            </ul>
          </div>
        </div>
      </motion>"""
        body = body.replace("<motion", "<div").replace("</motion>", "</div>")
        write(f"product/{p['slug']}/index.html", shell(2, p["title"], body))

    write(
        "collections/index.html",
        shell(
            1,
            "Коллекции",
            """
      <div class="wrap">
        <nav class="breadcrumbs"><a href="../">Главная</a> / <span>Коллекции</span></nav>
        <h1>Коллекции</h1>
        <p class="page-intro">Смысловые линейки и капсулы — отдельные посадочные в структуре SEO-ТЗ.</p>
        <motion class="collection-banner" style="margin-top:24px;">
          <div class="visual" style="background-image:url('https://images.unsplash.com/photo-1523381210434-271fa511ff93?auto=format&fit=crop&w=1000&q=80');"></div>
          <div class="copy">
            <h3>Russia Capsule</h3>
            <p>Флагманская капсула прототипа: куртки, свитшоты и акцентные принты. Рыбный storytelling блок.</p>
            <a class="btn btn-primary" href="russia-capsule/">Смотреть товары</a>
          </div>
        </div>
      </div>""".replace("<motion", "<div").replace("</motion>", "</div>"),
        ),
    )

    cap_products = [p for p in PRODUCTS if p["cat"] in ("futbolki", "svitshoty", "kurtki")][:4]
    write(
        "collections/russia-capsule/index.html",
        shell(
            2,
            "Russia Capsule",
            f"""
      <div class="wrap">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../">Коллекции</a> / <span>Russia Capsule</span></nav>
        <h1>Russia Capsule</h1>
        <p class="page-intro">Коллекционная посадочная: история капсулы, визуал и товары. Текст-рыба для согласования макета с клиентом.</p>
        <motion class="product-grid">{"".join(card(p, 2) for p in cap_products)}</div>
      </div>""".replace("<motion", "<div").replace("</motion>", "</div>"),
        ),
    )

    write(
        "delivery/index.html",
        shell(
            1,
            "Доставка и оплата",
            """
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="../">Главная</a> / <span>Доставка</span></nav>
        <div class="content-block">
          <h1>Доставка, оплата и возврат</h1>
          <p>Сервисная страница из SEO-карты сайта. Ниже — рыбные условия для прототипа.</p>
          <h2 id="delivery">Доставка по России</h2>
          <p>Москва — курьер 1–2 дня от 390 ₽. Регионы — СДЭК/Почта 3–7 дней от 290 ₽. Бесплатно от 7 000 ₽ (заглушка).</p>
          <h2>Оплата</h2>
          <p>Карта, СБП, оплата при получении в пилотных регионах — финальный список уточняется.</p>
          <h2 id="return">Возврат</h2>
          <p>14 дней на возврат нераспроданного товара. Пример текста для блока доверия в карточке товара.</p>
          <div class="faq" id="faq">
            <h2>FAQ</h2>
            <details open><summary>Как подобрать размер?</summary><p>Рыбный ответ со ссылкой на таблицу размеров в карточке и в блоге.</p></details>
            <details><summary>Есть ли подарочная упаковка?</summary><p>Да, опция появится на чекауте в следующей версии прототипа.</p></details>
          </div>
        </div>
      </div>""",
        ),
    )

    write(
        "about/index.html",
        shell(
            1,
            "О проекте",
            """
      <div class="wrap section">
        <div class="content-block">
          <h1>О Универмаге «Россия»</h1>
          <p>Официальный интернет-магазин одежды и мерча Национального центра «Россия». Этот абзац — рыбный текст о миссии, эксклюзивном праве на дизайн и связи с площадкой на ВДНХ.</p>
          <p>Страница закрывает брендовый и E-E-A-T спрос: кто мы, почему официальный канал, где производство и как связаться.</p>
        </div>
      </div>""",
        ),
    )

    write(
        "blog/index.html",
        shell(
            1,
            "Блог",
            """
      <div class="wrap section">
        <h1>Журнал</h1>
        <p class="page-intro">Информационный кластер: гиды, коллекции, подарки. Три демо-статьи.</p>
        <div class="blog-grid">
          <article class="blog-card"><div class="thumb" style="background-image:url('https://images.unsplash.com/photo-1445205170230-053b83016050?w=800');"></div><div class="body"><h3>Как выбрать размер свитшота</h3><p>Рыба · 5 мин</p></div></article>
          <article class="blog-card"><div class="thumb" style="background-image:url('https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800');"></div><motion class="body"><h3>Подарки с символикой: гид 2026</h3><p>Рыба · 7 мин</p></div></article>
          <article class="blog-card"><div class="thumb" style="background-image:url('https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=800');"></div><div class="body"><h3>История Russia Capsule</h3><p>Рыба · 4 мин</p></div></article>
        </div>
      </div>""".replace("<motion", "<motion").replace("<motion class", "<div class").replace("</motion>", "</div>"),
        ),
    )

    write(
        "gift-cards/index.html",
        shell(
            1,
            "Подарочные карты",
            """
      <div class="wrap section">
        <div class="content-block">
          <h1>Подарочные карты</h1>
          <p>Отдельный подарочный сценарий из семантического ТЗ. Номиналы 3 000 · 5 000 · 10 000 ₽ — рыбные данные.</p>
          <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:20px;">
            <button class="btn btn-secondary" type="button">3 000 ₽</button>
            <button class="btn btn-primary" type="button">5 000 ₽</button>
            <button class="btn btn-secondary" type="button">10 000 ₽</button>
          </div>
        </div>
      </div>""",
        ),
    )


if __name__ == "__main__":
    main()
