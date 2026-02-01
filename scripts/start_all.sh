#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}
BASE_URL=${BASE_URL:-http://127.0.0.1:${PORT}}
LOG_DIR=${LOG_DIR:-"$ROOT_DIR/logs"}
LOG_FILE=${LOG_FILE:-"$LOG_DIR/api.log"}

activate_venv() {
  if [[ -f "$ROOT_DIR/keepa/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$ROOT_DIR/keepa/bin/activate"
    echo "Activated virtual environment: $ROOT_DIR/keepa"
  else
    echo "Virtual environment not found at $ROOT_DIR/keepa. Using system Python."
  fi
}

kill_port() {
  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids=$(lsof -ti tcp:"$PORT" || true)
    if [[ -n "$pids" ]]; then
      echo "Port $PORT is in use. Stopping existing process(es): $pids"
      kill $pids || true
      sleep 1
    fi
  else
    echo "lsof not available. Skipping port check."
  fi
}

init_db() {
  "$ROOT_DIR/scripts/init_db_sqlite.sh"
}

start_api() {
  mkdir -p "$LOG_DIR"
  export PYTHONPATH=backend
  echo "Starting API on $HOST:$PORT"
  nohup uvicorn app.main:app --host "$HOST" --port "$PORT" >"$LOG_FILE" 2>&1 &
  echo $! >"$LOG_DIR/uvicorn.pid"
}

wait_for_health() {
  local url="$1"
  local name="$2"
  local retries=12
  local delay=1

  for _ in $(seq 1 "$retries"); do
    if curl -fsS "$url" >/dev/null; then
      echo "${name}: ok"
      return 0
    fi
    sleep "$delay"
  done

  echo "${name}: failed"
  return 1
}

check_endpoint() {
  local url="$1"
  local label="$2"
  local method="${3:-GET}"
  local data="${4:-}"
  
  if [[ "$method" == "POST" && -n "$data" ]]; then
    if curl -fsS -X POST -H "Content-Type: application/json" -d "$data" "$url" >/dev/null 2>&1; then
      echo "  ✓ $label"
      return 0
    else
      echo "  ✗ $label"
      return 1
    fi
  else
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "  ✓ $label"
      return 0
    else
      echo "  ✗ $label"
      return 1
    fi
  fi
}

check_endpoints() {
  local failed=0
  echo ""
  echo "🔍 ENDPOINT HEALTH CHECK"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  echo ""
  echo "📌 CORE ENDPOINTS"
  check_endpoint "$BASE_URL/health" "GET /health" || failed=1
  check_endpoint "$BASE_URL/" "GET /" || failed=1
  
  echo ""
  echo "🔐 AUTH ENDPOINTS"
  check_endpoint "$BASE_URL/auth/login" "POST /auth/login" "POST" '{"username":"test","password":"password123"}' || true
  check_endpoint "$BASE_URL/auth/register" "POST /auth/register" "POST" '{"username":"test","password":"password123"}' || true

  echo ""
  echo "📊 CATEGORY ENDPOINTS"
  check_endpoint "$BASE_URL/category/analysis" "GET /category/analysis" || failed=1
  check_endpoint "$BASE_URL/category/tree" "GET /category/tree" || true
  check_endpoint "$BASE_URL/category/products/1" "GET /category/products/{id}" || true

  echo ""
  echo "🏪 MARKETPLACE ENDPOINTS"
  check_endpoint "$BASE_URL/categories" "GET /categories" || true
  check_endpoint "$BASE_URL/top5" "GET /top5" || true
  check_endpoint "$BASE_URL/keepa/category" "GET /keepa/category" || true

  echo ""
  echo "🔍 KEEPA ENDPOINTS"
  if curl -fsS "$BASE_URL/keepa/health" >/dev/null 2>&1; then
    local keepa_data
    keepa_data=$(curl -fsS "$BASE_URL/keepa/health")
    local tokens
    tokens=$(echo "$keepa_data" | grep -o '"tokens_left":[0-9]*' | cut -d: -f2 || echo "?")
    echo "  ✓ GET /keepa/health (tokens: $tokens)"
  else
    echo "  ⚠ GET /keepa/health (non-fatal - check API key)"
  fi

  echo ""
  echo "📚 UI & DOCS"
  check_endpoint "$BASE_URL/docs" "GET /docs" || failed=1
  check_endpoint "$BASE_URL/ui/" "GET /ui/" || failed=1
  check_endpoint "$BASE_URL/ui/dashboard.html" "GET /ui/dashboard.html" || failed=1

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  return "$failed"
}

main() {
  activate_venv
  init_db
  kill_port
  start_api

  if ! check_endpoints; then
    echo ""
    echo "⚠ Some endpoints failed. Restarting API..."
    kill_port
    sleep 2
    start_api

    if ! check_endpoints; then
      echo ""
      echo "✗ API failed to fully start. Review logs:"
      echo "  $LOG_FILE"
      exit 1
    fi
  fi

  echo ""
  echo "✅ ALL SYSTEMS READY!"
  echo "API: $BASE_URL"
  echo "UI: $BASE_URL/ui/"
  echo "Docs: $BASE_URL/docs"
  echo "Logs: $LOG_FILE"
  echo ""
}

main
