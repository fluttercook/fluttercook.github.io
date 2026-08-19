#!/usr/bin/env python3
"""Publish FlutterCook articles to a Blogger blog via the Blogger API v3.

The post body is lifted from the already-built `dist/` HTML (the `.prose`
block), so what lands on Blogger is byte-for-byte what the site renders —
including Shiki's inline-styled code blocks, which need no external CSS.

Every post gets an attribution footer linking back to the canonical
fluttercook.github.io URL, because Blogger cannot set rel=canonical per post
and we do not want the mirror outranking the original.

A slug -> postId map is kept in data/blogger_sync.json so re-runs UPDATE the
existing Blogger post instead of creating a duplicate.

Auth: needs a token with scope https://www.googleapis.com/auth/blogger,
supplied via $BLOGGER_ACCESS_TOKEN or `gcloud auth print-access-token`.
The Blogger API must be enabled on the quota project.

Examples:
    # See exactly what would be sent, without touching the network:
    python3 scripts/publish_to_blogger.py --collection blog --lang vi --all --dry-run

    # Create drafts (safe: nothing goes public until you hit Publish in Blogger)
    python3 scripts/publish_to_blogger.py --collection blog --lang vi --all --draft

    # Go live
    python3 scripts/publish_to_blogger.py --collection news --lang vi --all --publish
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
STATE_FILE = ROOT / "data" / "blogger_sync.json"
SITE = "https://fluttercook.github.io"
DEFAULT_BLOG_ID = "8621533667729504576"  # trunghieu-it.blogspot.com

# collection -> (content dir, dist path prefix, site path prefix)
LAYOUT = {
    ("news", "en"): ("src/content/news", "news", "/news"),
    ("news", "vi"): ("src/content/news-vi", "vi/news", "/vi/news"),
    ("blog", "en"): ("src/content/blog", "blog", "/blog"),
    ("blog", "vi"): ("src/content/blog-vi", "vi/blog", "/vi/blog"),
}

FOOTER = {
    "en": (
        '<p><i>Originally published on <a href="{url}">FlutterCook</a>. '
        'Read the latest version there — that copy is the one kept up to date.</i></p>'
    ),
    "vi": (
        '<p><i>Bài viết gốc đăng tại <a href="{url}">FlutterCook</a>. '
        'Bản trên đó là bản được cập nhật mới nhất.</i></p>'
    ),
}


def read_frontmatter(md_path: Path) -> dict:
    text = md_path.read_text("utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit(f"{md_path}: no YAML frontmatter")
    return yaml.safe_load(m.group(1)) or {}


def extract_prose(html_path: Path) -> str:
    """Pull the <div class="prose"> subtree out of a built page."""
    html = html_path.read_text("utf-8")
    m = re.search(r'<div class="prose">', html)
    if not m:
        raise SystemExit(f"{html_path}: no .prose block — did you run `npm run build`?")
    start = m.end()
    i, depth = start, 1
    while depth > 0:
        nxt = re.search(r"<(/?)div\b", html[i:])
        if not nxt:
            raise SystemExit(f"{html_path}: unbalanced divs in .prose")
        i += nxt.end()
        depth += -1 if nxt.group(1) == "/" else 1
    return html[start : i - len("</div")].strip()


def absolutize(html: str) -> str:
    """Site-relative hrefs/srcs must become absolute once the HTML leaves the site."""
    html = re.sub(r'href="/(?!/)', f'href="{SITE}/', html)
    html = re.sub(r'src="/(?!/)', f'src="{SITE}/', html)
    return html


def build_post(collection: str, lang: str, slug: str) -> dict:
    content_dir, dist_prefix, site_prefix = LAYOUT[(collection, lang)]
    md_path = ROOT / content_dir / f"{slug}.md"
    html_path = DIST / dist_prefix / slug / "index.html"
    if not md_path.exists():
        raise SystemExit(f"missing source: {md_path}")
    if not html_path.exists():
        raise SystemExit(f"missing build output: {html_path} — run `npm run build` first")

    fm = read_frontmatter(md_path)
    canonical = f"{SITE}{site_prefix}/{slug}/"
    body = absolutize(extract_prose(html_path))
    content = f"{body}\n<hr />\n{FOOTER[lang].format(url=canonical)}"

    labels = list(fm.get("tags") or [])
    if collection == "blog":
        labels.append("Tutorial" if lang == "en" else "Hướng dẫn")
    # Blogger caps labels at 20 per post.
    labels = list(dict.fromkeys(labels))[:20]

    return {
        "kind": "blogger#post",
        "title": fm["title"],
        "content": content,
        "labels": labels,
    }


def refresh_token(token_file: Path, client_secret_file: Path) -> str:
    """Exchange a stored refresh token for a fresh access token."""
    tok = json.loads(token_file.read_text("utf-8"))
    if "refresh_token" not in tok:
        raise SystemExit(f"{token_file}: no refresh_token")
    client_id, client_secret = tok.get("client_id"), tok.get("client_secret")
    if not (client_id and client_secret):
        cs = json.loads(client_secret_file.read_text("utf-8"))
        inst = cs.get("installed") or cs.get("web") or {}
        client_id = client_id or inst.get("client_id")
        client_secret = client_secret or inst.get("client_secret")
    body = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    try:
        with urllib.request.urlopen(
            urllib.request.Request("https://oauth2.googleapis.com/token", data=body), timeout=60
        ) as resp:
            return json.loads(resp.read())["access_token"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        if "invalid_grant" in detail:
            raise SystemExit(
                f"{token_file.name}: the refresh token is dead (revoked or expired).\n"
                "Re-authorize that Google account through the OAuth consent flow to mint a new one."
            )
        raise SystemExit(f"token refresh failed: HTTP {exc.code}\n{detail}")


def access_token(token_file: Path | None, client_secret_file: Path) -> str:
    tok = os.environ.get("BLOGGER_ACCESS_TOKEN")
    if tok:
        return tok.strip()
    if token_file and token_file.exists():
        return refresh_token(token_file, client_secret_file)
    try:
        out = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True, timeout=60, check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"could not obtain a token via gcloud: {exc}")
    return out.stdout.strip()


def assert_can_write(blog_id: str, token: str) -> None:
    """Listing drafts needs author rights, so it is a safe write-permission probe."""
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?status=draft&maxResults=1"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        urllib.request.urlopen(req, timeout=60).read()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise SystemExit(
                f"no author rights on blog {blog_id} (HTTP {exc.code}).\n"
                "The signed-in Google account must be an Author or Admin on that blog:\n"
                "  Blogger -> Settings -> Permissions -> Blog admins and authors -> Invite,\n"
                "or authorize the account that already owns the blog and pass its --token-file."
            )
        raise SystemExit(f"permission probe failed: HTTP {exc.code}\n{exc.read().decode('utf-8','replace')}")


def api(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        if exc.code == 403 and "insufficient authentication scopes" in detail:
            raise SystemExit(
                "403: the token lacks the Blogger scope. Re-authenticate with:\n"
                "  gcloud auth application-default login --scopes="
                "openid,https://www.googleapis.com/auth/blogger,"
                "https://www.googleapis.com/auth/cloud-platform\n"
                "then export BLOGGER_ACCESS_TOKEN=$(gcloud auth application-default print-access-token)"
            )
        raise SystemExit(f"{method} {url} -> HTTP {exc.code}\n{detail}")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text("utf-8"))
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", "utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--collection", choices=["news", "blog"], required=True)
    ap.add_argument("--lang", choices=["en", "vi"], required=True)
    ap.add_argument("--slug", action="append", default=[], help="repeatable; omit with --all")
    ap.add_argument("--all", action="store_true", help="every non-draft entry in the collection")
    ap.add_argument("--blog-id", default=DEFAULT_BLOG_ID)
    ap.add_argument("--token-file", default=str(ROOT / ".app_dist" / "token_fluttercook.json"),
                    help="OAuth token JSON with a refresh_token and the blogger scope")
    ap.add_argument("--client-secret", default=str(ROOT / ".app_dist" / "client_secret.json"),
                    help="OAuth desktop client JSON, used to refresh the token")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="write the payloads to disk, send nothing")
    mode.add_argument("--draft", action="store_true", help="create/update as an unpublished draft")
    mode.add_argument("--publish", action="store_true", help="create/update as a live post")
    ap.add_argument("--out", default="/tmp/blogger-dry-run", help="where --dry-run writes previews")
    args = ap.parse_args()

    content_dir = ROOT / LAYOUT[(args.collection, args.lang)][0]
    if args.all:
        slugs = sorted(
            p.stem for p in content_dir.glob("*.md")
            if not (read_frontmatter(p).get("draft") or False)
        )
    elif args.slug:
        slugs = args.slug
    else:
        raise SystemExit("pass --slug SLUG (repeatable) or --all")

    posts = [(s, build_post(args.collection, args.lang, s)) for s in slugs]

    if args.dry_run:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for slug, post in posts:
            (out / f"{slug}.html").write_text(
                f"<h1>{post['title']}</h1>\n<!-- labels: {', '.join(post['labels'])} -->\n{post['content']}",
                "utf-8",
            )
            print(f"[dry-run] {slug}: {len(post['content']):,} bytes, labels={post['labels']}")
        print(f"\n{len(posts)} post(s) written to {out}/ — nothing was sent to Blogger.")
        return 0

    token = access_token(Path(args.token_file), Path(args.client_secret))
    assert_can_write(args.blog_id, token)
    state = load_state()
    key_prefix = f"{args.collection}/{args.lang}/"
    base = f"https://www.googleapis.com/blogger/v3/blogs/{args.blog_id}/posts"

    for slug, post in posts:
        key = key_prefix + slug
        existing = state.get(key, {}).get("postId")
        if existing:
            url = f"{base}/{existing}?" + urllib.parse.urlencode({"publish": str(bool(args.publish)).lower()})
            result = api("PUT", url, token, post)
            action = "updated"
        else:
            url = f"{base}?" + urllib.parse.urlencode({"isDraft": str(bool(args.draft)).lower()})
            result = api("POST", url, token, post)
            action = "created"
        state[key] = {"postId": result["id"], "url": result.get("url", ""), "title": post["title"]}
        save_state(state)
        print(f"{action}: {post['title']}\n  -> {result.get('url') or '(draft)'}  [id {result['id']}]")

    print(f"\n{len(posts)} post(s) {'published' if args.publish else 'saved as draft'} on blog {args.blog_id}.")
    print(f"sync map: {STATE_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
