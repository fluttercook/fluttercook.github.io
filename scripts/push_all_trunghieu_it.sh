#!/bin/bash
# Idempotent: skips already-synced posts/pages. Safe to re-run after quota reset.
set -euo pipefail
cd "$(dirname "$0")/.."
BLOG=trunghieu-it
ARGS=()
while read -r s; do ARGS+=(--slug "$s"); done < <(python3 - <<'PY'
from pathlib import Path
for p in sorted(Path('src/content/blog').glob('*.md')):
    if 'publishDate: "2026-09-10"' in p.read_text():
        print(p.stem)
PY
)
echo "== EN posts =="
python3 scripts/publish_to_blogger.py --blog "$BLOG" --collection blog --lang en "${ARGS[@]}" --publish --skip-existing --sleep 4
echo "== VI posts =="
python3 scripts/publish_to_blogger.py --blog "$BLOG" --collection blog --lang vi "${ARGS[@]}" --publish --skip-existing --sleep 4
echo "== Widget preview pages =="
python3 scripts/publish_html_page_to_blogger.py --key widget-preview/en \
  --title "Flutter Widget Preview — live Material demos" \
  --file blogger/pages/widget-preview-en.html --blog "$BLOG" --publish
python3 scripts/publish_html_page_to_blogger.py --key widget-preview/vi \
  --title "Xem trước Widget Flutter — demo Material trực tiếp" \
  --file blogger/pages/widget-preview-vi.html --blog "$BLOG" --publish --cross-key widget-preview/en
echo "DONE"
