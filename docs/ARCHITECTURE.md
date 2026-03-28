# ARCHITECTURE — OPERATION COPPERCLAW
COSMIC INDIGO // REL KESTREL COALITION | EXERCISE — EXERCISE — EXERCISE

Full Red Hat stack architecture for the COPPERCLAW F3EAD targeting simulation.

---

## 1. Eight Quarkus Agent Microservices

Each agent microservice is a Quarkus application that consumes from one Kafka topic, calls the Claude API to generate a structured report, and publishes the result to its output topic. All services are stateless per message; the CycleState is maintained by the state-service.

| Service | Input Topic | Output Topic | Claude API Call |
|---|---|---|---|
| isr-tasking-service | copperclaw.cycle-state | copperclaw.isr-tasking | Generates ISRTaskingOrder: selects PIR, assets, collection window based on CycleState. |
| collection-service | copperclaw.isr-tasking | copperclaw.collection | Generates CollectionReport: simulates sensor collection against tasked PIR/target. |
| assessment-service | copperclaw.collection | copperclaw.assessment | Generates IntelligenceAssessment: fuses multiple CollectionReports into all-source assessment. |
| nomination-service | copperclaw.assessment | copperclaw.nomination | Generates TargetNominationPackage: applies ROE Card Alpha-7, CDE, completes ROE checklist. |
| commander-service | copperclaw.nomination | copperclaw.authorization | Generates EngagementAuthorization: reviews TNP as COMKJTF; may be operator-injected. |
| execution-service | copperclaw.authorization | copperclaw.execution | Generates ExecutionReport: simulates fires/effects action against confirmed target grid. |
| bda-service | copperclaw.execution | copperclaw.bda | Generates BDAReport: assesses physical, functional, and network effects against desired effect. |
| develop-service | copperclaw.bda | copperclaw.develop | Generates DevelopLead: extracts DOMEX leads, generates new PIRs, recommends next cycle target. |

---

## 2. Python/FastAPI Operator Service

The operator-service is a Python/FastAPI application that provides:

- **Kafka consumer:** subscribes to all 11 topics (cycle-state, isr-tasking, collection, assessment, nomination, authorization, execution, bda, develop, commander-log, operator-commands)
- **Live CycleState:** maintains current CycleState in memory, updated on every Kafka message
- **SSE endpoint:** `GET /api/v1/stream` — streams SSEEvent JSON to the React frontend using Server-Sent Events
- **Kafka producer:** publishes to copperclaw.operator-commands and copperclaw.cycle-state
- **Operator LLM:** Claude API call with full CycleState context; can invoke six tool calls:
  - `cycle_start` — initiate a new F3EAD cycle
  - `retask_isr` — redirect named ISR asset to new target/PIR
  - `authorize_target` — inject COMKJTF engagement authorization into Commander agent
  - `hold_target` — place target on hold
  - `request_bda` — direct immediate BDA assessment
  - `inject_commander_guidance` — inject COMKJTF guidance into cycle state and agent contexts
- The operator LLM tool results are published as SSEEvents and written to the commander log

---

## 3. Quarkus State Service

- **Service:** state-service (Quarkus/Kafka Streams)
- **Consumes:** all agent output topics (isr-tasking, collection, assessment, nomination, authorization, execution, bda, develop, commander-log)
- **Maintains:** persistent CycleState in PostgreSQL (one row per cycle_id, updated on each new report)
- **Republishes:** updated CycleState to copperclaw.cycle-state after every state mutation
- **Ensures:** monotonically increasing cycle_sequence on each CycleState publish
- **Serves:** REST endpoint for CycleState retrieval by cycle_id

---

## 4. Quarkus SSE Bridge

- **Service:** sse-bridge-service (Quarkus/Reactive)
- **Consumes:** all Kafka topics (all 11)
- **Wraps:** each consumed message in SSEEvent envelope with event_type, cycle_id, sequence, timestamp_zulu, data
- **Streams:** SSEEvent JSON to React frontend via `GET /api/v1/stream` using Quarkus Reactive SSE
- **Frontend:** React app connects with EventSource; routes on event_type to update the correct UI panel
- **Note:** The Python operator-service also has an SSE endpoint; the Quarkus SSE bridge serves the main frontend stream

