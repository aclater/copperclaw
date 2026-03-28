# OPERATION COPPERCLAW — Architecture Reference
COSMIC INDIGO // REL KESTREL COALITION // EXERCISE — EXERCISE — EXERCISE

---

## Executive Summary

COPPERCLAW is a Red Hat–native, event-driven simulation of the F3EAD targeting
cycle (Find–Fix–Finish–Exploit–Assess–Develop) using LLM agents. It is designed
as a reference implementation demonstrating sovereign, open-standards-based
decision acceleration for NATO and UK MoD audiences.

**Strategic positioning:**

| Programme | Technology | COPPERCLAW relationship |
|---|---|---|
| **ASGARD** (UK MoD Digital Targeting Web) | CoT/XML mesh, Sitaware, Lattice, Altra, PRIISM, ATAK | Speaks CoT natively; models the DECIDE layer; PRIISM-analog Legal Review Service |
| **DDAfD** (Digital Decision Accelerators for Defence) | 26 contracts Jan 2026, five lots, Anduril/Helsing/Faculty AI | Positionable as reference implementation for Lot responses on AI-assisted targeting |
| **NATO MSS** (Palantir Maven Smart System) | Palantir Ontology on AWS Stockholm, SHAPE/JFC Brunssum | Sovereign alternative: same open standards (CoT, REST, Kafka), no Palantir, no AWS dependency |

COPPERCLAW runs entirely on Red Hat OpenShift with AMQ Streams (Kafka) as the
event bus, speaks Cursor on Target (CoT) as its external interface, and keeps
all LLM calls within a sovereign compute boundary. The architecture is derived
from the Emergency Response Demo pattern (`github.com/Emergency-Response-Demo`).

---

## Service Inventory

| Service | Language | Port | Input Topic(s) | Output Topic(s) | Role |
|---|---|---|---|---|---|
| `isr-tasking-service` | Quarkus/Java 21 | 8081 | `operator-commands`, `develop` | `isr-tasking` | J2 Collection Manager — translates PIRs to ISR tasks |
| `collection-service` | Quarkus/Java 21 | 8082 | `isr-tasking` | `collection` | Sensor/platform simulator — generates CollectionReports |
| `allsource-analyst-service` | Quarkus/Java 21 | 8083 | `collection` | `assessment` | J2 Fusion — accumulates reports, produces IntelligenceAssessment |
| `target-nomination-service` | Quarkus/Java 21 | 8084 | `assessment` | `nomination` | Targeting Officer — produces TargetNominationPackage |
| `legal-review-service` | Quarkus/Java 21 | 8092 | `nomination` | `legal-review` | PRIISM analog — ROE/CDE/LOAC compliance checklist |
| `commander-service` | Quarkus/Java 21 | 8085 | `legal-review`, `operator-commands` | `authorization`, `cycle-state` | COMKJTF voice — HOLD POINT, produces EngagementAuthorization |
| `execution-service` | Quarkus/Java 21 | 8086 | `authorization` | `execution`, `cot-out` | Fires/effects simulator |
| `bda-service` | Quarkus/Java 21 | 8087 | `execution` | `bda`, `cot-out` | Battle Damage Assessment |
| `develop-service` | Quarkus/Java 21 | 8088 | `bda` | `develop` | DOMEX/lead generation — closes loop to Find |
| `state-service` | Quarkus/Java 21 | 8089 | ALL internal topics | `cycle-state` | CycleState aggregator — PostgreSQL + compacted topic |
| `sse-bridge-service` | Quarkus/Java 21 | 8090 | `cycle-state`, `commander-log` | SSE (HTTP) | Kafka → browser SSE stream |
| `cot-gateway-service` | Quarkus/Java 21 | 8091 | UDP multicast / TAK TCP, `cot-out` | `collection` (cot-in→JSON), UDP/TAK (cot-out) | CoT↔JSON translation; external sensor/effector boundary |
| `operator-service` | Python/FastAPI | 8000 | `cycle-state` (REST), `operator-commands` (publish) | SSE (HTTP) | Operator LLM conversation + tool use |

---

## Kafka Topic Map

