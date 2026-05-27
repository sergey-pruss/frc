#!/usr/bin/env python3
"""Sync content strategy from Google Doc + spreadsheet into content-strategy/index.html."""

from __future__ import annotations

import csv
import html
import io
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_HTML = ROOT / "content-strategy" / "index.html"

DOC_ID = "1y5bkO5V0WYV8AOQpQM0EFSmpYwuqD5gp55fvV3DR8ZI"
SHEET_ID = "1PW_IG5uHiqvd-oRo2r7ZjQkvNJuvXgsfecF-EST7-UY"
SHEET_GID = "0"

DOC_URL = f"https://docs.google.com/document/d/{DOC_ID}/export?format=txt"
SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"
)
DOC_EDIT_URL = f"https://docs.google.com/document/d/{DOC_ID}/edit"
SHEET_EDIT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={SHEET_GID}"

SECTION_TITLES = [
    "Задача",
    "Общий вывод по конкурентам",
    "Шапка сайта",
    "Главная страница",
    "Tone of voice",
    "Подача патриотической темы",
    "Каталог и коллекции",
    "Карточки товаров",
    "Блог и статьи",
    "Основные аудитории проекта",
    "Основные выводы и рекомендации",
]

MATRIX_INSERT_AFTER = "Общий вывод по конкурентам"

ASSET_VERSION = "20260527b"

MATRIX_COLUMNS = (
    ("found", "Что обнаружено"),
    ("examples", "Примеры / формулировки"),
    ("conclusion", "Контентный вывод"),
    ("take", "Что взять для ФРК"),
    ("avoid", "Что не брать / риск"),
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "frc-content-sync/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").strip()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9а-яё]+", "-", value.lower()).strip("-")


def split_doc_sections(text: str) -> list[tuple[str, str]]:
    body_start = text.find("Задача\n")
    if body_start == -1:
        body_start = text.find("Задача\r")
    body = text[body_start:].strip() if body_start >= 0 else text

    positions: list[tuple[int, str]] = []
    for title in SECTION_TITLES:
        match = re.search(rf"(?:^|\n){re.escape(title)}\n", body)
        if match:
            positions.append((match.start() + (1 if body[match.start()] == "\n" else 0), title))
    positions.sort(key=lambda item: item[0])

    sections: list[tuple[str, str]] = []
    for index, (start, title) in enumerate(positions):
        chunk_start = start + len(title) + 1
        chunk_end = positions[index + 1][0] if index + 1 < len(positions) else len(body)
        chunk = body[chunk_start:chunk_end].strip()
        sections.append((title, chunk))
    return sections


def paragraphs_to_html(text: str) -> str:
    parts = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not parts:
        parts = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(f"<p>{html.escape(part)}</p>" for part in parts)


def recommendations_to_checklist(text: str) -> str:
    lead, _, rest = text.partition(". ")
    sentences = []
    if lead.strip():
        sentences.append(lead.strip().rstrip("."))
    if rest.strip():
        sentences.extend(
            s.strip().rstrip(".")
            for s in re.split(r"(?<=\.)\s+(?=[А-ЯA-Z«])", rest)
            if s.strip()
        )
    if len(sentences) < 4:
        return paragraphs_to_html(text)
    items = "\n".join(f"            <li>{html.escape(s)}.</li>" for s in sentences)
    return f"""          <ul class="checklist">
{items}
          </ul>"""


def audiences_to_cards(text: str) -> str:
    chunks = re.split(
        r"\s+(?=(?:Первое|Второе|Третье)(?:\s+ядро)?\s*[—–-]\s*)",
        text.strip(),
    )
    if len(chunks) < 3:
        return paragraphs_to_html(text)

    intro = chunks[0].strip()
    intro_html = f"<p>{html.escape(intro)}</p>" if intro else ""
    cards: list[str] = []
    for chunk in chunks[1:]:
        chunk = chunk.strip()
        if not chunk:
            continue
        title_match = re.match(
            r"^((?:Первое|Второе|Третье)(?:\s+ядро)?\s*[—–-]\s*[^.]+)",
            chunk,
        )
        if title_match:
            title = title_match.group(1).strip()
            body = chunk[len(title_match.group(0)) :].strip().lstrip(". ")
        else:
            title, _, body = chunk.partition(".")
            title, body = title.strip(), body.strip()
        cards.append(
            f"""            <article class="card">
              <h3>{html.escape(title)}</h3>
              <p>{html.escape(body)}</p>
            </article>"""
        )
    return f"""{intro_html}
          <div class="cards cs-audience-cards">
{chr(10).join(cards)}
          </div>"""


