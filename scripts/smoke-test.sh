#!/usr/bin/env bash
# OPERATION COPPERCLAW — Smoke Test
# COSMIC INDIGO // REL KESTREL COALITION // EXERCISE
# Usage: ./scripts/smoke-test.sh [--kafka-host localhost:9092]

set -euo pipefail

KAFKA_HOST="${KAFKA_HOST:-localhost:9092}"
PASS=0
FAIL=0

green='\033[0;32m'
red='\033[0;31m'
nc='\033[0m'

pass() { echo -e "${green}[PASS]${nc} $1"; ((PASS++)); }
fail() { echo -e "${red}[FAIL]${nc} $1"; ((FAIL++)); }

check_health() {
    local name=$1
    local url=$2
    if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
        pass "$name health endpoint: $url"
    else
        fail "$name health endpoint unreachable: $url"
    fi
}

echo "============================================================"
echo "OPERATION COPPERCLAW — SMOKE TEST"
echo "COSMIC INDIGO // REL KESTREL COALITION // EXERCISE"
echo "============================================================"
echo ""

# Health checks
check_health "isr-tasking-service"       "http://localhost:8081/api/isr-tasking/health"
check_health "collection-service"        "http://localhost:8082/api/collection/health"
check_health "allsource-analyst-service" "http://localhost:8083/api/analyst/health"
check_health "target-nomination-service" "http://localhost:8084/api/nomination/health"
check_health "commander-service"         "http://localhost:8085/api/commander/health"
check_health "execution-service"         "http://localhost:8086/api/execution/health"
check_health "bda-service"               "http://localhost:8087/api/bda/health"
check_health "develop-service"           "http://localhost:8088/api/develop/health"
check_health "state-service"             "http://localhost:8089/api/state/health"
check_health "sse-bridge-service"        "http://localhost:8090/api/stream/health"
check_health "legal-review-service"      "http://localhost:8091/q/health/live"
check_health "cot-gateway-service"       "http://localhost:8092/q/health/live"
check_health "operator-service"          "http://localhost:8000/health"

echo ""
echo "--- Kafka integration test ---"

# Publish a test cycle_start to operator-commands
TEST_MESSAGE='{
  "message_id": "smoke-test-001",
  "tool_name": "cycle_start",
  "input": {
    "priority_target": "TGT-ECHO-001",
    "operator_intent": "SMOKE TEST — Begin VARNAK targeting cycle",
    "cycle_id": "CYCLE-SMOKE-001"
  },
  "timestamp_zulu": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
  "source": "smoke-test",
  "classification": "COSMIC INDIGO // REL KESTREL COALITION",
  "exercise_serial": "COPPERCLAW-SIM-001"
}'

# Require kafka-console-producer from PATH or Strimzi container
if command -v kafka-console-producer.sh > /dev/null 2>&1; then
    echo "$TEST_MESSAGE" | kafka-console-producer.sh \
        --bootstrap-server "$KAFKA_HOST" \
        --topic copperclaw.operator-commands > /dev/null 2>&1
    pass "Published cycle_start to copperclaw.operator-commands"
elif command -v docker > /dev/null 2>&1 || command -v podman > /dev/null 2>&1; then
    CONTAINER_CMD=$(command -v podman 2>/dev/null || command -v docker)
    echo "$TEST_MESSAGE" | $CONTAINER_CMD exec -i kafka \
        kafka-console-producer.sh \
        --bootstrap-server localhost:9092 \
        --topic copperclaw.operator-commands > /dev/null 2>&1
    pass "Published cycle_start via container to copperclaw.operator-commands"
else
    fail "Cannot publish to Kafka — kafka-console-producer.sh not in PATH and no container runtime found"
fi

echo "Waiting 30 seconds for ISR tasking service to respond..."
sleep 30

# Check if copperclaw.isr-tasking has received a message
echo "Checking copperclaw.isr-tasking for messages..."
if command -v kafka-console-consumer.sh > /dev/null 2>&1; then
    MSG=$(timeout 10 kafka-console-consumer.sh \
        --bootstrap-server "$KAFKA_HOST" \
        --topic copperclaw.isr-tasking \
        --from-beginning \
        --max-messages 1 \
        2>/dev/null || true)
    if [ -n "$MSG" ]; then
        pass "copperclaw.isr-tasking has messages (ISR tasking service responded)"
    else
        fail "copperclaw.isr-tasking has no messages (ISR tasking service did not respond within 30s)"
    fi
elif command -v docker > /dev/null 2>&1 || command -v podman > /dev/null 2>&1; then
    CONTAINER_CMD=$(command -v podman 2>/dev/null || command -v docker)
    MSG=$(timeout 10 $CONTAINER_CMD exec kafka \
        kafka-console-consumer.sh \
        --bootstrap-server localhost:9092 \
        --topic copperclaw.isr-tasking \
        --from-beginning \
        --max-messages 1 \
        2>/dev/null || true)
    if [ -n "$MSG" ]; then
        pass "copperclaw.isr-tasking has messages (ISR tasking service responded)"
    else
        fail "copperclaw.isr-tasking has no messages (ISR tasking service did not respond within 30s)"
    fi
else
    fail "Cannot check Kafka topic — kafka-console-consumer.sh not in PATH and no container runtime found"
fi

echo ""
echo "============================================================"
echo "RESULTS: ${PASS} PASS / ${FAIL} FAIL"
echo "============================================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
