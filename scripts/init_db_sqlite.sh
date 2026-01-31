#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

DB_FILE="amazon_sourcing.db"

if [[ -f "$DB_FILE" ]]; then
  echo "Database already exists at $DB_FILE"
else
  echo "Creating new SQLite database..."
  sqlite3 "$DB_FILE" < schema_sqlite.sql
  echo "Database initialized at $DB_FILE"
fi
