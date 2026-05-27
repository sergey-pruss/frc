#!/usr/bin/env python3
"""Generate static shop prototype pages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_DIR = "design"


def asset_root(prototype_depth: int) -> str:
    return "../" * (prototype_depth + 1)


def page_root(prototype_depth: int) -> str:
    return "../" * prototype_depth
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

ASSET_VERSION = "20260525a"
BASE_URL = "https://frc.serenity-dev.ru"
FILTER_SIZES = ("XS", "S", "M", "L", "XL", "2XL", "3XL")
FILTER_COLORS = [
    ("belye", "белый", "белые"),
    ("sinie", "синий", "синие"),
    ("krasnye", "красный", "красные"),
    ("chernye", "чёрный", "чёрные"),
    ("rozovye", "розовый", "розовые"),
]

CATEGORY_SEO_NOUNS = {
    "hudi": ("худи", "худи"),
    "svitshoty": ("свитшот", "свитшоты"),
    "futbolki": ("футболка", "футболки"),
    "vetrovki": ("ветровка", "ветровки"),
    "kurtki": ("куртка", "куртки"),
    "aksessuary": ("аксессуар", "аксессуары"),
}


def fmt_price(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f") + " ₽"


def shell(prototype_depth: int, title: str, body: str, desc: str | None = None, canonical_path: str = "") -> str:
    root = asset_root(prototype_depth)
    canonical_url = f"{BASE_URL}/{PROTOTYPE_DIR}/{canonical_path}"
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
    <script src="{root}assets/site.js?v={ASSET_VERSION}" data-depth="{prototype_depth}"></script>
  </body>
</html>
"""


def normalize_color(value: str) -> str:
    normalized = value.replace("ё", "е").lower()
    if "чер" in normalized:
        return "chernye"
    if "бел" in normalized or "молоч" in normalized:
        return "belye"
    if "син" in normalized or "голуб" in normalized:
        return "sinie"
    if "крас" in normalized or "борд" in normalized:
        return "krasnye"
    if "роз" in normalized:
        return "rozovye"
    return normalized


MODEL_CARD_IMAGES = {
    "hudi": "/assets/generated/fashion/khudi-models.png",
    "svitshoty": "/assets/generated/fashion/svitshoty-bez-flisa-models.png",
    "futbolki": "/assets/generated/fashion/futbolki-models.png",
    "vetrovki": "/assets/generated/fashion/vetrovki-models.png",
    "kurtki": "/assets/generated/fashion/kurtki-models.png",
    "aksessuary": "/assets/generated/fashion/aksessuary-models.png",
}

def project_image_path(image: str, prototype_depth: int) -> str:
    if image.startswith(("http://", "https://")):
        return image
    if image.startswith("/"):
        return f"{asset_root(prototype_depth)}{image.lstrip('/')}"
    return image


def model_card_image(p: dict, depth: int) -> str:
    return project_image_path(MODEL_CARD_IMAGES.get(p["cat"], p["img"]), depth)