def render_body_html(title: str, body: str) -> str:
    if title == "Основные выводы и рекомендации":
        return recommendations_to_checklist(body)
    if title == "Основные аудитории проекта":
        return audiences_to_cards(body)
    return paragraphs_to_html(body)


def load_competitor_rows(csv_text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(csv_text))
    rows: list[dict[str, str]] = []
    current = ""
    for raw in reader:
        if raw.get("Конкурент", "").strip():
            current = raw["Конкурент"].strip()
        rows.append(
            {
                "competitor": current,
                "block": raw.get("Блок анализа", "").strip(),
                "found": raw.get("Что обнаружено", "").strip(),
                "examples": raw.get("Конкретные примеры / формулировки", "").strip(),
                "conclusion": raw.get("Контентный вывод", "").strip(),
                "take": raw.get("Что можно взять для ФРК", "").strip(),
                "avoid": raw.get("Что не брать / риск", "").strip(),
            }
        )
    return rows


def group_competitors(rows: list[dict[str, str]]) -> list[tuple[str, list[dict[str, str]]]]:
    order: list[str] = []
    buckets: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        name = row["competitor"]
        if name not in buckets:
            order.append(name)
            buckets[name] = []
        buckets[name].append(row)
    return [(name, buckets[name]) for name in order]


def render_matrix_row(item: dict[str, str]) -> str:
    cells = "\n".join(
        f"                  <td>{html.escape(item[key])}</td>" for key, _ in MATRIX_COLUMNS
    )
    return f"""                <tr>
                  <th scope="row">{html.escape(item['block'])}</th>
{cells}
                </tr>"""


def render_competitor_table(competitor: str, items: list[dict[str, str]]) -> str:
    head = "\n".join(f"                  <th>{html.escape(label)}</th>" for _, label in MATRIX_COLUMNS)
    rows = "\n".join(render_matrix_row(item) for item in items)
    anchor = slugify(competitor)
    return f"""          <div class="cs-competitor" id="matrix-{anchor}">
            <h3 class="subsection-title">{html.escape(competitor)}</h3>
            <div class="table-wrap">
              <table class="cs-matrix-table">
                <thead>
                  <tr>
                    <th scope="col">Блок анализа</th>
{head}
                  </tr>
                </thead>
                <tbody>
{rows}
                </tbody>
              </table>
            </div>
          </div>"""


def render_competitor_matrix(rows: list[dict[str, str]]) -> str:
    blocks = [render_competitor_table(name, items) for name, items in group_competitors(rows)]
    return "\n".join(blocks)


def render_matrix_section(matrix_html: str) -> str:
    return f"""      <section class="section highlight" id="matrix">
        <div class="wrap">
          <span class="section-label">Таблица</span>
          <h2>Сравнительный анализ конкурентов</h2>
          <p class="section-intro">
            Детальная таблица по Putin Team, GLORY SEASON, Bosco, Третьяковской галереи и Зениту.
            Широкие колонки прокручиваются горизонтально — как в разделе «Анализ конкурентов».
          </p>
{matrix_html}
        </div>
      </section>"""


def render_doc_section(
    title: str,
    body: str,
    *,
    section_index: int,
    muted: bool,
) -> str:
    anchor = slugify(title)
    tone = " muted" if muted else ""
    return f"""      <section class="section{tone}" id="{html.escape(anchor)}">
        <div class="wrap">
          <span class="section-label">Раздел {section_index}</span>
          <h2>{html.escape(title)}</h2>
          <div class="prose">
{render_body_html(title, body)}
          </div>
        </div>
      </section>"""


def render_sections_flow(
    sections: list[tuple[str, str]],
    matrix_html: str,
) -> str:
    parts: list[str] = []
    section_index = 0
    matrix_block = render_matrix_section(matrix_html)
    matrix_inserted = False

    for title, body in sections:
        section_index += 1
        parts.append(
            render_doc_section(
                title,
                body,
                section_index=section_index,
                muted=section_index % 2 == 0,
            )
        )
        if title == MATRIX_INSERT_AFTER and not matrix_inserted:
            parts.append(matrix_block)
            matrix_inserted = True

    if not matrix_inserted:
        parts.append(matrix_block)
    return "\n".join(parts)


