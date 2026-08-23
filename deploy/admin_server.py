#!/usr/bin/env python3
"""Admin dashboard and API for the FlutterCook Blogger sync.

Shows what is published where, and lets you kick off a sync run without an SSH
session. Standard library only — the content server needs Node and PyYAML for
the sync itself, and nothing more for this.

It binds to localhost by default and is meant to sit behind nginx with TLS (see
deploy/nginx.conf.example). Every /api route except /api/health requires a
bearer token, which is read from $ADMIN_TOKEN or $VAR_DIR/admin_token.

    deploy/admin_server.py                  # 127.0.0.1:8787
    deploy/admin_server.py --port 9000
    deploy/admin_server.py --host 0.0.0.0   # only behind a firewall

The dashboard holds the token in sessionStorage and sends it as an
Authorization header, so there is no cookie to forge and no CSRF surface: a
cross-site form post cannot set that header.
"""
from __future__ import annotations

import argparse
import hmac
import json
import mimetypes
import os
import secrets
import shlex
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
APP_DIR = Path(os.environ.get("APP_DIR") or HERE.parent)
VAR_DIR = Path(os.environ.get("VAR_DIR") or "/var/lib/fluttercook")
LOG_DIR = VAR_DIR / "logs"
RUNS_FILE = VAR_DIR / "runs.json"
TOKEN_FILE = VAR_DIR / "admin_token"
SYNC = HERE / "sync.sh"
MAX_RUNS = 50

# One sync at a time. Two concurrent runs would race on the sync map and on
# dist/, and Blogger would throttle them both into failure anyway.
_lock = threading.Lock()
_current: dict | None = None


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def admin_token() -> str:
    """The shared secret, minted on first use if it does not exist yet."""
    env = os.environ.get("ADMIN_TOKEN", "").strip()
    if env:
        return env
    if TOKEN_FILE.exists():
        tok = TOKEN_FILE.read_text("utf-8").strip()
        if tok:
            return tok
    tok = secrets.token_urlsafe(32)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(tok + "\n", "utf-8")
    TOKEN_FILE.chmod(0o600)
    print(f"minted a new admin token in {TOKEN_FILE}")
    return tok


def load_runs() -> list[dict]:
    try:
        return json.loads(RUNS_FILE.read_text("utf-8"))
    except (OSError, ValueError):
        return []


def save_runs(runs: list[dict]) -> None:
    RUNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = RUNS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(runs[-MAX_RUNS:], indent=2), "utf-8")
    tmp.replace(RUNS_FILE)


def record(run: dict) -> None:
    runs = [r for r in load_runs() if r["id"] != run["id"]]
    runs.append(run)
    save_runs(sorted(runs, key=lambda r: r["id"]))


