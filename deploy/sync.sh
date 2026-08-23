#!/usr/bin/env bash
#
# One sync run: bring the checkout up to date, rebuild the site, and mirror any
# articles that are not yet on each Blogger blog.
#
# Meant for cron/systemd on the content server, but it is an ordinary script —
# run it by hand any time. Everything it writes that is not the build output
# lands in $VAR_DIR, outside the checkout, so step 1 can hard-reset the repo
# without destroying the slug -> postId map.
#
#   deploy/sync.sh                 # normal run, honours SYNC_LIMIT
#   deploy/sync.sh --dry-run       # build and render payloads, send nothing
#   deploy/sync.sh --no-pull       # use the working tree as-is
#   deploy/sync.sh --limit 10      # override SYNC_LIMIT for this run
#   deploy/sync.sh --blog flutter9 # one blog instead of all of them
#
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_APP_DIR="$(dirname "$HERE")"

# Config comes from the environment, an env file, or these defaults — in that
# order of precedence, so systemd can set one thing without restating the rest.
for f in /etc/fluttercook/sync.env "$HERE/.env"; do
  # shellcheck disable=SC1090
  [ -f "$f" ] && . "$f"
done

APP_DIR="${APP_DIR:-$DEFAULT_APP_DIR}"
VAR_DIR="${VAR_DIR:-/var/lib/fluttercook}"
BRANCH="${BRANCH:-main}"
SYNC_LIMIT="${SYNC_LIMIT:-3}"
SYNC_SLEEP="${SYNC_SLEEP:-6}"
SYNC_BLOGS="${SYNC_BLOGS:-trunghieu-it fluttercook flutter9}"
SYNC_COLLECTIONS="${SYNC_COLLECTIONS:-blog news}"
SYNC_LANGS="${SYNC_LANGS:-en vi}"

PULL=1
DRY=""
# --dry-run and --publish are mutually exclusive on the publisher, so this is
# one flag with two values rather than a flag plus a modifier.
MODE="--publish"
ONE_BLOG=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)  DRY=1; MODE="--dry-run"; shift ;;
    --no-pull)  PULL=0; shift ;;
    --limit)    SYNC_LIMIT="$2"; shift 2 ;;
    --blog)     ONE_BLOG="$2"; shift 2 ;;
    -h|--help)  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)          echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[ -n "$ONE_BLOG" ] && SYNC_BLOGS="$ONE_BLOG"

# The sync map and the status reports live here, not in the repo. Losing the map
# means the next run cannot find the posts it already made and creates a second
# copy of every article, so this separation is the point of the whole layout.
export BLOGGER_SYNC_STATE="${BLOGGER_SYNC_STATE:-$VAR_DIR/blogger_sync.json}"
export BLOGGER_STATUS_JSON="${BLOGGER_STATUS_JSON:-$VAR_DIR/blogger-status.json}"
export BLOGGER_STATUS_MD="${BLOGGER_STATUS_MD:-$VAR_DIR/blogger-status.md}"
mkdir -p "$VAR_DIR" "$VAR_DIR/logs"

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
say "sync starting $started"
echo "    repo   $APP_DIR (branch $BRANCH)"
echo "    state  $VAR_DIR"
echo "    limit  ${SYNC_LIMIT} post(s) per blog/collection/lang${DRY:+  [DRY RUN]}"

cd "$APP_DIR" || { echo "no such directory: $APP_DIR" >&2; exit 1; }

# The publish step needs the built HTML, and the credentials are not in git.
if [ ! -d .app_dist ]; then
  echo "FATAL: $APP_DIR/.app_dist is missing — copy the OAuth token files there." >&2
  echo "       See deploy/README.md, 'Credentials'." >&2
  exit 1
fi

if [ "$PULL" = 1 ]; then
  say "updating checkout"
  git fetch --quiet origin "$BRANCH" || { echo "git fetch failed" >&2; exit 1; }
  before=$(git rev-parse HEAD)
  # Hard reset rather than pull: the build writes into the tree and a merge
  # conflict at 3am is worse than discarding local edits on a mirror checkout.
  git reset --hard "origin/$BRANCH" --quiet || exit 1
  after=$(git rev-parse HEAD)
  if [ "$before" = "$after" ]; then
    echo "    already at $(git log -1 --format='%h %s')"
  else
    echo "    $before -> $after"
    git --no-pager log --oneline "$before..$after" | sed 's/^/      /'
  fi
fi

say "installing dependencies"
if [ ! -d node_modules ] || [ package-lock.json -nt node_modules ]; then
  npm ci --no-audit --no-fund || { echo "npm ci failed" >&2; exit 1; }
else
  echo "    node_modules is current, skipping npm ci"
fi

say "building the site"
npm run build || { echo "astro build failed — not publishing a stale dist/" >&2; exit 1; }
pages=$(find dist -name '*.html' | wc -l | tr -d ' ')
echo "    $pages page(s) in dist/"

say "mirroring to Blogger"
failed=()
attempted=0
for blog in $SYNC_BLOGS; do
  for collection in $SYNC_COLLECTIONS; do
    for lang in $SYNC_LANGS; do
      attempted=$((attempted + 1))
      printf '\n--- %s / %s / %s ---\n' "$blog" "$collection" "$lang"
      # A blog we lack rights on must not abort the other five targets, so each
      # combination is judged on its own and reported in the summary below.
      if ! python3 scripts/publish_to_blogger.py \
             --blog "$blog" --collection "$collection" --lang "$lang" \
             --all "$MODE" --skip-existing \
             --limit "$SYNC_LIMIT" --sleep "$SYNC_SLEEP"; then
        failed+=("$blog/$collection/$lang")
      fi
    done
  done
done

say "refreshing status report"
python3 scripts/blogger_status.py || echo "    status probe failed (report may be stale)"

say "summary"
echo "    started  $started"
echo "    finished $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "    targets  $attempted attempted, ${#failed[@]} failed"
if [ ${#failed[@]} -gt 0 ]; then
  printf '    failed:  %s\n' "${failed[*]}"
fi

# A single blocked blog is the expected steady state while a role is still being
# granted, so it is a warning. Everything failing means credentials or network,
# which is worth waking someone for.
if [ ${#failed[@]} -ge "$attempted" ] && [ "$attempted" -gt 0 ]; then
  echo "    every target failed — check credentials and connectivity" >&2
  exit 1
fi
exit 0