def card(
    p: dict,
    depth: int,
    *,
    editorial: bool = False,
    seo_keyword: str | None = None,
    image_override: str | None = None,
    extra_class: str = "",
) -> str:
    root = page_root(depth)
    old = f'<span class="price-old">{fmt_price(p["old"])}</span>' if p["old"] else ""
    extra = " product-card--editorial" if editorial else ""
    extra += f" {extra_class}" if extra_class else ""
    short = "" if editorial else f"<p>{p['short']}</p>"
    colors = " ".join(sorted({normalize_color(c) for c in p["colors"]}))
    sizes = " ".join(size.lower() for size in FILTER_SIZES)
    alt = seo_keyword or f"{p['title']} — {BRAND['name']}"
    image = image_override or model_card_image(p, depth)
    subcategory = p.get("subcat", "")
    return f"""
        <article class="product-card{extra}" data-product-card data-category="{p['cat']}" data-subcategory="{subcategory}" data-colors="{colors}" data-sizes="{sizes}" data-price="{p['price']}">
          <a href="{root}product/{p['slug']}/">
            <div class="product-thumb">
              <span class="product-tag">{p['tag']}</span>
              <img src="{image}" alt="{alt}" loading="lazy" width="400" height="500">
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
            f"""<a class="hero-mosaic__tile {area}" href="{root}product/{p['slug']}/" style="background-image:url('{project_image_path(p['img'], depth)}')">
              <span class="hero-mosaic__label">{p['title']}</span>
            </a>"""
        )
    return f"""
      <section class="hero-mosaic">
        <div class="wrap hero-mosaic__layout">
          <div class="hero-mosaic__intro">
            <p class="eyebrow">Официальный магазин · {BRAND['center']}</p>
            <h1>{BRAND['name']}</h1>
            <p class="hero-lead">Lifestyle-мерч в премиальной сдержанной подаче: качество, посадка, материалы и цитаты видны до карточки товара.</p>
            <div class="hero-nav-cta">
              <a class="btn btn-primary btn-xl" href="{root}catalog/">Каталог</a>
              <a class="btn btn-primary btn-xl" href="{root}gift-cards/">Сертификаты</a>
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
        f"""<a class="editorial-shot" href="{root}{s['href']}" style="background-image:url('{project_image_path(s['img'], depth)}')">
            <span class="editorial-shot__title">{s['title']}</span>
          </a>"""
        for s in EDITORIAL_SHOTS
    )
    return f"""
      <section class="editorial-strip">
        <div class="wrap">
          <div class="section-head section-head--minimal">
            <h2>Образы</h2>
            <p>Фотологика по ТЗ: вертикальные кадры, запас фона, полный рост, 3/4, детали и взаимодействия с вещью.</p>
          </div>
          <div class="editorial-grid">{shots}</div>
        </div>
      </section>"""


def home_apple_html(prototype_depth: int = 0) -> str:
    root = page_root(prototype_depth)
    assets = asset_root(prototype_depth)
    new_items = [
        p for p in PRODUCTS if p["tag"] in ("Новинка", "−9%", "−10%", "−38%", "Набор")
    ][:8]
    popular_items = [
        p for p in PRODUCTS if p["tag"] in ("Хит", "Премиум", "Зима", "Подарок")
    ][:8]
    product_rails = (
        product_rail_html("Новинки", f"{root}catalog/new/", "Смотреть все", new_items, prototype_depth, root),
        product_rail_html("Популярное", f"{root}catalog/", "Весь каталог", popular_items, prototype_depth, root),
    )
    return f"""
      <section class="apple-hero">
        <div class="apple-hero__content" data-parallax="text" data-parallax-speed="0.018" data-parallax-limit="14">
          <h1>Мерч — как любимая вещь</h1>
          <p>Премиальная одежда и аксессуары Национального центра «Россия»: спокойная современность, качественные материалы и точная посадка.</p>
          <div class="hero-nav-cta">
            <a class="btn btn-primary btn-xl" href="{root}catalog/">Смотреть каталог</a>
            <a class="btn btn-secondary btn-xl" href="{root}gift-cards/">Подарочные сертификаты</a>
          </div>
        </div>
        <div class="apple-hero__media" data-parallax="image" data-parallax-speed="0.042" data-parallax-limit="34">
          <img src="{assets}assets/generated/editorial/home-hero-apple-wall.png" alt="Модели в одежде и аксессуарах Универмага «Россия»">
        </div>
      </section>
      <section class="apple-feature apple-feature--light">
        <div class="apple-feature__copy" data-parallax="text" data-parallax-speed="0.018" data-parallax-limit="16">
          <p class="eyebrow">Lifestyle-мерч</p>
          <h2>Для себя. Для подарка. Для спокойного ежедневного образа.</h2>
          <p>Без визуального шума и лишнего пафоса: одежда, которую можно носить каждый день, сохраняя официальный характер проекта.</p>
        </div>
        <img data-parallax="image" data-parallax-speed="0.052" data-parallax-limit="48" src="{assets}assets/generated/editorial/home-feature-style.png" alt="Модели в одежде и аксессуарах Универмага «Россия»">
      </section>
      <section class="apple-feature apple-feature--dark">
        <div class="apple-feature__copy" data-parallax="text" data-parallax-speed="0.018" data-parallax-limit="16">
          <p class="eyebrow">Одежда и аксессуары</p>
          <h2>Категории сразу ведут к выбору.</h2>
          <p>Худи, свитшоты, футболки, ветровки, куртки, кепки, шапки, шоперы, книги, значки и детские игры — в одном каталоге с понятными фильтрами.</p>
        </div>
        <img data-parallax="image" data-parallax-speed="0.052" data-parallax-limit="48" src="{assets}assets/generated/editorial/home-feature-family.png" alt="Верхняя одежда, сумки и аксессуары Универмага «Россия»">
      </section>
      {"".join(product_rails)}
      <section class="apple-category-band">
        <div class="wrap">
          <div class="apple-section-head">
            <h2>Выберите категорию.</h2>
            <a href="{root}catalog/">Весь каталог</a>
          </div>
          <div class="apple-category-row">{category_visual_tiles(prototype_depth)}</div>
        </div>
      </section>"""


