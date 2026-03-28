#!/usr/bin/env bash
# OPERATION COPPERCLAW — Stop script
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE_CMD=""
if command -v podman-compose &>/dev/null; then
    COMPOSE_CMD="podman-compose"
elif command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "ERROR: No container runtime found." >&2
    exit 1
fi

OVERRIDE_FILE=".compose.platform-override.yml"
COMPOSE_ARGS="-f podman-compose.yml"
[ -f "$OVERRIDE_FILE" ] && COMPOSE_ARGS="$COMPOSE_ARGS -f $OVERRIDE_FILE"

echo "Stopping COPPERCLAW..."
# shellcheck disable=SC2086
$COMPOSE_CMD $COMPOSE_ARGS down "$@"

# Kill any lingering tail on the log
PID_FILE="logs/compose.pid"
if [ -f "$PID_FILE" ]; then
    rm -f "$PID_FILE"
fi

echo "Done."
