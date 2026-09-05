#!/bin/sh
set -eu

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 \
  --set=runtime_password="$PEOPLEPAY360_RUNTIME_PASSWORD" \
  --set=migration_password="$PEOPLEPAY360_MIGRATION_PASSWORD" \
  --set=analytics_password="$PEOPLEPAY360_ANALYTICS_PASSWORD" \
  --file=/docker-entrypoint-initdb.d/01-roles.sql.in
