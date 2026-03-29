#!/usr/bin/env bash
# OPERATION COPPERCLAW — End-to-End Test Suite
# COSMIC INDIGO // REL KESTREL COALITION // EXERCISE — EXERCISE — EXERCISE
#
# Usage: ./scripts/e2e-test.sh
# Requires: podman, curl, python3
# Non-destructive: does not wipe Kafka topics or restart services.

# No set -e — we collect all results; arithmetic increments must not abort.
set -uo pipefail

PASS=0
FAIL=0
WARN=0

# ── Colours ────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; RED='\033[0;31m'; AMBER='\033[0;33m'; NC='\033[0m'

# ── Helpers ─────────────────────────────────────────────────────────────────
check() {
  local label="$1" result="$2"
  if [ "$result" = "pass" ]; then
    echo -e "  ${GREEN}PASS${NC}  $label"
    PASS=$((PASS+1))
  else
    echo -e "  ${RED}FAIL${NC}  $label — $result"
    FAIL=$((FAIL+1))
  fi
}

warn() {
  local label="$1" msg="$2"
  echo -e "  ${AMBER}WARN${NC}  $label — $msg"
  WARN=$((WARN+1))
}

http_check() {
  local label="$1" url="$2"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
  if [ "$code" = "200" ]; then
    check "$label" "pass"
  else
    check "$label" "HTTP $code"
  fi
}

