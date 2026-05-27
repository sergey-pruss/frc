#!/usr/bin/env python3
"""Merge browser-scraped Wordstat rows into wordstat-scraped-catalog.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "wordstat-scraped-catalog.json"
BATCH = ROOT / "data" / "wordstat-browser-batch.json"


def main() -> None:
    existing: dict[str, dict] = {}
    if OUT.exists():
        for item in json.loads(OUT.read_text(encoding="utf-8")).get("queries", []):
            existing[item["phrase"].lower()] = item

    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    seed = batch["seed"]
    for row in batch["rows"]:
        phrase = row["phrase"].strip()
        key = phrase.lower()
        item = {
            "seed": seed,
            "phrase": phrase,
            "shows": int(row["shows"]),
            "cluster": row.get("cluster"),
        }
        if key not in existing or existing[key]["shows"] < item["shows"]:
            existing[key] = item

    payload = {
        "generated_at": batch.get("generated_at", ""),
        "queries": sorted(existing.values(), key=lambda x: (-x["shows"], x["phrase"])),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Merged {len(batch['rows'])} rows for seed={seed!r}; total {len(existing)} -> {OUT}")


if __name__ == "__main__":
    main()
