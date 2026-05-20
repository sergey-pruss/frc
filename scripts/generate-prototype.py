#!/usr/bin/env python3
"""Generate static shop prototype pages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from content import (  # noqa: E402
    BLOG_POSTS,
    BRAND,
    BRAND_QUOTE,
    CATEGORIES,
    COLLECTIONS,
    EDITORIAL_SHOTS,
    HERO_MOSAIC_SLUGS,
    PRODUCTS,
)

ASSET_VERSION = "20260520d"
BASE_URL = "https://frc.sergeypruss.ru"


def fmt_price(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f") + " ₽"


def shell(depth: int, title: str, body: str, desc: str | None = None, canonical_path: str = "") -> str:
    root = "../" * depth
    canonical_url = f"{BASE_URL}/{canonical_path}"
    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — {BRAND['name']}</title>
    <meta name="description" content="{desc or BRAND['tagline']}">
    <meta name="robots" content="noindex, nofollow">
    <link rel="canonical" href="{canonical_url}">
    <link rel="icon" type="image/png" sizes="32x32" href="{root}assets/favicon-32.png?v={ASSET_VERSION}">
    <link rel="icon" type="image/png" sizes="512x512" href="{root}assets/favicon.png?v={ASSET_VERSION}">
    <link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png?v={ASSET_VERSION}">
    <link rel="stylesheet" href="{root}assets/shop.css?v={ASSET_VERSION}">
  </head>
  <body>
    <div data-site-header></div>
    <main>
{body}
    </main>
    <div data-site-footer></div>
    <script src="{root}assets/site.js?v={ASSET_VERSION}" data-depth="{depth}"></script>
  </body>
</html>
"""


def card(p: dict, depth: int, *, editorial: bool = False) -> str:
    root = "../" * depth
    old = f'<span class="price-old">{fmt_price(p["old"])}</span>' if p["old"] else ""
    extra = " product-card--editorial" if editorial else ""
    short = "" if editorial else f"<p>{p['short']}</p>"
    return f"""
        <article class="product-card{extra}">
          <a href="{root}product/{p['slug']}/">
            <div class="product-thumb">
              <span class="product-tag">{p['tag']}</span>
              <img src="{p['img']}" alt="{p['title']} — {BRAND['name']}" loading="lazy" width="400" height="500">
            </div>
            <div class="product-body">
              <h3>{p['title']}</h3>
              {short}
              <div class="price-row">
                <span class="price">{fmt_price(p['price'])}</span>
                {old}
              </div>
            </div>
          </a>
        </article>"""


def product_by_slug(slug: str) -> dict:
    return next(p for p in PRODUCTS if p["slug"] == slug)


def hero_mosaic_html(depth: int = 0) -> str:
    root = "../" * depth
    areas = [
        "hero-mosaic__tile--a",
        "hero-mosaic__tile--b",
        "hero-mosaic__tile--c",
        "hero-mosaic__tile--d",
    ]
    tiles = []
    for area, slug in zip(areas, HERO_MOSAIC_SLUGS):
        p = product_by_slug(slug)
        tiles.append(
            f"""<a class="hero-mosaic__tile {area}" href="{root}product/{p['slug']}/" style="background-image:url('{p['img']}')">
              <span class="hero-mosaic__label">{p['title']}</span>
            </a>"""
        )
    return f"""
      <section class="hero-mosaic">
        <div class="wrap hero-mosaic__layout">
          <div class="hero-mosaic__intro">
            <p class="eyebrow">Официальный магазин · {BRAND['center']}</p>
            <h1>{BRAND['name']}</h1>
            <p class="hero-lead">Минималистичная витрина с акцентом на визуал: крупные фото, простой каталог и понятные кнопки.</p>
            <div class="hero-nav-cta">
              <a class="btn btn-primary btn-xl" href="{root}catalog/">Каталог</a>
              <a class="btn btn-primary btn-xl" href="{root}collections/">Мерч</a>
              <a class="btn btn-secondary btn-xl" href="{root}contacts/">Контакты</a>
            </div>
          </div>
          <div class="hero-mosaic__grid" aria-label="Подборка товаров">
            {"".join(tiles)}
          </div>
        </div>
      </section>"""


