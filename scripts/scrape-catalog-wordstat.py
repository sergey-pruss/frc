#!/usr/bin/env python3
"""Scrape catalog Wordstat seeds into data/wordstat-scraped-catalog.json."""

from __future__ import annotations

import json
import re
import time
import urllib.parse
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SEEDS_FILE = ROOT / "data" / "wordstat-seeds-catalog.txt"
OUT = ROOT / "data" / "wordstat-scraped-catalog.json"


def load_seeds() -> list[str]:
    return [
        line.strip()
        for line in SEEDS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def parse_table(page) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
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


SEED_CLUSTER = {
    "худи купить": "Худи",
    "свитшот купить": "Свитшоты",
    "футболка купить": "Футболки",
    "ветровка купить": "Ветровки",
    "куртка купить": "Куртки",
    "кепка купить": "Кепки",
    "шапка купить": "Шапки",
    "значок купить": "Значки",
    "шопер купить": "Шоперы",
    "детская игра купить": "Детские игры",
    "подарочный сертификат купить": "Сертификаты",
    "книга купить": "Книги",
    "подарочная книга": "Книги",
    "книга о россии": "Книги",
    "сувенирная книга": "Книги",
}


def infer_cluster(phrase: str, seed: str) -> str | None:
    if seed in SEED_CLUSTER:
        return SEED_CLUSTER[seed]
    low = phrase.lower()
    if "книг" in low:
        return "Книги"
    if "шопер" in low:
        return "Шоперы"
    if "игр" in low:
        return "Детские игры"
    if "значк" in low:
        return "Значки"
    if "худи" in low:
        return "Худи"
    if "свитшот" in low:
        return "Свитшоты"
    if "футболк" in low:
        return "Футболки"
    if "ветровк" in low:
        return "Ветровки"
    if "куртк" in low:
        return "Куртки"
    if "кепк" in low or "бейсболк" in low:
        return "Кепки"
    if "шапк" in low:
        return "Шапки"
    if "сертификат" in low:
        return "Сертификаты"
    return None


def main() -> None:
    seeds = load_seeds()
    collected: dict[str, dict] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="ru-RU")
        page = context.new_page()

        for seed in seeds:
            url = (
                "https://wordstat.yandex.ru/?region=all&view=table&words="
                + urllib.parse.quote(seed)
            )
            page.goto(url, wait_until="networkidle", timeout=90000)
            time.sleep(2)
            if "passport.yandex" in page.url:
                print("Not logged in to Yandex. Log in via browser, then re-run.")
                browser.close()
                return
            for phrase, shows in parse_table(page):
                key = phrase.lower()
                row = {
                    "seed": seed,
                    "phrase": phrase,
                    "shows": shows,
                    "cluster": infer_cluster(phrase, seed),
                }
                if key not in collected or collected[key]["shows"] < shows:
                    collected[key] = row
            print(f"{seed}: {len(parse_table(page))} rows")
            time.sleep(1.5)

        browser.close()

    payload = {
        "generated_at": time.strftime("%Y-%m-%d"),
        "seeds": seeds,
        "queries": sorted(collected.values(), key=lambda x: (-x["shows"], x["phrase"])),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(collected)} unique phrases -> {OUT}")


if __name__ == "__main__":
    main()
