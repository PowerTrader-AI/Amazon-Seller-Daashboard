#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

export PYTHONPATH=backend

uvicorn app.main:app --host 0.0.0.0 --port 8000
