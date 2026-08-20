#!/usr/bin/env python3
"""Inline data/screenshot-templates.json into the Screenshot Studio fragment.

studio.html has to stay a single self-contained file: the Astro pages and the
Blogger mirror all splice it in as-is, and Blogger cannot fetch a sibling JSON
file. So the library lives in JSON (readable, diffable, one entry per design)
and this script writes it into the TEMPLATES:BEGIN/END block in the fragment.

Output is ASCII-escaped on purpose — Blogger rewrites non-ASCII characters
inside <script> as HTML entities, which then render literally.

Usage:
    python3 scripts/build_studio_templates.py
    python3 scripts/build_studio_templates.py --check     # CI: fail if stale
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "screenshot-templates.json"
DEST = ROOT / "tools" / "screenshot-studio" / "studio.html"

BLOCK = re.compile(
    r"(/\* TEMPLATES:BEGIN.*?\*/\n)(.*?)(\n  /\* TEMPLATES:END \*/)",
    re.S,
)

# Keys the editor reads. Anything else in the JSON is documentation for us.
KEYS = ["id", "name", "tone", "tags", "bgMode", "bg1", "bg2", "fg", "accent",
        "font", "layout", "frame", "blobs"]


def render(templates: list[dict]) -> str:
    rows = []
    for t in templates:
        row = {k: t[k] for k in KEYS if k in t}
        rows.append("    " + json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return "  var TEMPLATES = [\n" + ",\n".join(rows) + "\n  ];"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if studio.html is out of date instead of writing it")
    args = ap.parse_args()

    data = json.loads(SRC.read_text("utf-8"))
    templates = data["templates"]

    ids = [t["id"] for t in templates]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"duplicate template ids: {', '.join(sorted(dupes))}")
    for t in templates:
        missing = [k for k in ("id", "name", "tone", "bgMode", "bg1", "bg2", "fg", "accent") if k not in t]
        if missing:
            raise SystemExit(f"{t.get('id', '?')}: missing {', '.join(missing)}")
        if t["tone"] not in data["tones"]:
            raise SystemExit(f"{t['id']}: tone {t['tone']!r} is not one of {data['tones']}")

    html = DEST.read_text("utf-8")
    if not BLOCK.search(html):
        raise SystemExit("studio.html is missing its TEMPLATES:BEGIN/END block")
    updated = BLOCK.sub(lambda m: m.group(1) + render(templates) + m.group(3), html, count=1)

    if args.check:
        if updated != html:
            print(f"stale: run python3 scripts/build_studio_templates.py")
            return 1
        print(f"up to date ({len(templates)} templates)")
        return 0

    if updated == html:
        print(f"unchanged ({len(templates)} templates)")
        return 0
    DEST.write_text(updated, "utf-8")
    print(f"{len(templates)} templates -> {DEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
