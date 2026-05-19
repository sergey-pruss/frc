#!/usr/bin/env python3
"""Generate static shop prototype pages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from content import BLOG_POSTS, BRAND, BRIEF_PRINCIPLES, CATEGORIES, COLLECTIONS, PRODUCTS, REFERENCES  # noqa: E402


def fmt_price(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f") + " ₽"


def shell(depth: int, title: str, body: str, desc: str | None = None) -> str:
    root = "../" * depth
    canonical_path = "" if title == "Главная" else f"{title.lower().replace(' ', '-')}/"
    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — {BRAND['name']}</title>
    <meta name="description" content="{desc or BRAND['tagline']}">
    <meta name="robots" content="noindex, nofollow">
    <link rel="canonical" href="https://sergey-pruss.github.io/frc/{canonical_path}">
    <link rel="stylesheet" href="{root}assets/shop.css">
  </head>
  <body>
    <div data-site-header></div>
    <main>
{body}
    </main>
    <div data-site-footer></div>
    <script src="{root}assets/site.js" data-depth="{depth}"></script>
  </body>
</html>
"""


def card(p: dict, depth: int) -> str:
    root = "../" * depth
    old = f'<span class="price-old">{fmt_price(p["old"])}</span>' if p["old"] else ""
    return f"""
        <article class="product-card">
          <a href="{root}product/{p['slug']}/">
            <div class="product-thumb">
              <span class="product-tag">{p['tag']}</span>
              <img src="{p['img']}" alt="{p['title']} — {BRAND['name']}" loading="lazy" width="400" height="500">
            </div>
            <div class="product-body">
              <h3>{p['title']}</h3>
              <p>{p['short']}</p>
              <div class="price-row">
                <span class="price">{fmt_price(p['price'])}</span>
                {old}
              </div>
            </div>
          </a>
        </article>"""


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("wrote", rel)


def category_chips(depth: int, active: str | None) -> str:
    root = "../" * depth
    parts = [f'<a href="{root}catalog/" class="{"is-active" if active is None else ""}">Все</a>']
    for slug, label, _, _ in CATEGORIES:
        cls = "is-active" if active == slug else ""
        parts.append(f'<a href="{root}catalog/{slug}/" class="{cls}">{label}</a>')
    return "\n".join(parts)


def products_for_collection(slug: str) -> list:
    if slug == "russia-capsule":
        return [p for p in PRODUCTS if p["collection"] == "Russia Capsule"]
    if slug == "mystery-box":
        return [p for p in PRODUCTS if p["slug"] in ("podarochnyj-nabor", "sumka-shopper", "kepka-simvol")]
    if slug == "zimnyaya-liniya":
        return [p for p in PRODUCTS if p["cat"] in ("kurtki", "svitshoty")]
    return []


