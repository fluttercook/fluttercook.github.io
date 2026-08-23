#!/usr/bin/env python3
"""Report which FlutterCook articles have landed on which Blogger blog.

Reads the article inventory straight from src/content/, cross-references
data/blogger_sync.json (written by publish_to_blogger.py), and — unless
--offline — asks each blog's API whether our credentials can actually write
there and which of our posts already exist.

Writes a machine-readable data/blogger-status.json and a human-readable
docs/blogger-status.md, and prints a short summary.

    python3 scripts/blogger_status.py            # probe the API, refresh both files
    python3 scripts/blogger_status.py --offline  # no network, state file only
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish_to_blogger import (  # noqa: E402
    BLOGS as BLOG_CREDENTIALS,
    LAYOUT,
    ROOT,
    STATE_FILE,
    load_state,
    read_frontmatter,
    refresh_token,
    rel,
)

# Overridable for the same reason STATE_FILE is: the deployment writes its
# reports outside the checkout, which it resets to origin/main on every run.
REPORT_JSON = Path(os.environ.get("BLOGGER_STATUS_JSON") or ROOT / "data" / "blogger-status.json")
REPORT_MD = Path(os.environ.get("BLOGGER_STATUS_MD") or ROOT / "docs" / "blogger-status.md")

# The blogs we mirror to, in priority order. Credentials live in the single table
# in publish_to_blogger.py — the two scripts kept their own copies and drifted, so
# only the reporting extras stay here. Everything else is derived from the short
# name, which is also the blogspot subdomain.
EXTRAS = {
    "8621533667729504576": {"priority": 1, "api_key_file": ".app_dist/trunghieu-it/api_key.txt"},
    "2374794397032110467": {"priority": 2},
    "954315885651943515": {"priority": 3},
}
BLOGS = [
    {
        "id": blog_id,
        "name": f"{BLOG_CREDENTIALS[blog_id]['name']}.blogspot.com",
        "url": f"https://{BLOG_CREDENTIALS[blog_id]['name']}.blogspot.com/",
        "token_file": BLOG_CREDENTIALS[blog_id]["token_file"],
        "client_secret": BLOG_CREDENTIALS[blog_id]["client_secret"],
        **extras,
    }
    for blog_id, extras in sorted(EXTRAS.items(), key=lambda kv: kv[1]["priority"])
]


def inventory(collections: tuple[str, ...]) -> list[dict]:
    """Every publishable article, as {key, collection, lang, slug, title, date}."""
    items = []
    for (collection, lang), (content_dir, _, site_prefix) in LAYOUT.items():
        if collection not in collections:
            continue
        for md in sorted((ROOT / content_dir).glob("*.md")):
            fm = read_frontmatter(md)
            if fm.get("draft"):
                continue
            items.append({
                "key": f"{collection}/{lang}/{md.stem}",
                "collection": collection,
                "lang": lang,
                "slug": md.stem,
                "title": fm.get("title", md.stem),
                "publishDate": str(fm.get("publishDate", "")),
                "siteUrl": f"https://fluttercook.github.io{site_prefix}/{md.stem}/",
            })
    return sorted(items, key=lambda i: (i["collection"], i["lang"], i["publishDate"]))


def get(url: str, token: str) -> tuple[int, dict]:
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        exc.read()
        return exc.code, {}
    except OSError:
        return 0, {}


def list_posts_with_key(blog: dict) -> dict:
    """Read a public blog with an API key. Keys can never write — reads only."""
    key = (ROOT / blog["api_key_file"]).read_text("utf-8").strip()
    titles, page = {}, None
    while True:
        params = {"key": key, "maxResults": "100", "fetchBodies": "false"}
        if page:
            params["pageToken"] = page
        code, data = get(
            f"https://blogger.googleapis.com/v3/blogs/{blog['id']}/posts?" + urllib.parse.urlencode(params),
            token="",
        )
        if code != 200:
            break
        for post in data.get("items", []):
            titles[post.get("title", "").strip()] = {"id": post.get("id", ""), "url": post.get("url", "")}
        page = data.get("nextPageToken")
        if not page:
            break
    return titles


def probe(blog: dict) -> dict:
    """Can we write to this blog, and what of ours is already on it?"""
    token_file = ROOT / blog["token_file"]
    if not token_file.exists():
        if blog.get("api_key_file") and (ROOT / blog["api_key_file"]).exists():
            titles = list_posts_with_key(blog)
            return {
                "access": "read-only-key",
                "detail": f"API key reads {len(titles)} public post(s); keys cannot write — "
                          f"needs an Admin OAuth token",
                "titles": titles,
            }
        return {"access": "no-credentials", "detail": f"missing {blog['token_file']}", "titles": {}}
    try:
        token = refresh_token(token_file, ROOT / blog["client_secret"])
    except SystemExit as exc:
        return {"access": "token-dead", "detail": str(exc).splitlines()[0], "titles": {}}

    code, _ = get(
        f"https://www.googleapis.com/blogger/v3/blogs/{blog['id']}/posts?status=draft&maxResults=1",
        token,
    )
    if code in (401, 403):
        return {"access": "forbidden", "detail": f"HTTP {code} — account is not an Author/Admin", "titles": {}}
    if code != 200:
        return {"access": "unknown", "detail": f"HTTP {code}", "titles": {}}

    # Reading drafts only proves Author rights, and an Author gets 403 on posts.insert —
    # creating posts through the API needs Admin. Check the role before claiming we can publish.
    role = "?"
    code, data = get("https://www.googleapis.com/blogger/v3/users/self/blogs?fetchUserInfo=true", token)
    for info in data.get("blogUserInfos", []):
        if info.get("blog", {}).get("id") == blog["id"]:
            role = info.get("blog_user_info", {}).get("role", "?")
    access = "ok" if role == "ADMIN" else "author-cannot-create"

    # Index live posts by title so we can spot posts made outside our sync map.
    titles, page, partial = {}, None, False
    while True:
        params = {"maxResults": "100", "fetchBodies": "false"}
        if page:
            params["pageToken"] = page
        code, data = get(
            f"https://www.googleapis.com/blogger/v3/blogs/{blog['id']}/posts?" + urllib.parse.urlencode(params),
            token,
        )
        if code != 200:
            # One throttled page used to end the loop quietly, and a count that
            # stopped at a round 100 read like a real total — enough to look
            # like posts had appeared out of nowhere on the next run. Say so.
            partial = True
            break
        for post in data.get("items", []):
            titles[post.get("title", "").strip()] = {"id": post.get("id", ""), "url": post.get("url", "")}
        page = data.get("nextPageToken")
        if not page:
            break
    detail = f"role {role}, {'at least ' if partial else ''}{len(titles)} post(s) live"
    if partial:
        detail += " (listing was cut short)"
    if access != "ok":
        detail += " — needs Admin to create new posts"
    return {"access": access, "detail": detail, "titles": titles}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip API probes; report from the sync map only")
    ap.add_argument("--adopt", action="store_true",
                    help="claim posts that already exist on a blog under our title, so later runs "
                         "update them instead of creating duplicates")
    ap.add_argument("--include-recipes", action="store_true",
                    help="also track the 1,000 recipe pages (off by default: at Blogger's ~100 "
                         "posts/day they are a multi-day job, and they would drown the report)")
    args = ap.parse_args()

    articles = inventory(("news", "blog", "recipes") if args.include_recipes else ("news", "blog"))
    state = load_state()
    adopted = 0
    today = dt.date.today().isoformat()

    report = {"generated": today, "articles": len(articles), "blogs": []}
    for blog in BLOGS:
        info = ({"access": "not-probed", "detail": "--offline", "titles": {}}
                if args.offline else probe(blog))
        synced = state.get("blogs", {}).get(blog["id"], {}).get("posts", {})
        rows, done = [], 0
        for art in articles:
            rec = synced.get(art["key"])
            live = info["titles"].get(art["title"].strip())
            if rec:
                status, url = rec.get("status", "LIVE"), rec.get("url", "")
            elif live:
                status, url = "LIVE-UNTRACKED", live["url"]
                if args.adopt:
                    state.setdefault("blogs", {}).setdefault(blog["id"], {}).setdefault("posts", {})[art["key"]] = {
                        "postId": live["id"], "url": live["url"], "title": art["title"],
                        "status": "LIVE", "adopted": today,
                        # Written by an older toolchain: often EN+VI in one post, so a
                        # single-language update would destroy half of it.
                        "legacy": True,
                    }
                    status, adopted = "LIVE", adopted + 1
            elif info["access"] in ("forbidden", "token-dead", "no-credentials", "author-cannot-create", "read-only-key"):
                status, url = "BLOCKED", ""
            else:
                status, url = "PENDING", ""
            if status.startswith("LIVE"):
                done += 1
            rows.append({**art, "status": status, "blogUrl": url})
        report["blogs"].append({
            "id": blog["id"], "name": blog["name"], "url": blog["url"],
            "priority": blog["priority"], "access": info["access"], "detail": info["detail"],
            "done": done, "total": len(articles), "posts": rows,
        })

    if adopted:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", "utf-8")
        print(f"adopted {adopted} existing post(s) into {rel(STATE_FILE)}\n")

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", "utf-8")

    icon = {"ok": "🟢", "forbidden": "🔴", "token-dead": "🔴", "no-credentials": "⚪",
            "author-cannot-create": "🟠", "read-only-key": "🟠", "unknown": "🟡", "not-probed": "⚪"}
    md = [
        "# Blogger publish status",
        "",
        f"_Generated {today} by `scripts/blogger_status.py`. Source of truth for post ids: "
        f"`{rel(STATE_FILE)}`._",
        "",
        f"**{len(articles)} publishable articles** on the site "
        f"({sum(1 for a in articles if a['collection'] == 'news')} news, "
        f"{sum(1 for a in articles if a['collection'] == 'blog')} blog).",
        "",
        "| Blog | Access | Published | Note |",
        "|---|---|---|---|",
    ]
    for b in report["blogs"]:
        md.append(f"| [{b['name']}]({b['url']}) | {icon.get(b['access'], '?')} {b['access']} | "
                  f"{b['done']}/{b['total']} | {b['detail']} |")
    md += ["", "Status values: **LIVE** synced by us · **LIVE-UNTRACKED** exists on the blog but not in our "
           "sync map · **PENDING** ready to publish · **BLOCKED** no write access yet.", ""]

    for b in report["blogs"]:
        md += [f"## {b['name']}", "",
               f"Blog id `{b['id']}` · access **{b['access']}** ({b['detail']}) · {b['done']}/{b['total']} published.",
               "", "| # | Article | Lang | Type | Status | On blog |", "|---:|---|---|---|---|---|"]
        for n, p in enumerate(b["posts"], 1):
            link = f"[open]({p['blogUrl']})" if p["blogUrl"] else "—"
            md.append(f"| {n} | [{p['title']}]({p['siteUrl']}) | {p['lang']} | {p['collection']} | "
                      f"{p['status']} | {link} |")
        md.append("")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(md), "utf-8")

    print(f"{len(articles)} articles\n")
    for b in report["blogs"]:
        print(f"  {icon.get(b['access'], '?')} {b['name']:<28} {b['done']:>3}/{b['total']:<3} "
              f"{b['access']} — {b['detail']}")
    print(f"\nwrote {rel(REPORT_MD)} and {rel(REPORT_JSON)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