def topbar(active: str) -> str:
    tabs = [
        ("seo", "SEO-стратегия", "../seo/"),
        ("analysis", "Анализ конкурентов", "../analysis/"),
        ("content", "Контент-стратегия", None),
    ]
    items = []
    for key, label, href in tabs:
        if key == active:
            items.append(f'        <a class="site-topbar__tab is-active">{label}</a>')
        else:
            items.append(f'        <a class="site-topbar__tab" href="{href}">{label}</a>')
    return f"""    <div class="site-topbar" id="projectTopbar">
      <div class="site-topbar__tabs">
{chr(10).join(items)}
      </div>
    </div>"""


def build_toc(sections: list[tuple[str, str]], competitors: list[str]) -> list[str]:
    items: list[str] = []
    for index, (title, _) in enumerate(sections, start=1):
        anchor = slugify(title)
        short = title if len(title) <= 42 else title[:39] + "…"
        items.append(
            f'<a class="toc-item" href="#{html.escape(anchor)}">'
            f'<span class="toc-num">{index}</span> {html.escape(short)}</a>'
        )

    matrix_index = next(
        (i for i, (title, _) in enumerate(sections, start=1) if title == MATRIX_INSERT_AFTER),
        len(sections),
    )
    for offset, name in enumerate(competitors, start=1):
        anchor = f"matrix-{slugify(name)}"
        short = name if len(name) <= 36 else name[:33] + "…"
        items.append(
            f'<a class="toc-item toc-item--compact" href="#{html.escape(anchor)}">'
            f'<span class="toc-num">{matrix_index}.{offset}</span> {html.escape(short)}</a>'
        )
    return items