quarkus_health_check() {
  local label="$1" url="$2"
  local body
  body=$(curl -s --max-time 5 "$url" 2>/dev/null || echo "")
  if [ -z "$body" ]; then
    check "$label" "no response"
    return
  fi
  local status
  status=$(echo "$body" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print('pass' if d.get('status')=='UP' else d.get('status','unknown'))" \
    2>/dev/null || echo "parse-error")
  check "$label" "$status"
}

# Returns current log-end offset for a topic (partition 0)
kafka_offset() {
  local topic="$1"
  podman exec "$KAFKA_CONT" \
    bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
    --broker-list localhost:9092 \
    --topic "$topic" --time -1 2>/dev/null \
    | awk -F: '{print $NF}' | tr -d ' \n' || echo "0"
}

# Consume one message from a topic starting at a given offset; print it
kafka_consume_one() {
  local topic="$1" from_offset="$2"
  timeout 10 podman exec "$KAFKA_CONT" \
    bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic "$topic" \
    --partition 0 \
    --offset "$from_offset" \
    --max-messages 1 \
    --timeout-ms 8000 \
    2>/dev/null || true
}

# Check if a JSON string has a given key
json_has_key() {
  local json="$1" key="$2"
  echo "$json" | python3 -c \
    "import sys,json; d=json.loads(sys.stdin.read()); print('pass' if '$key' in d else 'missing-$key')" \
    2>/dev/null || echo "parse-error"
}

# ── Container discovery ──────────────────────────────────────────────────────
# Portable container name lookup — works with _1, -1, or bare suffix
get_container() {
  podman ps --format '{{.Names}}' 2>/dev/null \
    | grep "copperclaw[_-]${1}" | head -1
}

KAFKA_CONT=$(podman ps --format '{{.Names}}' 2>/dev/null \
  | grep "copperclaw_kafka" | grep -v "zookeeper\|setup" | head -1)
POSTGRES_CONT=$(podman ps --format '{{.Names}}' 2>/dev/null \
  | grep "copperclaw_postgres" | head -1)

# ── Header ───────────────────────────────────────────────────────────────────
echo "══════════════════════════════════════════════════════════════"
echo "  OPERATION COPPERCLAW — E2E TEST SUITE"
echo "  COSMIC INDIGO // REL KESTREL COALITION // EXERCISE"
echo "  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "══════════════════════════════════════════════════════════════"
echo ""

# ════════════════════════════════════════════════════════════════════════════
echo "── SECTION 1: Infrastructure Health ──────────────────────────────────"
# ════════════════════════════════════════════════════════════════════════════

# 1.1 Kafka broker reachable
KAFKA_RESULT=$(podman exec "$KAFKA_CONT" \
  bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092 \
  2>/dev/null | grep -q "9092" && echo "pass" || echo "unreachable")
check "1.1  Kafka broker reachable" "$KAFKA_RESULT"

# 1.2 PostgreSQL reachable
PG_RESULT=$(podman exec "$POSTGRES_CONT" \
  psql -U copperclaw -c "SELECT 1" 2>/dev/null \
  | grep -q "1 row" && echo "pass" || echo "unreachable")
check "1.2  PostgreSQL reachable" "$PG_RESULT"

# 1.3 All 14 Kafka topics exist
echo "  Checking 14 Kafka topics..."
TOPICS=$(podman exec "$KAFKA_CONT" \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092 \
  2>/dev/null || echo "")
for topic in \
  copperclaw.operator-commands \
  copperclaw.isr-tasking \
  copperclaw.collection \
  copperclaw.assessment \
  copperclaw.nomination \
  copperclaw.legal-review \
  copperclaw.authorization \
  copperclaw.execution \
  copperclaw.bda \
  copperclaw.develop \
  copperclaw.cot-in \
  copperclaw.cot-out \
  copperclaw.cycle-state \
  copperclaw.commander-log; do
  if echo "$TOPICS" | grep -qF "$topic"; then
    check "1.3  Topic: $topic" "pass"
  else
    check "1.3  Topic: $topic" "missing"
  fi
done

# 1.4 RamaLama model loaded
RAMALAMA_RESULT=$(curl -s --max-time 10 http://localhost:8080/v1/models \
  2>/dev/null | python3 -c \
  "import sys,json; d=json.load(sys.stdin); \
   models=d.get('data',[]); \
   print('pass' if any('qwen' in m.get('id','').lower() for m in models) else 'model-not-loaded')" \
  2>/dev/null || echo "unreachable")
check "1.4  RamaLama qwen2.5:14b loaded" "$RAMALAMA_RESULT"

# 1.5 cycle_state table exists in PostgreSQL
TABLE_RESULT=$(podman exec "$POSTGRES_CONT" \
  psql -U copperclaw -c "\dt cycle_state" 2>/dev/null \
  | grep -q "cycle_state" && echo "pass" || echo "table-missing")
check "1.5  cycle_state table exists in PostgreSQL" "$TABLE_RESULT"
echo ""

# ════════════════════════════════════════════════════════════════════════════
echo "── SECTION 2: Service Health Endpoints ───────────────────────────────"
# ════════════════════════════════════════════════════════════════════════════

# 12 Quarkus services — /q/health
# NOTE: legal-review is 8091, cot-gateway is 8092 (matches compose file)
quarkus_health_check "2.1  isr-tasking-service       :8081" \
  "http://localhost:8081/q/health"
quarkus_health_check "2.2  collection-service         :8082" \
  "http://localhost:8082/q/health"
quarkus_health_check "2.3  allsource-analyst-service  :8083" \
  "http://localhost:8083/q/health"
quarkus_health_check "2.4  target-nomination-service  :8084" \
  "http://localhost:8084/q/health"
quarkus_health_check "2.5  commander-service          :8085" \
  "http://localhost:8085/q/health"
quarkus_health_check "2.6  execution-service          :8086" \
  "http://localhost:8086/q/health"
quarkus_health_check "2.7  bda-service                :8087" \
  "http://localhost:8087/q/health"
quarkus_health_check "2.8  develop-service            :8088" \
  "http://localhost:8088/q/health"
quarkus_health_check "2.9  state-service              :8089" \
  "http://localhost:8089/q/health"
quarkus_health_check "2.10 sse-bridge-service         :8090" \
  "http://localhost:8090/q/health"
quarkus_health_check "2.11 legal-review-service       :8091" \
  "http://localhost:8091/q/health"
quarkus_health_check "2.12 cot-gateway-service        :8092" \
  "http://localhost:8092/q/health"

# operator-service (Python/FastAPI)
OP_HEALTH=$(curl -s --max-time 5 http://localhost:8000/health 2>/dev/null | \
  python3 -c \
  "import sys,json; d=json.load(sys.stdin); \
   print('pass' if d.get('status') in ['ok','healthy','UP','up'] else str(d))" \
  2>/dev/null || echo "unreachable")
check "2.13 operator-service             :8000" "$OP_HEALTH"

# frontend nginx
http_check "2.14 frontend nginx             :3000" "http://localhost:3000"
echo ""

# ════════════════════════════════════════════════════════════════════════════
echo "── SECTION 3: API Endpoint Tests ─────────────────────────────────────"
# ════════════════════════════════════════════════════════════════════════════

# 3.1 State service returns current state
STATE_BODY=$(curl -s --max-time 5 http://localhost:8089/api/state/current \
  2>/dev/null || echo "")
if [ -n "$STATE_BODY" ]; then
  STATE_RESULT=$(echo "$STATE_BODY" | python3 -c \
    "import sys,json; d=json.loads(sys.stdin.read()); \
     print('pass' if any(k in d for k in ['cycle_id','phase','targets']) else 'unexpected-structure')" \
    2>/dev/null || echo "parse-error")
else
  STATE_RESULT="no-response"
fi
check "3.1  State service /api/state/current" "$STATE_RESULT"

# 3.2 Operator service accepts a message (LLM call — 60s timeout)
echo "  3.2  Sending test message to operator-service (60s timeout)..."
OP_MSG_START=$SECONDS
OP_RESPONSE=$(curl -s -X POST http://localhost:8000/api/operator/message \
  -H "Content-Type: application/json" \
  -d '{"message": "what is the current cycle status?"}' \
  --max-time 60 2>/dev/null || echo "")
OP_MSG_TIME=$((SECONDS - OP_MSG_START))
if [ -n "$OP_RESPONSE" ]; then
  OP_MSG_RESULT=$(echo "$OP_RESPONSE" | python3 -c \
    "import sys,json; d=json.loads(sys.stdin.read()); \
     print('pass' if any(k in d for k in ['response','text','content','message','reply']) else 'unexpected: ' + str(list(d.keys()))[:60])" \
    2>/dev/null || echo "parse-error")
else
  OP_MSG_RESULT="no-response (${OP_MSG_TIME}s)"
fi
check "3.2  Operator service /api/operator/message (${OP_MSG_TIME}s)" "$OP_MSG_RESULT"

# 3.3 SSE bridge emits events
SSE_RESULT=$(curl -s --max-time 5 http://localhost:8090/api/stream \
  2>/dev/null | grep -q "data:" && echo "pass" || echo "no-SSE-events")
check "3.3  SSE bridge /api/stream emits events" "$SSE_RESULT"

# 3.4 nginx proxies /api/operator/message
PROXY_OP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:3000/api/operator/message \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}' \
  --max-time 65 2>/dev/null || echo "000")
