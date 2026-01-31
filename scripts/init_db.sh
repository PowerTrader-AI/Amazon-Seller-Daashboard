#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

: "${PGUSER:?Missing PGUSER}"
: "${PGPASSWORD:?Missing PGPASSWORD}"
: "${PGDATABASE:?Missing PGDATABASE}"
: "${PGHOST:?Missing PGHOST}"
: "${PGPORT:?Missing PGPORT}"

if [[ "$PGHOST" != "localhost" && "$PGHOST" != "127.0.0.1" ]]; then
  echo "PGHOST must be local for this script." >&2
  exit 1
fi

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${PGUSER}') THEN
    CREATE USER ${PGUSER} WITH PASSWORD '${PGPASSWORD}';
  END IF;
END$$;
SQL

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${PGDATABASE}') THEN
    CREATE DATABASE ${PGDATABASE} OWNER ${PGUSER};
  END IF;
END$$;
SQL

PGPASSWORD="$PGPASSWORD" psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f schema.sql

echo "Local DB initialized."
