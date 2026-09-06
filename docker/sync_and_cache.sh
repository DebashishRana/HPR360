#!/bin/bash
set -e
SRC=/workspace/hpr360
DST=/home/frappe/benches/frappe-bench/apps/hrms
echo "Syncing $SRC -> $DST"
mkdir -p "$DST"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude .git \
    --exclude node_modules \
    --exclude docker \
    --exclude data \
    --exclude .cursor \
    --exclude canvases \
    "$SRC/" "$DST/"
else
  find "$DST" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  cp -a "$SRC/." "$DST/"
fi
chown -R frappe:frappe "$DST" || true
echo "www files:"
ls -la "$DST/hrms/www"
cd /home/frappe/benches/frappe-bench
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost clear-cache || true
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost clear-website-cache || true
echo DONE
