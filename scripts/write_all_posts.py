#!/usr/bin/env python3
"""Write EN+VI Markdown posts for the 2026 content batch."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN_DIR = ROOT / "src" / "content" / "blog"
VI_DIR = ROOT / "src" / "content" / "blog-vi"
DATE = "2026-09-10"
AUTHOR = "Trung Hieu"

# Import feature batch 1
sys.path.insert(0, str(Path(__file__).parent))
from content_batch_features_1 import FEATURES  # noqa: E402


def ydump(keywords: list[str], sources: list[tuple[str, str]], related: list[tuple[str, str]], tags: list[str]) -> str:
    kw = "\n".join(f"  - {k}" for k in keywords)
    tg = ", ".join(f'"{t}"' for t in tags)
    src = "\n".join(f'  - name: "{n}"\n    url: "{u}"' for n, u in sources)
    rel = "\n".join(f'  - slug: "{s}"\n    title: "{t}"' for s, t in related)
    return f"""keywords:
{kw}
tags: [{tg}]
sources:
{src}
related:
{rel}
"""


def write_feature(item: dict) -> None:
    slug = item["slug"]
    # EN
    en = f"""---
title: "{item['title_en']}"
description: "{item['desc_en']}"
seoDescription: "{item['seo_en']}"
{ydump(item["keywords"], item["sources"], [(s, s.replace('-', ' ').title()) for s in item["related"]], item["tags"])}category: "{item['category']}"
topic: "{item['topic']}"
level: "{item['level']}"
author: "{AUTHOR}"
publishDate: "{DATE}"
emoji: "{item['emoji']}"
draft: false
---

{item["body_en"].strip()}

![Diagram: {item['title_en']}](/blog/images/{slug}.svg)
"""
    # Image after first H2 is better for SEO reading order — insert after intro
    # We'll place image right after frontmatter intro by simple replace of first blank after first paragraph
    body = item["body_en"].strip()
    parts = body.split("\n\n", 1)
    if len(parts) == 2:
        body = f"{parts[0]}\n\n![Diagram: {item['title_en']}](/blog/images/{slug}.svg)\n\n{parts[1]}"
    else:
        body = f"{body}\n\n![Diagram: {item['title_en']}](/blog/images/{slug}.svg)"
    en = f"""---
title: "{item['title_en']}"
description: "{item['desc_en']}"
seoDescription: "{item['seo_en']}"
{ydump(item["keywords"], item["sources"], [(s, s.replace('-', ' ').title()) for s in item["related"]], item["tags"])}category: "{item['category']}"
topic: "{item['topic']}"
level: "{item['level']}"
author: "{AUTHOR}"
publishDate: "{DATE}"
emoji: "{item['emoji']}"
draft: false
---

{body}
"""
    # VI
    body_vi = item["body_vi"].strip()
    parts_vi = body_vi.split("\n\n", 1)
    if len(parts_vi) == 2:
        body_vi = f"{parts_vi[0]}\n\n![Sơ đồ: {item['title_vi']}](/blog/images/{slug}.svg)\n\n{parts_vi[1]}"
    else:
        body_vi = f"{body_vi}\n\n![Sơ đồ: {item['title_vi']}](/blog/images/{slug}.svg)"
    vi = f"""---
title: "{item['title_vi']}"
description: "{item['desc_vi']}"
seoDescription: "{item['seo_vi']}"
{ydump(item["keywords"], item["sources"], [(s, s.replace('-', ' ').title()) for s in item["related"]], item["tags"])}category: "{item['category']}"
topic: "{item['topic']}"
level: "{item['level']}"
author: "{AUTHOR}"
publishDate: "{DATE}"
emoji: "{item['emoji']}"
draft: false
---

{body_vi}
"""
    EN_DIR.mkdir(parents=True, exist_ok=True)
    VI_DIR.mkdir(parents=True, exist_ok=True)
    (EN_DIR / f"{slug}.md").write_text(en, encoding="utf-8")
    (VI_DIR / f"{slug}.md").write_text(vi, encoding="utf-8")
    print(f"wrote {slug}")


def main() -> None:
    # FEATURES_2 and OSS imported from sibling modules
    from content_batch_features_2 import FEATURES_2
    from content_batch_oss import OSS

    all_items = list(FEATURES) + list(FEATURES_2) + list(OSS)
    for item in all_items:
        write_feature(item)
    print(f"TOTAL {len(all_items)} topics → {len(all_items)*2} files")


if __name__ == "__main__":
    main()
