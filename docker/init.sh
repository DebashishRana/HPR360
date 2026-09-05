#!/bin/bash
set -e

export PATH="${NVM_DIR}/versions/node/v${NODE_VERSION_DEVELOP}/bin/:${PATH}"
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=3072}"

cd /home/frappe

bind_web_host() {
	sed -i 's/bench serve.*/bench serve --host 0.0.0.0 --port 8000/' ./Procfile
}

if [ -d "frappe-bench/apps/frappe" ]; then
	echo "Bench already exists, starting..."
	cd frappe-bench
	bind_web_host
	bench start
	exit 0
fi

echo "Creating new bench..."

bench init --skip-redis-config-generation frappe-bench

cd frappe-bench

bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile
bind_web_host

bench get-app erpnext
bench get-app hrms

bench new-site hrms.localhost \
--force \
--mariadb-root-password 123 \
--admin-password admin \
--no-mariadb-socket

bench --site hrms.localhost install-app hrms
bench --site hrms.localhost set-config developer_mode 1
bench --site hrms.localhost enable-scheduler
bench --site hrms.localhost clear-cache
bench use hrms.localhost

bench start