---

## 5. Canonical Cycle Flow Diagram

```
OPERATOR INPUT
      │
      ▼
┌─────────────────┐
│  cycle_start    │──────────────────────────────────────────────────┐
│  (operator tool)│                                                  │
└─────────────────┘                                                  │
                                                                     ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        F3EAD TARGETING CYCLE                                 ║
║                                                                               ║
║  FIND ──────────────────────────────────────────────────────────────────────  ║
║  │                                                                            ║
║  │  [ISR-TASKING-SERVICE]                                                     ║
║  │  copperclaw.cycle-state → ISRTaskingOrder → copperclaw.isr-tasking         ║
║  │                                                                            ║
║  FIX ───────────────────────────────────────────────────────────────────────  ║
║  │                                                                            ║
║  │  [COLLECTION-SERVICE]                                                      ║
║  │  copperclaw.isr-tasking → CollectionReport → copperclaw.collection         ║
║  │                                                                            ║
║  │  [ASSESSMENT-SERVICE]                                                      ║
║  │  copperclaw.collection → IntelligenceAssessment → copperclaw.assessment    ║
║  │                                                                            ║
║  │  ┌─ PID not met? → retask ISR (operator: retask_isr) → back to FIND ──┐   ║
║  │  └──────────────────────────────────────────────────────────────────── ┘   ║
║  │                                                                            ║
║  FINISH ────────────────────────────────────────────────────────────────────  ║
║  │                                                                            ║
║  │  [NOMINATION-SERVICE]                                                      ║
║  │  copperclaw.assessment → TargetNominationPackage → copperclaw.nomination   ║
║  │                                                                            ║
║  │  *** COMMANDER HOLD POINT ***                                              ║
║  │  [COMMANDER-SERVICE] ← operator: authorize_target / hold_target            ║
║  │  copperclaw.nomination → EngagementAuthorization → copperclaw.authorization║
║  │                                                                            ║
║  │  ┌─ authorized=False? → HOLD phase → await operator input ─────────────┐  ║
║  │  └──────────────────────────────────────────────────────────────────── ┘  ║
║  │                                                                            ║
║  EXPLOIT ───────────────────────────────────────────────────────────────────  ║
║  │                                                                            ║
║  │  [EXECUTION-SERVICE]                                                       ║
║  │  copperclaw.authorization → ExecutionReport → copperclaw.execution         ║
║  │                                                                            ║
║  ASSESS ────────────────────────────────────────────────────────────────────  ║
║  │                                                                            ║
║  │  [BDA-SERVICE]                                                             ║
║  │  copperclaw.execution → BDAReport → copperclaw.bda                         ║
║  │                                                                            ║
║  │  operator: request_bda (out-of-cycle immediate BDA)                        ║
║  │                                                                            ║
║  DEVELOP ───────────────────────────────────────────────────────────────────  ║
║  │                                                                            ║
║  │  [DEVELOP-SERVICE]                                                         ║
║  │  copperclaw.bda → DevelopLead → copperclaw.develop                         ║
║  │                                                                            ║
║  └──── new leads → back to FIND (next cycle) ───────────────────────────────  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

STATE LAYER:
  All topics ──▶ [STATE-SERVICE] ──▶ PostgreSQL + copperclaw.cycle-state

SSE STREAM:
  All topics ──▶ [SSE-BRIDGE-SERVICE] ──▶ React frontend (EventSource)

OPERATOR LAYER:
  Operator CLI ──▶ [OPERATOR-SERVICE] ──▶ Operator LLM (Claude API)
                                       ──▶ copperclaw.operator-commands
                                       ──▶ copperclaw.cycle-state
```

---

## 6. Commander Hold Point

The commander hold point is the human-in-the-loop gate in the FINISH phase:

1. nomination-service publishes TargetNominationPackage to copperclaw.nomination
2. state-service updates CycleState.pending_commander_decision = TNP report_id
3. CycleState republished with pending_commander_decision populated
4. SSE bridge streams the updated CycleState to frontend
5. Frontend detects pending_commander_decision != null → renders Commander Decision UI (Approve/Hold/More Intel)
6. Operator reviews TNP and issues one of:
   - `authorize_target` tool call → operator-service publishes to copperclaw.operator-commands
   - `hold_target` tool call → operator-service publishes hold instruction
7. operator-commands consumed by commander-service
8. commander-service generates EngagementAuthorization with operator_injected=True, operator_instruction populated
9. If authorized=True → execution-service proceeds
10. If authorized=False → CycleState.overall_phase = HOLD; cycle pauses until operator resumes
11. All decisions written to CommanderLogEntry on copperclaw.commander-log

---

## 7. Local Development: Podman Compose Services Required

```yaml
services:
  kafka:          # Apache Kafka (AMQ Streams compatible) — port 9092
  zookeeper:      # Zookeeper for Kafka — port 2181
  kafka-ui:       # Kafka UI for topic inspection — port 8080
  postgres:       # PostgreSQL 15 for state-service — port 5432
  isr-tasking-service:    # Quarkus agent — port 8081
  collection-service:     # Quarkus agent — port 8082
  assessment-service:     # Quarkus agent — port 8083
  nomination-service:     # Quarkus agent — port 8084
  commander-service:      # Quarkus agent — port 8085
  execution-service:      # Quarkus agent — port 8086
  bda-service:            # Quarkus agent — port 8087
  develop-service:        # Quarkus agent — port 8088
  state-service:          # Quarkus Kafka Streams — port 8089
  sse-bridge-service:     # Quarkus Reactive — port 8090
  operator-service:       # Python/FastAPI — port 8091
  frontend:               # React (Vite) — port 3000
```

All Quarkus services require: `KAFKA_BOOTSTRAP_SERVERS`, `ANTHROPIC_API_KEY`
operator-service requires: `KAFKA_BOOTSTRAP_SERVERS`, `ANTHROPIC_API_KEY`, `POSTGRES_URL`
state-service requires: `KAFKA_BOOTSTRAP_SERVERS`, `POSTGRES_URL`

---

## 8. OpenShift: AMQ Streams Operator, Required CRDs

Deploy on OpenShift using the Red Hat AMQ Streams Operator (based on Strimzi):

### Operator Installation

```
Red Hat AMQ Streams Operator
Namespace: copperclaw
Channel: stable
Install Mode: SingleNamespace
```

### Required CRDs (created by AMQ Streams Operator)

- `Kafka` — defines the Kafka cluster (3 broker replicas, 3 ZooKeeper replicas)
- `KafkaTopic` — declares each of the 11 COPPERCLAW topics with replication factor 3
- `KafkaUser` — SCRAM-SHA-512 credentials for each service
- `KafkaConnect` (optional) — for external connector integration

### KafkaTopic CR example (one per topic)

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: copperclaw-cycle-state
  labels:
    strimzi.io/cluster: copperclaw-kafka
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000   # 7 days
    cleanup.policy: latest
```

### All 11 topics to create as KafkaTopic CRs

```
copperclaw.isr-tasking
copperclaw.collection
copperclaw.assessment
copperclaw.nomination
copperclaw.authorization
copperclaw.execution
copperclaw.bda
copperclaw.develop
copperclaw.cycle-state
copperclaw.commander-log
copperclaw.operator-commands
```

### Deployment notes

- **Quarkus services:** Deploy as OpenShift Deployments with ConfigMaps for Kafka bootstrap and Secrets for ANTHROPIC_API_KEY.
- **operator-service:** Deploy as a Deployment with PostgreSQL via CrunchyData PGO or a simple StatefulSet.
- **Frontend:** Deploy as a Deployment behind a Route.
