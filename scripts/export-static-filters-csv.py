#!/usr/bin/env python3
"""Export static SEO filter whitelist rows to CSV for Drive."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FULL = ROOT / "data" / "catalog-wordstat-full.json"
OUT = ROOT / "data" / "export" / "static-filter-candidates.csv"

# From seo/index.html static-filters whitelist (meeting 2026-05)
ROWS = [
    ("Футболки + цвет", "купить белую футболку", 6880, "/catalog/futbolki/belye/"),
    ("Футболки + цвет", "купить черную футболку", 3879, "/catalog/futbolki/chernye/"),
    ("Футболки + цвет", "купить красную футболку", 1512, "/catalog/futbolki/krasnye/"),
    ("Футболки + размер", "купить футболку размер", 11646, "/catalog/futbolki/razmery/"),
    ("Футболки + размер", "купить футболку большого размера", 6952, "/catalog/futbolki/bolshie-razmery/"),
    ("Футболки + свойство", "купить футболку с принтом", 4418, "/catalog/futbolki/s-printom/"),
    ("Худи + цвет", "купить черный худи", 568, "/catalog/hudi/chernye/"),
    ("Худи + цвет", "купить белое худи", 377, "/catalog/hudi/belye/"),
    ("Худи + конструкция", "купить худи с капюшоном", 1478, "/catalog/hudi/s-kapyushonom/"),
    ("Худи + конструкция", "худи на молнии купить", 569, "/catalog/hudi/na-molnii/"),
    ("Куртки + размер", "купить куртку размера", 9102, "/catalog/kurtki/razmery/"),
    ("Куртки + сезон", "купить демисезонную куртку", 13719, "/catalog/kurtki/demisezonnye/"),
    ("Куртки + конструкция", "купить куртку с капюшоном", 4012, "/catalog/kurtki/s-kapyushonom/"),
    ("Ветровки + конструкция", "ветровка с капюшоном купить", 1488, "/catalog/vetrovki/s-kapyushonom/"),
    ("Свитшоты + цвет", "свитшоты черные купить", 110, "/catalog/svitshoty/chernye/"),
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Фильтр", "Запрос", "Показы/мес", "Пример URL"])
        for row in ROWS:
            w.writerow(row)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
