#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

API_PORT=${API_PORT:-8000}
UI_PORT=${UI_PORT:-8080}
API_HOST=${API_HOST:-0.0.0.0}
LOG_DIR=${LOG_DIR:-/tmp}
BACKEND_LOG=${BACKEND_LOG:-"$LOG_DIR/backend.log"}
FRONTEND_LOG=${FRONTEND_LOG:-"$LOG_DIR/frontend.log"}

# Load environment variables if they exist
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

export PYTHONPATH=backend

kill_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids=$(lsof -ti tcp:"$port" || true)
    if [[ -n "$pids" ]]; then
      echo "🔁 Port $port in use. Stopping: $pids"
      kill $pids || true
      sleep 1

      local remaining
      remaining=$(lsof -ti tcp:"$port" || true)
      if [[ -n "$remaining" ]]; then
        echo "⚠ Port $port still in use. Force stopping: $remaining"
        kill -9 $remaining || true
        sleep 1
      fi
    fi
  fi
}

wait_for_http_ok() {
  local url="$1"
  local label="$2"
  local retries=20
  local delay=1

  for _ in $(seq 1 "$retries"); do
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)
    if [[ "$code" == "200" ]]; then
      echo "  ✅ $label"
      return 0
    fi
    sleep "$delay"
  done

  echo "  ❌ $label"
  return 1
}

check_cors_header() {
  local endpoint="$1"
  local origin="$2"
  local label="$3"

  local headers
  headers=$(curl -s -i -X OPTIONS "$endpoint" \
    -H "Origin: $origin" \
    -H "Access-Control-Request-Method: GET" || true)

  if echo "$headers" | grep -qi "Access-Control-Allow-Origin"; then
    echo "  ✅ $label"
    return 0
  fi

  echo "  ❌ $label"
  return 1
}

echo "🚀 Starting Amazon Seller Dashboard..."
echo ""

mkdir -p "$LOG_DIR"
kill_port "$API_PORT"
kill_port "$UI_PORT"

PYTHON_BIN="$ROOT_DIR/keepa/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

echo "📌 Starting Backend API on port $API_PORT..."
"$PYTHON_BIN" -m uvicorn app.main:app \
  --host "$API_HOST" \
  --port "$API_PORT" \
  > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

echo "📌 Starting Frontend HTTP Server on port $UI_PORT..."
cd "$ROOT_DIR/frontend"
python3 -m http.server "$UI_PORT" > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd "$ROOT_DIR"

echo ""
echo "🔍 STARTUP VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

failed=0
wait_for_http_ok "http://127.0.0.1:${API_PORT}/health" "Backend health (/health)" || failed=1
wait_for_http_ok "http://127.0.0.1:${API_PORT}/keepa/health" "Keepa health (/keepa/health)" || failed=1
wait_for_http_ok "http://127.0.0.1:${API_PORT}/ui/dashboard.html" "Backend-served Dashboard UI (/ui/dashboard.html)" || failed=1
wait_for_http_ok "http://127.0.0.1:${UI_PORT}/" "Standalone frontend (:${UI_PORT})" || failed=1
check_cors_header "http://127.0.0.1:${API_PORT}/keepa/health" "http://localhost:${UI_PORT}" "CORS preflight for localhost:${UI_PORT} -> :${API_PORT}" || failed=1

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ "$failed" -ne 0 ]]; then
  echo ""
  echo "❌ Startup validation failed."
  echo "Backend log:  $BACKEND_LOG"
  echo "Frontend log: $FRONTEND_LOG"
  exit 1
fi

CODESPACE_DOMAIN=${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}
if [[ -n "${CODESPACE_NAME:-}" ]]; then
  API_PUBLIC="https://${CODESPACE_NAME}-${API_PORT}.${CODESPACE_DOMAIN}"
  UI_PUBLIC_SAME_ORIGIN="${API_PUBLIC}/ui/dashboard.html"
  UI_PUBLIC_8080="https://${CODESPACE_NAME}-${UI_PORT}.${CODESPACE_DOMAIN}/"
else
  API_PUBLIC=""
  UI_PUBLIC_SAME_ORIGIN=""
  UI_PUBLIC_8080=""
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        🎉 DASHBOARD SERVICES STARTED + VALIDATED 🎉        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 LOCAL URLs"
echo "   ✅ Backend API:      http://localhost:${API_PORT}/health"
echo "   ✅ Recommended UI:   http://localhost:${API_PORT}/ui/dashboard.html"
echo "   ✅ Standalone UI:    http://localhost:${UI_PORT}/"

if [[ -n "$API_PUBLIC" ]]; then
  echo ""
  echo "🌐 CODESPACES URLs"
  echo "   ✅ API:              ${API_PUBLIC}/health"
  echo "   ✅ Recommended UI:   ${UI_PUBLIC_SAME_ORIGIN}"
  echo "   ⚠ Standalone UI:     ${UI_PUBLIC_8080} (may hit cross-port auth/CORS)"
fi

echo ""
echo "📊 LOGS"
echo "   Backend:  tail -f $BACKEND_LOG"
echo "   Frontend: tail -f $FRONTEND_LOG"
echo ""
echo "⏹️  To stop"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Keep script running
wait
