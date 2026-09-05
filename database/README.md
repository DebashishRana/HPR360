# PeoplePay360 database foundation

This directory is independent of Frappe HRMS. It uses numbered, plain SQL files
executed by `psql`; this keeps DDL reviewable and avoids adding an ORM or a
second schema-management framework.

## Local development

1. Copy `.env.example` to `.env` and provide unique local-only passwords.
2. From this directory run `docker compose --env-file .env up -d`.
3. Run `./scripts/migrate.ps1` with
   `PEOPLEPAY360_MIGRATION_DATABASE_URL` set to a direct PostgreSQL URL, for
   example `postgresql://peoplepay360_migrator:...@localhost:5432/peoplepay360`.
4. Run `./scripts/test.ps1` with the equivalent `peoplepay360_test` URL.

Application traffic must use PgBouncer at port `6432` with
`peoplepay360_runtime`. Migrations intentionally use PostgreSQL directly on
port `5432`. PgBouncer is pinned to **session** pooling; do not switch to
transaction pooling without confirming every application session setting is
transaction-local.

Payroll calculation and posting code must open one transaction, acquire the
run lock with `SELECT payroll.lock_run(:payroll_run_id)`, then claim its
idempotency key and update the run/scope. The lock is transaction-scoped and
is released automatically by commit or rollback.

The Docker volume is local development state. Do not use `docker compose down
-v` against a database containing data that matters.
