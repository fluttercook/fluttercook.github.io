#!/bin/bash
# Publish the Widget Preview gallery pages to Blogger mirrors.
# Blogger daily quota is ~100 creates; re-run when rate-limited.
set -euo pipefail
cd "$(dirname "$0")/.."

for BLOG in trunghieu-it flutter9; do
  echo "=== $BLOG EN ==="
  python3 scripts/publish_html_page_to_blogger.py \
    --key widget-preview/en \
    --title "Flutter Widget Preview — live Material demos" \
    --file blogger/pages/widget-preview-en.html \
    --blog "$BLOG" --publish
  echo "=== $BLOG VI ==="
  python3 scripts/publish_html_page_to_blogger.py \
    --key widget-preview/vi \
    --title "Xem trước Widget Flutter — demo Material trực tiếp" \
    --file blogger/pages/widget-preview-vi.html \
    --blog "$BLOG" --publish --cross-key widget-preview/en
done
