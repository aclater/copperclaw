# COPPERCLAW — Project context for Claude Code

Read this file completely before touching any code.
This is not boilerplate — every section affects
decisions you will make.

═══════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════

Operation COPPERCLAW is an F3EAD targeting cycle
simulation using AI agents. It is a Red Hat field
demo — not a research project, not a product, not
a toy. It will be demonstrated to NATO customers,
UK MoD, and European defence ministries in Amsterdam
by a Chief Architect from Red Hat's Field CTO org.

Strategic positioning:
- Sovereign alternative to Palantir MSS NATO
  (deployed at SHAPE/JFC Brunssum on AWS)
- ASGARD DDAfD Decide-layer reference implementation
  (UK MoD digital targeting web)
- Runs entirely on OpenShift with AMQ Streams —
  no Palantir, no AWS, no proprietary dependency

The demo must work flawlessly in a briefing room.
Reliability beats features. If something is fragile,
fix it before adding anything new.

═══════════════════════════════════════════════════════════
WHAT IT DOES
═══════════════════════════════════════════════════════════

Models the NATO F3EAD cycle (Find-Fix-Finish-
Exploit-Assess-Develop) as event-driven microservices:

  Operator types plain English
       ↓
  Operator LLM (FastAPI/Python) translates to tool calls
       ↓
  Kafka event bus routes messages between agents
       ↓
  10 Quarkus agent services process each phase
       ↓
  Commander HOLD POINT — cycle pauses, waits for human
       ↓
  Operator authorizes → cycle completes
       ↓
  Frontend shows everything in real time

The HOLD POINT is the demo's key moment. An AI system
that processes intelligence autonomously and then stops
and waits for a human decision before acting. That is
the story. Do not break the hold point logic.

═══════════════════════════════════════════════════════════
SCENARIO (locked — do not change)
═══════════════════════════════════════════════════════════

Fictional state of VALDORIA. TF KESTREL. AO HARROW.
Classification: COSMIC INDIGO // REL KESTREL COALITION
All content: EXERCISE — EXERCISE — EXERCISE

Five targets on the HPTL:
  TGT-ECHO-001  VARNAK     HVI, capture preferred
  TGT-ECHO-002  KAZMER     HVI, capture preferred
  TGT-GAMMA-001 IRONBOX    C2 node, CDE required
  TGT-DELTA-001 OILCAN     Fuel depot, RTL, civilian window
  TGT-GAMMA-002 STONEPILE  Mortar position, expedited auth

Best first demo target: STONEPILE (expedited authority,
open terrain, no DOMEX value, clean kinetic engagement)

Demo start command:
  "initiate targeting cycle against STONEPILE —
   mortar threat to FOB GREYSTONE, priority immediate"

Demo authorization:
  "authorize M109A7 Paladin fire mission on STONEPILE
   — mortar position confirmed, CDE acceptable"

═══════════════════════════════════════════════════════════
ARCHITECTURE (locked — do not redesign)
═══════════════════════════════════════════════════════════

Runtime: podman-compose, 15+ containers
Target deploy: OpenShift + AMQ Streams Operator
Local dev: Fedora workstation, NVIDIA 4070 Ti

Services and ports:
  operator-service         8000  Python/FastAPI
  isr-tasking-service      8081  Quarkus/Java 21
  collection-service       8082  Quarkus/Java 21
  allsource-analyst-service 8083 Quarkus/Java 21
  target-nomination-service 8084 Quarkus/Java 21
  commander-service        8085  Quarkus/Java 21
  execution-service        8086  Quarkus/Java 21
  bda-service              8087  Quarkus/Java 21
  develop-service          8088  Quarkus/Java 21
  state-service            8089  Quarkus/Java 21
  sse-bridge-service       8090  Quarkus/Java 21
  cot-gateway-service      8091  Quarkus/Java 21
  legal-review-service     8092  Quarkus/Java 21
  frontend (React/nginx)   3000

LLM backend: RamaLama (default) → qwen2.5:14b
  NVIDIA 4070 Ti, 12GB VRAM, CDI passthrough
  Falls back to Anthropic API if LLM_BACKEND=anthropic
  CI uses Anthropic claude-haiku (no GPU in runners)

Java package: com.copperclaw (NOT com.redhat.copperclaw)
  The package rename is complete. Do not reintroduce
  com.redhat anywhere.

Kafka topics (14):
  copperclaw.operator-commands  — operator tool calls in
  copperclaw.isr-tasking        — collection tasking
  copperclaw.collection         — sensor reports
  copperclaw.assessment         — J2 fusion output
  copperclaw.nomination         — target nomination pkg
  copperclaw.legal-review       — ROE/CDE assessment
  copperclaw.authorization      — engagement auth
  copperclaw.execution          — fires/effects report
  copperclaw.bda                — battle damage assessment
  copperclaw.develop            — DOMEX leads → Find
  copperclaw.cot-in             — external CoT (reserved)
  copperclaw.cot-out            — CoT to ATAK/Sitaware
  copperclaw.cycle-state        — compacted, current state
  copperclaw.commander-log      — append-only decision log

═══════════════════════════════════════════════════════════
KEY DESIGN DECISIONS (do not relitigate)
═══════════════════════════════════════════════════════════

