#!/usr/bin/env python3
"""Build competitor VH/SCH semantics from Yandex Suggest and optional Wordstat API."""

from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "competitor-semantics.json"

# Wordstat API (https://yandex.ru/dev/wordstat/doc/dg-v1/concepts/about)
WORDSTAT_TOKEN = os.environ.get("YANDEX_WORDSTAT_TOKEN", "").strip()
REGION_RU = 225

VH_MIN = 3000
SCH_MIN = 150

PUTIN_SEEDS = [
    "putin team",
    "putin team russia",
    "putin team одежда",
    "путин тим",
    "putin team купить",
    "putin team футболка",
    "putin team худи",
    "putin team свитшот",
    "putin team кепка",
    "putin team подарочный сертификат",
    "putin team доставка",
    "putin team красная машина",
    "putin team капсульная коллекция",
    "putin team распродажа",
]

GLORY_SEEDS = [
    "сезон славы",
    "сезон славы одежда",
    "glory season",
    "glory season одежда",
    "russia capsule",
    "mystery box",
    "сезон славы худи",
    "сезон славы куртка",
    "сезон славы пуховик",
    "glory season промокод",
    "сезон славы интернет магазин",
]

NOISE_PATTERNS = re.compile(
    r"(перевод|отзывы|фото|шереметьевск|пулковск|дзержинск|"
    r"anime|stardew|wildberries|золотое яблоко|flower knows|"
    r"три дня дождя|азбука скачать|чей бренд|кто владелец|"
    r"mystery box game|mystery box japan|mystery box bundle)",
    re.I,
)


def yandex_suggest(phrase: str) -> list[str]:
    url = (
        "https://yandex.ru/suggest/suggest-ya.cgi?v=4&part="
        + urllib.parse.quote(phrase)
        + "&lang=ru&n=20"
    )
    with urllib.request.urlopen(url, timeout=12) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return list(data[1]) if len(data) > 1 else []


def wordstat_top_requests(phrase: str) -> list[tuple[str, int]]:
    if not WORDSTAT_TOKEN:
        return []
    body = json.dumps(
        {"phrase": phrase, "regions": [REGION_RU], "devices": ["all"]},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.wordstat.yandex.net/v1/topRequests",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {WORDSTAT_TOKEN}",
            "Content-Type": "application/json;charset=utf-8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return []
    items = payload.get("topRequests") or payload.get("popular") or []
    out: list[tuple[str, int]] = []
    for item in items:
        if isinstance(item, dict):
            p = item.get("phrase") or item.get("text")
            c = item.get("count") or item.get("shows") or 0
            if p:
                out.append((str(p), int(c)))
    return out


def wordstat_frequency(phrase: str) -> int | None:
    tops = wordstat_top_requests(phrase)
    if not tops:
        return None
    target = phrase.lower().strip()
    for p, c in tops:
        if p.lower().strip() == target:
            return c
    return tops[0][1] if tops else None


def classify(count: int | None, phrase: str) -> str:
    if count is not None:
        if count >= VH_MIN:
            return "ВЧ"
        if count >= SCH_MIN:
            return "СЧ"
        return "НЧ"
    words = phrase.split()
    if len(words) <= 2:
        return "ВЧ*"
    if len(words) <= 4:
        return "СЧ*"
    return "НЧ*"


def collect_for_competitor(seeds: list[str], site_filter) -> list[dict]:
    seen: set[str] = set()
    rows: list[dict] = []

    for seed in seeds:
        candidates = {seed, *yandex_suggest(seed)}
        if WORDSTAT_TOKEN:
            for p, c in wordstat_top_requests(seed):
                candidates.add(p)
            time.sleep(0.2)

        for phrase in sorted(candidates, key=len):
            key = phrase.lower().strip()
            if not key or key in seen or NOISE_PATTERNS.search(key):
                continue
            if not site_filter(key):
                continue
            seen.add(key)
            count = wordstat_frequency(phrase) if WORDSTAT_TOKEN else None
            if WORDSTAT_TOKEN:
                time.sleep(0.15)
            rows.append(
                {
                    "phrase": phrase,
                    "shows": count,
                    "type": classify(count, phrase),
                }
            )

    rows.sort(key=lambda r: (r["shows"] is None, -(r["shows"] or 0), r["phrase"]))
    return rows


def putin_filter(key: str) -> bool:
    markers = (
        "putin",
        "путин",
        "тим",
        "team russia",
        "красная машина",
        "outdoor",
        "капсул",
    )
    if any(m in key for m in markers):
        return True
    # generic merch queries relevant to store
    return key in {
        "худи купить",
        "футболки мужские",
        "толстовка мужская",
        "свитшот мужской",
        "подарочный сертификат",
        "подарочный сертификат одежда",
    }


def glory_filter(key: str) -> bool:
    markers = (
        "сезон слав",
        "glory season",
        "gloryseason",
        "russia capsule",
        "mystery box",
        "kozhan",
        "fluffy",
        "darkprincess",
    )
    if any(m in key for m in markers):
        return True
    return key in {
        "худи купить",
        "футболки мужские",
        "толстовка мужская",
        "свитшот мужской",
    }


def main() -> None:
    putin = collect_for_competitor(PUTIN_SEEDS, putin_filter)
    glory = collect_for_competitor(GLORY_SEEDS, glory_filter)

    payload = {
        "generated_at": time.strftime("%Y-%m-%d"),
        "region": "Россия (225)",
        "source": "Yandex Suggest"
        + (" + Wordstat API v1" if WORDSTAT_TOKEN else ""),
        "thresholds": {"vh_min": VH_MIN, "sch_min": SCH_MIN},
        "note": (
            "Тип ВЧ/СЧ по показам Wordstat (РФ). "
            "Если показов нет — тип с * по длине фразы (нужен YANDEX_WORDSTAT_TOKEN)."
        ),
        "putin_team": putin,
        "gloryseason": glory,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"putin-team: {len(putin)} phrases, gloryseason: {len(glory)} phrases")
    if not WORDSTAT_TOKEN:
        print("Set YANDEX_WORDSTAT_TOKEN to fill Wordstat shows.")


if __name__ == "__main__":
    main()
