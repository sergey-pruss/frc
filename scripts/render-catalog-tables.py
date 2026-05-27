#!/usr/bin/env python3
"""Inject catalog Wordstat tables into seo/index.html from JSON exports."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEO = ROOT / "seo" / "index.html"
FULL = ROOT / "data" / "catalog-wordstat-full.json"
TOP = ROOT / "data" / "catalog-keywords-top10.json"

# Landing URL map for «Ключевые запросы 100+»
LANDING = {
    "Футболки": "/catalog/futbolki/",
    "Куртки": "/catalog/kurtki/",
    "Кепки": "/catalog/aksessuary/kepki/",
    "Ветровки": "/catalog/vetrovki/",
    "Худи": "/catalog/hudi/",
    "Свитшоты": "/catalog/svitshoty/",
    "Шапки": "/catalog/aksessuary/shapki/",
    "Значки": "/catalog/aksessuary/znachki/",
    "Шоперы": "/catalog/aksessuary/shopery/",
    "Детские игры": "/catalog/aksessuary/detskie-igry/",
    "Книги": "/catalog/aksessuary/knigi/",
    "Сертификаты": "/gift-cards/",
}

PRIORITY = {
    "Футболки": "Высокий",
    "Куртки": "Высокий",
    "Худи": "Высокий",
    "Свитшоты": "Средний",
    "Ветровки": "Средний",
    "Кепки": "Средний",
    "Шапки": "Средний",
    "Шоперы": "Средний",
    "Книги": "Низкий",
    "Детские игры": "Низкий",
    "Значки": "Низкий",
    "Сертификаты": "Средний",
}

USAGE = {
    "Футболки": "Основной запрос категории: title, H1, intro.",
    "Куртки": "Основной запрос категории.",
    "Кепки": "Основной запрос категории.",
    "Ветровки": "Основной запрос категории.",
    "Худи": "Отдельная посадочная; не смешивать со свитшотами.",
    "Свитшоты": "Основной запрос категории.",
    "Шапки": "Основной запрос категории.",
    "Значки": "Категория; нужна чистка сувенирного хвоста.",
    "Шоперы": "Основной запрос категории.",
    "Детские игры": "Открывать при реальном ассортименте игр.",
    "Книги": "Открывать после подтверждения ассортимента.",
    "Сертификаты": "Отдельная коммерческая страница сертификата.",
}

FILTER_WHITELIST = [
    ("Футболки", "купить белую футболку", "/catalog/futbolki/belye/"),
    ("Футболки", "купить черную футболку", "/catalog/futbolki/chernye/"),
    ("Футболки", "купить красную футболку", "/catalog/futbolki/krasnye/"),
    ("Футболки", "купить футболку размер", "/catalog/futbolki/razmery/"),
    ("Футболки", "купить футболку большого размера", "/catalog/futbolki/bolshie-razmery/"),
    ("Футболки", "купить футболку с принтом", "/catalog/futbolki/s-printom/"),
    ("Худи", "купить черный худи", "/catalog/hudi/chernye/"),
    ("Худи", "купить белое худи", "/catalog/hudi/belye/"),
    ("Худи", "купить худи с капюшоном", "/catalog/hudi/s-kapyushonom/"),
    ("Худи", "худи на молнии купить", "/catalog/hudi/na-molnii/"),
    ("Куртки", "купить куртку размера", "/catalog/kurtki/razmery/"),
    ("Куртки", "купить демисезонную куртку", "/catalog/kurtki/demisezonnye/"),
    ("Куртки", "купить куртку с капюшоном", "/catalog/kurtki/s-kapyushonom/"),
    ("Ветровки", "ветровка с капюшоном купить", "/catalog/vetrovki/s-kapyushonom/"),
    ("Свитшоты", "свитшоты черные купить", "/catalog/svitshoty/chernye/"),
]

RECOMMENDED_FILTERS = [
    ("Футболки", "цвет, размер, принт, большие размеры", "/catalog/futbolki/belye/, /catalog/futbolki/razmery/, /catalog/futbolki/s-printom/", "MVP"),
    ("Худи", "цвет, капюшон, молния", "/catalog/hudi/chernye/, /catalog/hudi/s-kapyushonom/", "MVP"),
    ("Свитшоты", "цвет; флис — подкатегории", "/catalog/svitshoty/chernye/, /catalog/svitshoty/s-flisom/", "MVP"),
    ("Куртки", "демисезон, капюшон, размер", "/catalog/kurtki/demisezonnye/, /catalog/kurtki/s-kapyushonom/", "При SKU"),
    ("Ветровки", "капюшон", "/catalog/vetrovki/s-kapyushonom/", "При SKU"),
    ("Кепки", "цвет — точечно", "—", "При матрице"),
    ("Шапки", "сезон — после SKU", "—", "При матрице"),
    ("Значки", "без SEO-фильтров на старте", "—", "Категория"),
    ("Шоперы", "без SEO-фильтров на старте", "—", "Категория"),
    ("Книги", "без SEO-фильтров на старте", "—", "После ассортимента"),
    ("Детские игры", "без SEO-фильтров на старте", "—", "После ассортимента"),
]


def tr(cells: list[str]) -> str:
    return "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>\n"


def replace_table(html: str, title: str, new_tbody: str) -> str:
    pattern = (
        rf'(<h3 class="subsection-title">{re.escape(title)}</h3>[\s\S]*?<tbody>\n)'
        r"[\s\S]*?"
        r"(\n\s*</tbody>)"
    )
    return re.sub(pattern, rf"\1{new_tbody}\2", html, count=1)


def main() -> None:
    full = json.loads(FULL.read_text(encoding="utf-8"))
    top = json.loads(TOP.read_text(encoding="utf-8"))
    html = SEO.read_text(encoding="utf-8")

    # Ключевые запросы 100+ — top anchor per cluster (first 2 from top file)
    rows = []
    for cluster, items in top["clusters"].items():
        for item in items[:2]:
            rows.append(
                tr(
                    [
                        cluster,
                        item["phrase"],
                        str(item["shows"]),
                        LANDING.get(cluster, "/catalog/"),
                        USAGE.get(cluster, "Категория."),
                        PRIORITY.get(cluster, "Средний"),
                    ]
                )
            )
    keywords_body = "".join(rows)
    html = replace_table(html, "Ключевые запросы 100+ для структуры", keywords_body)

    # Сводка по кластерам
    summary_rows = []
    for cluster, count in sorted(full["cluster_counts"].items(), key=lambda x: -x[1]):
        directions = ", ".join(x["phrase"] for x in top["clusters"].get(cluster, [])[:3])
        decision = {
            "Футболки": "Категория + цветовые и размерные SEO-фильтры.",
            "Куртки": "Категория + фильтры под подтверждённые свойства.",
            "Кепки": "Категория + точечные цветовые фильтры.",
            "Ветровки": "Категория + фильтры по конструкции.",
            "Худи": "Отдельная посадочная + точечные фильтры.",
            "Свитшоты": "Категория + точечные фильтры.",
            "Шапки": "Категория; фильтры после SKU.",
            "Значки": "Категория; фильтры не приоритетны.",
            "Шоперы": "Категория без SEO-фильтров на старте.",
            "Книги": "Категория после подтверждения ассортимента.",
            "Детские игры": "Категория после уточнения типов игр.",
            "Сертификаты": "Отдельная страница сертификата.",
        }.get(cluster, "Категория.")
        summary_rows.append(tr([cluster, str(count), directions, decision]))
    html = replace_table(html, "Сводка по кластерам и решениям", "".join(summary_rows))

    # Recommended filters by category (new block - insert if missing)
    if 'id="recommended-filters-by-category"' not in html:
        block = """
      <section class="section" id="recommended-filters-by-category">
        <div class="wrap">
          <h2>Рекомендуемые фильтры по категориям</h2>
          <p>
            Сводная таблица для согласования: какие одиночные ЧПУ-фильтры открывать в индекс, а какие
            комбинации оставить только в AJAX. Источники: кластеризация, поле сбора семантики и белый
            список из раздела «Статичные SEO-фильтры».
          </p>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Категория</th>
                  <th>Направления спроса</th>
                  <th>Примеры статичных URL</th>
                  <th>Статус</th>
                </tr>
              </thead>
              <tbody>
                TBODY_PLACEHOLDER
              </tbody>
            </table>
          </div>
        </div>
      </section>
"""
        rf_rows = "".join(tr(list(r)) for r in RECOMMENDED_FILTERS)
        block = block.replace("TBODY_PLACEHOLDER", rf_rows.strip())
        html = html.replace(
            '<section class="section" id="recommended-structure-tree">',
            block + '\n      <section class="section" id="recommended-structure-tree">',
        )
        # TOC link
        html = html.replace(
            '<a class="toc-item" href="#recommended-structure"><span class="toc-num">2</span>',
            '<a class="toc-item" href="#recommended-filters-by-category"><span class="toc-num">2a</span> Рекомендуемые фильтры</a>\n            '
            '<a class="toc-item" href="#recommended-structure"><span class="toc-num">2</span>',
        )

    SEO.write_text(html, encoding="utf-8")
    print(f"Updated {SEO}")


if __name__ == "__main__":
    main()