def editorial_strip_html(depth: int = 0) -> str:
    root = "../" * depth
    shots = "".join(
        f"""<a class="editorial-shot" href="{root}{s['href']}" style="background-image:url('{s['img']}')">
            <span class="editorial-shot__title">{s['title']}</span>
          </a>"""
        for s in EDITORIAL_SHOTS
    )
    return f"""
      <section class="editorial-strip">
        <div class="wrap">
          <div class="section-head section-head--minimal">
            <h2>Образы</h2>
            <p>Мерч на моделях и крупные планы — как в референсах fashion-брендов.</p>
          </div>
          <div class="editorial-grid">{shots}</div>
        </div>
      </section>"""


def category_visual_tiles(depth: int = 0) -> str:
    root = "../" * depth
    parts = []
    for slug, label, _ in CATEGORIES:
        img = next((p["img"] for p in PRODUCTS if p["cat"] == slug), "")
        parts.append(
            f'<a class="category-visual" href="{root}catalog/{slug}/" style="background-image:url(\'{img}\')"><span>{label}</span></a>'
        )
    return "".join(parts)


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("wrote", rel)


def simple_page(title: str, intro: str, inner: str, depth: int = 1) -> str:
    root = "../" * depth
    return f"""
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="{root}">Главная</a> / <span>{title}</span></nav>
        <div class="page-hero">
          <p class="eyebrow">{BRAND['name']}</p>
          <h1>{title}</h1>
          <p>{intro}</p>
        </div>
{inner}
      </div>"""


def category_chips(depth: int, active: str | None) -> str:
    root = "../" * depth
    parts = [f'<a href="{root}catalog/" class="{"is-active" if active is None else ""}">Все</a>']
    for slug, label, _ in CATEGORIES:
        cls = "is-active" if active == slug else ""
        parts.append(f'<a href="{root}catalog/{slug}/" class="{cls}">{label}</a>')
    return "\n".join(parts)