def product_rail_html(title: str, url: str, link_label: str, products: list[dict], depth: int, root: str) -> str:
    cards = []
    for index, product in enumerate(products):
        extra_class = "product-card--model" if index == 0 and title == "Новинки" else ""
        cards.append(card(product, depth, editorial=True, extra_class=extra_class))
    return f"""
      <section class="apple-shop-preview">
        <div class="wrap">
          <div class="apple-section-head">
            <h2>{title}</h2>
            <a href="{url}">{link_label}</a>
          </div>
          <div class="apple-store-grid">{"".join(cards)}</div>
        </div>
      </section>"""


def unique_products(candidates: list[dict], limit: int, exclude_slug: str = "") -> list[dict]:
    selected = []
    seen = {exclude_slug}
    for product in candidates:
        if product["slug"] in seen:
            continue
        selected.append(product)
        seen.add(product["slug"])
        if len(selected) == limit:
            break
    return selected


def product_recommendation_rails(p: dict, depth: int, root: str) -> str:
    viewed_with = unique_products(
        [x for x in PRODUCTS if x["cat"] == p["cat"]]
        + [x for x in PRODUCTS if x["collection"] == p["collection"]]
        + PRODUCTS,
        8,
        p["slug"],
    )
    popular_items = unique_products(
        [x for x in PRODUCTS if x["tag"] in ("Хит", "Премиум", "Зима", "Подарок")] + PRODUCTS,
        8,
        p["slug"],
    )
    new_items = unique_products(
        [x for x in PRODUCTS if x["tag"] in ("Новинка", "−9%", "−10%", "−38%", "Набор")] + PRODUCTS,
        8,
        p["slug"],
    )
    return "".join(
        (
            product_rail_html("С этим смотрят", f"{root}catalog/{p['cat']}/", "В категорию", viewed_with, depth, root),
            product_rail_html("Популярное", f"{root}catalog/", "Весь каталог", popular_items, depth, root),
            product_rail_html("Новинки", f"{root}catalog/new/", "Смотреть все", new_items, depth, root),
        )
    )


def store_category_row(prototype_depth: int = 1) -> str:
    root = page_root(prototype_depth)
    icons = "".join(
        f"""<a class="store-category" href="{root}catalog/{slug}/">
          <img src="{project_image_path(next((p['img'] for p in PRODUCTS if p['cat'] == slug), ''), prototype_depth)}" alt="">
          <span>{label}</span>
        </a>"""
        for slug, label, _ in CATEGORIES
    )
    return f'<div class="store-category-row">{icons}</div>'