def build_page(
    *,
    sections: list[tuple[str, str]],
    matrix_html: str,
    competitors: list[str],
    generated_at: str,
) -> str:
    sections_html = render_sections_flow(sections, matrix_html)
    toc_items = build_toc(sections, competitors)

    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Контент-стратегия для разработки сайта — Универмаг «Россия»</title>
    <meta name="description" content="Контент-стратегия для разработки интернет-магазина Универмаг «Россия»: выводы по конкурентам, tone of voice, структура страниц и рекомендации по наполнению.">
    <meta name="robots" content="noindex, nofollow">
    <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png?v={ASSET_VERSION}">
    <link rel="icon" type="image/png" sizes="512x512" href="../assets/favicon.png?v={ASSET_VERSION}">
    <link rel="apple-touch-icon" href="../assets/apple-touch-icon.png?v={ASSET_VERSION}">
    <link rel="stylesheet" href="../assets/styles.css?v={ASSET_VERSION}">
    <style>
      body {{ -webkit-font-smoothing: antialiased; }}
      .section-label {{
        display: inline-block;
        margin: 0 0 12px;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: .04em;
        text-transform: uppercase;
        color: var(--accent-2);
        background: rgba(31,95,104,.08);
      }}
      .section-intro {{ max-width: 720px; color: var(--muted); font-size: 17px; line-height: 1.6; }}
      .prose {{ max-width: 820px; }}
      .prose p {{ margin-bottom: 16px; color: var(--ink); font-size: 17px; line-height: 1.65; }}
      .toc-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 12px;
        margin-top: 20px;
      }}
      .toc-item {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 18px;
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 10px;
        text-decoration: none;
        color: var(--ink);
        font-weight: 600;
        font-size: 15px;
        transition: border-color .2s, box-shadow .2s;
      }}
      .toc-item--compact {{ font-size: 14px; padding: 12px 16px; }}
      .toc-item:hover {{ border-color: #2f4d2b; box-shadow: 0 2px 12px rgba(47,77,43,.08); }}
      .toc-num {{
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 32px;
        height: 32px;
        padding: 0 6px;
        border-radius: 8px;
        background: #2f4d2b;
        color: #fff;
        font-size: 13px;
        font-weight: 700;
        flex-shrink: 0;
      }}
      @media (max-width: 640px) {{
        .toc-grid {{ grid-template-columns: 1fr; }}
      }}
      .source-links {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; }}
      .source-links a {{
        font-size: 14px; font-weight: 600; color: #2f4d2b;
        text-decoration: none; border-bottom: 1px dashed rgba(47,77,43,.35);
      }}
      .source-links a:hover {{ border-bottom-style: solid; }}
      .cs-competitor {{ margin-top: 36px; }}
      .cs-competitor:first-of-type {{ margin-top: 24px; }}
      .cs-competitor .subsection-title {{
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(47,77,43,.12);
        font-family: "PT Serif", Georgia, serif;
      }}
      .cs-matrix-table {{
        min-width: 1280px;
        font-size: 14px;
        line-height: 1.5;
      }}
      .cs-matrix-table th,
      .cs-matrix-table td {{
        min-width: 200px;
        max-width: 320px;
      }}
      .cs-matrix-table th:first-child,
      .cs-matrix-table td:first-child {{
        position: sticky;
        left: 0;
        z-index: 1;
        min-width: 168px;
        max-width: 200px;
        background: #f4f7f4;
        box-shadow: 2px 0 0 var(--line);
      }}
      .cs-matrix-table thead th {{
        background: #2f4d2b;
        color: #fff;
        font-size: 12px;
        vertical-align: bottom;
      }}
      .cs-matrix-table thead th:first-child {{
        z-index: 2;
        background: #1a3518;
      }}
      .cs-matrix-table tbody th {{
        font-weight: 600;
        color: #1a3518;
      }}
      .cs-matrix-table tbody tr:hover td,
      .cs-matrix-table tbody tr:hover th {{
        background: rgba(47,77,43,.05);
      }}
      .cs-matrix-table tbody tr:hover th {{
        background: #e8efe6;
      }}
      .cs-audience-cards {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
        margin-top: 24px;
      }}
      .cs-audience-cards .card h3 {{
        font-size: 17px;
        color: #2f4d2b;
      }}
      @media (max-width: 900px) {{
        .cs-audience-cards {{ grid-template-columns: 1fr; }}
      }}
      .sync-meta {{ margin-top: 8px; font-size: 13px; color: var(--muted); }}
      @media print {{ .site-topbar {{ display: none !important; }} }}
    </style>
  </head>
  <body>
{topbar("content")}
    <header class="hero">
      <div class="wrap">
        <p class="eyebrow">ФРК / Национальный центр «Россия»</p>
        <h1>Контент-стратегия для разработки сайта Универмаг «Россия»</h1>
        <p class="lead">
          Рабочий документ для разработки сайта: анализ конкурентов и брифа, tone of voice,
          структура страниц, коллекции, карточки товаров и рекомендации по наполнению.
        </p>
        <p class="sync-meta">Обновлено из Google Docs: {html.escape(generated_at)} UTC</p>
        <div class="source-links">
          <a href="{html.escape(DOC_EDIT_URL)}" target="_blank" rel="noopener">Исходный документ (Google Docs)</a>
          <a href="{html.escape(SHEET_EDIT_URL)}" target="_blank" rel="noopener">Таблица сравнения конкурентов</a>
        </div>
      </div>
    </header>
    <main>
      <section class="section muted">
        <div class="wrap">
          <span class="section-label">Навигация</span>
          <h2>Содержание</h2>
          <div class="toc-grid">
{chr(10).join('            ' + item for item in toc_items)}
          </div>
        </div>
      </section>

{sections_html}
    </main>
  </body>
</html>
"""


def main() -> None:
    doc_raw = normalize_text(fetch(DOC_URL))
    sheet_raw = normalize_text(fetch(SHEET_URL))

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "content-strategy-doc.txt").write_text(doc_raw, encoding="utf-8")
    (DATA_DIR / "content-strategy-competitors.csv").write_text(sheet_raw, encoding="utf-8")

    sections = split_doc_sections(doc_raw)
    rows = load_competitor_rows(sheet_raw)
    grouped = group_competitors(rows)
    matrix_html = render_competitor_matrix(rows)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    meta = {
        "generated_at": generated_at,
        "doc_url": DOC_EDIT_URL,
        "sheet_url": SHEET_EDIT_URL,
        "section_count": len(sections),
        "matrix_rows": len(rows),
        "competitors": [name for name, _ in grouped],
    }
    (DATA_DIR / "content-strategy-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    page = build_page(
        sections=sections,
        matrix_html=matrix_html,
        competitors=[name for name, _ in grouped],
        generated_at=generated_at,
    )
    OUT_HTML.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT_HTML} ({len(page)} chars, {len(sections)} sections, {len(rows)} matrix rows)")


if __name__ == "__main__":
    main()