def git_head() -> dict:
    def q(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=APP_DIR, capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    return {"sha": q("rev-parse", "--short", "HEAD"),
            "subject": q("log", "-1", "--format=%s"),
            "date": q("log", "-1", "--format=%cI"),
            "branch": q("rev-parse", "--abbrev-ref", "HEAD")}


def start_run(mode: str, limit: int, dry: bool, blog: str | None) -> dict:
    """Spawn sync.sh in the background, streaming its output to a log file."""
    global _current
    if not _lock.acquire(blocking=False):
        raise RuntimeError("a sync is already running")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = LOG_DIR / f"{run_id}.log"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if mode == "status":
        cmd = ["python3", str(APP_DIR / "scripts" / "blogger_status.py")]
    else:
        cmd = [str(SYNC), "--limit", str(limit)]
        if dry:
            cmd.append("--dry-run")
        if blog:
            cmd += ["--blog", blog]

    run = {"id": run_id, "mode": mode, "limit": limit, "dry": dry, "blog": blog,
           "started": now(), "finished": None, "exit": None,
           "cmd": " ".join(shlex.quote(c) for c in cmd), "log": log_path.name}
    record(run)
    _current = run

    def worker() -> None:
        global _current
        env = {**os.environ,
               "APP_DIR": str(APP_DIR), "VAR_DIR": str(VAR_DIR),
               "BLOGGER_SYNC_STATE": str(VAR_DIR / "blogger_sync.json"),
               "BLOGGER_STATUS_JSON": str(VAR_DIR / "blogger-status.json"),
               "BLOGGER_STATUS_MD": str(VAR_DIR / "blogger-status.md")}
        code = -1
        try:
            with log_path.open("w", encoding="utf-8") as log:
                log.write(f"$ {run['cmd']}\n\n")
                log.flush()
                proc = subprocess.Popen(cmd, cwd=APP_DIR, env=env, stdout=log,
                                        stderr=subprocess.STDOUT)
                code = proc.wait()
        except OSError as exc:
            log_path.write_text(f"failed to start: {exc}\n", "utf-8")
        finally:
            run["finished"], run["exit"] = now(), code
            record(run)
            _current = None
            _lock.release()

    threading.Thread(target=worker, daemon=True).start()
    return run


def status_payload() -> dict:
    """Everything the dashboard needs in one round trip."""
    report = {}
    for candidate in (VAR_DIR / "blogger-status.json", APP_DIR / "data" / "blogger-status.json"):
        try:
            report = json.loads(candidate.read_text("utf-8"))
            report["_source"] = str(candidate)
            break
        except (OSError, ValueError):
            continue

    blogs = [{k: b.get(k) for k in ("id", "name", "url", "access", "detail", "done", "total")}
             for b in report.get("blogs", [])]
    # The per-article rows are the bulk of that file; the dashboard only wants
    # the ones still waiting, so the rest never crosses the wire.
    pending = []
    for b in report.get("blogs", []):
        for p in b.get("posts", []):
            if p.get("status") == "PENDING":
                pending.append({"blog": b.get("name"), "title": p.get("title"),
                                "lang": p.get("lang"), "collection": p.get("collection"),
                                "siteUrl": p.get("siteUrl")})
    return {"generated": report.get("generated"), "articles": report.get("articles"),
            "source": report.get("_source"), "blogs": blogs,
            "pending": pending[:200], "pendingTotal": len(pending),
            "git": git_head(), "running": _current, "runs": load_runs()[-15:][::-1],
            "now": now()}


class Handler(BaseHTTPRequestHandler):
    server_version = "fluttercook-admin"

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    # -- plumbing -------------------------------------------------------
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def json(self, code: int, payload: dict | list) -> None:
        self._send(code, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def authed(self) -> bool:
        header = self.headers.get("Authorization", "")
        given = header[7:].strip() if header.lower().startswith("bearer ") else ""
        if given and hmac.compare_digest(given, admin_token()):
            return True
        # Slow down a guessing loop without holding a worker thread for long.
        time.sleep(0.5)
        self.json(401, {"error": "bad or missing token"})
        return False

    # -- routes ---------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        url = urlparse(self.path)
        route, query = url.path.rstrip("/") or "/", parse_qs(url.query)

        if route == "/api/health":
            self.json(200, {"ok": True, "running": bool(_current), "now": now()})
            return

        if route in ("/", "/index.html"):
            page = HERE / "admin" / "index.html"
            if not page.exists():
                self.json(500, {"error": f"missing {page}"})
                return
            self._send(200, page.read_bytes(), "text/html; charset=utf-8")
            return

        if not route.startswith("/api/"):
            self.json(404, {"error": "not found"})
            return
        if not self.authed():
            return

        if route == "/api/status":
            self.json(200, status_payload())
        elif route == "/api/runs":
            self.json(200, {"runs": load_runs()[::-1], "running": _current})
        elif route == "/api/log":
            run_id = (query.get("id") or [""])[0]
            # Resolve under LOG_DIR and compare, so "../../etc/passwd" cannot escape.
            path = (LOG_DIR / f"{run_id}.log").resolve()
            if not run_id or LOG_DIR.resolve() not in path.parents or not path.exists():
                self.json(404, {"error": "no such log"})
                return
            text = path.read_text("utf-8", errors="replace")
            self._send(200, text.encode(), "text/plain; charset=utf-8")
        else:
            self.json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        route = urlparse(self.path).path.rstrip("/") or "/"
        if not route.startswith("/api/"):
            self.json(404, {"error": "not found"})
            return
        if not self.authed():
            return

        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            self.json(400, {"error": "body must be JSON"})
            return

        if route not in ("/api/sync", "/api/status-refresh"):
            self.json(404, {"error": "not found"})
            return

        mode = "status" if route == "/api/status-refresh" else "sync"
        try:
            limit = max(0, min(int(body.get("limit", 3)), 100))
        except (TypeError, ValueError):
            self.json(400, {"error": "limit must be a number"})
            return
        blog = body.get("blog") or None
        if blog is not None and not isinstance(blog, str):
            self.json(400, {"error": "blog must be a string"})
            return
        # Only the three names sync.sh knows; anything else is rejected here
        # rather than becoming an argument we pass on trust.
        if blog and blog not in ("trunghieu-it", "fluttercook", "flutter9"):
            self.json(400, {"error": f"unknown blog {blog!r}"})
            return

        try:
            run = start_run(mode, limit, bool(body.get("dry")), blog)
        except RuntimeError as exc:
            self.json(409, {"error": str(exc), "running": _current})
            return
        self.json(202, {"started": run})

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=os.environ.get("ADMIN_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("ADMIN_PORT", "8787")))
    ap.add_argument("--print-token", action="store_true", help="show the token and exit")
    args = ap.parse_args()

    if args.print_token:
        print(admin_token())
        return 0

    mimetypes.init()
    token = admin_token()
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    print(f"repo    {APP_DIR}")
    print(f"state   {VAR_DIR}")
    print(f"listen  http://{args.host}:{args.port}/")
    print(f"token   {'from $ADMIN_TOKEN' if os.environ.get('ADMIN_TOKEN') else TOKEN_FILE} "
          f"({len(token)} chars)")
    if args.host not in ("127.0.0.1", "::1", "localhost"):
        print("WARNING: binding beyond localhost — put nginx and TLS in front of this.")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
