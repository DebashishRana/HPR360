#!/bin/sh
set -eu

# PgBouncer reads this file at startup. It is created in the container from
# environment variables so passwords are never committed to source control.
umask 077
cat > /tmp/peoplepay360-users.txt <<EOF
"peoplepay360_runtime" "${PEOPLEPAY360_RUNTIME_PASSWORD}"
"peoplepay360_migrator" "${PEOPLEPAY360_MIGRATION_PASSWORD}"
"peoplepay360_analytics" "${PEOPLEPAY360_ANALYTICS_PASSWORD}"
EOF

exec pgbouncer /etc/pgbouncer/pgbouncer.ini
