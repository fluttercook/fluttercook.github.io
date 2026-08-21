#!/usr/bin/env python3
"""Publish the Screenshot Studio tool to a Blogger blog as a *page* (not a post).

Blogger pages live at /p/<slug>.html and stay out of the post feed, which is
what a permanent tool belongs in. The body is assembled from the same source
the website uses:

    tools/screenshot-studio/studio.html     the editor (markup + CSS + JS)
    tools/screenshot-studio/blogger-<lang>.html   surrounding copy, <!--STUDIO--> marker

Auth, retry/backoff and the sync map are shared with publish_to_blogger.py;
page ids are recorded under blogs.<id>.pages so re-runs UPDATE in place instead
of creating a second copy.

SEO note: the Blogger API exposes only title and content for a page. A search
description (customMetaData / metaDescription) is silently dropped — probed and
confirmed — and canonical, hreflang and OG tags live in the theme, which has no
API at all. So everything we can control is emitted into the body: JSON-LD
(SoftwareApplication + FAQPage + BreadcrumbList), a cross-language link, and a
footer pointing at the canonical copy on fluttercook.github.io.

Examples:
    python3 scripts/publish_page_to_blogger.py --lang en --dry-run
    python3 scripts/publish_page_to_blogger.py --lang vi --blog trunghieu-it --publish
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from publish_to_blogger import (  # noqa: E402  (path shim has to come first)
    BLOG_ID_BY_NAME,
    BLOGS,
    DEFAULT_BLOG_ID,
    ROOT,
    SITE,
    access_token,
    api,
    assert_can_write,
    blog_state,
    load_state,
    resolve_blog,
    save_state,
)

TOOL_DIR = ROOT / "tools" / "screenshot-studio"

OTHER = {"en": "vi", "vi": "en"}

META = {
    "en": {
        "title": "App Store Screenshot Generator — free, in your browser",
        "canonical": f"{SITE}/tools/screenshot-studio/",
        "locale": "en",
        "description": (
            "Free browser-based App Store and Google Play screenshot generator: pick one of 24 "
            "templates, drop in your app screens, write captions and export PNGs at the exact "
            "store sizes. Nothing is uploaded."
        ),
        "attribution": (
            'This tool is maintained at <a href="{url}">{url}</a> — '
            "the version there is always the newest."
        ),
        "crossLabel": "Tiếng Việt",
        "crossLead": "Also available in",
        "home": "Home",
    },
    "vi": {
        "title": "Tạo ảnh chụp màn hình App Store — miễn phí, ngay trên trình duyệt",
        "canonical": f"{SITE}/vi/tools/screenshot-studio/",
        "locale": "vi",
        "description": (
            "Công cụ tạo ảnh chụp màn hình App Store và Google Play miễn phí, chạy ngay trong "
            "trình duyệt: chọn 1 trong 24 mẫu, thả ảnh màn hình ứng dụng, viết caption và xuất "
            "PNG đúng kích thước store. Không tải ảnh lên máy chủ."
        ),
        "attribution": (
            'Công cụ này được duy trì tại <a href="{url}">{url}</a> — '
            "bản ở đó luôn là bản mới nhất."
        ),
        "crossLabel": "English",
        "crossLead": "Bản khác",
        "home": "Trang chủ",
    },
}


def escape_script_unicode(html: str) -> str:
    """Rewrite non-ASCII inside <script> as \\uXXXX before handing HTML to Blogger.

    Blogger turns characters like — and ◀ into numeric HTML entities wherever
    they appear, including inside script bodies, where they end up rendered
    literally as "&#8212;". Entity-safe \\u escapes survive the round trip.
    Text outside <script> is left alone: entities render correctly there.
    """
    def esc(match: re.Match) -> str:
        out = []
        for ch in match.group(2):
            cp = ord(ch)
            if cp < 128:
                out.append(ch)
            elif cp > 0xFFFF:                      # astral plane -> surrogate pair
                cp -= 0x10000
                out.append("\\u%04x\\u%04x" % (0xD800 + (cp >> 10), 0xDC00 + (cp & 0x3FF)))
            else:
                out.append("\\u%04x" % cp)
        return match.group(1) + "".join(out) + match.group(3)

    return re.sub(r"(<script\b[^>]*>)(.*?)(</script>)", esc, html, flags=re.S)


FAQ_RE = re.compile(r"<p><b>(.+?)</b><br />\s*(.+?)</p>", re.S)


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def faq_pairs(wrapper: str) -> list[tuple[str, str]]:
    """Read the FAQ straight out of the visible copy.

    The alternative — a hand-written list of questions next to the markup — goes
    stale the first time somebody edits one and not the other, and a FAQPage
    that does not match the page is exactly what structured-data spam looks like.
    """
    return [(strip_tags(q), strip_tags(a)) for q, a in FAQ_RE.findall(wrapper)]


def structured_data(lang: str, wrapper: str, page_url: str, blog_home: str) -> str:
    """A JSON-LD block for the Blogger mirror.

    Blogger gives us no head control: no meta description, no canonical, no
    hreflang (see --help). The body is the only surface we own, and JSON-LD is
    the one head-level signal that is valid inside it.
    """
    meta = META[lang]
    graph = [
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": meta["title"].split(" — ")[0],
            "description": meta["description"],
            "url": page_url or meta["canonical"],
            "sameAs": [meta["canonical"]],
            "applicationCategory": "DesignApplication",
            "operatingSystem": "Any (web browser)",
            "browserRequirements": "Requires JavaScript and HTML5 canvas",
            "inLanguage": meta["locale"],
            "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "creator": {"@type": "Organization", "name": "FlutterCook", "url": SITE},
        }
    ]

    pairs = faq_pairs(wrapper)
    if pairs:
        graph.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "inLanguage": meta["locale"],
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in pairs
            ],
        })

    if page_url:
        graph.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": meta["home"], "item": blog_home},
                {"@type": "ListItem", "position": 2, "name": meta["title"], "item": page_url},
            ],
        })

    out = []
    for node in graph:
        out.append('<script type="application/ld+json">'
                   + json.dumps(node, ensure_ascii=False, separators=(",", ":"))
                   + "</script>")
    return "".join(out)


def cross_link(lang: str, other_url: str) -> str:
    """One visible link to the other language's mirror.

    Blogger cannot emit <link rel="alternate" hreflang>, so this carries the
    hreflang on the <a> instead — a weaker signal, but a real one, and readers
    who land on the wrong language get out in one click.
    """
    if not other_url:
        return ""
    meta = META[lang]
    return (
        '<p style="font-size:14px;opacity:.8;margin:14px 0 0">'
        f'{meta["crossLead"]}: '
        f'<a href="{other_url}" hreflang="{META[OTHER[lang]]["locale"]}" '
        f'lang="{META[OTHER[lang]]["locale"]}" rel="alternate">{meta["crossLabel"]}</a>'
        "</p>"
    )


def page_urls(lang: str, blog_id: str) -> tuple[str, str, str]:
    """(this page's url, the other language's url, blog home) from the sync map."""
    pages = blog_state(load_state(), blog_id).get("pages", {})

    def url_of(key: str) -> str:
        v = pages.get(key)
        return v.get("url", "") if isinstance(v, dict) else ""

    this_url = url_of(f"screenshot-studio-{lang}")
    other_url = url_of(f"screenshot-studio-{OTHER[lang]}")
    home = re.sub(r"^(https?://[^/]+)/.*$", r"\1/", this_url or other_url or "")
    return this_url, other_url, home


def build_body(lang: str, blog_id: str = DEFAULT_BLOG_ID) -> str:
    studio = (TOOL_DIR / "studio.html").read_text("utf-8")
    if lang == "vi":
        studio = studio.replace('data-lang="en"', 'data-lang="vi"')

    wrapper = (TOOL_DIR / f"blogger-{lang}.html").read_text("utf-8")
    if "<!--STUDIO-->" not in wrapper:
        raise SystemExit(f"blogger-{lang}.html is missing its <!--STUDIO--> marker")
    body = wrapper.replace("<!--STUDIO-->", studio)

    # The theme drop-caps the first letter of the whole post body, so the
    # language link goes *after* the intro paragraph — in front of it, "Also"
    # turns into a 80px "A" floating beside the page.
    this_url, other_url, home = page_urls(lang, blog_id)
    link = cross_link(lang, other_url)
    if link:
        cut = body.find("</p>")
        body = body[:cut + 4] + link + body[cut + 4:] if cut >= 0 else link + body

    meta = META[lang]
    footer = (
        '<hr style="margin:32px 0 16px;border:0;border-top:1px solid #ddd" />'
        '<p style="font-size:14px;opacity:.75">'
        + meta["attribution"].format(url=meta["canonical"])
        + "</p>"
        + structured_data(lang, wrapper, this_url, home)
    )
    return escape_script_unicode(body + footer)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", choices=["en", "vi"], required=True)
    ap.add_argument("--blog", "--blog-id", dest="blog", default=DEFAULT_BLOG_ID,
                    help="blog id or short name: " + ", ".join(BLOG_ID_BY_NAME) +
                         f" (default: {BLOGS[DEFAULT_BLOG_ID]['name']})")
    ap.add_argument("--token-file", default=None,
                    help="(default: whichever token --blog needs)")
    ap.add_argument("--client-secret", default=None,
                    help="(default: whichever client --blog needs)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="write the payload to disk, send nothing")
    mode.add_argument("--draft", action="store_true")
    mode.add_argument("--publish", action="store_true")
    ap.add_argument("--out", default="/tmp/blogger-page-dry-run")
    args = ap.parse_args()

    blog_id, creds = resolve_blog(args.blog)
    token_file = Path(args.token_file) if args.token_file else ROOT / creds["token_file"]
    client_secret = Path(args.client_secret) if args.client_secret else ROOT / creds["client_secret"]

    body = build_body(args.lang, blog_id)
    title = META[args.lang]["title"]
    key = f"screenshot-studio-{args.lang}"

    if args.dry_run:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        dest = out / f"{key}.html"
        dest.write_text(f"<h1>{title}</h1>\n{body}", "utf-8")
        print(f"dry run -> {dest}  ({len(body):,} bytes of body)")
        return 0

    token = access_token(token_file, client_secret)
    assert_can_write(blog_id, token)

    state = load_state()
    entry = blog_state(state, blog_id)
    pages = entry.setdefault("pages", {})

    base = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/pages"
    payload = {"kind": "blogger#page", "title": title, "content": body}
    page_id = pages.get(key, {}).get("id") if isinstance(pages.get(key), dict) else pages.get(key)

    if page_id:
        res = api("PUT", f"{base}/{page_id}", token, payload)
        verb = "updated"
    else:
        url = base + ("?isDraft=true" if args.draft else "?isDraft=false")
        res = api("POST", url, token, payload)
        verb = "created"

    pages[key] = {"id": res.get("id"), "url": res.get("url", "")}
    save_state(state)

    print(f"{verb}: {title}")
    print(f"  -> {res.get('url', '(draft, no public url yet)')}  [id {res.get('id')}]")
    print(f"sync map: data/blogger_sync.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