PARALLEL EVENT MODEL: agents are not sequential —
  they react to Kafka messages independently. The
  all-source analyst has a 10-second accumulation
  window to fuse multiple collection reports before
  calling the LLM. This is intentional.

COMMANDER HOLD: the commander-service never
  auto-authorizes. It publishes AWAITING_COMMANDER
  to cycle-state and waits for an operator tool call.
  Any change that makes it auto-authorize breaks the
  demo's core narrative.

PLAIN JDBC IN STATE-SERVICE: no Hibernate, no Panache.
  ByteBuddy fails with Java 25 on the host. State
  service uses AgroalDataSource directly. Do not add
  Hibernate to state-service.

RAMALAMA NOT OLLAMA: LLM inference uses RamaLama
  (Red Hat project, OCI model artifacts). The API
  surface is OpenAI-compatible. Do not switch to
  Ollama — the project alignment matters for the demo.

COT GATEWAY SIMULATION MODE: when COT_SIMULATION_MODE
  =true (default), the gateway generates synthetic
  CoT events without external hardware. The demo
  must be self-contained — no external network,
  no ATAK hardware required.

MOCK_STATE FALLBACK: the frontend renders from
  MOCK_STATE when SSE is not connected. This ensures
  the display always looks correct even before a cycle
  runs. Do not remove MOCK_STATE.

LEGAL REVIEW AS DISCRETE SERVICE: the legal-review-
  service sits between nomination and commander. It
  is a PRIISM analog. legal_cleared=false blocks
  the cycle regardless of operator instruction.
  This is the AI governance story made concrete.

═══════════════════════════════════════════════════════════
AUDIENCE CONTEXT (affects every UI decision)
═══════════════════════════════════════════════════════════

The room will contain both military and civilian
audiences simultaneously:
  - NATO J2/J3 officers who know F3EAD doctrine
  - Ministry officials and programme managers who don't
  - Defence industry technical leads
  - Red Hat account executives

UI must serve both. Large numbers and plain English
for non-ops. Dense technical data for operators.
The "Waiting for you" label on the commander agent
and the "3m 08s / −94% vs baseline" cycle timer
are the most important non-ops legibility moments.

Do not make the UI more complex without also making
it more legible. If in doubt, add plain English
labels alongside technical terms.

═══════════════════════════════════════════════════════════
KNOWN ISSUES AND CURRENT STATE
═══════════════════════════════════════════════════════════

Check git log --oneline -10 for latest commits.
Check open issues before starting any new work.

Known issues at time of writing:
  - commander-log has no producer (fix in progress)
  - cot-in topic orphaned (documented, sim mode works)
  - Container naming portability (fix in progress)
  - nginx proxy 404 on /api/operator/message
    requires podman-compose up --build frontend

To verify the system is healthy before any changes:
  make test-fast
  make logs-errors
  curl -s http://localhost:3000/nginx-health

═══════════════════════════════════════════════════════════
THINGS THAT MUST NEVER HAPPEN
═══════════════════════════════════════════════════════════

- Do not add "Red Hat" as an adjective anywhere in
  source code, comments, or system prompts.
  Package names (com.copperclaw) are fine.
  Product names (OpenShift, AMQ Streams, Quarkus,
  RamaLama) are fine.

- Do not make the commander-service auto-authorize.
  The human hold point is non-negotiable.

- Do not add Hibernate or Panache to state-service.

- Do not switch from RamaLama to Ollama.

- Do not remove MOCK_STATE from useCycleState.ts.

- Do not commit broken Maven builds. Run:
    mvn package -f parent-pom.xml -DskipTests
  before committing Java changes.

- Do not hardcode container names with _1 suffix.
  Use the get_container() helper in Makefile and
  e2e-test.sh.

- Do not add external map tile services (Leaflet/OSM).
  The tactical map is a custom SVG — it must work
  air-gapped with no internet.

- Do not touch agents/*/system-prompt.md without
  reading it first. System prompts are carefully
  calibrated — a small change breaks agent behavior.

- Do not touch frontend/src/config/displayMap.ts
  without understanding the enum→label mapping.

═══════════════════════════════════════════════════════════
STANDARD COMMIT FORMAT
═══════════════════════════════════════════════════════════

git commit -m "type(scope): description

Body explaining what and why.

COSMIC INDIGO // REL KESTREL COALITION
EXERCISE — EXERCISE — EXERCISE"

Types: feat, fix, refactor, test, docs, ci, chore
Scopes: frontend, backend, agents, infra, llm, ops

═══════════════════════════════════════════════════════════
HOW TO RUN
═══════════════════════════════════════════════════════════

cp .env.example .env   # add ANTHROPIC_API_KEY if needed
podman-compose up --build
# Frontend: http://localhost:3000
# Operator: http://localhost:8000/docs

First demo command:
  "initiate targeting cycle against STONEPILE,
   priority immediate — mortar threat to FOB GREYSTONE"

Then:
  "authorize M109A7 Paladin fire mission on STONEPILE
   — mortar position confirmed, CDE acceptable"

Useful make targets:
  make test-fast      — quick health + API checks
  make logs-errors    — recent errors across services
  make logs-live      — tail all logs in real time
  make kafka-watch topic=copperclaw.cycle-state
  make observe        — start Prometheus + Grafana