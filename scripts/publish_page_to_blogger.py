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

Examples:
    python3 scripts/publish_page_to_blogger.py --lang en --dry-run
    python3 scripts/publish_page_to_blogger.py --lang vi --blog-id 8621533667729504576 \
        --token-file .app_dist/trunghieu-it/token.json \
        --client-secret .app_dist/trunghieu-it/client_secret.json --publish
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from publish_to_blogger import (  # noqa: E402  (path shim has to come first)
    DEFAULT_BLOG_ID,
    ROOT,
    SITE,
    access_token,
    api,
    assert_can_write,
    blog_state,
    load_state,
    save_state,
)

TOOL_DIR = ROOT / "tools" / "screenshot-studio"

META = {
    "en": {
        "title": "App Store Screenshot Generator — free, in your browser",
        "canonical": f"{SITE}/tools/screenshot-studio/",
        "attribution": (
            'This tool is maintained at <a href="{url}">{url}</a> — '
            "the version there is always the newest."
        ),
    },
    "vi": {
        "title": "Tạo ảnh chụp màn hình App Store — miễn phí, ngay trên trình duyệt",
        "canonical": f"{SITE}/vi/tools/screenshot-studio/",
        "attribution": (
            'Công cụ này được duy trì tại <a href="{url}">{url}</a> — '
            "bản ở đó luôn là bản mới nhất."
        ),
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


def build_body(lang: str) -> str:
    studio = (TOOL_DIR / "studio.html").read_text("utf-8")
    if lang == "vi":
        studio = studio.replace('data-lang="en"', 'data-lang="vi"')

    wrapper = (TOOL_DIR / f"blogger-{lang}.html").read_text("utf-8")
    if "<!--STUDIO-->" not in wrapper:
        raise SystemExit(f"blogger-{lang}.html is missing its <!--STUDIO--> marker")
    body = wrapper.replace("<!--STUDIO-->", studio)

    meta = META[lang]
    footer = (
        '<hr style="margin:32px 0 16px;border:0;border-top:1px solid #ddd" />'
        '<p style="font-size:14px;opacity:.75">'
        + meta["attribution"].format(url=meta["canonical"])
        + "</p>"
    )
    return escape_script_unicode(body + footer)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", choices=["en", "vi"], required=True)
    ap.add_argument("--blog-id", default=DEFAULT_BLOG_ID)
    ap.add_argument("--token-file", default=str(ROOT / ".app_dist" / "token_fluttercook.json"))
    ap.add_argument("--client-secret", default=str(ROOT / ".app_dist" / "client_secret.json"))
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="write the payload to disk, send nothing")
    mode.add_argument("--draft", action="store_true")
    mode.add_argument("--publish", action="store_true")
    ap.add_argument("--out", default="/tmp/blogger-page-dry-run")
    args = ap.parse_args()

    body = build_body(args.lang)
    title = META[args.lang]["title"]
    key = f"screenshot-studio-{args.lang}"

    if args.dry_run:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        dest = out / f"{key}.html"
        dest.write_text(f"<h1>{title}</h1>\n{body}", "utf-8")
        print(f"dry run -> {dest}  ({len(body):,} bytes of body)")
        return 0

    token_file = Path(args.token_file)
    token = access_token(token_file if token_file.exists() else None, Path(args.client_secret))
    assert_can_write(args.blog_id, token)

    state = load_state()
    entry = blog_state(state, args.blog_id)
    pages = entry.setdefault("pages", {})

    base = f"https://www.googleapis.com/blogger/v3/blogs/{args.blog_id}/pages"
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
