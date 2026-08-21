#!/usr/bin/env python3
"""Publish a plain HTML fragment to a Blogger blog as a *page* (not a post).

publish_page_to_blogger.py does the same job but its body is assembled from the
Screenshot Studio sources and is hard-wired to that tool. This one takes any
file under blogger/pages/ and pushes it, which is what standing pages (privacy,
terms, about) need.

Page ids are recorded in data/blogger_sync.json under blogs.<id>.pages, keyed by
the --key you pass, so a re-run UPDATES in place instead of creating a second
copy. Keep the key stable.

If the file contains the literal `__CROSS_URL__`, it is replaced with the public
URL of the page published under --cross-key (read from the sync map). Publish
the other language first, or run this twice — the second run fills it in.

Only `title` and `content` exist in the Blogger page API. A search description
(customMetaData / metaDescription) is accepted and silently dropped, and there
is no theme API, so anything else has to be set by hand in the Blogger UI.

Examples:
    python3 scripts/publish_html_page_to_blogger.py --key privacy/vi \
        --title "Chính sách quyền riêng tư" --file blogger/pages/privacy-vi.html --dry-run

    python3 scripts/publish_html_page_to_blogger.py --key privacy/vi \
        --title "Chính sách quyền riêng tư" --file blogger/pages/privacy-vi.html \
        --cross-key privacy/en --blog trunghieu-it --publish
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from publish_to_blogger import (  # noqa: E402  (path shim has to come first)
    BLOG_ID_BY_NAME,
    BLOGS,
    DEFAULT_BLOG_ID,
    ROOT,
    access_token,
    api,
    assert_can_write,
    blog_state,
    load_state,
    resolve_blog,
    save_state,
)

CROSS_MARKER = "__CROSS_URL__"


def page_url(blog_id: str, key: str) -> str:
    """Public URL of an already-published page, from the sync map ('' if unknown)."""
    rec = blog_state(load_state(), blog_id).get("pages", {}).get(key)
    if isinstance(rec, dict):
        return rec.get("url", "")
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--key", required=True, help="stable sync-map key, e.g. privacy/vi")
    ap.add_argument("--title", required=True)
    ap.add_argument("--file", required=True, help="HTML fragment, relative to the repo root")
    ap.add_argument("--cross-key", help="sync-map key whose URL replaces __CROSS_URL__")
    ap.add_argument("--blog", "--blog-id", dest="blog", default=DEFAULT_BLOG_ID,
                    help="blog id or short name: " + ", ".join(BLOG_ID_BY_NAME) +
                         f" (default: {BLOGS[DEFAULT_BLOG_ID]['name']})")
    ap.add_argument("--token-file", default=None,
                    help="(default: whichever token --blog needs)")
    ap.add_argument("--client-secret", default=None,
                    help="(default: whichever client --blog needs)")
    ap.add_argument("--draft", action="store_true", help="create as a draft (new pages only)")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--publish", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    blog_id, creds = resolve_blog(args.blog)
    token_file = Path(args.token_file) if args.token_file else ROOT / creds["token_file"]
    client_secret = Path(args.client_secret) if args.client_secret else ROOT / creds["client_secret"]

    src = Path(args.file)
    if not src.is_absolute():
        src = ROOT / src
    body = src.read_text("utf-8").strip()

    if CROSS_MARKER in body:
        cross = page_url(blog_id, args.cross_key) if args.cross_key else ""
        if cross:
            body = body.replace(CROSS_MARKER, cross)
        else:
            # No sibling page yet. Drop the whole paragraph rather than ship a
            # dead link — re-running after the sibling exists puts it back.
            body = "\n".join(l for l in body.splitlines() if CROSS_MARKER not in l).strip()
            print(f"  note: no URL for --cross-key {args.cross_key!r} yet; cross-link line dropped")

    if args.dry_run:
        print(f"dry run: {args.title}")
        print(f"  key {args.key}  blog {blog_id}  {len(body):,} bytes of body")
        print(f"  existing: {page_url(blog_id, args.key) or '(new page)'}")
        return 0

    token = access_token(token_file, client_secret)
    assert_can_write(blog_id, token)

    state = load_state()
    entry = blog_state(state, blog_id)
    pages = entry.setdefault("pages", {})

    base = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/pages"
    payload = {"kind": "blogger#page", "title": args.title, "content": body}
    rec = pages.get(args.key)
    page_id = rec.get("id") if isinstance(rec, dict) else rec

    if page_id:
        res = api("PUT", f"{base}/{page_id}", token, payload)
        verb = "updated"
    else:
        res = api("POST", base + ("?isDraft=true" if args.draft else "?isDraft=false"), token, payload)
        verb = "created"

    pages[args.key] = {"id": res.get("id"), "url": res.get("url", "")}
    save_state(state)

    print(f"{verb}: {args.title}")
    print(f"  -> {res.get('url') or '(draft, no public url yet)'}  [id {res.get('id')}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