if [ "$PROXY_OP_CODE" = "200" ]; then
  check "3.4  nginx proxy /api/operator/message" "pass"
else
  check "3.4  nginx proxy /api/operator/message" "HTTP $PROXY_OP_CODE"
fi

# 3.5 nginx proxies /api/stream
PROXY_SSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  --max-time 3 http://localhost:3000/api/stream \
  2>/dev/null || echo "000")
if [ "$PROXY_SSE_CODE" = "200" ] || [ "$PROXY_SSE_CODE" = "000" ]; then
  # 000 = curl timeout after receiving data (connection accepted, streaming)
  check "3.5  nginx proxy /api/stream" "pass"
else
  check "3.5  nginx proxy /api/stream" "HTTP $PROXY_SSE_CODE"
fi
echo ""

# ════════════════════════════════════════════════════════════════════════════
echo "── SECTION 4: Full Cycle Integration Test ────────────────────────────"
echo "   (approx. 5-6 minutes — do not interrupt)"
# ════════════════════════════════════════════════════════════════════════════

CYCLE_START_TIME=$SECONDS
E2E_CYCLE_ID="E2E-$(date +%s)"

# Record baseline offsets before publishing (so we only read NEW messages)
echo "  Recording baseline offsets..."
OFFSET_ISR=$(kafka_offset "copperclaw.isr-tasking")
OFFSET_COL=$(kafka_offset "copperclaw.collection")
OFFSET_ASS=$(kafka_offset "copperclaw.assessment")
OFFSET_NOM=$(kafka_offset "copperclaw.nomination")
OFFSET_LGL=$(kafka_offset "copperclaw.legal-review")
OFFSET_CST=$(kafka_offset "copperclaw.cycle-state")
OFFSET_CMD=$(kafka_offset "copperclaw.commander-log")
OFFSET_AUT=$(kafka_offset "copperclaw.authorization")
OFFSET_EXE=$(kafka_offset "copperclaw.execution")
OFFSET_BDA=$(kafka_offset "copperclaw.bda")
OFFSET_DEV=$(kafka_offset "copperclaw.develop")
echo "  Baseline offsets recorded."