def product_body(p: dict) -> str:
    thumbs = "".join(
        f'<button type="button" class="{"is-active" if i == 0 else ""}"><img src="{p["img"]}" alt=""></button>'
        for i in range(4)
    )
    related = [x for x in PRODUCTS if x["cat"] == p["cat"] and x["slug"] != p["slug"]][:2]
    return f"""
      <div class="wrap">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../../catalog/">Каталог</a> / <a href="../../catalog/{p['cat']}/">{p['cat_label']}</a> / <span>{p['title']}</span></nav>
        <div class="product-page">
          <div>
            <div class="gallery-main"><img src="{p['img']}" alt="{p['title']} — {BRAND['name']}"></div>
            <div class="gallery-thumbs">{thumbs}</div>
          </div>
          <div class="product-info">
            <p class="pill" style="display:inline-block;">{p['tag']} · {p['collection']}</p>
            <h1>{p['title']}</h1>
            <p class="lead-price">{fmt_price(p['price'])}</p>
            <p>{p['long']}</p>
            <p><strong>Размер</strong> · <a href="../../sizes/">таблица размеров</a></p>
            <div class="size-grid">
              <button type="button">XS</button><button type="button">S</button><button type="button" class="is-active">M</button><button type="button">L</button><button type="button">XL</button>
            </div>
            <div class="cta-row">
              <button class="btn btn-primary" type="button" data-demo-cart>В корзину</button>
              <a class="btn btn-secondary" href="../../delivery/">Доставка и возврат</a>
            </div>
            <ul class="spec-list">
              <li><span>Коллекция</span><span>{p['collection']}</span></li>
              <li><span>Аудитория</span><span>{p['gender']}</span></li>
              <li><span>Состав</span><span>{p['composition']}</span></li>
              <li><span>Уход</span><span>{p['care']}</span></li>
              <li><span>Артикул</span><span>UR-{p['slug'][:8].upper()}</span></li>
              <li><span>Наличие</span><span>В наличии</span></li>
            </ul>
            <script type="application/ld+json">
              {{
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "{p['title']}",
                "brand": {{"@type": "Brand", "name": "{BRAND['name']}"}},
                "category": "{p['cat_label']}",
                "image": "{p['img']}",
                "description": "{p['short']}",
                "sku": "UR-{p['slug'][:8].upper()}",
                "offers": {{
                  "@type": "Offer",
                  "priceCurrency": "RUB",
                  "price": "{p['price']}",
                  "availability": "https://schema.org/InStock"
                }}
              }}
            </script>
          </div>
        </div>
        <section class="section" style="padding-top:0;">
          <h2 class="subsection-title">Похожие товары</h2>
          <div class="product-grid">{"".join(card(x, 2) for x in related)}</div>
        </section>
      </div>""".replace("<div class=", "<div class=").replace("<div class=", "<div class=").replace("</div>", "</div>")



