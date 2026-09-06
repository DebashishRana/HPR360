#!/bin/bash
set -e

export HOME=/home/frappe
export PATH="${NVM_DIR}/versions/node/v${NODE_VERSION_DEVELOP:-18}/bin/:${PATH}"

BENCHES=/home/frappe/benches
BENCH_DIR="${BENCHES}/frappe-bench"
LOCAL_HRMS=/workspace/hpr360

as_frappe() {
	runuser -u frappe -- env HOME=/home/frappe USER=frappe PATH="$PATH" "$@"
}

sync_local_hrms() {
	if [ ! -f "${LOCAL_HRMS}/pyproject.toml" ]; then
		echo Local HPR360 not found; skipping sync
		return 0
	fi
	echo Syncing local PeoplePay360 into apps/hrms...
	mkdir -p "${BENCH_DIR}/apps/hrms"
	if command -v rsync >/dev/null 2>&1; then
		rsync -a --delete \
			--exclude .git \
			--exclude node_modules \
			--exclude __pycache__ \
			--exclude .cursor \
			--exclude canvases \
			--exclude docker \
			--exclude data \
			"${LOCAL_HRMS}/" "${BENCH_DIR}/apps/hrms/"
	else
		find "${BENCH_DIR}/apps/hrms" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
		cp -a "${LOCAL_HRMS}/." "${BENCH_DIR}/apps/hrms/"
		rm -rf "${BENCH_DIR}/apps/hrms/.git" \
			"${BENCH_DIR}/apps/hrms/node_modules" \
			"${BENCH_DIR}/apps/hrms/.cursor" \
			"${BENCH_DIR}/apps/hrms/canvases" \
			"${BENCH_DIR}/apps/hrms/docker" \
			"${BENCH_DIR}/apps/hrms/data" || true
	fi
	chown -R frappe:frappe "${BENCH_DIR}/apps/hrms" || true
}

start_bench() {
	cd "${BENCH_DIR}"
	sync_local_hrms
	if [ -f apps/hrms/pyproject.toml ]; then
		as_frappe bench setup requirements --app hrms || true
	fi
	sed -i -E 's|^web: bench serve.*|web: bench serve --host 0.0.0.0 --port 8000|' ./Procfile || true
	sed -i '/redis/d' ./Procfile || true
	sed -i '/watch/d' ./Procfile || true
	as_frappe bench start
	exit 0
}

mkdir -p "${BENCHES}"
chown frappe:frappe "${BENCHES}" || true

# Convenience symlink expected by some tooling
ln -sfn "${BENCH_DIR}" /home/frappe/frappe-bench || true

if [ -d "${BENCH_DIR}/apps/frappe" ] && [ -f "${BENCH_DIR}/sites/common_site_config.json" ]; then
	# Fully initialized
	if [ -d "${BENCH_DIR}/sites/hrms.localhost" ]; then
		echo Bench and site already exist, starting...
		start_bench
	fi
fi

if [ -d "${BENCH_DIR}/apps/frappe" ]; then
	echo Partial bench found — repairing and continuing setup...
	cd "${BENCH_DIR}"
	# Reinstall editable apps into this path (fixes broken venv after moves)
	as_frappe bash -lc "cd '${BENCH_DIR}' && ./env/bin/python -m pip install -q -e apps/frappe || uv pip install -q -e apps/frappe --python ./env/bin/python"
	if [ -d apps/erpnext ]; then
		as_frappe bash -lc "cd '${BENCH_DIR}' && ./env/bin/python -m pip install -q -e apps/erpnext || uv pip install -q -e apps/erpnext --python ./env/bin/python"
		as_frappe bench build --app erpnext || true
	else
		as_frappe bench get-app erpnext --skip-assets || as_frappe bench get-app erpnext
	fi
else
	echo Creating new bench in ${BENCH_DIR}...
	as_frappe bash -lc "cd '${BENCHES}' && bench init --skip-redis-config-generation frappe-bench"
	cd "${BENCH_DIR}"
	as_frappe bench set-mariadb-host mariadb
	as_frappe bench set-redis-cache-host redis://redis:6379
	as_frappe bench set-redis-queue-host redis://redis:6379
	as_frappe bench set-redis-socketio-host redis://redis:6379
	sed -i '/redis/d' ./Procfile
	sed -i '/watch/d' ./Procfile
	sed -i -E 's|^web: bench serve.*|web: bench serve --host 0.0.0.0 --port 8000|' ./Procfile
	as_frappe bench get-app erpnext --skip-assets || as_frappe bench get-app erpnext
fi

cd "${BENCH_DIR}"

if [ -f "${LOCAL_HRMS}/pyproject.toml" ]; then
	echo Installing local PeoplePay360 as hrms app...
	sync_local_hrms
	if ! grep -qx hrms apps.txt 2>/dev/null; then
		echo hrms >> apps.txt
	fi
	chown frappe:frappe apps.txt || true
	as_frappe bash -lc "cd '${BENCH_DIR}' && ./env/bin/python -m pip install -q -e apps/hrms || uv pip install -q -e apps/hrms --python ./env/bin/python" || true
	as_frappe bench setup requirements --app hrms || true
	as_frappe bench build --app hrms || true
else
	as_frappe bench get-app hrms --skip-assets || as_frappe bench get-app hrms
fi

echo Waiting for MariaDB...
for i in $(seq 1 90); do
	if mysqladmin ping -h mariadb -uroot -p123 --silent; then
		echo MariaDB is up
		break
	fi
	sleep 2
done

if [ ! -d "${BENCH_DIR}/sites/hrms.localhost" ]; then
	as_frappe bench new-site hrms.localhost \
		--force \
		--mariadb-root-password 123 \
		--admin-password admin \
		--no-mariadb-socket
fi

as_frappe bench --site hrms.localhost install-app erpnext || true
as_frappe bench --site hrms.localhost install-app hrms || true
as_frappe bench --site hrms.localhost set-config developer_mode 1
as_frappe bench --site hrms.localhost enable-scheduler
as_frappe bench --site hrms.localhost clear-cache
as_frappe bench use hrms.localhost

as_frappe bench start
