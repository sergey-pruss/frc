#!/usr/bin/env python3
"""Build catalog Wordstat full export, top keywords, and CSV for Drive."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "data" / "catalog-wordstat-100plus.json"
RAW_SCRAPED = ROOT / "data" / "wordstat-scraped-catalog.json"
EXCLUDE_FILE = ROOT / "data" / "wordstat-exclude-patterns.txt"
SEEDS_FILE = ROOT / "data" / "wordstat-seeds-catalog.txt"
LOG_DIR = Path.home() / ".cursor/browser-logs"

OUT_FULL = ROOT / "data" / "catalog-wordstat-full.json"
OUT_TOP = ROOT / "data" / "catalog-keywords-top10.json"
OUT_CSV_FULL = ROOT / "data" / "export" / "catalog-wordstat-full.csv"
OUT_CSV_TOP = ROOT / "data" / "export" / "catalog-keywords-top10.csv"

THRESHOLD = 100
TOP_PER_CLUSTER = 10

# Editorial anchors for top-10 (meeting 2026-05); must exist in full export when possible
CLUSTER_ANCHORS: dict[str, list[str]] = {
    "Худи": ["худи купить", "купить худи с капюшоном", "купить черный худи"],
    "Свитшоты": ["купить свитшот", "свитшоты черные купить"],
    "Футболки": ["футболки купить", "купить белую футболку", "купить черную футболку", "купить футболку с принтом"],
    "Ветровки": ["купить ветровку", "ветровка с капюшоном купить"],
    "Куртки": ["купить куртку", "купить демисезонную куртку", "купить куртку с капюшоном"],
    "Кепки": ["купить кепку", "купить черную кепку"],
    "Шапки": ["купить шапку", "шапка купить"],
    "Значки": ["значки купить", "значок купить"],
    "Шоперы": ["шопер купить", "сумка шопер купить"],
    "Детские игры": ["детская игра купить", "детские настольные игры купить", "настольные игры для детей купить"],
    "Книги": [
        "купить книгу",
        "подарочные книги",
        "купить подарочную книгу",
        "книга россия купить",
        "купить книгу о россии",
        "сувенирные книги",
    ],
    "Сертификаты": ["купить подарочный сертификат", "электронный подарочный сертификат"],
}

SEED_CLUSTER: dict[str, str] = {
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
    "сумка шопер купить": "Шоперы",
    "тканевый шопер": "Шоперы",
    "настольная игра для детей": "Детские игры",
    "развивающая игра купить": "Детские игры",
    "сувенирный значок": "Значки",
    "металлический значок": "Значки",
}

CLUSTER_PHRASE_HINTS: list[tuple[str, str]] = [
    (r"\bхуди\b|\bтолстовк", "Худи"),
    (r"\bсвитшот", "Свитшоты"),
    (r"\bфутболк|\bполо\b", "Футболки"),
    (r"\bветровк", "Ветровки"),
    (r"\bкуртк|\bбомбер|\bпуховик", "Куртки"),
    (r"\bкепк|\bбейсболк", "Кепки"),
    (r"\bшапк|\bбини\b", "Шапки"),
    (r"\bзначк|\bбейдж", "Значки"),
    (r"\bшопер|\bсумка шопер", "Шоперы"),
    (r"\bкниг", "Книги"),
    (r"\bигр", "Детские игры"),
    (r"сертификат", "Сертификаты"),
]


def load_exclude_patterns() -> list[re.Pattern[str]]:
    patterns: list[re.Pattern[str]] = []
    if not EXCLUDE_FILE.exists():
        return patterns
    for line in EXCLUDE_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(re.compile(line, re.I))
    return patterns


def is_excluded(phrase: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.search(phrase) for p in patterns)


BOOK_NOISE = re.compile(
    r"купить книгу \d|купить \d книг|бывш|сколько|книгу \d|"
    r"можно купить|куплено \d|история книги|книга жизни|"
    r"книга покупок|блокнот|книжный купить|стоя книга|"
    r"какую книгу|читай|где купить|где можно|"
    r"^\d+ | \d+ \d+ книг|книга \d|книги \d",
    re.I,
)


def is_commercial_book(phrase: str) -> bool:
    low = phrase.lower()
    if BOOK_NOISE.search(low):
        return False
    if re.search(r"подарочн.*книг|сувенир.*книг", low):
        return True
    if re.search(r"книг.*росси", low) and re.search(r"купить", low):
        return True
    if re.search(r"купить", low) and re.search(r"книг", low):
        if re.search(r"на озон|томами|больше|про$|город купить|магазины", low):
            return False
        return len(low.split()) <= 4
    return False


def parse_snapshot(path: Path) -> list[tuple[str, int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    cells = re.findall(r"- role: cell\n\s+name: ([^\n]+)\n\s+ref: e\d+", text)
    rows: list[tuple[str, int]] = []
    i = 0
    while i < len(cells) - 1:
        phrase = cells[i].strip()
        count_raw = cells[i + 1].strip().replace("\u00a0", "").replace(" ", "")
        if phrase and re.fullmatch(r"\d+", count_raw):
            rows.append((phrase, int(count_raw)))
            i += 2
        else:
            i += 1
    return rows


def infer_cluster(phrase: str, seed: str | None = None) -> str | None:
    if seed and seed in SEED_CLUSTER:
        return SEED_CLUSTER[seed]
    low = phrase.lower()
    for pattern, cluster in CLUSTER_PHRASE_HINTS:
        if re.search(pattern, low):
            return cluster
    return None


def load_legacy() -> list[dict]:
    if not LEGACY.exists():
        return []
    data = json.loads(LEGACY.read_text(encoding="utf-8"))
    return list(data.get("all_queries", []))


def load_scraped() -> list[dict]:
    if not RAW_SCRAPED.exists():
        return []
    data = json.loads(RAW_SCRAPED.read_text(encoding="utf-8"))
    items = data.get("queries") or data.get("items") or []
    out: list[dict] = []
    for item in items:
        phrase = item.get("phrase") or item.get("query")
        shows = item.get("shows") or item.get("count")
        if phrase and shows is not None:
            out.append(
                {
                    "seed": item.get("seed", ""),
                    "phrase": phrase.strip(),
                    "shows": int(shows),
                    "cluster": item.get("cluster") or infer_cluster(phrase, item.get("seed")),
                }
            )
    return out


def load_browser_snapshots(seeds: set[str]) -> list[dict]:
    if not LOG_DIR.exists():
        return []
    out: list[dict] = []
    for path in sorted(LOG_DIR.glob("snapshot-*.log")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "wordstat" not in text.lower() and "популярные" not in text.lower():
            continue
        seed_hint = None
        for seed in seeds:
            if seed in text.lower():
                seed_hint = seed
                break
        for phrase, shows in parse_snapshot(path):
            if shows < THRESHOLD:
                continue
            out.append(
                {
                    "seed": seed_hint or "",
                    "phrase": phrase,
                    "shows": shows,
                    "cluster": infer_cluster(phrase, seed_hint),
                }
            )
    return out


def merge_queries(sources: list[list[dict]]) -> list[dict]:
    merged: dict[str, dict] = {}
    for batch in sources:
        for item in batch:
            phrase = item["phrase"].strip()
            key = phrase.lower()
            cluster = item.get("cluster") or infer_cluster(phrase, item.get("seed"))
            row = {
                "seed": item.get("seed") or "",
                "phrase": phrase,
                "shows": int(item["shows"]),
                "cluster": cluster or "Прочее",
            }
            if key not in merged or merged[key]["shows"] < row["shows"]:
                merged[key] = row
    return sorted(merged.values(), key=lambda x: (-x["shows"], x["phrase"]))


def build_top(queries: list[dict], per_cluster: int = TOP_PER_CLUSTER) -> dict:
    by_cluster: dict[str, list[dict]] = defaultdict(list)
    index = {q["phrase"].lower(): q for q in queries}
    for q in queries:
        by_cluster[q["cluster"]].append(q)
    top: dict[str, list[dict]] = {}
    for cluster, items in sorted(by_cluster.items()):
        chosen: list[dict] = []
        seen: set[str] = set()
        for anchor in CLUSTER_ANCHORS.get(cluster, []):
            row = index.get(anchor.lower())
            if row and row["cluster"] == cluster:
                chosen.append(row)
                seen.add(row["phrase"].lower())
        if cluster == "Книги":
            top[cluster] = chosen
            continue
        for row in sorted(items, key=lambda x: (-x["shows"], x["phrase"])):
            key = row["phrase"].lower()
            if key in seen:
                continue
            if cluster == "Книги" and not is_commercial_book(row["phrase"]):
                continue
            chosen.append(row)
            seen.add(key)
            if len(chosen) >= per_cluster:
                break
        top[cluster] = chosen[:per_cluster]
    return {
        "generated_at": date.today().isoformat(),
        "source": OUT_FULL.name,
        "per_cluster": per_cluster,
        "clusters": top,
    }


def cluster_counts(queries: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for q in queries:
        counts[q["cluster"]] += 1
    return dict(counts)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    seeds = {
        line.strip()
        for line in SEEDS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    patterns = load_exclude_patterns()

    raw_sources = [
        load_legacy(),
        load_scraped(),
        load_browser_snapshots(seeds),
    ]
    merged = merge_queries(raw_sources)
    cleaned = [q for q in merged if q["shows"] >= THRESHOLD and not is_excluded(q["phrase"], patterns)]

    # Drop unclustered noise unless clearly product-related
    cleaned = [q for q in cleaned if q["cluster"] != "Прочее" or infer_cluster(q["phrase"])]

    # Books: keep commercial buy-intent phrases only
    cleaned = [
        q
        for q in cleaned
        if q["cluster"] != "Книги" or is_commercial_book(q["phrase"])
    ]

    full_doc = {
        "generated_at": date.today().isoformat(),
        "source": "Яндекс Wordstat, вкладка Популярные, регион Россия, все устройства",
        "threshold": f"{THRESHOLD} показов/мес и выше",
        "note": (
            "Полный очищенный массив для вкладки 1 (Drive) и аргументации top-10. "
            "Минус-лист: data/wordstat-exclude-patterns.txt"
        ),
        "total_clean_queries": len(cleaned),
        "cluster_counts": cluster_counts(cleaned),
        "all_queries": cleaned,
    }
    OUT_FULL.write_text(json.dumps(full_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    top_doc = build_top(cleaned)
    OUT_TOP.write_text(json.dumps(top_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_csv(
        OUT_CSV_FULL,
        cleaned,
        ["cluster", "phrase", "shows", "seed"],
    )
    top_rows: list[dict] = []
    for cluster, items in top_doc["clusters"].items():
        for rank, item in enumerate(items, 1):
            top_rows.append(
                {
                    "cluster": cluster,
                    "rank": rank,
                    "phrase": item["phrase"],
                    "shows": item["shows"],
                    "seed": item.get("seed", ""),
                }
            )
    write_csv(OUT_CSV_TOP, top_rows, ["cluster", "rank", "phrase", "shows", "seed"])

    # Keep legacy path in sync for tests until migrated
    LEGACY.write_text(json.dumps(full_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Full: {len(cleaned)} queries -> {OUT_FULL}")
    print(f"Top clusters: {len(top_doc['clusters'])} -> {OUT_TOP}")
    for cluster, count in sorted(full_doc["cluster_counts"].items(), key=lambda x: -x[1]):
        print(f"  {cluster}: {count}")


if __name__ == "__main__":
    main()