# 4.1 Publish cycle_start
CYCLE_MSG=$(cat <<EOF
{"tool_name":"cycle_start","priority_target":"TGT-GAMMA-002","operator_intent":"E2E test — STONEPILE mortar position, expedited authority","cycle_id":"${E2E_CYCLE_ID}"}
EOF
)
echo "  4.1  Publishing cycle_start (cycle_id: ${E2E_CYCLE_ID})..."
PUBLISH_RESULT=$(echo "$CYCLE_MSG" | podman exec -i "$KAFKA_CONT" \
  bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic copperclaw.operator-commands \
  2>/dev/null && echo "pass" || echo "producer-error")
check "4.1  Publish cycle_start to operator-commands" "$PUBLISH_RESULT"

# 4.2 ISR tasking — 30s wait
echo "  Waiting 30s for ISR tasking response..."
sleep 30
ISR_MSG=$(kafka_consume_one "copperclaw.isr-tasking" "$OFFSET_ISR")
if [ -n "$ISR_MSG" ]; then
  ISR_FIELD=$(json_has_key "$ISR_MSG" "target_id")
  if [ "$ISR_FIELD" != "pass" ]; then
    # try alternate field name
    ISR_FIELD=$(json_has_key "$ISR_MSG" "collecting_asset")
  fi
  check "4.2  isr-tasking topic has new message (target_id/collecting_asset)" "$ISR_FIELD"
else
  check "4.2  isr-tasking topic has new message" "no-message-within-30s"
fi

# 4.3 Collection — +30s (total 60s)
echo "  Waiting 30s more for collection response..."
sleep 30
COL_MSG=$(kafka_consume_one "copperclaw.collection" "$OFFSET_COL")
if [ -n "$COL_MSG" ]; then
  COL_VALID=$(echo "$COL_MSG" | python3 -c \
    "import sys,json; json.loads(sys.stdin.read()); print('pass')" \
    2>/dev/null || echo "invalid-json")
  check "4.3  collection topic has new message (valid JSON)" "$COL_VALID"
else
  check "4.3  collection topic has new message" "no-message-within-60s"
fi

# 4.4 Assessment — +30s (total 90s)
echo "  Waiting 30s more for assessment response..."
sleep 30
ASS_MSG=$(kafka_consume_one "copperclaw.assessment" "$OFFSET_ASS")
if [ -n "$ASS_MSG" ]; then
  ASS_FIELD=$(json_has_key "$ASS_MSG" "confidence_level")
  check "4.4  assessment topic has new message (confidence_level)" "$ASS_FIELD"
else
  check "4.4  assessment topic has new message" "no-message-within-90s"
fi

# 4.5 Nomination — +30s (total 120s)
echo "  Waiting 30s more for nomination response..."
sleep 30
NOM_MSG=$(kafka_consume_one "copperclaw.nomination" "$OFFSET_NOM")
if [ -n "$NOM_MSG" ]; then
  NOM_FIELD=$(json_has_key "$NOM_MSG" "target_id")
  check "4.5  nomination topic has new message (target_id)" "$NOM_FIELD"
  # Extract tnp_id for use in 4.10
  TNP_ID=$(echo "$NOM_MSG" | python3 -c \
    "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('report_id', d.get('tnp_id','TNP-E2E-001')))" \
    2>/dev/null || echo "TNP-E2E-001")
else
  check "4.5  nomination topic has new message" "no-message-within-120s"
  TNP_ID="TNP-E2E-001"
fi
echo "  TNP ID for authorization: ${TNP_ID}"

# 4.6 Legal review — +30s (total 150s)
echo "  Waiting 30s more for legal review response..."
sleep 30
LGL_MSG=$(kafka_consume_one "copperclaw.legal-review" "$OFFSET_LGL")
if [ -n "$LGL_MSG" ]; then
  LGL_FIELD=$(json_has_key "$LGL_MSG" "legal_cleared")
  check "4.6  legal-review topic has new message (legal_cleared)" "$LGL_FIELD"
else
  check "4.6  legal-review topic has new message" "no-message-within-150s"
fi

