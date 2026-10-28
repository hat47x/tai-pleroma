#!/usr/bin/env bash
set -euo pipefail

# Smoke-test the EKI Control Plane and Agent on WSL. This is not a
# Task-executing Worker; it proves both binaries start and the Client API and
# Worker test profile are reachable.

EKI_ROOT="${EKI_ROOT:-/home/hat47x/eki-worker}"
IMAGE="${EKI_IMAGE:-golang:1.27}"
CONFIG="${CONFIG:-$(cd "$(dirname "$0")" && pwd)/config/control.json}"
AGENT_CONFIG="${AGENT_CONFIG:-$(cd "$(dirname "$0")" && pwd)/config/agent.json}"
BIN_DIR="$EKI_ROOT/bin"
CONTROL_PID=""
AGENT_PID=""

cleanup() {
  for pid in "$AGENT_PID" "$CONTROL_PID"; do
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT

mkdir -p "$BIN_DIR"
docker run --rm \
  -v "$EKI_ROOT":/src \
  -w /src \
  "$IMAGE" \
  sh -c 'mkdir -p /src/bin && go build -o /src/bin/eki-control ./cmd/eki-control && go build -o /src/bin/eki-agent ./cmd/eki-agent'

rm -f /tmp/eki-worker-smoke.db /tmp/eki-agent-smoke.db
"$BIN_DIR/eki-control" --config "$CONFIG" >/tmp/eki-worker-smoke.log 2>&1 &
CONTROL_PID=$!

for _ in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer scn001-token-0123456789' http://127.0.0.1:18086/v1/tasks || true)
  if [ "$code" = "405" ]; then
    break
  fi
  sleep 1
done
if [ "${code:-}" != "405" ]; then
  echo "control smoke: failed" >&2
  cat /tmp/eki-worker-smoke.log >&2 || true
  exit 1
fi

"$BIN_DIR/eki-agent" --config "$AGENT_CONFIG" >/tmp/eki-agent-smoke.log 2>&1 &
AGENT_PID=$!
for _ in $(seq 1 20); do
  if grep -q "agent delivering claims" /tmp/eki-agent-smoke.log 2>/dev/null; then
    echo "control smoke: ok (GET /v1/tasks -> 405)"
    echo "agent smoke: ok (claim delivery started)"
    exit 0
  fi
  if ! kill -0 "$AGENT_PID" 2>/dev/null; then
    break
  fi
  sleep 1
done

echo "agent smoke: failed" >&2
cat /tmp/eki-agent-smoke.log >&2 || true
exit 1