def category_visual_tiles(prototype_depth: int = 0) -> str:
    root = page_root(prototype_depth)
    parts = []
    for slug, label, _ in CATEGORIES:
        img = project_image_path(MODEL_CARD_IMAGES.get(slug, next((p["img"] for p in PRODUCTS if p["cat"] == slug), "")), prototype_depth)
        parts.append(
            f'<a class="category-visual" href="{root}catalog/{slug}/" style="background-image:url(\'{img}\')"><span class="category-visual__title">{label}</span></a>'
        )
    return "".join(parts)


def subcategory_chips(active: str | None = None) -> str:
    options = [
        ("", "Все свитшоты"),
        ("С флисом", "С флисом"),
        ("Без флиса", "Без флиса"),
    ]
    links = "".join(
        f'<button type="button" class="{"is-active" if active == value else ""}" data-filter-subcategory="{value}">{label}</button>'
        for value, label in options
    )
    return f"""
            <fieldset>
              <legend>Тип свитшота</legend>
              <div class="filter-pills filter-pills--buttons">{links}</div>
            </fieldset>"""


def write(rel: str, content: str) -> None:
    path = ROOT / PROTOTYPE_DIR / rel
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


def catalog_filter_panel(depth: int, *, active: str | None = None, color: str | None = None, size: str | None = None) -> str:
    root = "../" * depth
    active_label = "Все товары"
    if active:
        active_label = next((label for slug, label, _ in CATEGORIES if slug == active), active_label)
    color_options = "".join(
        f'<button type="button" class="{"is-active" if color == slug else ""}" data-filter-color="{slug}" style="--swatch:{swatch}" aria-label="{label}"></button>'
        for slug, label, _label_plural, swatch in [
            ("belye", "Белый", "белые", "#fff"),
            ("sinie", "Синий", "синие", "#12345a"),
            ("chernye", "Чёрный", "чёрные", "#111"),
            ("krasnye", "Красный", "красные", "#9b1c31"),
            ("rozovye", "Розовый", "розовые", "#e8b7c7"),
        ]
    )
    size_options = "".join(
        f'<label class="{"is-active" if size == item.lower() else ""}"><input type="checkbox" data-filter-size="{item.lower()}" {"checked" if size == item.lower() else ""}> {item}</label>'
        for item in FILTER_SIZES
    )
    return f"""
        <aside class="store-filter-panel" aria-label="Фильтры каталога">
          <div class="store-filter-panel__head">
            <span>Фильтры</span>
            <a href="{root}catalog/" data-filter-reset>Сбросить</a>
          </div>
          <fieldset>
            <legend>Категория</legend>
            <div class="filter-pills">
              <a class="{"is-active" if active is None else ""}" href="{root}catalog/" data-filter-category="all">Все</a>
              {''.join(f'<a class="{"is-active" if active == slug else ""}" href="{root}catalog/{slug}/" data-filter-category="{slug}">{label}</a>' for slug, label, _ in CATEGORIES)}
            </div>
          </fieldset>
          {subcategory_chips() if active == "svitshoty" else ""}
          <fieldset>
            <legend>Размер</legend>
            <div class="filter-options">{size_options}</div>
          </fieldset>
          <fieldset>
            <legend>Цвет</legend>
            <div class="color-options">{color_options}</div>
          </fieldset>
          <fieldset>
            <legend>Цена</legend>
            <div class="filter-options"><label><input type="checkbox" data-filter-price="0-5000"> до 5 000 ₽</label><label><input type="checkbox" data-filter-price="5000-10000"> 5 000–10 000 ₽</label><label><input type="checkbox" data-filter-price="10000-999999"> от 10 000 ₽</label></div>
          </fieldset>
          <fieldset>
            <legend>Наличие</legend>
            <div class="filter-options"><label class="is-active"><input type="checkbox" checked data-filter-stock> В наличии</label><label><input type="checkbox" data-filter-gift> Подарочные сертификаты</label></div>
          </fieldset>
          <p class="filter-demo-note">Комбинации цвет + размер меняют выдачу через AJAX без смены URL. В индекс попадают только одиночные ЧПУ-фильтры из SEO-белого списка.</p>
        </aside>"""