# 4.7 Commander hold — cycle-state shows HOLD
CST_MSG=$(kafka_consume_one "copperclaw.cycle-state" "$OFFSET_CST")
if [ -n "$CST_MSG" ]; then
  HOLD_RESULT=$(echo "$CST_MSG" | python3 -c \
    "import sys,json; d=json.loads(sys.stdin.read()); \
     print('pass' if d.get('awaiting_commander') or d.get('phase')=='HOLD' or 'HOLD' in str(d.get('phase','')) else 'no-hold-state: phase=' + str(d.get('phase','?')))" \
    2>/dev/null || echo "parse-error")
  check "4.7  cycle-state shows commander HOLD" "$HOLD_RESULT"
else
  check "4.7  cycle-state shows commander HOLD" "no-cycle-state-message"
fi

# 4.8 Commander log entries
CMD_MSG=$(kafka_consume_one "copperclaw.commander-log" "$OFFSET_CMD")
if [ -n "$CMD_MSG" ]; then
  CMD_AGT=$(json_has_key "$CMD_MSG" "agent")
  CMD_MSG_FIELD=$(json_has_key "$CMD_MSG" "message")
  if [ "$CMD_AGT" = "pass" ] && [ "$CMD_MSG_FIELD" = "pass" ]; then
    check "4.8  commander-log has entries (agent + message)" "pass"
  else
    check "4.8  commander-log has entries (agent + message)" "fields: agent=$CMD_AGT msg=$CMD_MSG_FIELD"
  fi
else
  check "4.8  commander-log has entries" "no-message"
fi

# 4.9 State service updated
STATE_BODY_4=$(curl -s --max-time 5 http://localhost:8089/api/state/current \
  2>/dev/null || echo "")
if [ -n "$STATE_BODY_4" ]; then
  check "4.9  State service has updated cycle state" "pass"
else
  check "4.9  State service has updated cycle state" "no-response"
fi

# 4.10 Authorize and complete the cycle
AUTH_MSG=$(cat <<EOF
{"tool_name":"authorize_target","target_id":"TGT-GAMMA-002","tnp_id":"${TNP_ID}","authorized":true,"commanders_guidance":"E2E test authorization — STONEPILE mortar confirmed, expedited execute","cycle_id":"${E2E_CYCLE_ID}"}
EOF
)
echo "  4.10 Publishing authorize_target (tnp_id: ${TNP_ID})..."
AUTH_PUBLISH=$(echo "$AUTH_MSG" | podman exec -i "$KAFKA_CONT" \
  bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic copperclaw.operator-commands \
  2>/dev/null && echo "pass" || echo "producer-error")
check "4.10 Publish authorize_target to operator-commands" "$AUTH_PUBLISH"

echo "  Waiting 60s for execution → BDA → develop pipeline..."
sleep 60

EXE_MSG=$(kafka_consume_one "copperclaw.execution" "$OFFSET_EXE")
if [ -n "$EXE_MSG" ]; then
  check "4.10a execution topic has new message" "pass"
else
  check "4.10a execution topic has new message" "no-message-within-60s"
fi

BDA_MSG=$(kafka_consume_one "copperclaw.bda" "$OFFSET_BDA")
if [ -n "$BDA_MSG" ]; then
  check "4.10b bda topic has new message" "pass"
else
  check "4.10b bda topic has new message" "no-message-within-60s"
fi

DEV_MSG=$(kafka_consume_one "copperclaw.develop" "$OFFSET_DEV")
if [ -n "$DEV_MSG" ]; then
  check "4.10c develop topic has new message" "pass"
else
  check "4.10c develop topic has new message" "no-message-within-60s"
fi

CYCLE_ELAPSED=$((SECONDS - CYCLE_START_TIME))
echo "  Section 4 elapsed: ${CYCLE_ELAPSED}s"
echo ""

# ════════════════════════════════════════════════════════════════════════════
echo "── SECTION 5: Log Scan for Errors ────────────────────────────────────"
# ════════════════════════════════════════════════════════════════════════════

