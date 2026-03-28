# COPPERCLAW

A simulation of the **F3EAD targeting cycle** (Find–Fix–Finish–Exploit–Assess–Develop) using LLM agents. Built as a reference implementation for sovereign, open-standards-based decision acceleration, compatible with NATO and UK MoD tooling.

---

## Overview

COPPERCLAW orchestrates 13 microservices across the full targeting workflow:

| Phase | Services |
|---|---|
| **Find / Fix** | ISR tasking, sensor collection, all-source intelligence fusion |
| **Finish** | Target nomination, legal review (ROE/CDE/LOAC), commander authorization |
| **Exploit / Assess / Develop** | Execution simulation, battle damage assessment, lead generation |

All services communicate over Apache Kafka. An LLM agent runs at each decision point, backed by either a local [RamaLama](https://ramalama.ai/) runtime (air-gapped default) or Anthropic Claude (cloud optional). A React/TypeScript frontend and Python FastAPI operator interface complete the stack.

The CoT Gateway speaks **Cursor on Target (CoT)** standard, enabling integration with ATAK, Sitaware, Lattice, and ASGARD.

---

## Architecture

```
Frontend (React)  ←SSE→  SSE Bridge  ←Kafka←  State Service
      ↓                                              ↑
Operator Service (FastAPI / Claude)        cycle-state topic
      ↓
 operator-commands topic
      ↓
ISR Tasking → Collection → All-Source Analyst
                                   ↓
                         Target Nomination → Legal Review
                                                   ↓
                                          Commander (hold point)
                                                   ↓
                              Execution → BDA → Develop → (loop)

CoT Gateway ←→ cot-in / cot-out topics ←→ ATAK / Sitaware / Lattice
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full reference.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent services (×10) | Java 21 + Quarkus 3.9.4 + LangChain4j 0.36.0 |
| Operator service | Python 3.11 + FastAPI + Anthropic SDK |
| Frontend | React 18.3 + TypeScript 5.4 + Vite 5.2 |
| Message bus | Apache Kafka 3.7.0 (14 topics) |
| Database | PostgreSQL 15 (plain JDBC, no ORM) |
| LLM runtime | RamaLama (local) or Anthropic Claude (cloud) |
| Containers | Podman + podman-compose (OpenShift-ready) |

---

## Prerequisites

- Java 21 JDK
- Maven 3.9+
- Python 3.11+
- Podman + podman-compose (or Docker / docker-compose)
- `ANTHROPIC_API_KEY` — optional; only required if `LLM_BACKEND=anthropic`

---

## Getting Started

### 1. Build

```bash
# Install shared Java library
mvn install -f shared-java/pom.xml

# Build all Quarkus services
mvn package -f parent-pom.xml -DskipTests
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — set LLM_BACKEND, model, and optionally ANTHROPIC_API_KEY
```

### 3. Run

```bash
podman-compose up
```

### 4. Access

| Interface | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Operator API | http://localhost:8000 |
| Kafka | localhost:9092 |
| PostgreSQL | localhost:5432 |
| RamaLama (LLM) | http://localhost:8080/v1 |

### 5. Smoke test

```bash
./scripts/smoke-test.sh
```

Validates all 13 service health endpoints and the end-to-end Kafka flow.

---

## Configuration

Key variables in `.env` (see `.env.example` for full list):

| Variable | Default | Description |
|---|---|---|
| `LLM_BACKEND` | `ramalama` | `ramalama` (local/air-gapped) or `anthropic` (cloud) |
| `LLM_MODEL` | `qwen2.5:14b` | Model identifier |
| `RAMALAMA_BASE_URL` | `http://localhost:8080/v1` | OpenAI-compatible endpoint |
| `ANTHROPIC_API_KEY` | — | Required when `LLM_BACKEND=anthropic` |
| `COT_SIMULATION_MODE` | `true` | Generate synthetic CoT events (no external hardware needed) |
| `COT_SIMULATION_INTERVAL_SECONDS` | `30` | Interval for synthetic events |

---

## Service Map

| Service | Port | Role |
|---|---|---|
| operator-service | 8000 | Operator LLM + tool orchestration |
| isr-tasking-service | 8081 | ISR collection manager |
| collection-service | 8082 | Sensor / platform simulator |
| allsource-analyst-service | 8083 | Intelligence fusion |
| target-nomination-service | 8084 | Targeting officer |
| commander-service | 8085 | COMKJTF decision hold point |
| execution-service | 8086 | Effects simulator |
| bda-service | 8087 | Battle damage assessment |
| develop-service | 8088 | DOMEX / lead generation |
| state-service | 8089 | Cycle state aggregation |
| sse-bridge-service | 8090 | Kafka → SSE stream broker |
| cot-gateway-service | 8091 | CoT ↔ JSON translation |
| legal-review-service | 8092 | ROE / CDE / LOAC compliance |
| frontend | 3000 | React web UI |

---

## Key Features

- **Full F3EAD simulation** — LLM agent at every decision point in the cycle
- **Legal review service** — dedicated ROE/CDE/LOAC compliance check (PRIISM analog)
- **CoT gateway** — bidirectional CoT XML ↔ internal JSON; UDP multicast and TAK TCP transport
- **Hybrid LLM backend** — local RamaLama (air-gapped) or Anthropic cloud, configurable per service
- **Event-driven** — 14 Kafka topics; compacted `cycle-state` topic for state aggregation
- **Simulation mode** — synthetic CoT event generation for self-contained demos
- **Classification marking** — all messages tagged `COSMIC INDIGO // REL KESTREL COALITION` with exercise serial support
- **OpenShift-ready** — Podman-native; AMQ Streams operator manifests in Phase 6 docs

---

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — service mesh, Kafka topics, CoT gateway detail
- [`docs/SCHEMAS.md`](docs/SCHEMAS.md) — message schema reference
- [`docs/PLATFORM_ANNEX.md`](docs/PLATFORM_ANNEX.md) — deployment and platform notes

---

## Disclaimer

COPPERCLAW is a simulation and reference implementation. It does not connect to, control, or interact with any real weapons system, sensor network, or operational military infrastructure.
