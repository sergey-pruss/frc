#!/usr/bin/env python3
"""Scrape Wordstat popular queries via Playwright (needs Yandex login in profile)."""

from __future__ import annotations

import json
import re
import time
import urllib.parse
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "wordstat-scraped.json"

SEEDS = [
    "putin team",
    "putin team russia",
    "putin team одежда",
    "putin team худи",
    "putin team футболка",
    "putin team подарочный сертификат",
    "сезон славы",
    "сезон славы одежда",
    "сезон славы худи",
    "glory season",
    "glory season одежда",
    "russia capsule",
    "mystery box одежда",
    "худи купить",
    "футболки мужские",
    "подарочный сертификат",
]

VH_MIN = 1000
SCH_MIN = 100


def classify(count: int) -> str:
    if count >= VH_MIN:
        return "ВЧ"
    if count >= SCH_MIN:
        return "СЧ"
    return "НЧ"


def parse_table(page) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    # Wordstat table cells: query link + count cell pairs
    cells = page.locator('[role="cell"]').all_inner_texts()
    i = 0
    while i < len(cells) - 1:
        phrase = cells[i].strip()
        count_text = cells[i + 1].strip().replace("\u00a0", "").replace(" ", "")
        if phrase and re.fullmatch(r"\d+", count_text):
            rows.append((phrase, int(count_text)))
            i += 2
        else:
            i += 1
    return rows


def main() -> None:
    all_rows: dict[str, int] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="ru-RU")
        page = context.new_page()

        for seed in SEEDS:
            url = (
                "https://wordstat.yandex.ru/?region=all&view=table&words="
                + urllib.parse.quote(seed)
            )
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(2)
            if "passport.yandex" in page.url:
                print("Not logged in to Yandex. Open Wordstat in browser and log in.")
                break
            for phrase, count in parse_table(page):
                key = phrase.lower().strip()
                all_rows[key] = max(all_rows.get(key, 0), count)
            print(f"{seed}: +{len(parse_table(page))} rows")
            time.sleep(1)

        browser.close()

    payload = [
        {"phrase": p, "shows": c, "type": classify(c)}
        for p, c in sorted(all_rows.items(), key=lambda x: -x[1])
    ]
    OUT.write_text(
        json.dumps(
            {
                "generated_at": time.strftime("%Y-%m-%d"),
                "region": "Россия, все регионы",
                "source": "Яндекс Wordstat (популярные запросы)",
                "thresholds": {"vh_min": VH_MIN, "sch_min": SCH_MIN},
                "queries": payload,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {OUT} ({len(payload)} unique phrases)")


if __name__ == "__main__":
    main()