def products_for_collection(slug: str) -> list:
    if slug == "russia-capsule":
        return [p for p in PRODUCTS if p["collection"] == "Russia Capsule"]
    if slug == "mystery-box":
        return [p for p in PRODUCTS if p["collection"] == "Mystery Box" or p["slug"] in ("podarochnyj-nabor", "sumka-shopper")]
    if slug == "zimnyaya-liniya":
        return [p for p in PRODUCTS if p["collection"] == "Зимняя линейка 2026"]
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
    new_items = [p for p in PRODUCTS if p["tag"] in ("Новинка", "−9%", "−10%", "−38%", "Набор")][:8]
    coll_tiles = "".join(
        f"""
        <a class="collection-tile" href="collections/{c['slug']}/">
          <div class="collection-tile__img" style="background-image:url('{c['img']}')"></div>
          <div class="collection-tile__body"><h3>{c['title']}</h3><p>{c['lead'][:110]}…</p></div>
        </a>"""
        for c in COLLECTIONS
    )
    write(
        "index.html",
        shell(
            0,
            "Главная",
            f"""
      {hero_mosaic_html(0)}
      {editorial_strip_html(0)}
      <section class="section">
        <div class="wrap">
          <div class="section-head section-head--minimal"><h2>Новинки</h2><a class="btn btn-ghost" href="catalog/new/">Смотреть все</a></div>
          <div class="product-grid product-grid--editorial">{"".join(card(p, 0, editorial=True) for p in new_items[:4])}</div>
        </div>
      </section>
      <section class="section muted">
        <div class="wrap">
          <div class="section-head section-head--minimal"><h2>Категории</h2></div>
          <div class="category-visual-grid">{category_visual_tiles(0)}</div>
        </div>
      </section>
      <section class="section">
        <div class="wrap">
          <div class="section-head section-head--minimal"><h2>Коллекции</h2></div>
          <div class="collection-tiles">{coll_tiles}</div>
        </div>
      </section>""",
            BRAND["tagline"],
            canonical_path="",
        ),
    )

    cat_links = "".join(
        f'<a class="category-link-card" href="{slug}/"><strong>{label}</strong><span>{seo[:70]}…</span></a>'
        for slug, label, seo in CATEGORIES
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
        <div class="category-visual-grid">{category_visual_tiles(1)}</div>
        <h2 class="subsection-title">Все товары</h2>
        <div class="product-grid product-grid--editorial">{"".join(card(p, 1, editorial=True) for p in PRODUCTS)}</div>
      </div>""",
            "Каталог официальной одежды и мерча Национального центра «Россия»: категории, коллекции, подарки и доставка по России.",
        ),
    )

    search_results = "".join(card(p, 1) for p in PRODUCTS[:4])
    favorite_items = "".join(card(p, 1) for p in (PRODUCTS[0], PRODUCTS[4], PRODUCTS[10]))
    cart_rows = "".join(
        f"""
        <li class="cart-item">
          <img src="{p['img']}" alt="{p['title']} — {BRAND['name']}">
          <div><strong>{p['title']}</strong><span>{p['cat_label']} · размер M</span></div>
          <b>{fmt_price(p['price'])}</b>
        </li>"""
        for p in PRODUCTS[:3]
    )
    order_rows = "".join(
        f"<li><span>{p['title']}</span><strong>{fmt_price(p['price'])}</strong></li>"
        for p in PRODUCTS[:3]
    )
    store_cards = """
        <article class="store-card"><strong>ВДНХ, павильон Национального центра «Россия»</strong><span>Главная точка продаж, примерка и самовывоз заказов.</span><small>Ежедневно 10:00–21:00</small></article>
        <article class="store-card"><strong>Временная витрина мероприятий</strong><span>Поп-ап формат для форумов, выставок и специальных программ центра.</span><small>По расписанию мероприятий</small></article>
        <article class="store-card"><strong>Онлайн-заказ по России</strong><span>Доставка СДЭК, Почтой России и курьером по Москве.</span><small>Отправка 1–2 рабочих дня</small></article>"""
    account_nav = """
        <div class="account-shell">
          <aside class="account-nav">
            <a href="../login/">Вход</a>
            <a href="../profile/">Профиль</a>
            <a href="../orders/">Заказы</a>
            <a href="../wishlist/">Wish list</a>
          </aside>"""

    write(
        "stores/index.html",
        shell(
            1,
            "Магазины",
            simple_page(
                "Магазины",
                "Точки продаж, самовывоз и временные витрины Универмага «Россия».",
                f'<div class="store-grid">{store_cards}</div><div class="map-panel">Карта магазинов и зон самовывоза</div>',
            ),
        ),
    )

    write(
        "favorites/index.html",
        shell(
            1,
            "Избранное",
            simple_page(
                "Избранное",
                "Сохраненные товары для быстрой покупки или сравнения перед визитом в магазин.",
                f'<div class="product-grid">{favorite_items}</div>',
            ),
        ),
    )

    write(
        "cart/index.html",
        shell(
            1,
            "Корзина",
            simple_page(
                "Корзина",
                "Проверьте состав заказа, размеры и условия доставки.",
                f"""
        <div class="checkout-layout">
          <section class="content-block"><ul class="cart-list">{cart_rows}</ul></section>
          <aside class="summary-card"><h2>Итого</h2><p>3 товара</p><strong>{fmt_price(sum(p['price'] for p in PRODUCTS[:3]))}</strong><a class="btn btn-primary" href="../checkout/">Оформить заказ</a></aside>
        </div>""",
            ),
        ),
    )

    write(
        "checkout/index.html",
        shell(
            1,
            "Оформление заказа",
            simple_page(
                "Оформление заказа",
                "Контакты, доставка, оплата и подтверждение заказа в одном спокойном сценарии.",
                f"""
        <div class="checkout-layout">
          <form class="content-block demo-form" onsubmit="return false;">
            <label>Имя <input type="text" value="Сергей"></label>
            <label>Телефон <input type="tel" value="+7"></label>
            <label>Город <input type="text" value="Москва"></label>
            <label>Способ доставки <select><option>Курьер</option><option>Самовывоз с ВДНХ</option><option>СДЭК</option></select></label>
            <label>Комментарий <textarea rows="4">Подарочная упаковка</textarea></label>
          </form>
          <aside class="summary-card"><h2>Ваш заказ</h2><ul>{order_rows}</ul><strong>{fmt_price(sum(p['price'] for p in PRODUCTS[:3]))}</strong><button class="btn btn-primary" type="button">Подтвердить</button></aside>
        </div>""",
            ),
        ),
    )

    write(
        "search/index.html",
        shell(
            1,
            "Поиск",
            simple_page(
                "Поиск",
                "Результаты поиска по каталогу, коллекциям и материалам журнала.",
                f"""
        <form class="search-panel" onsubmit="return false;"><input type="search" value="футболка россия" aria-label="Поиск"><button class="btn btn-primary" type="submit">Найти</button></form>
        <h2 class="subsection-title">Результаты поиска</h2>
        <div class="product-grid">{search_results}</div>
        <section class="empty-state"><h2>Ничего не найдено</h2><p>Проверьте запрос или перейдите в каталог. Для такой страницы нужен отдельный текст, чтобы не оставлять пользователя в тупике.</p><a class="btn btn-secondary" href="../catalog/">В каталог</a></section>""",
            ),
        ),
    )

    write(
        "404.html",
        shell(
            0,
            "404",
            """
      <div class="wrap section">
        <section class="not-found">
          <p class="eyebrow">Страница не найдена</p>
          <h1>404</h1>
          <p>Такой страницы в Универмаге «Россия» нет. Можно вернуться в каталог, посмотреть коллекции или воспользоваться поиском.</p>
          <div class="cta-row"><a class="btn btn-primary" href="catalog/">Каталог</a><a class="btn btn-secondary" href="search/">Поиск</a></div>
        </section>
      </div>""",
        ),
    )

    write(
        "login/index.html",
        shell(
            1,
            "Вход и регистрация",
            simple_page(
                "Вход и регистрация",
                "Личный кабинет хранит заказы, избранное, адреса доставки и бонусные баллы.",
                """
        <div class="auth-grid">
          <form class="content-block demo-form" onsubmit="return false;"><h2>Войти</h2><label>Email <input type="email"></label><label>Пароль <input type="password"></label><button class="btn btn-primary" type="submit">Войти</button></form>
          <form class="content-block demo-form" onsubmit="return false;"><h2>Регистрация</h2><label>Имя <input type="text"></label><label>Email <input type="email"></label><label>Телефон <input type="tel"></label><button class="btn btn-secondary" type="submit">Создать аккаунт</button></form>
        </div>""",
            ),
        ),
    )

    write(
        "profile/index.html",
        shell(
            1,
            "Профиль",
            simple_page(
                "Профиль",
                "Персональные данные, адреса доставки и настройки уведомлений.",
                f"""{account_nav}<section class="content-block"><h2>Личные данные</h2><p><strong>Имя:</strong> Сергей</p><p><strong>Email:</strong> sergey@example.com</p><p><strong>Адрес:</strong> Москва, ВДНХ</p></section></div>""",
            ),
        ),
    )

    write(
        "orders/index.html",
        shell(
            1,
            "Заказы",
            simple_page(
                "Заказы",
                "История покупок и статусы доставки.",
                f"""{account_nav}<section class="content-block"><h2>Последние заказы</h2><ul class="order-list"><li><span>UR-260519-01 · Сборка</span><strong>18 470 ₽</strong></li><li><span>UR-250519-04 · Доставлен</span><strong>5 490 ₽</strong></li></ul></section></div>""",
            ),
        ),
    )

    write(
        "wishlist/index.html",
        shell(
            1,
            "Wish list",
            simple_page(
                "Wish list",
                "Личный список желаний внутри кабинета.",
                f"""{account_nav}<section><div class="product-grid">{favorite_items}</div></section></div>""",
            ),
        ),
    )

    for slug, label, seo in CATEGORIES:
        items = [p for p in PRODUCTS if p["cat"] == slug]
        write(
            f"catalog/{slug}/index.html",
            shell(
                2,
                label,
                f"""
      <div class="wrap section">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../">Каталог</a> / <span>{label}</span></nav>
        <h1>{label} — купить с доставкой по России</h1>
        <p class="page-intro">{seo}</p>
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
          <p>{BRAND['tagline']}. Площадка — {BRAND['center']} на ВДНХ.</p>
          <p>Фирменные цвета универмага — зелёный Pantone 4216 и золотой Pantone 871. Упаковка и бирки выполняются в крафтовой палитре с лентами красного, зелёного и белого цвета.</p>
          <h2>В магазине</h2>
          <ul><li>Одежда и аксессуары с символикой центра</li><li>Коллекции Russia Capsule, Mystery Box и сезонные линейки</li><li>Подарочные наборы, сертификаты и корпоративные заказы</li></ul>
          <blockquote class="brand-quote-card brand-quote">
            <p class="brand-quote__lead">{BRAND_QUOTE['before']} <span class="brand-quote__accent">{BRAND_QUOTE['accent']}</span></p>
            <p class="brand-quote__dash" aria-hidden="true">—</p>
            <p class="brand-quote__rest">{BRAND_QUOTE['after']}</p>
          </blockquote>
          <h2>Контакты</h2>
          <p><a href="../contacts/">Связаться с нами</a> · <a href="../stores/">Магазины и самовывоз</a></p>
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
