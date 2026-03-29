#!/usr/bin/env bash
# COPPERCLAW WATCH — continuous test watcher
# Polls origin/master every 30s, runs scoped test suite on new commits

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

WATCH_LOG="/tmp/copperclaw_watch.log"
LAST_RUN_LOG="/tmp/copperclaw_last_run.txt"

LAST_KNOWN=$(git rev-parse HEAD)
LAST_SHORT=$(git rev-parse --short HEAD)

echo ""
echo "  COPPERCLAW WATCH — ACTIVE"
echo "  COSMIC INDIGO // EXERCISE"
echo "  ─────────────────────────────────────"
echo "  Polling: every 30 seconds"
echo "  Branch:  origin/master"
echo "  Baseline: $LAST_SHORT"
echo "  Test log: $WATCH_LOG"
echo "  ─────────────────────────────────────"
echo "  Commit scope → test suite:"
echo "    schema/infra change  → full suite (~6 min)"
echo "    backend only         → api + cycle (~3 min)"
echo "    frontend only        → infra + health (~1 min)"
echo "    docs/config only     → fast check (~2 min)"
echo "  ─────────────────────────────────────"
echo "  Watching..."
echo ""

while true; do

  sleep 30

  git fetch origin master --quiet 2>/dev/null || {
    echo "$(date -u +%H:%M:%SZ) WARN: git fetch failed — network or auth issue, retrying next cycle"
    continue
  }

  CURRENT=$(git rev-parse origin/master)

  if [ "$CURRENT" != "$LAST_KNOWN" ]; then

    git pull origin master --quiet

    NEW_COMMITS=$(git log "${LAST_KNOWN}..HEAD" --oneline --no-walk=unsorted 2>/dev/null || \
                  git log "${LAST_KNOWN}..HEAD" --oneline)

    echo ""
    echo "═══════════════════════════════════════"
    echo "NEW COMMIT DETECTED — $(date -u +%H:%M:%SZ)"
    echo "═══════════════════════════════════════"
    echo "$NEW_COMMITS"
    echo ""

    CHANGED_FILES=$(git diff --name-only "${LAST_KNOWN}..HEAD")

    FRONTEND_CHANGED=$(echo "$CHANGED_FILES" | grep "^frontend/" | wc -l)
    BACKEND_CHANGED=$(echo "$CHANGED_FILES" | grep -E "^agents/|^operator-service/|^state-service/|^sse-bridge" | wc -l)
    INFRA_CHANGED=$(echo "$CHANGED_FILES" | grep -E "^podman-compose|^parent-pom|\.env\.example|^scripts/" | wc -l)
    SCHEMA_CHANGED=$(echo "$CHANGED_FILES" | grep -E "^shared/|^shared-java/" | wc -l)

    echo "Changed: frontend=$FRONTEND_CHANGED backend=$BACKEND_CHANGED infra=$INFRA_CHANGED schema=$SCHEMA_CHANGED"
    echo ""

    if [ "$SCHEMA_CHANGED" -gt 0 ] || [ "$INFRA_CHANGED" -gt 0 ]; then
      echo "SCOPE: Full suite (schema or infra changed)"
      RUN_SUITE="full"
    elif [ "$BACKEND_CHANGED" -gt 0 ] && [ "$FRONTEND_CHANGED" -gt 0 ]; then
      echo "SCOPE: Full suite (frontend + backend changed)"
      RUN_SUITE="full"
    elif [ "$BACKEND_CHANGED" -gt 0 ]; then
      echo "SCOPE: API + cycle tests (backend changed)"
      RUN_SUITE="api"
    elif [ "$FRONTEND_CHANGED" -gt 0 ]; then
      echo "SCOPE: Infra + health only (frontend only)"
      RUN_SUITE="infra"
    else
      echo "SCOPE: Fast check (docs/config only)"
      RUN_SUITE="fast"
    fi

    START_TIME=$(date +%s)
    HEAD_SHORT=$(git rev-parse --short HEAD)

    case $RUN_SUITE in
      full)
        timeout 600 bash scripts/e2e-test.sh 2>&1 | tee "$LAST_RUN_LOG"
        ;;
      api)
        timeout 600 bash scripts/e2e-test.sh --api-only 2>&1 | tee "$LAST_RUN_LOG"
        ;;
      infra)
        timeout 600 bash scripts/e2e-test.sh --infra-only 2>&1 | tee "$LAST_RUN_LOG"
        ;;
      fast)
        timeout 600 bash scripts/e2e-test.sh --fast 2>&1 | tee "$LAST_RUN_LOG"
        ;;
    esac

    EXIT_CODE=$?
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))

    # Handle timeout (exit code 124)
    if [ $EXIT_CODE -eq 124 ]; then
      echo ""
      echo "═══════════════════════════════════════"
      echo "TEST TIMEOUT — killed after 10 minutes."
      echo "Likely cause: cycle did not complete, commander hold"
      echo "not resolving, or RamaLama inference hung."
      echo "Commit: $HEAD_SHORT"
      echo "═══════════════════════════════════════"
      echo ""
      echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | COMMIT: $HEAD_SHORT | SCOPE: $RUN_SUITE | RESULT: TIMEOUT | TIME: ${ELAPSED}s | TRIGGER: $CHANGED_FILES" >> "$WATCH_LOG"
      LAST_KNOWN=$CURRENT
      continue
    fi

    echo ""
    echo "═══════════════════════════════════════"
    if [ $EXIT_CODE -eq 0 ]; then
      echo "RESULT: PASS (${ELAPSED}s)"
      echo "Commit: $HEAD_SHORT"
      echo "$(date -u +%H:%M:%SZ) — all checks green"
      RESULT_STR="PASS"
    else
      echo "RESULT: FAIL (${ELAPSED}s)"
      echo "Commit: $HEAD_SHORT"
      echo "$(date -u +%H:%M:%SZ) — FAILURES DETECTED"
      echo ""
      echo "Failed commit details:"
      git log -1 --format="  Author: %an%n  Message: %s%n  Files: $(git diff --name-only HEAD~1..HEAD | tr '\n' ' ')"
      echo ""

      # --- TRIAGE ---
      echo "--- TRIAGE ---"
      echo "Specific failures:"
      grep "  FAIL" "$LAST_RUN_LOG" 2>/dev/null | head -20 || echo "  (no structured FAIL lines found)"
      echo ""
      echo "Service health at time of failure:"
      UNHEALTHY_SVCS=""
      for port in 8081 8082 8083 8084 8085 8086 8087 8088 8089 8090 8091 8092 8000; do
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://localhost:$port/q/health" 2>/dev/null || echo "ERR")
        if [ "$STATUS" != "200" ]; then
          echo "  UNHEALTHY: port $port — HTTP $STATUS"
          UNHEALTHY_SVCS="$UNHEALTHY_SVCS $port"
        fi
      done
      [ -z "$UNHEALTHY_SVCS" ] && echo "  All probed ports healthy"

      # Classify
      echo ""
      CYCLE_FAIL=$(grep -c "cycle" "$LAST_RUN_LOG" 2>/dev/null || true)
      INFRA_FAIL=$(grep -cE "kafka|postgres|PostgreSQL|Kafka" "$LAST_RUN_LOG" 2>/dev/null || true)
      NGINX_FAIL=$(grep -ci "nginx\|proxy" "$LAST_RUN_LOG" 2>/dev/null || true)

      if [ -n "$UNHEALTHY_SVCS" ]; then
        echo "CLASSIFICATION: SERVICE DOWN — ports$UNHEALTHY_SVCS not responding"
      elif [ "$CYCLE_FAIL" -gt 0 ]; then
        echo "CLASSIFICATION: CYCLE FAILURE — agents running but cycle did not complete. Check Kafka topic flow."
      elif [ "$INFRA_FAIL" -gt 0 ]; then
        echo "CLASSIFICATION: INFRASTRUCTURE FAILURE — Kafka or PostgreSQL issue. Check podman ps for container status."
      elif [ "$NGINX_FAIL" -gt 0 ]; then
        echo "CLASSIFICATION: NGINX PROXY FAILURE — frontend cannot reach backend services. Check nginx.conf."
      else
        echo "CLASSIFICATION: UNKNOWN — review $LAST_RUN_LOG for details"
      fi

      echo ""
      echo "To investigate:"
      echo "  make logs svc=<service-name>"
      echo "  make test-fast"
      echo "  git log --oneline -3"
      echo "  cat $LAST_RUN_LOG"
      RESULT_STR="FAIL"
    fi
    echo "═══════════════════════════════════════"
    echo ""

    # Append to watch log
    TRIGGER_DESC="${CHANGED_FILES//$'\n'/ }"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | COMMIT: $HEAD_SHORT | SCOPE: $RUN_SUITE | RESULT: $RESULT_STR | TIME: ${ELAPSED}s | TRIGGER: $TRIGGER_DESC" >> "$WATCH_LOG"

    LAST_KNOWN=$CURRENT

    # Schema rebuild reminder
    if [ "$SCHEMA_CHANGED" -gt 0 ]; then
      echo "NOTE: Schema files changed."
      echo "If services are running, rebuild:"
      echo "  make restart svc=allsource-analyst-service"
      echo "  (or podman-compose up --build)"
      echo ""
    fi

    # Infra restart reminder
    if [ "$INFRA_CHANGED" -gt 0 ]; then
      echo "NOTE: podman-compose.yml or POM changed."
      echo "Consider: podman-compose up --build"
      echo ""
    fi

  fi

done