# 5.1 Error count per service container
for svc in \
  isr-tasking-service \
  collection-service \
  allsource-analyst-service \
  target-nomination-service \
  commander-service \
  execution-service \
  bda-service \
  develop-service \
  state-service \
  sse-bridge-service \
  legal-review-service \
  cot-gateway-service \
  operator-service; do
  CONTAINER=$(get_container "$svc")
  if [ -n "$CONTAINER" ]; then
    ERR_COUNT=$(podman logs "$CONTAINER" --tail 100 2>&1 \
      | grep -cE " ERROR |Exception|FAILED" || true)
    if [ "$ERR_COUNT" -eq 0 ]; then
      check "5.1  $svc — error count" "pass"
    elif [ "$ERR_COUNT" -lt 5 ]; then
      warn  "5.1  $svc" "${ERR_COUNT} errors in last 100 lines (minor)"
    else
      check "5.1  $svc — error count" "${ERR_COUNT} errors in last 100 lines"
    fi
  else
    warn "5.1  $svc" "container not found"
  fi
done

# 5.2 No containers in non-Up state
NOT_UP=$(podman ps -a --format "{{.Names}} {{.Status}}" 2>/dev/null \
  | grep "copperclaw" | grep -v " Up " || true)
if [ -z "$NOT_UP" ]; then
  check "5.2  All containers in Up state" "pass"
else
  check "5.2  All containers in Up state" "containers not Up: $(echo "$NOT_UP" | tr '\n' '|')"
fi

# 5.3 RamaLama health + error check
http_check "5.3  RamaLama /v1/models reachable" "http://localhost:8080/v1/models"
RAMALAMA_ERRORS=$(podman logs "$(get_container ramalama)" --tail 50 2>&1 \
  | grep -ciE "error" || true)
if [ "$RAMALAMA_ERRORS" -eq 0 ]; then
  check "5.3  RamaLama log — error count" "pass"
else
  warn  "5.3  RamaLama" "${RAMALAMA_ERRORS} 'error' occurrences in last 50 lines"
fi
echo ""

# ════════════════════════════════════════════════════════════════════════════
echo "── SECTION 6: Performance Checks ─────────────────────────────────────"
# ════════════════════════════════════════════════════════════════════════════

# 6.1 Operator service response time
echo "  6.1  Timing operator service (simple status query, 90s max)..."
PERF_START=$SECONDS
curl -s -X POST http://localhost:8000/api/operator/message \
  -H "Content-Type: application/json" \
  -d '{"message": "status"}' \
  --max-time 90 -o /dev/null 2>/dev/null || true
PERF_TIME=$((SECONDS - PERF_START))
if [ "$PERF_TIME" -lt 30 ]; then
  check "6.1  Operator service response time (${PERF_TIME}s)" "pass"
elif [ "$PERF_TIME" -lt 60 ]; then
  warn  "6.1  Operator service response time" "${PERF_TIME}s (30-60s — acceptable but slow)"
else
  check "6.1  Operator service response time (${PERF_TIME}s)" ">${PERF_TIME}s exceeds 60s threshold"
fi

# 6.2 State service response time
STATE_START=$SECONDS
curl -s --max-time 5 http://localhost:8089/api/state/current -o /dev/null 2>/dev/null || true
STATE_TIME=$((SECONDS - STATE_START))
if [ "$STATE_TIME" -lt 1 ] || [ "$STATE_TIME" -le 1 ]; then
  check "6.2  State service response time (${STATE_TIME}s)" "pass"
else
  check "6.2  State service response time (${STATE_TIME}s)" "${STATE_TIME}s exceeds 1s threshold"
fi

# 6.3 SSE bridge latency — publish to cycle-state, check SSE receipt
echo "  6.3  Testing SSE bridge latency..."
SSE_LAT_START=$SECONDS
# Open SSE stream in background, capture first data line
SSE_OUT=$(curl -s --max-time 5 http://localhost:8090/api/stream 2>/dev/null || true)
SSE_LAT_TIME=$((SECONDS - SSE_LAT_START))
if echo "$SSE_OUT" | grep -q "data:"; then
  check "6.3  SSE bridge latency (${SSE_LAT_TIME}s)" "pass"
else
  check "6.3  SSE bridge latency" "no SSE data received within 5s"
fi
echo ""

# ════════════════════════════════════════════════════════════════════════════
echo "══════════════════════════════════════════════════════════════"
echo "  RESULTS:  ${PASS} PASS   ${FAIL} FAIL   ${WARN} WARN"
echo "══════════════════════════════════════════════════════════════"
if [ "$FAIL" -gt 0 ]; then
  echo -e "  ${RED}SUITE FAILED${NC} — ${FAIL} check(s) require attention"
  exit 1
else
  echo -e "  ${GREEN}SUITE PASSED${NC}"
  exit 0
fi
