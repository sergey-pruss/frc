#!/usr/bin/env python3
"""Build competitor Wordstat JSON from browser snapshot logs."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "competitor-wordstat.json"
LOG_DIR = Path.home() / ".cursor/browser-logs"
PUTIN_LOG = ROOT / "data" / "wordstat-putin-team.log"
GLORY_LOG = LOG_DIR / "snapshot-2026-05-19T11-17-49-860Z-ys34ck.log"

VH_MIN = 1000
SCH_MIN = 100

GLORY_NOISE = re.compile(
    r"слава \d|дорам|сериал|серия|гайд|дата выхода|сколько сезон|обречен|"
    r"иллюзия славы|выход \d|песн|альбом|три дня|сезон дождей|когда выйдет|"
    r"есть ли \d|танцы \d| \bвк\b",
    re.I,
)


def classify(shows: int) -> str:
    if shows >= VH_MIN:
        return "ВЧ"
    if shows >= SCH_MIN:
        return "СЧ"
    return "НЧ"


def parse_snapshot(path: Path) -> list[tuple[str, int]]:
    text = path.read_text(encoding="utf-8")
    cells = re.findall(r"- role: cell\n\s+name: ([^\n]+)\n\s+ref: e\d+", text)
    rows: list[tuple[str, int]] = []
    i = 0
    while i < len(cells) - 1:
        phrase = cells[i].strip()
        count_raw = cells[i + 1].strip().replace("\u00a0", "").replace(" ", "")
        if re.fullmatch(r"\d+", count_raw):
            rows.append((phrase, int(count_raw)))
            i += 2
        else:
            i += 1
    return rows


def to_items(rows: list[tuple[str, int]], competitor: str) -> list[dict]:
    return [
        {
            "phrase": phrase,
            "shows": shows,
            "type": classify(shows),
            "competitor": competitor,
        }
        for phrase, shows in rows
    ]


def filter_glory(rows: list[tuple[str, int]]) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for phrase, shows in rows:
        low = phrase.lower()
        if GLORY_NOISE.search(low):
            continue
        if "сезон слав" in low or "glory season" in low or "russia capsule" in low:
            out.append((phrase, shows))
            continue
        if any(
            x in low
            for x in (
                "худи",
                "куртк",
                "пуховик",
                "бомбер",
                "дубленк",
                "футбол",
                "лонгслив",
                "бренд одежды",
                "магазин",
                "промокод",
                "mystery box",
            )
        ):
            out.append((phrase, shows))
    return out


def dedupe_max(items: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for item in items:
        key = item["phrase"].lower()
        if key not in merged or merged[key]["shows"] < item["shows"]:
            merged[key] = item
    return sorted(merged.values(), key=lambda x: (-x["shows"], x["phrase"]))


def main() -> None:
    putin_rows: list[tuple[str, int]] = []
    if PUTIN_LOG.exists():
        putin_rows = parse_snapshot(PUTIN_LOG)

    glory_rows: list[tuple[str, int]] = []
    if GLORY_LOG.exists():
        glory_rows = filter_glory(parse_snapshot(GLORY_LOG))

    manual_glory = [
        ("сезон славы одежда", 514),
        ("glory season одежда", 64),
        ("россия сезон славы одежда", 26),
        ("бренд одежды сезон славы", 18),
    ]

    putin = dedupe_max(to_items(putin_rows, "putin-team.ru"))
    glory = dedupe_max(
        to_items(glory_rows, "gloryseason.ru")
        + [
            {
                "phrase": p,
                "shows": c,
                "type": classify(c),
                "competitor": "gloryseason.ru",
            }
            for p, c in manual_glory
        ]
    )

    # Exclude ambiguous head term without «одежда» from commerce table
    glory = [g for g in glory if g["phrase"].lower() != "сезон славы"]

    payload = {
        "generated_at": time.strftime("%Y-%m-%d"),
        "region": "Россия, все регионы",
        "source": "Яндекс Wordstat → вкладка «Популярные» (запросы со словами)",
        "thresholds": {
            "vh_min": VH_MIN,
            "sch_min": SCH_MIN,
            "legend": "ВЧ — от 1000 показов/мес, СЧ — 100–999, НЧ — до 99",
        },
        "notes": [
            "Частотность — суммарные показов по кластеру запроса в Wordstat.",
            "Запрос «сезон славы» без уточнений в топе смешан с дорамами и музыкой — в таблице gloryseason.ru не используется как коммерческий ВЧ.",
        ],
        "putin_team": putin,
        "gloryseason": glory,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}: putin {len(putin)}, glory {len(glory)}")


if __name__ == "__main__":
    main()