### External boundary topics (CoT XML strings)
| Topic | Direction | Format | Description |
|---|---|---|---|
| `copperclaw.cot-in` | Inbound | CoT XML | Raw CoT events from external sensors, TAK clients, Altra drones |
| `copperclaw.cot-out` | Outbound | CoT XML | Execution and BDA events translated to CoT for effectors and ATAK display |

### Internal F3EAD cycle topics (JSON)
| Topic | Producer | Consumer(s) | Schema |
|---|---|---|---|
| `copperclaw.operator-commands` | operator-service | isr-tasking, commander | CycleStartTool / AuthorizeTargetTool / HoldTargetTool / etc. |
| `copperclaw.isr-tasking` | isr-tasking | collection | ISRTaskingOrder |
| `copperclaw.collection` | collection, cot-gateway | allsource-analyst, state | CollectionReport |
| `copperclaw.assessment` | allsource-analyst | target-nomination, state | IntelligenceAssessment |
| `copperclaw.nomination` | target-nomination | legal-review, state | TargetNominationPackage |
| `copperclaw.legal-review` | legal-review | commander, state | LegalReviewAssessment |
| `copperclaw.authorization` | commander | execution, state | EngagementAuthorization |
| `copperclaw.execution` | execution | bda, cot-gateway, state | ExecutionReport |
| `copperclaw.bda` | bda | develop, cot-gateway, state | BDAReport |
| `copperclaw.develop` | develop | isr-tasking, state | DevelopLead |

### State and streaming topics
| Topic | Producer | Consumer(s) | Notes |
|---|---|---|---|
| `copperclaw.cycle-state` | state-service | sse-bridge, operator-service | Compacted — only latest value per cycle_id key |
| `copperclaw.commander-log` | commander | sse-bridge, state | Append-only decision audit log |

---

## Canonical Flow Diagram

```
════════════════════════════════════════════════════════════════════════
EXTERNAL BOUNDARY
════════════════════════════════════════════════════════════════════════

  [Altra drones]  [ATAK clients]  [Sitaware C2]  [TAK Server]
        │                │               │              │
        └────────────────┴───────────────┴──────────────┘
                                 │ UDP multicast 239.2.3.1:6969
                                 │ or TAK TCP
                         ┌───────▼────────┐
                         │ cot-gateway    │ port 8091
                         │ CoT ↔ JSON     │◄── copperclaw.cot-out
                         └───────┬────────┘
                                 │ copperclaw.cot-in → copperclaw.collection
════════════════════════════════════════════════════════════════════════
FIND / FIX — PHASE SERPENT
════════════════════════════════════════════════════════════════════════

  [operator-service] ──────────────────────────────┐
    port 8000              operator-commands         │
    FastAPI + Claude                                 │
         ▲                                          ▼
         │ SSE             ┌──────────────────────────┐
         │                 │   isr-tasking-service    │ port 8081
  [sse-bridge] 8090        │   J2 Collection Manager  │◄── develop
         │                 └──────────┬───────────────┘
         │                            │ isr-tasking
         │                 ┌──────────▼───────────────┐
         │                 │   collection-service     │ port 8082
         │                 │   Sensor/Platform Sim    │◄── cot-gateway
         │                 └──────────┬───────────────┘
         │                            │ collection
         │                 ┌──────────▼───────────────┐
         │                 │ allsource-analyst        │ port 8083
         │                 │ J2 Fusion (accumulator)  │
         │                 └──────────┬───────────────┘
════════════════════════════════════════════════════════════════════════
FINISH — PHASE COPPER
════════════════════════════════════════════════════════════════════════
         │                            │ assessment
         │                 ┌──────────▼───────────────┐
         │                 │ target-nomination        │ port 8084
         │                 │ Targeting Officer        │
         │                 └──────────┬───────────────┘
         │                            │ nomination
         │                 ┌──────────▼───────────────┐
         │                 │ legal-review-service     │ port 8092
         │                 │ PRIISM analog (ROE/CDE)  │
         │                 └──────────┬───────────────┘
         │                            │ legal-review
         │                 ┌──────────▼───────────────┐
         │◄────────────────│ commander-service        │ port 8085
         │  AWAITING_CMD   │ COMKJTF — HOLD POINT     │
         │──────────────── │ authorize_target /       │
         │  operator input │ hold_target              │
         │                 └──────────┬───────────────┘
         │                            │ authorization (only after operator input)
         │                 ┌──────────▼───────────────┐
         │                 │ execution-service        │ port 8086
         │                 │ Fires/Effects Simulator  │──► cot-gateway (cot-out)
         │                 └──────────┬───────────────┘
════════════════════════════════════════════════════════════════════════
ASSESS / DEVELOP — PHASE CLAW
════════════════════════════════════════════════════════════════════════
         │                            │ execution
         │                 ┌──────────▼───────────────┐
         │                 │ bda-service              │ port 8087
         │                 │ Battle Damage Assessment │──► cot-gateway (cot-out)
         │                 └──────────┬───────────────┘
         │                            │ bda
         │                 ┌──────────▼───────────────┐
         │                 │ develop-service          │ port 8088
         │                 │ DOMEX / Lead Generation  │
         │                 └──────────┬───────────────┘
         │                            │ develop ──────────► isr-tasking (next cycle)
         │
════════════════════════════════════════════════════════════════════════
STATE AND STREAMING (subscribes ALL internal topics)
════════════════════════════════════════════════════════════════════════
         │
         │          ┌─────────────────────────────────────┐
         │          │ state-service            port 8089  │
         │          │ CycleState aggregator               │
         │          │ PostgreSQL (plain JDBC)             │
         │          │ Publishes: copperclaw.cycle-state   │
         │          └──────────────────────┬──────────────┘
         │                                 │ cycle-state
         │          ┌──────────────────────▼──────────────┐
         └──────────│ sse-bridge-service   port 8090      │
                    │ Kafka → SSE stream to frontend       │
                    └──────────────────────────────────────┘
```