def store_collection_cards(prototype_depth: int = 1) -> str:
    root = page_root(prototype_depth)
    picks = [
        ("Одежда на каждый день", "Футболки, лонгсливы, худи и костюмы с нейтральной посадкой.", "futbolka-oranzhevaya", "catalog/futbolki/"),
        ("Аксессуары и поездки", "Кепки, шапки, шоперы, значки, книги и детские игры в одной ветке.", "sumka-shopper", "catalog/aksessuary/"),
        ("Подарочные сценарии", "Электронные сертификаты и наборы, когда размер лучше выбрать позже.", "podarochnyj-nabor", "catalog/aksessuary/"),
    ]
    return "".join(
        f"""<a class="store-promo-card" href="{root}{href}">
          <img src="{project_image_path(product_by_slug(slug)['img'], prototype_depth)}" alt="">
          <span>{title}</span>
          <p>{text}</p>
        </a>"""
        for title, text, slug, href in picks
    )


# (category_slug, url_slug, title_keyword, optional color_slug for product filter)
SEO_FILTER_PAGES: list[tuple[str, str, str, str | None]] = [
    ("futbolki", "belye", "купить белую футболку", "belye"),
    ("futbolki", "chernye", "купить черную футболку", "chernye"),
    ("futbolki", "krasnye", "купить красную футболку", "krasnye"),
    ("futbolki", "razmery", "купить футболку размер", None),
    ("futbolki", "bolshie-razmery", "купить футболку большого размера", None),
    ("futbolki", "s-printom", "купить футболку с принтом", None),
    ("hudi", "chernye", "купить черный худи", "chernye"),
    ("hudi", "belye", "купить белое худи", "belye"),
    ("hudi", "s-kapyushonom", "купить худи с капюшоном", None),
    ("hudi", "na-molnii", "худи на молнии купить", None),
    ("svitshoty", "chernye", "свитшоты черные купить", "chernye"),
    ("kurtki", "razmery", "купить куртку размера", None),
    ("kurtki", "demisezonnye", "купить демисезонную куртку", None),
    ("kurtki", "s-kapyushonom", "купить куртку с капюшоном", None),
    ("vetrovki", "s-kapyushonom", "ветровка с капюшоном купить", None),
]


def seo_filter_heading(category_slug: str, keyword: str) -> str:
    plural = CATEGORY_SEO_NOUNS.get(category_slug, ("товар", "товары"))[1]
    return f"{keyword.capitalize()} — {plural} Универмага «Россия»"


def products_for_collection(slug: str) -> list:
    if slug == "russia-capsule":
        return [p for p in PRODUCTS if p["collection"] == "Russia Capsule"]
    if slug == "mystery-box":
        return [p for p in PRODUCTS if p["collection"] == "Mystery Box" or p["slug"] in ("podarochnyj-nabor", "sumka-shopper")]
    if slug == "zimnyaya-liniya":
        return [p for p in PRODUCTS if p["collection"] == "Зимняя линейка 2026"]
    return []


