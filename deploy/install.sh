#!/usr/bin/env bash
#
# Provision the sync + admin service on a Debian/Ubuntu box. Idempotent: run it
# again after a change and it updates what moved, leaving credentials and the
# sync map alone.
#
#   sudo bash deploy/install.sh
#   sudo bash deploy/install.sh --host jo.fighttech.vn --dir /opt/fluttercook
#
# It deliberately stops short of two things, because both are outward-facing and
# should be a human decision: it does not request a TLS certificate, and it does
# not start a sync. It prints the commands for both at the end.
#
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/fluttercook/fluttercook.github.io.git}"
APP_DIR="${APP_DIR:-/opt/fluttercook}"
VAR_DIR="${VAR_DIR:-/var/lib/fluttercook}"
ETC_DIR="/etc/fluttercook"
SVC_USER="${SVC_USER:-fluttercook}"
ADMIN_HOST="${ADMIN_HOST_NAME:-jo.fighttech.vn}"
BRANCH="${BRANCH:-main}"

while [ $# -gt 0 ]; do
  case "$1" in
    --host) ADMIN_HOST="$2"; shift 2 ;;
    --dir)  APP_DIR="$2"; shift 2 ;;
    --repo) REPO_URL="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    -h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

[ "$(id -u)" -eq 0 ] || { echo "run this with sudo." >&2; exit 1; }
step() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

step "packages"
apt-get update -qq
apt-get install -y -qq git curl nginx python3 python3-yaml ca-certificates
if ! command -v node >/dev/null 2>&1; then
  echo "    installing Node.js 22 from NodeSource"
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  apt-get install -y -qq nodejs
fi
echo "    node $(node --version), npm $(npm --version), python $(python3 --version | cut -d' ' -f2)"

step "service account"
if ! id "$SVC_USER" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "/home/$SVC_USER" --shell /usr/sbin/nologin "$SVC_USER"
  echo "    created $SVC_USER"
else
  echo "    $SVC_USER exists"
fi

step "checkout at $APP_DIR"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch --quiet origin "$BRANCH"
  git -C "$APP_DIR" reset --hard "origin/$BRANCH" --quiet
  echo "    updated to $(git -C "$APP_DIR" log -1 --format='%h %s')"
else
  git clone --quiet --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
  echo "    cloned $REPO_URL"
fi
chown -R "$SVC_USER:$SVC_USER" "$APP_DIR"

step "state directory at $VAR_DIR"
install -d -o "$SVC_USER" -g "$SVC_USER" -m 750 "$VAR_DIR" "$VAR_DIR/logs"
install -d -m 755 "$ETC_DIR"
if [ ! -f "$ETC_DIR/sync.env" ]; then
  install -o root -g "$SVC_USER" -m 640 "$APP_DIR/deploy/env.example" "$ETC_DIR/sync.env"
  sed -i "s#^APP_DIR=.*#APP_DIR=$APP_DIR#; s#^VAR_DIR=.*#VAR_DIR=$VAR_DIR#; s#^BRANCH=.*#BRANCH=$BRANCH#" "$ETC_DIR/sync.env"
  echo "    wrote $ETC_DIR/sync.env from env.example"
else
  echo "    $ETC_DIR/sync.env exists, left alone"
fi

step "admin token"
if [ ! -f "$VAR_DIR/admin_token" ]; then
  python3 -c "import secrets; print(secrets.token_urlsafe(32))" > "$VAR_DIR/admin_token"
  chown "$SVC_USER:$SVC_USER" "$VAR_DIR/admin_token"
  chmod 600 "$VAR_DIR/admin_token"
  echo "    minted $VAR_DIR/admin_token"
else
  echo "    token exists, left alone"
fi

step "node dependencies"
sudo -u "$SVC_USER" bash -lc "cd '$APP_DIR' && npm ci --no-audit --no-fund" \
  || echo "    npm ci failed — run it by hand and check the output"

step "systemd units"
for unit in fluttercook-sync.service fluttercook-sync.timer fluttercook-admin.service; do
  # Paths in the shipped units assume /opt/fluttercook; rewrite them if the
  # operator chose somewhere else.
  sed "s#/opt/fluttercook#$APP_DIR#g; s#/var/lib/fluttercook#$VAR_DIR#g; s#^User=.*#User=$SVC_USER#; s#^Group=.*#Group=$SVC_USER#" \
      "$APP_DIR/deploy/$unit" > "/etc/systemd/system/$unit"
  echo "    installed $unit"
done
systemctl daemon-reload
systemctl enable --now fluttercook-admin.service
systemctl enable --now fluttercook-sync.timer
echo "    admin: $(systemctl is-active fluttercook-admin.service), timer: $(systemctl is-active fluttercook-sync.timer)"

step "nginx site for $ADMIN_HOST"
sed "s/jo\.fighttech\.vn/$ADMIN_HOST/g" "$APP_DIR/deploy/nginx.conf.example" \
  > "/etc/nginx/sites-available/$ADMIN_HOST"
ln -sf "/etc/nginx/sites-available/$ADMIN_HOST" "/etc/nginx/sites-enabled/$ADMIN_HOST"
# The TLS server block has no certificate yet, so nginx -t fails until certbot
# runs. Report it rather than pretending the site is up.
if nginx -t 2>/dev/null; then
  systemctl reload nginx
  echo "    nginx reloaded"
else
  echo "    nginx config not valid yet — expected before certbot has issued a certificate"
fi

step "credentials check"
missing=0
for f in .app_dist/trunghieu-it/token.json .app_dist/trunghieu-it/client_secret.json \
         .app_dist/token_fluttercook.json .app_dist/client_secret.json; do
  if [ -f "$APP_DIR/$f" ]; then
    echo "    ok      $f"
  else
    echo "    MISSING $f"
    missing=1
  fi
done

cat <<SUMMARY

────────────────────────────────────────────────────────────
Installed.

  checkout   $APP_DIR
  state      $VAR_DIR
  config     $ETC_DIR/sync.env
  admin      http://127.0.0.1:8787  (behind $ADMIN_HOST)
  schedule   $(systemctl list-timers fluttercook-sync.timer --no-pager 2>/dev/null | sed -n 2p | tr -s ' ' || echo 'see: systemctl list-timers')

Admin token:
  sudo cat $VAR_DIR/admin_token

Still to do, by hand:
SUMMARY

if [ "$missing" = 1 ]; then
cat <<'CREDS'
  1. Copy the OAuth credentials. They are not in git and never should be:
       scp -r .app_dist USER@SERVER:/tmp/app_dist
       sudo mv /tmp/app_dist APP_DIR/.app_dist
       sudo chown -R SVC_USER:SVC_USER APP_DIR/.app_dist
       sudo chmod -R go-rwx APP_DIR/.app_dist
CREDS
fi

cat <<TLS
  2. Point $ADMIN_HOST at this box (A record), then issue a certificate:
       sudo certbot --nginx -d $ADMIN_HOST

  3. Dry-run once before letting the timer publish anything:
       sudo -u $SVC_USER $APP_DIR/deploy/sync.sh --dry-run --no-pull

  4. Open https://$ADMIN_HOST/ and paste the token.
────────────────────────────────────────────────────────────
TLS