---

## CoT Gateway Service

The CoT gateway is the external interface layer between COPPERCLAW and the
broader NATO targeting web. It implements the Cursor on Target (CoT) standard
(derived from MIL-STD-2525, used by ATAK, Sitaware, Lattice, and ASGARD).

### Inbound (sensor → COPPERCLAW)

The gateway listens on:
- **UDP multicast** `239.2.3.1:6969` — standard CoT multicast address used by
  ATAK, Altra, Lattice, and all ASGARD-compatible sensors
- **TAK Server TCP** (configurable host:port) — for authenticated TAK network connections

Incoming CoT XML is parsed and translated to a `CollectionReport` JSON object,
then published to `copperclaw.collection`. The All-Source Analyst treats these
reports identically to simulation-generated collection — the gateway is
transparent to all downstream agents.

CoT type mapping to COPPERCLAW intel source types:
- `a-h-G-U-C` (hostile ground unit confirmed) → `IMINT` or `HUMINT` based on sensor type in `<detail>`
- `a-h-G-E-S` (hostile ground unit suspected) → `IMINT`, confidence `UNCONFIRMED`
- `b-t-f` (friendly track) → not forwarded (filtered)

### Outbound (COPPERCLAW → effectors)

The gateway subscribes to `copperclaw.execution` and `copperclaw.bda`. On
receiving an `ExecutionReport` or `BDAReport`, it generates a CoT event and:
- Broadcasts on UDP multicast `239.2.3.1:6969`
- Pushes to TAK Server if configured

Execution events use CoT type `t-k` (task). BDA events use `t-b-a` (battle
damage assessment). COPPERCLAW-specific metadata (cycle_id, target_codename,
bda_outcome) is encoded in the CoT `<detail>` element.

### Simulation mode (default for demo)

When `COT_SIMULATION_MODE=true` (the default), the gateway generates synthetic
CoT events on a configurable timer (`COT_SIMULATION_INTERVAL_SECONDS`, default
30). Synthetic events simulate ISR sensor contacts against the five HPTL
targets, driving the collection pipeline without requiring external hardware.
This makes the demo entirely self-contained.

---

## Legal Review Service

The Legal Review Service is the COPPERCLAW analog to PRIISM (Research
Innovations), the dedicated legal review component in ASGARD. It extracts ROE
compliance checking, CDE assessment, and LOAC analysis from the Target
Nomination agent into an explicit, auditable service.

