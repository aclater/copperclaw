#!/usr/bin/env bash
# OPERATION COPPERCLAW — Stop script
set -euo pipefail

_find_project_root() {
    local dir
    dir="$(cd "$(dirname "$0")" && pwd)"
    while [ "$dir" != "/" ]; do
        [ -f "$dir/podman-compose.yml" ] && { echo "$dir"; return 0; }
        dir="$(dirname "$dir")"
    done
    echo "ERROR: could not locate project root (no podman-compose.yml found)" >&2
    exit 1
}
PROJECT_ROOT="$(_find_project_root)"

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

OVERRIDE_FILE="$PROJECT_ROOT/.compose.platform-override.yml"
COMPOSE_ARGS="-f $PROJECT_ROOT/podman-compose.yml"
[ -f "$OVERRIDE_FILE" ] && COMPOSE_ARGS="$COMPOSE_ARGS -f $OVERRIDE_FILE"

echo "Stopping COPPERCLAW..."
# shellcheck disable=SC2086
$COMPOSE_CMD $COMPOSE_ARGS down "$@"

# Kill any lingering tail on the log
PID_FILE="$PROJECT_ROOT/logs/compose.pid"
if [ -f "$PID_FILE" ]; then
    rm -f "$PID_FILE"
fi

echo "Done."