def product_body(p: dict) -> str:
    root = "../../"
    primary_image = model_card_image(p, 2)
    gallery_images = [primary_image] + [project_image_path(p["img"], 2) for _ in range(3)]
    thumbs = "".join(
        f'<button type="button" class="{"is-active" if i == 0 else ""}"><img src="{src}" alt=""></button>'
        for i, src in enumerate(gallery_images)
    )
    recommendation_rails = product_recommendation_rails(p, 2, root)
    return f"""
      <div class="wrap">
        <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../../catalog/">Каталог</a> / <a href="../../catalog/{p['cat']}/">{p['cat_label']}</a> / <span>{p['title']}</span></nav>
        <div class="product-page">
          <div class="product-gallery">
            <div class="gallery-main"><img src="{primary_image}" alt="{p['title']} на модели — {BRAND['name']}"></div>
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
                "image": "{primary_image}",
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
      </div>
      {recommendation_rails}""".replace("<div class=", "<div class=").replace("<div class=", "<div class=").replace("</div>", "</div>")



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
            home_apple_html(0),
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
      <section class="store-hero">
        <div class="wrap">
          <nav class="breadcrumbs"><a href="../">Главная</a> / <span>Каталог</span></nav>
          <h1>Магазин. <span>Выберите вещь для себя или в подарок.</span></h1>
          <p>Один каталог с фильтрами: размер S–3XL, цвет, цена и наличие. СДЭК или Яндекс, оплата сразу или при получении.</p>
        </div>
      </section>
      <section class="store-categories">
        <div class="wrap">{store_category_row(1)}</div>
      </section>
      <section class="store-products" id="odezhda">
        <div class="wrap">
          <div class="apple-section-head"><h2>Все товары.</h2><a href="../delivery/">Доставка и оплата</a></div>
          <div class="store-layout">
            {catalog_filter_panel(1)}
            <div>
              <div class="store-sortbar">
                <span><b data-filter-count>{len(PRODUCTS)}</b> товаров · размер S–3XL · цвета из брифа</span>
                <select aria-label="Сортировка"><option>Рекомендованные</option><option>Сначала новые</option><option>По возрастанию цены</option></select>
              </div>
              <div class="apple-store-grid apple-store-grid--catalog">{"".join(card(p, 1, editorial=True) for p in PRODUCTS)}</div>
              <div class="filter-empty" data-filter-empty>По выбранным фильтрам товаров не найдено. Сбросьте фильтр или выберите соседний размер.</div>
            </div>
          </div>
        </div>
      </section>""",
            "Каталог официальной одежды и мерча Национального центра «Россия»: категории, фильтры, подарки, СДЭК, Яндекс и оплата при получении.",
        ),
    )

    search_results = "".join(card(p, 1) for p in PRODUCTS[:4])
    favorite_items = "".join(card(p, 1) for p in (PRODUCTS[0], PRODUCTS[4], PRODUCTS[10]))
    cart_rows = "".join(
        f"""
        <li class="cart-item">
          <img src="{project_image_path(p['img'], 1)}" alt="{p['title']} — {BRAND['name']}">
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
        <article class="store-card"><strong>Онлайн-заказ по России</strong><span>Доставка СДЭК или Яндекс. Стоимость доставки клиент оплачивает отдельно.</span><small>Оплата сразу или при получении</small></article>"""
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
                "Контакты, СДЭК или Яндекс, оплата сразу или при получении и подтверждение заказа в одном спокойном сценарии.",
                f"""
        <div class="checkout-layout">
          <form class="content-block demo-form" onsubmit="return false;">
            <label>Имя <input type="text" value="Сергей"></label>
            <label>Телефон <input type="tel" value="+7"></label>
            <label>Город <input type="text" value="Москва"></label>
            <label>Способ доставки <select><option>СДЭК</option><option>Яндекс</option><option>Самовывоз из магазина</option></select></label>
            <label>Оплата <select><option>Сразу на сайте</option><option>При получении</option></select></label>
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
      <section class="store-hero store-hero--category">
        <div class="wrap">
          <nav class="breadcrumbs"><a href="../../">Главная</a> / <a href="../">Каталог</a> / <span>{label}</span></nav>
          <h1>{label}. <span>Выберите вещь без лишнего шума.</span></h1>
          <p>{seo}</p>
        </div>
      </section>
      <section class="store-categories">
        <div class="wrap">{store_category_row(2)}</div>
      </section>
      <section class="store-products">
        <div class="wrap">
          <div class="apple-section-head"><h2>{label}.</h2><a href="../../catalog/">Весь каталог</a></div>
          <div class="store-layout">
            {catalog_filter_panel(2, active=slug)}
            <div>
              <div class="store-sortbar">
                <span><b data-filter-count>{len(items)}</b> товаров · СДЭК или Яндекс · оплата сразу или при получении</span>
                <select aria-label="Сортировка"><option>Рекомендованные</option><option>Сначала новые</option><option>По возрастанию цены</option></select>
              </div>
              <div class="apple-store-grid apple-store-grid--catalog">{"".join(card(p, 2, editorial=True) for p in items)}</div>
              <div class="filter-empty" data-filter-empty>По выбранным фильтрам товаров не найдено. Сбросьте фильтр или выберите соседний размер.</div>
            </div>
          </div>
          <div class="faq category-faq store-faq">
            <h2>Вопросы о категории</h2>
            <details open><summary>Как подобрать размер?</summary><p>Используйте фильтр S–3XL и таблицу размеров в карточке товара.</p></details>
            <details><summary>Как доставляют заказ?</summary><p>Доступны СДЭК или Яндекс. Стоимость доставки оплачивается отдельно.</p></details>
          </div>
        </div>
      </section>""",
                seo,
            ),
        )

        for cat_slug, url_slug, keyword, color_slug in SEO_FILTER_PAGES:
            if cat_slug != slug:
                continue
            if color_slug:
                filter_products = [
                    p
                    for p in items
                    if color_slug in {normalize_color(c) for c in p["colors"]}
                ] or items[: min(4, len(items))]
            else:
                filter_products = items[: min(8, len(items))] or items
            heading = seo_filter_heading(slug, keyword)
            color_plural = next(
                (plural for s, _b, plural in FILTER_COLORS if s == color_slug),
                "все цвета",
            )
            write(
                f"catalog/{slug}/{url_slug}/index.html",
                shell(
                    3,
                    heading,
                    f"""
      <section class="store-hero store-hero--category">
        <div class="wrap">
          <nav class="breadcrumbs"><a href="../../../">Главная</a> / <a href="../../">Каталог</a> / <a href="../">{label}</a> / <span>{keyword}</span></nav>
          <h1>{heading}</h1>
          <p>{keyword}: статичная SEO-страница с ЧПУ-адресом <code>/catalog/{slug}/{url_slug}/</code>. Отдельные title, description, h1 и alt у товарных фото.</p>
        </div>
      </section>
      <section class="store-products store-products--seo-filter">
        <div class="wrap">
          <div class="store-layout">
            {catalog_filter_panel(3, active=slug, color=color_slug)}
            <div>
              <div class="store-sortbar">
                <span><b data-filter-count>{len(filter_products)}</b> товаров · одиночный SEO-фильтр{f" · {color_plural}" if color_slug else ""}</span>
                <select aria-label="Сортировка"><option>Рекомендованные</option><option>Сначала новые</option><option>По возрастанию цены</option></select>
              </div>
              <div class="apple-store-grid apple-store-grid--catalog">{"".join(card(p, 3, editorial=True, seo_keyword=f"{keyword} — {p['title']} в Универмаге «Россия»") for p in filter_products)}</div>
              <div class="filter-empty" data-filter-empty>По выбранным фильтрам товаров не найдено. Сбросьте фильтр или выберите соседний размер.</div>
            </div>
          </div>
          <section class="content-block prose seo-filter-copy">
            <h2>{keyword}: посадочная под поисковый спрос</h2>
            <p>Одиночное свойство в URL индексируется отдельно. Комбинации «цвет + размер» в боковой панели работают через AJAX и не создают новых адресов — как в ТЗ для CMS.</p>
          </section>
        </div>
      </section>""",
                    f"{keyword} в официальном магазине Национального центра «Россия». Доставка СДЭК или Яндекс, оплата сразу или при получении.",
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
          <div class="visual" style="background-image:url('{project_image_path(c['img'], 1)}')"></div>
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
        f'<article class="blog-card"><a href="{post["slug"]}/"><div class="thumb" style="background-image:url(\'{project_image_path(post["img"], 1)}\')"></div><div class="body"><h3>{post["title"]}</h3><p>{post["excerpt"]}</p></div></a></article>'
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
