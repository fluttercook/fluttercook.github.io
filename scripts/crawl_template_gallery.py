#!/usr/bin/env python3
"""Crawl a public screenshot-template gallery for catalogue *metadata*.

What this collects: slugs, display names, URLs, which device surface a template
targets, and whether it is derived from a named brand. All of it comes from the
site's own sitemap.xml, which robots.txt allows.

What this deliberately does NOT collect: preview images, layer data, or colour
values. Those are the gallery's creative work. This file exists to tell us what
the template *space* looks like — how many portrait phone sets versus watch or
landscape sets, which style vocabulary is in use — so data/screenshot-templates.json
can cover the same ground with original designs.

Roughly half of the entries in the surveyed gallery are "inspired-by-<brand>"
clones of shipped apps. Those are marked brandDerived and are not a model for
anything we publish: reproducing another company's trade dress in our own tool
would be passing off their design work, whoever generated the pixels.

Usage:
    python3 scripts/crawl_template_gallery.py
    python3 scripts/crawl_template_gallery.py --source https://example.com/sitemap.xml
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "template_research.json"
DEFAULT_SOURCE = "https://appscreens.com/sitemap.xml"

# Style and category vocabulary as the gallery's own filter UI presents it.
# Recorded once here rather than re-scraped: it is a short, stable list.
TAXONOMY = {
    "orientation": ["portrait", "landscape"],
    "tone": ["light", "dark", "colourful"],
    "style": ["simple", "advanced", "multi layered", "gradient", "graphics"],
    "appStoreCategories": [
        "books", "business", "education", "entertainment", "developer tools",
        "finance", "food & drink", "games", "graphics & design",
        "health & fitness", "lifestyle", "music", "photo & video",
        "productivity", "reference", "social networking", "utilities",
    ],
}

# slug prefix -> the surface the template is drawn for
SURFACE_RULES = [
    ("google-feature-graphic", "play-feature-graphic"),
    ("landscape-", "phone-landscape"),
    ("apple-vision-pro", "vision"),
    ("watch-", "watch"),
    ("macos", "macos"),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "FlutterCookBot/1.0 (+https://fluttercook.github.io)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "replace")


def surface_of(slug: str) -> str:
    for prefix, surface in SURFACE_RULES:
        if slug.startswith(prefix):
            return surface
    return "phone-portrait"


def display_name(slug: str) -> str:
    s = re.sub(r"^(free-|landscape-)", "", slug)
    s = s.replace("-", " ").strip()
    return s[:1].upper() + s[1:]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    xml = fetch(args.source)
    locs = re.findall(r"<loc>([^<]*/template/[^<]*)</loc>", xml)

    templates = []
    seen = set()
    for url in locs:
        parts = [p for p in url.split("/") if p]
        # .../template/<store-type>/<slug>/<id>
        try:
            i = parts.index("template")
            store_type, slug = parts[i + 1], parts[i + 2]
        except (ValueError, IndexError):
            continue
        if slug in seen:
            continue
        seen.add(slug)
        templates.append({
            "slug": slug,
            "name": display_name(slug),
            "url": url,
            "storeType": store_type,
            "surface": surface_of(slug),
            "brandDerived": "inspired-by" in slug or "inspired-from" in slug,
            "free": slug.startswith("free-"),
        })

    templates.sort(key=lambda t: (t["surface"], t["slug"]))
    surfaces = Counter(t["surface"] for t in templates)
    brand = sum(1 for t in templates if t["brandDerived"])

    payload = {
        "source": args.source,
        "note": (
            "Metadata only — names, URLs and surface classification derived from "
            "the public sitemap. No artwork or design data is copied. Templates "
            "marked brandDerived reproduce a named app's look and are excluded "
            "from anything we ship."
        ),
        "counts": {
            "total": len(templates),
            "brandDerived": brand,
            "original": len(templates) - brand,
            "bySurface": dict(sorted(surfaces.items())),
        },
        "taxonomy": TAXONOMY,
        "templates": templates,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", "utf-8")

    print(f"{len(templates)} templates -> {out}")
    print(f"  brand-derived: {brand}   original: {len(templates) - brand}")
    for k, v in sorted(surfaces.items()):
        print(f"  {k:<24} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