**Position in the cycle:** Between Target Nomination and Commander. The
Commander now consumes `LegalReviewAssessment` (not `TargetNominationPackage`
directly), ensuring every engagement decision has passed through structured
legal review before reaching COMKJTF.

**Processing logic:**
1. Receives `TargetNominationPackage` from `copperclaw.nomination`
2. Applies ROE Card Alpha-7 as a structured checklist (rule-based, not LLM):
   - Military necessity confirmed (target on HPTL, contributes to commander's objectives)
   - Distinction verified (`pid_standard_met` from ROEChecklist)
   - Proportionality assessed (CDE tier assigned based on target location and method)
   - Precaution applied (civilian window confirmed for RTL targets)
   - NSL check (distance from known NSL objects)
   - Engagement authority confirmed (authority table from ROE Alpha-7)
3. Calls Claude for the `legal_assessment` narrative (one paragraph, COMKJTF-grade language)
4. Produces `LegalReviewAssessment` to `copperclaw.legal-review`

**`legal_cleared: false`** blocks the cycle at the Commander. The Commander
service will not emit to `copperclaw.authorization` if it receives a
`LegalReviewAssessment` with `legal_cleared: false`, even if the operator
issues `authorize_target`. It surfaces the legal block in the cycle state for
operator awareness.

---

## Parallel Event Model

Agents are not sequential pipeline stages — they are event-driven consumers
that process any qualifying message on their input topic, regardless of origin.
This enables:

- **CoT injection:** Incoming CoT events from external sensors are published to
  `copperclaw.collection` by the gateway. The All-Source Analyst processes them
  identically to simulation-generated reports.
- **ISR retasking mid-cycle:** An operator `retask_isr` command produces a new
  `ISRTaskingOrder` mid-cycle. The Collection agent processes it and generates a
  new `CollectionReport`, which feeds back into the All-Source Analyst
  accumulator for the current cycle.
- **Multi-source fusion:** The All-Source Analyst maintains an in-memory
  accumulator (`ConcurrentHashMap<String, List<String>>` keyed by `cycle_id`)
  collecting all `CollectionReport` messages for a 10-second window before
  running a single Claude call. This produces fused assessments rather than
  one-report-in, one-assessment-out.

---

## Schema Additions

The following were added beyond the original Phase 2 schema library:

### `LegalReviewAssessment` (Python and Java)

| Field | Type | Description |
|---|---|---|
| `report_id` | str | UUID4 |
| `cycle_id` | str | Propagated from TNP |
| `classification` | ClassificationMarking | Always COSMIC INDIGO |
| `target_id` | TargetID | From TNP |
| `tnp_id` | str | report_id of upstream TNP |
| `timestamp_zulu` | datetime | Production time |
| `roe_checklist` | ROEChecklist | Completed checklist from TNP, validated |
| `cde_tier` | CDETier | Assigned CDE tier |
| `legal_assessment` | str | Claude-generated narrative |
| `legal_cleared` | bool | True = cleared for Commander review |
| `blocking_issues` | list[str] | If not cleared, list of blocking issues |
| `legal_reviewer` | str | Always "LEGAL-REVIEW-SERVICE" |
| `recommended_engagement_method` | ExecutionMethod | Validated method |

### New Kafka topic constants

| Constant | Value |
|---|---|
| `COT_IN` | `copperclaw.cot-in` |
| `COT_OUT` | `copperclaw.cot-out` |
| `LEGAL_REVIEW` | `copperclaw.legal-review` |

---

## Port Map

| Service | Port | Language |
|---|---|---|
| operator-service | 8000 | Python/FastAPI |
| isr-tasking-service | 8081 | Quarkus/Java 21 |
| collection-service | 8082 | Quarkus/Java 21 |
| allsource-analyst-service | 8083 | Quarkus/Java 21 |
| target-nomination-service | 8084 | Quarkus/Java 21 |
| commander-service | 8085 | Quarkus/Java 21 |
| execution-service | 8086 | Quarkus/Java 21 |
| bda-service | 8087 | Quarkus/Java 21 |
| develop-service | 8088 | Quarkus/Java 21 |
| state-service | 8089 | Quarkus/Java 21 |
| sse-bridge-service | 8090 | Quarkus/Java 21 |
| cot-gateway-service | 8091 | Quarkus/Java 21 |
| legal-review-service | 8092 | Quarkus/Java 21 |

---

## LLM Backend Configuration

COPPERCLAW defaults to local RamaLama inference.
RamaLama is Red Hat's container-native LLM runtime —
models are OCI artifacts, runtime is rootless Podman,
deployment target is OpenShift.

| Variable | Default | Description |
|---|---|---|
| LLM_BACKEND | ramalama | ramalama or anthropic |
| LLM_MODEL | qwen2.5:14b | model name |
| RAMALAMA_BASE_URL | http://localhost:8080/v1 | RamaLama API |
| ANTHROPIC_API_KEY | (empty) | required if backend=anthropic |

### GPU support
Current: NVIDIA CUDA — deploy.resources.reservations
in podman-compose.yml.
Future AMD ROCm migration: swap deploy block for
/dev/kfd and /dev/dri device mounts. No code changes
required — same OpenAI-compatible API surface.

### Local development
If RamaLama runs natively on host (not in compose):
  RAMALAMA_BASE_URL=http://localhost:8080/v1

If services run in compose and RamaLama on host:
  RAMALAMA_BASE_URL=http://host.containers.internal:8080/v1

### Air-gapped / briefing room
Set LLM_BACKEND=ramalama. Model pulled as OCI artifact
on first start. No internet required after pull.

### Anthropic API (opt-in, highest quality)
Set LLM_BACKEND=anthropic and ANTHROPIC_API_KEY.
Recommended for operator LLM if network available.
Hybrid config: set per-service for local agents
+ cloud operator.

---

## Local Development

### Prerequisites
- Java 21 (JDK), Maven 3.9+
- Python 3.11+
- Podman + podman-compose
- `ANTHROPIC_API_KEY` environment variable

### Build all Quarkus services
```bash
# Install shared Java library first
mvn install -f shared-java/pom.xml

# Build all services
mvn package -f parent-pom.xml -DskipTests
```

### Start locally
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
podman-compose up
```

### Service port map for local debugging
```bash
# Check all health endpoints
for port in 8081 8082 8083 8084 8085 8086 8087 8088 8089 8090 8091 8092; do
  curl -s http://localhost:$port/q/health | jq .status
done
curl -s http://localhost:8000/health
```

### Tail Kafka topics
```bash
# Watch the cycle in real time
podman exec -it copperclaw_kafka_1 \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic copperclaw.cycle-state \
  --from-beginning
```

### Send a test cycle_start
```bash
podman exec -it copperclaw_kafka_1 \
  bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic copperclaw.operator-commands <<EOF
{"tool_name":"cycle_start","priority_target":"TGT-ECHO-001","operator_intent":"Begin VARNAK location development — continue PIR-001 collection."}
EOF
```

---

## OpenShift Deployment

Deploy using AMQ Streams Operator for Kafka and standard OpenShift resources for services.

```bash
# Install AMQ Streams Operator (via OperatorHub in console, or:)
oc apply -f https://operatorhub.io/install/amq-streams.yaml

# Create Kafka cluster
oc apply -f openshift/kafka-cluster.yaml

# Create topics
oc apply -f openshift/kafka-topics.yaml

# Deploy services
oc apply -f openshift/deployments/

# Expose operator service
oc expose svc/operator-service
```

OpenShift manifests (Deployment, Service, Route per service) are generated in Phase 6.

---

## Design Decisions

- **CoT multicast address 239.2.3.1:6969** is the standard ATAK/TAK multicast group used across NATO forces and all ASGARD-compatible components.
- **Legal Review as a discrete service** (not embedded in Target Nomination) mirrors PRIISM's architecture in ASGARD and provides a clean audit boundary — every legal review is a discrete, persisted message on `copperclaw.legal-review`.
- **Parallel event model** (accumulator in All-Source Analyst) is necessary for CoT integration — external sensors produce bursts of reports, not one-at-a-time sequential messages.
- **Plain JDBC in state-service** (not Hibernate) avoids ByteBuddy failures in Java 25 host environments and keeps the state service dependency-minimal.
- **Simulation mode in CoT gateway** ensures the demo is self-contained and can run without any external hardware or network connectivity.
