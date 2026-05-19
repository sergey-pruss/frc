#!/usr/bin/env python3
"""Render Wordstat VH/SCH HTML block from competitor-wordstat.json."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "competitor-wordstat.json"
OUT = ROOT / "data" / "competitor-wordstat-block.html"


def fmt_shows(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f")


def recommend(phrase: str, site: str) -> str:
    low = phrase.lower()
    if low in ("putin team", "putin team russia") or (
        site == "gloryseason.ru" and low in ("россия сезон славы", "сезон славы бренд")
    ):
        return (
            "Брендовый ВЧ/СЧ: главная, «О проекте», единый title/H1 с официальным магазином."
        )
    if any(x in low for x in ("официальн", "сайт", "интернет магазин")):
        return (
            "Закрепить: Универмаг «Россия», официальный магазин, "
            "Национальный центр «Россия» — title, H1, Organization schema."
        )
    if any(x in low for x in ("купить", "магазин")):
        return "В категориях: «купить» + «доставка по России» в title и H1."
    if any(x in low for x in ("худи", "футбол", "куртк", "костюм", "толстовк", "кепк", "кожан", "кофт")):
        return "Посадочная категории: уникальный H1, intro 300–600 знаков, FAQ."
    if any(x in low for x in ("отзыв", "владелец", "чей бренд", "перевод", "инн")):
        return "Инфо/FAQ; не смешивать с товарными посадочными."
    if any(x in low for x in ("подар", "сертификат", "mystery", "capsule", "мерч", "сумка")):
        return "Отдельная посадочная: коллекции, подарки, аксессуары."
    if site == "gloryseason.ru" and "россия" in low and "сезон слав" in low:
        return "Усилить коллекции Russia / мерч Национального центра «Россия»."
    return "Мониторить в Вебмастере; в контент — только при наличии товара."


def site_table(items: list[dict], site: str, title: str) -> str:
    rows = [i for i in items if i["type"] in ("ВЧ", "СЧ")]
    body = "\n".join(
        "                <tr>\n"
        f"                  <td>{html.escape(i['phrase'])}</td>\n"
        f"                  <td>{fmt_shows(i['shows'])}</td>\n"
        f"                  <td><strong>{i['type']}</strong></td>\n"
        f"                  <td>{html.escape(recommend(i['phrase'], site))}</td>\n"
        "                </tr>"
        for i in rows
    )
    return f"""          <h4 class="subsection-title">{html.escape(title)}</h4>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Запрос</th>
                  <th>Показов/мес</th>
                  <th>ВЧ/СЧ</th>
                  <th>Рекомендация для Универмага «Россия»</th>
                </tr>
              </thead>
              <tbody>
{body}
              </tbody>
            </table>
          </motion>
""".replace("</motion>", "</div>")


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    notes_li = "\n".join(f"            <li>{html.escape(n)}</li>" for n in payload.get("notes", []))
    block = f"""          <h3 class="subsection-title">Основная семантика конкурентов: ВЧ и СЧ (Wordstat)</h3>
          <p>
            Данные из <strong>Яндекс Wordstat</strong> ({html.escape(payload['region'])}), вкладка
            «Популярные» (запросы со словами), выгрузка от {payload['generated_at']}.
            {html.escape(payload['thresholds']['legend'])}. В таблицах — коммерчески релевантные
            запросы; сериалы, музыка и «перевод» в ВЧ/СЧ для мерча не учитываются.
          </p>
          <ul class="checklist">
{notes_li}
          </ul>
{site_table(payload['putin_team'], 'putin-team.ru', 'putin-team.ru — запросы с частотностью')}
{site_table(payload['gloryseason'], 'gloryseason.ru', 'gloryseason.ru — запросы с частотностью')}
          <h3 class="subsection-title">Сводка по реальным ВЧ/СЧ конкурентов</h3>
          <ul class="checklist">
            <li><strong>putin-team.ru:</strong> ВЧ — «putin team» (3\u202f383), «putin team russia» (1\u202f479); ключевой СЧ — «putin team одежда» (981), кластеры «официальный сайт», «магазин».</li>
            <li><strong>gloryseason.ru:</strong> «сезон славы» без «одежда» — не коммерческий ВЧ; опора — «сезон славы одежда» (514), «россия сезон славы» (982), «куртка сезон славы» (345), «сезон славы худи» (294).</li>
            <li><strong>Russia Capsule / Mystery Box</strong> в Wordstat &lt;100 показов — SEO через структуру и контент, не как отдельные ВЧ.</li>
            <li><strong>Для нас:</strong> те же типы кластеров — бренд+официальный магазин (ВЧ), категория+купить (СЧ), коллекции и подарки (СЧ).</li>
          </ul>
"""
    OUT.write_text(block, encoding="utf-8")
    print(f"Wrote {OUT} ({len(block)} chars)")


if __name__ == "__main__":
    main()
