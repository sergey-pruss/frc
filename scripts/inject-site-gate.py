#!/usr/bin/env python3
"""Inject inline site gate guard into static HTML pages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gate_snippet import EXTERNAL_GATE_RE, GATE_GUARD_MARKER, GATE_GUARD_SCRIPT  # noqa: E402
SKIP_DIRS = {"gate", "data", "export", "node_modules", ".git"}
SKIP_FILES = {ROOT / "gate" / "index.html"}


def should_process(path: Path) -> bool:
    if path in SKIP_FILES:
        return False
    if path.name != "index.html" and path.suffix != ".html":
        return False
    return not any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts)


def inject(html: str) -> tuple[str, bool]:
    updated = EXTERNAL_GATE_RE.sub("\n", html)
    changed = updated != html

    if GATE_GUARD_MARKER in updated and "location.replace(g+" in updated:
        return updated, changed

    match = re.search(r'(<meta charset="utf-8">\n)', updated, re.IGNORECASE)
    if not match:
        return updated, changed
    pos = match.end()
    return updated[:pos] + GATE_GUARD_SCRIPT + updated[pos:], True


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if not should_process(path):
            continue
        text = path.read_text(encoding="utf-8")
        updated, did_change = inject(text)
        if did_change:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"  + {path.relative_to(ROOT)}")
    print(f"Gate injected into {changed} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