def main() -> None:
    new_items = [p for p in PRODUCTS if p["tag"] in ("Новинка", "−9%", "Набор")][:8]
    coll_tiles = "".join(
        f"""
        <a class="collection-tile" href="collections/{c['slug']}/">
          <div class="collection-tile__img" style="background-image:url('{c['img']}')"></div>
          <div class="collection-tile__body"><h3>{c['title']}</h3><p>{c['lead'][:110]}…</p></div>
        </a>"""
        for c in COLLECTIONS
    )
    reference_links = "".join(
        f'<a class="reference-link" href="{url}" target="_blank" rel="noreferrer">{label}</a>'
        for label, url in REFERENCES
    )
    principles = "".join(f"<li>{item}</li>" for item in BRIEF_PRINCIPLES)

    write(
        "index.html",
        shell(
            0,
            "Главная",
            f"""
      <section class="hero-shop">
        <div class="wrap hero-grid">
          <div class="hero-copy">
            <div class="hero-badges">
              <span class="pill">Официальный магазин</span>
              <span class="pill">Доставка по России</span>
              <span class="pill">{BRAND['center']}</span>
            </div>
            <h1>Официальный мерч {BRAND['center']}</h1>
            <p>{BRAND['tagline']}. Прототип учитывает клиентский бриф, SEO-ТЗ, структуру интернет-магазина и референсы Универмага.</p>
            <div class="cta-row">
              <a class="btn btn-primary" href="catalog/">Каталог</a>
              <a class="btn btn-secondary" href="collections/">Коллекции</a>
            </div>
          </div>
          <div class="hero-visual" aria-hidden="true"></div>
        </div>
      </section>
      <section class="section muted">
        <div class="wrap brief-grid">
          <div class="content-block">
            <p class="eyebrow">Бриф клиента</p>
            <h2>В меру современно, аккуратно, без провокаций</h2>
            <p>Прототип держит государственный контекст: официальность, спокойная премиальность, понятная коммерческая структура и отдельный слой коллекционных историй.</p>
          </div>
          <div class="content-block">
            <h3>Принципы</h3>
            <ul class="checklist">{principles}</ul>
          </div>
        </div>
      </section>
      <section class="section">
        <div class="wrap">
          <div class="section-head"><h2>Кому подбираем</h2><p>Быстрый вход в ключевые покупательские сценарии.</p></div>
          <div class="audience-grid">
            <a class="audience-card" href="catalog/futbolki/"><strong>Мужчинам и женщинам</strong><span>Футболки, свитшоты, куртки</span></a>
            <a class="audience-card" href="gift-cards/"><strong>Подарки</strong><span>Сертификаты и наборы</span></a>
            <a class="audience-card" href="collections/mystery-box/"><strong>Mystery Box</strong><span>Сюрприз-набор</span></a>
            <a class="audience-card" href="corporate/"><strong>Бизнесу</strong><span>Опт и мерч</span></a>
          </div>
        </div>
      </section>
      <section class="section muted">
        <div class="wrap">
          <div class="section-head"><h2>Новинки</h2><a class="btn btn-ghost" href="catalog/new/">Все новинки</a></div>
          <div class="product-grid">{"".join(card(p, 0) for p in new_items)}</div>
        </div>
      </section>
      <section class="section">
        <div class="wrap">
          <div class="section-head"><h2>Коллекции</h2><p>Капсулы, сезонные витрины и подарочные сценарии.</p></div>
          <div class="collection-tiles">{coll_tiles}</div>
        </div>
      </section>
      <section class="section">
        <div class="wrap trust-row">
          <div class="trust-card"><strong>Официальный магазин</strong>Мерч только здесь.</div>
          <div class="trust-card"><strong>Доставка по РФ</strong>СДЭК, Почта, курьер.</div>
          <div class="trust-card"><strong>Возврат 14 дней</strong>При сохранении бирок.</div>
          <div class="trust-card"><strong>Лояльность</strong><a href="loyalty/">баллы</a> с покупки.</div>
        </div>
      </section>""",
        ),
    )

    cat_links = "".join(
        f'<a class="category-link-card" href="{slug}/"><strong>{label}</strong><span>{seo[:70]}…</span></a>'
        for slug, label, seo, _ in CATEGORIES
    )
    write(
        "catalog/index.html",
        shell(
            1,
            "Каталог",
            f"""
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="../">Главная</a> / <span>Каталог</span></nav>
        <h1>Каталог</h1>
        <p class="page-intro">Купить мерч {BRAND['center']} онлайн — все категории и коллекции.</p>
        <div class="category-chips">{category_chips(1, None)}</div>
        <div class="category-links">{cat_links}</div>
        <h2 class="subsection-title">Все товары</h2>
        <div class="product-grid">{"".join(card(p, 1) for p in PRODUCTS)}</div>
      </div>""",
            "Каталог официальной одежды и мерча Национального центра «Россия»: категории, коллекции, подарки и доставка по России.",
        ),
    )

    for slug, label, seo, note in CATEGORIES:
        items = [p for p in PRODUCTS if p["cat"] == slug]
        write(
            f"catalog/{slug}/index.html",
            shell(
                2,
                label,
                f"""
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../">Каталог</a> / <span>{label}</span></nav>
        <h1>{label}</h1>
        <p class="page-intro">{seo}</p>
        <p class="page-note">{note}</p>
        <div class="category-chips">{category_chips(2, slug)}</div>
        <div class="filters-bar">
          <div>Фильтр: размер · цвет · коллекция · цена</div>
          <select aria-label="Сортировка"><option>По популярности</option><option>Сначала новые</option></select>
        </div>
        <div class="product-grid">{"".join(card(p, 2) for p in items)}</div>
        <div class="faq category-faq">
          <h2>Вопросы о категории</h2>
          <details open><summary>Как подобрать размер?</summary><p><a href="../../sizes/">Таблица размеров</a>.</p></details>
          <details><summary>Доставка в регионы?</summary><p><a href="../../delivery/">Условия доставки</a>.</p></details>
        </div>
      </div>""",
                seo,
            ),
        )

    write(
        "catalog/new/index.html",
        shell(
            2,
            "Новинки",
            f"""
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../">Каталог</a> / <span>Новинки</span></nav>
        <h1>Новинки</h1>
        <p class="page-intro">Свежие поступления сезона.</p>
        <div class="product-grid">{"".join(card(p, 2) for p in new_items)}</div>
      </div>""",
        ),
    )

    for p in PRODUCTS:
        write(f"product/{p['slug']}/index.html", shell(2, p["title"], product_body(p), p["short"]))

    banners = "".join(
        f"""
        <article class="collection-banner" style="margin-bottom:24px;">
          <div class="visual" style="background-image:url('{c['img']}')"></div>
          <div class="copy"><h3>{c['title']}</h3><p>{c['lead']}</p><a class="btn btn-primary" href="{c['slug']}/">Смотреть</a></div>
        </article>"""
        for c in COLLECTIONS
    )
    write(
        "collections/index.html",
        shell(1, "Коллекции", f'<div class="wrap section"><nav class="breadcrumbs"><a href="../">Главная</a> / <span>Коллекции</span></nav><h1>Коллекции</h1><p class="page-intro">Капсулы, подарочные наборы и сезонные витрины: отдельный SEO-слой для историй, образов и товарных подборок.</p>{banners}</div>'),
    )

    for c in COLLECTIONS:
        prods = products_for_collection(c["slug"])
        write(
            f"collections/{c['slug']}/index.html",
            shell(
                2,
                c["title"],
                f"""
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../">Коллекции</a> / <span>{c['title']}</span></nav>
        <h1>{c['title']}</h1>
        <p class="page-intro">{c['lead']}</p>
        <p class="page-note">{c['story']}</p>
        <div class="product-grid">{"".join(card(p, 2) for p in prods)}</div>
      </div>""",
                c["lead"],
            ),
        )

    write(
        "delivery/index.html",
        shell(
            1,
            "Доставка и оплата",
            f"""
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="../">Главная</a> / <span>Доставка</span></nav>
        <div class="content-block prose">
          <h1>Доставка, оплата и возврат</h1>
          <p>Сервисная страница доверия для {BRAND['name']}: доставка, оплата, возврат, размеры и контакты.</p>
          <h2 id="delivery">Доставка</h2>
          <ul><li>Москва — курьер 1–2 дня, от 390 ₽.</li><li>Регионы — СДЭК / Почта 3–7 дней, от 290 ₽.</li><li>Бесплатно от 7 000 ₽.</li></ul>
          <h2>Оплата</h2>
          <p>Карты, СБП. Юрлица — <a href="../corporate/">по счёту</a>.</p>
          <h2 id="return">Возврат</h2>
          <p>14 дней. <a href="../sizes/">Размеры</a>.</p>
          <div class="faq" id="faq">
            <h2>FAQ</h2>
            <details open><summary>Как отследить заказ?</summary><p>SMS и email со ссылкой.</p></details>
            <details><summary>Подарочная упаковка?</summary><p>+290 ₽ в корзине.</p></details>
            <details><summary>Контакты?</summary><p><a href="../contacts/">Контакты</a>, {BRAND['email']}</p></details>
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
            f"""
      <div class="wrap section">
        <div class="content-block prose">
          <h1>О {BRAND['name']}</h1>
          <p>{BRAND['tagline']} {BRAND['center']} на ВДНХ.</p>
          <p>Сайт проектируется как официальный интернет-магазин: каталог, коллекции, подарочные сценарии, сервисные страницы и SEO-документ для разработки.</p>
          <h2>В магазине</h2>
          <ul><li>Одежда и аксессуары</li><li>Коллекции и капсулы</li><li>Подарки и корпоратив</li></ul>
          <h2>Фирменные материалы и референсы</h2>
          <div class="reference-list">{reference_links}</div>
        </div>
      </div>""",
        ),
    )

    write(
        "contacts/index.html",
        shell(
            1,
            "Контакты",
            f"""
      <div class="wrap section">
        <div class="content-block prose">
          <h1>Контакты</h1>
          <p><strong>Адрес:</strong> {BRAND['address']}</p>
          <p><strong>Телефон:</strong> <a href="tel:+74950000000">{BRAND['phone']}</a></p>
          <p><strong>Email:</strong> <a href="mailto:{BRAND['email']}">{BRAND['email']}</a></p>
          <form class="demo-form" onsubmit="return false;">
            <label>Имя <input type="text"></label>
            <label>Email <input type="email"></label>
            <label>Сообщение <textarea rows="4"></textarea></label>
            <button class="btn btn-primary" type="submit">Отправить</button>
          </form>
        </div>
      </div>""",
        ),
    )

    write(
        "sizes/index.html",
        shell(
            1,
            "Размеры",
            """
      <div class="wrap section">
        <div class="content-block prose">
          <h1>Таблица размеров</h1>
          <p>Отдельная посадочная для карточек товаров, FAQ и снижения возвратов.</p>
          <table class="size-table">
            <thead><tr><th>Размер</th><th>Грудь</th><th>Длина</th><th>Рукав</th></tr></thead>
            <tbody>
              <tr><td>XS</td><td>88–92</td><td>66</td><td>60</td></tr>
              <tr><td>S</td><td>92–96</td><td>68</td><td>61</td></tr>
              <tr><td>M</td><td>96–100</td><td>70</td><td>62</td></tr>
              <tr><td>L</td><td>100–104</td><td>72</td><td>63</td></tr>
              <tr><td>XL</td><td>104–108</td><td>74</td><td>64</td></tr>
            </tbody>
          </table>
        </div>
      </div>""",
        ),
    )

    write(
        "loyalty/index.html",
        shell(1, "Программа лояльности", '<div class="wrap section"><div class="content-block prose"><h1>Программа лояльности</h1><p>5% баллами, 1 балл = 1 ₽, списание до 30%.</p></div></div>'),
    )

    write(
        "corporate/index.html",
        shell(
            1,
            "Корпоративным клиентам",
            f'<div class="wrap section"><div class="content-block prose"><h1>Корпоративным клиентам</h1><p>Опт от 50 шт., брендирование. <a href="mailto:{BRAND["email"]}">{BRAND["email"]}</a></p></div></div>',
        ),
    )

    write(
        "gift-cards/index.html",
        shell(
            1,
            "Подарочные карты",
            f"""
      <div class="wrap section">
        <div class="content-block prose">
          <h1>Подарочные карты</h1>
          <p>Сертификаты и <a href="../product/podarochnyj-nabor/">набор «Старт»</a>.</p>
          <div class="cta-row">
            <button class="btn btn-secondary" type="button">3 000 ₽</button>
            <button class="btn btn-primary" type="button">5 000 ₽</button>
            <button class="btn btn-secondary" type="button">10 000 ₽</button>
          </div>
        </div>
      </div>""",
        ),
    )

    blog_cards = "".join(
        f'<article class="blog-card"><a href="{post["slug"]}/"><div class="thumb" style="background-image:url(\'{post["img"]}\')"></div><div class="body"><h3>{post["title"]}</h3><p>{post["excerpt"]}</p></div></a></article>'
        for post in BLOG_POSTS
    )
    write("blog/index.html", shell(1, "Журнал", f'<div class="wrap section"><h1>Журнал</h1><p class="page-intro">Гиды и коллекции.</p><div class="blog-grid">{blog_cards}</div></div>'))

    for post in BLOG_POSTS:
        write(
            f"blog/{post['slug']}/index.html",
            shell(
                2,
                post["title"],
                f"""
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../">Журнал</a> / <span>{post['title']}</span></nav>
        <article class="content-block prose">
          <h1>{post['title']}</h1>
          <p>{post['excerpt']}</p>
          <p>{post['body']}</p>
          <p><a class="btn btn-secondary" href="../../catalog/">В каталог</a></p>
        </article>
      </div>""",
            ),
        )


if __name__ == "__main__":
    main()
