#!/usr/bin/env bash
# Tarayıcı testlerini tek komutla çalıştırır: sunucuyu boş bir geçici veri klasörüyle kendisi başlatır, bitince kapatır.
# Kullanım: npm run test:e2e        (Python 3 ve Playwright gerekir, bkz. README "Test" bölümü)
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${E2E_PORT:-$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])')}"
DATA_DIR="$(mktemp -d)"
export ADMIN_TOKEN="e2e-$(python3 -c 'import secrets; print(secrets.token_hex(8))')"
LOG="$(mktemp)"

cleanup() {
  [ -n "${SERVER_PID:-}" ] && kill "$SERVER_PID" 2>/dev/null || true
  rm -rf "$DATA_DIR" "$LOG"
}
trap cleanup EXIT

PORT="$PORT" DATA_DIR="$DATA_DIR" DATABASE_URL="" node server.js >"$LOG" 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 60); do
  if curl -fs "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1; then break; fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then echo "Sunucu başlamadı:"; cat "$LOG"; exit 1; fi
  sleep 0.5
done
curl -fs "http://127.0.0.1:$PORT/healthz" >/dev/null || { echo "Sunucu yanıt vermedi:"; cat "$LOG"; exit 1; }

echo "Sunucu http://127.0.0.1:$PORT adresinde (geçici veri klasörü), tarayıcı testleri başlıyor..."
python3 tests/e2e.py "http://127.0.0.1:$PORT"
