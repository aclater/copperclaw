"""
OPERATION COPPERCLAW — Shared Schema Library
=============================================
COSMIC INDIGO // REL KESTREL COALITION
EXERCISE — EXERCISE — EXERCISE

Pydantic v2 message schemas for the F3EAD targeting simulation.
All agent-to-agent messages, operator layer types, and cycle state
are defined here. This module is the single source of truth for
both the FastAPI backend and the LangGraph orchestration layer.

Import pattern:
    from copperclaw.schemas import (
        CollectionReport, IntelligenceAssessment, TargetNominationPackage,
        EngagementAuthorization, ExecutionReport, BDAReport, DevelopLead,
        CycleState, CommanderLogEntry, OperatorToolCall, OperatorToolResult,
    )

Doctrine references:
    AJP-3.9 Edition B Version 1 — Allied Joint Doctrine for Joint Targeting
    FM 3-60 (Nov 2010) — The Targeting Process
    JP 3-60 — Joint Targeting
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


class ClassificationMarking(str, Enum):
    """
    Exercise classification markings used throughout COPPERCLAW.
    These are fictional and carry no real classification meaning.
    All outputs are UNCLASSIFIED for exercise purposes.
    """
    COSMIC_INDIGO = "COSMIC INDIGO"
    COSMIC_INDIGO_REL = "COSMIC INDIGO // REL KESTREL COALITION"
    UNCLASSIFIED_EXERCISE = "UNCLASSIFIED // EXERCISE"


class TargetID(str, Enum):
    """
    Authoritative target identifiers drawn from the HPTL.
    These are the only valid target identifiers in the simulation.
    """
    ECHO_001 = "TGT-ECHO-001"    # VARNAK — Component ECHO Commander (HVI / TST)
    ECHO_002 = "TGT-ECHO-002"    # KAZMER — IED Facilitator (HVI / TST)
    GAMMA_001 = "TGT-GAMMA-001"  # IRONBOX — Component GAMMA C2 Node
    DELTA_001 = "TGT-DELTA-001"  # OILCAN — PRENN Fuel Depot (dual-use)
    GAMMA_002 = "TGT-GAMMA-002"  # STONEPILE — Indirect Fire Position


class TargetCodename(str, Enum):
    """Human-readable codenames corresponding to TargetID entries."""
    VARNAK = "VARNAK"
    KAZMER = "KAZMER"
    IRONBOX = "IRONBOX"
    OILCAN = "OILCAN"
    STONEPILE = "STONEPILE"


class ComponentID(str, Enum):
    """SLV component identifiers."""
    GAMMA = "GAMMA"    # Conventional remnant force
    DELTA = "DELTA"    # State-backed non-state actors
    ECHO = "ECHO"      # Extremist HVI sub-cell
    UNKNOWN = "UNKNOWN"


class ISRAsset(str, Enum):
    """
    Named ISR collection assets available to TF KESTREL.
    ISR Tasking agent and Collection agent use these identifiers.
    """
    RAVEN_1 = "RAVEN-1"          # Fixed-wing, SAR+EO, 18hr endurance, on VICTOR-5-KILO
    RAVEN_2 = "RAVEN-2"          # Fixed-wing, reserve, available for retasking
    KITE_7 = "KITE-7"            # HUMINT source, PRENN logistics access
    EAGLE_SIGINT = "EAGLE-SIGINT" # SIGINT platform, SLV comms bands, intermittent
    SHADOW_COMMS = "SHADOW-COMMS" # National SIGINT regiment, 48hr response
    JTAC_TEAM = "JTAC-TEAM"      # Joint Terminal Attack Controller (3 available)


class PIRNumber(str, Enum):
    """
    Priority Intelligence Requirements active in AO HARROW.
    Every CollectionReport must reference at least one PIR it addresses.
    """
    PIR_001 = "PIR-001"  # VARNAK location at 72hr intervals, pattern of life
    PIR_002 = "PIR-002"  # KAZMER confirmed location in HESSEK north
    PIR_003 = "PIR-003"  # IRONBOX current readiness status
    PIR_004 = "PIR-004"  # Civilian absence window at OILCAN, 2200–0300 local
    PIR_NEW = "PIR-NEW"  # Placeholder for Develop agent to generate new PIRs


class EngagementAuthority(str, Enum):
    """
    Engagement authority levels as defined in ROE Card Alpha-7.
    The Commander agent must verify authority level before issuing EngagementAuthorization.
    """
    COMKJTF = "COMKJTF"              # Required for HVI, TST, dual-use (OILCAN with CDE)
    TF_KESTREL_CDR = "TF-KESTREL-CDR"  # Delegated: STONEPILE, expedited targets
    J3_FIRES = "J3-FIRES"            # Non-lethal effects only (EW, influence ops)
    DENIED = "DENIED"                # Authority explicitly withheld
    PENDING = "PENDING"              # Awaiting legal review or further intelligence


class CyclePhase(str, Enum):
    """
    F3EAD cycle phases. The LangGraph state machine transitions through these.
    PHASE SERPENT = Find/Fix | PHASE COPPER = Finish/Exploit | PHASE CLAW = Assess/Develop
    """
    FIND = "FIND"          # SERPENT: ISR Tasking → Collection
    FIX = "FIX"            # SERPENT: Collection → All-Source Analyst
    FINISH = "FINISH"      # COPPER: Target Nomination → Commander → Execution
    EXPLOIT = "EXPLOIT"    # COPPER: Execution → DOMEX/tactical questioning
    ASSESS = "ASSESS"      # CLAW: BDA → assessment
    DEVELOP = "DEVELOP"    # CLAW: Develop → new leads → back to FIND
    HOLD = "HOLD"          # Commander has placed the cycle on hold
    COMPLETE = "COMPLETE"  # Cycle closed; no further action this iteration


class ConfidenceLevel(str, Enum):
    """
    Standard intelligence confidence levels.
    Used in IntelligenceAssessment and CollectionReport source grading.
    """
    HIGH = "HIGH"        # Multiple corroborating sources, recent, reliable
    MODERATE = "MODERATE"  # Single reliable source or corroborated but aged
    LOW = "LOW"          # Single source, uncorroborated, or source reliability unknown
    UNCONFIRMED = "UNCONFIRMED"  # Raw intelligence, not yet assessed


class CDETier(str, Enum):
    """
    Collateral Damage Estimation tiers per ROE Card Alpha-7 Section 5.
    CDE 1–3 = TF KESTREL CDR; CDE 4–5 = COMKJTF; CDE 6 = KJTF Legal + COMKJTF.
    """
    CDE_1 = "CDE-1"   # Minimal risk; rural, no civilian presence
    CDE_2 = "CDE-2"   # Low risk; rural, sparse population
    CDE_3 = "CDE-3"   # Moderate risk; TF CDR can approve
    CDE_4 = "CDE-4"   # Elevated risk; COMKJTF required
    CDE_5 = "CDE-5"   # High risk; urban, significant civilian presence; COMKJTF required
    CDE_6 = "CDE-6"   # Exceptional; KJTF Legal + COMKJTF; report to higher HQ
    NOT_REQUIRED = "NOT-REQUIRED"  # Outside VICTOR-5/6 grid; no CDE mandate


class EffectType(str, Enum):
    """
    Desired effects vocabulary drawn from FM 3-60 Section 1-6.
    Target Nomination agent selects the effect; Execution agent simulates it.
    """
    DESTROY = "DESTROY"      # Eliminate capability; cannot be restored without rebuild
    NEUTRALISE = "NEUTRALISE"  # Render incapable for duration of operation
    DISRUPT = "DISRUPT"      # Interrupt flow; temporary impairment
    DEGRADE = "DEGRADE"      # Reduce effectiveness; partial impairment
    DENY = "DENY"            # Prevent use by adversary
    SUPPRESS = "SUPPRESS"    # Temporarily reduce performance below threshold
    DECEIVE = "DECEIVE"      # Manipulate adversary perception
    DELAY = "DELAY"          # Slow arrival or deployment of forces/capability
    INTERDICT = "INTERDICT"  # Prevent effective use before it can affect friendlies
    REMOVE = "REMOVE"        # HVI-specific: capture or lethal removal from network
    EXPLOIT = "EXPLOIT"      # Non-lethal: access adversary systems/intel


class IntelSourceType(str, Enum):
    """Intelligence source disciplines."""
    SIGINT = "SIGINT"    # Signals intelligence
    HUMINT = "HUMINT"    # Human intelligence
    IMINT = "IMINT"      # Imagery intelligence
    OSINT = "OSINT"      # Open source intelligence
    DOMEX = "DOMEX"      # Document and media exploitation
    ACOUSTIC = "ACOUSTIC"  # Acoustic detection (e.g., STONEPILE mortar cueing)
    FUSION = "FUSION"    # All-source fused assessment


class TargetType(str, Enum):
    """Target categories per FM 3-60."""
    PERSONALITY = "PERSONALITY"    # HVI — person
    MATERIEL = "MATERIEL"          # Physical asset (vehicle, weapon system)
    NODE = "NODE"                  # C2 or logistics node
    DUAL_USE = "DUAL_USE"          # Civilian infrastructure with military use
    FIRE_POSITION = "FIRE_POSITION"  # Crew-served weapon/mortar position
    NETWORK = "NETWORK"            # Abstract network target (not yet kinetically targetable)


class ExecutionMethod(str, Enum):
    """
    Methods available to the Execution agent.
    No real weapon system designations per scenario constraints.
    """
    PRECISION_STRIKE = "PRECISION-STRIKE"        # Air or ground precision munition
    ARTILLERY_FIRE = "ARTILLERY-FIRE"            # 155mm self-propelled battery
    ATTACK_AVIATION = "ATTACK-AVIATION"          # Rotary-wing attack
    SOF_DIRECT_ACTION = "SOF-DIRECT-ACTION"      # KSOF capture/removal operation
    NON_KINETIC_EW = "NON-KINETIC-EW"           # Electronic warfare effect
    NON_KINETIC_INFLUENCE = "NON-KINETIC-INFLUENCE"  # Influence operations
    SURVEILLANCE_ONLY = "SURVEILLANCE-ONLY"      # No effect; ISR continuation


class BDAOutcome(str, Enum):
    """Battle Damage Assessment outcomes."""
    TARGET_DESTROYED = "TARGET-DESTROYED"
    TARGET_NEUTRALISED = "TARGET-NEUTRALISED"
    TARGET_DISRUPTED = "TARGET-DISRUPTED"
    EFFECT_NOT_ACHIEVED = "EFFECT-NOT-ACHIEVED"
    PARTIAL_EFFECT = "PARTIAL-EFFECT"
    UNKNOWN = "UNKNOWN"                # BDA collection incomplete
    CIVCAS_ASSESSED = "CIVCAS-ASSESSED"  # Civilian casualty assessed — mandatory reporting


class HoldReason(str, Enum):
    """Reasons a Commander agent may place a target on hold."""
    PID_INSUFFICIENT = "PID-INSUFFICIENT"          # Does not meet 72hr POL standard
    CDE_UNACCEPTABLE = "CDE-UNACCEPTABLE"          # Proportionality not satisfied
    NSL_PROXIMITY = "NSL-PROXIMITY"                # Too close to No-Strike List object
    ROE_NOT_MET = "ROE-NOT-MET"                   # General ROE failure
    INTEL_STALE = "INTEL-STALE"                   # Intelligence too old to act on
    LEGAL_REVIEW_REQUIRED = "LEGAL-REVIEW-REQUIRED"  # Requires JAG assessment
    COMMANDER_DISCRETION = "COMMANDER-DISCRETION"  # COMKJTF discretionary hold
    AWAIT_CIVILIAN_WINDOW = "AWAIT-CIVILIAN-WINDOW"  # OILCAN — wait for absence window


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — BASE TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class GridReference(BaseModel):
    """
    Military Grid Reference System (MGRS) location within AO HARROW.
    COPPERCLAW uses the fictional VICTOR-N-LETTER-XXXXXX format.
    Example: VICTOR-5-KILO-229-447 (VARNAK safe house grid)
    """
    zone: str = Field(
        ...,
        description="Grid zone, e.g. 'VICTOR-5'",
        examples=["VICTOR-5", "VICTOR-4", "VICTOR-6"],
    )
    sector: str = Field(
        ...,
        description="Sector letter within zone, e.g. 'KILO', 'LIMA', 'NOVEMBER'",
        examples=["KILO", "LIMA", "NOVEMBER", "OSCAR"],
    )
    easting: str = Field(
        ...,
        description="3-digit easting within sector",
        examples=["229", "312", "088"],
    )
    northing: str = Field(
        ...,
        description="3-digit northing within sector",
        examples=["447", "509", "271"],
    )

    @property
    def full_grid(self) -> str:
        return f"{self.zone}-{self.sector}-{self.easting}-{self.northing}"

    def __str__(self) -> str:
        return self.full_grid


class TimeWindow(BaseModel):
    """
    A time window in Zulu time. Used for civilian absence windows (OILCAN),
    ISR tasking windows, and POL observation periods.
    """
    start_zulu: str = Field(
        ...,
        description="Window start time in HHMM Zulu, e.g. '2200' for OILCAN civilian absence",
        examples=["2200", "0600", "1200"],
    )
    end_zulu: str = Field(
        ...,
        description="Window end time in HHMM Zulu",
        examples=["0300", "1800", "2359"],
    )
    duration_hours: Optional[float] = Field(
        None,
        description="Duration in hours, computed or supplied",
    )
    confirmed: bool = Field(
        False,
        description="Whether this window has been confirmed by collection (e.g. KITE-7 OILCAN window)",
    )


class IntelSource(BaseModel):
    """
    A single intelligence source contributing to a report.
    Multiple sources may be listed; confidence is assessed across all.
    """
    source_type: IntelSourceType = Field(
        ...,
        description="Intelligence discipline of this source",
    )
    asset_id: Optional[ISRAsset] = Field(
        None,
        description="Named ISR asset if applicable, e.g. RAVEN-1, KITE-7",
    )
    report_age_hours: float = Field(
        ...,
        description="Age of this source's reporting in hours at time of assessment. "
                    "KESTREL standard: >72hr is considered stale for personality targets.",
        examples=[0.5, 6.0, 36.0, 48.0, 72.0],
    )
    reliability_grade: str = Field(
        ...,
        description="Source reliability grade A–F (A=completely reliable, F=reliability unknown). "
                    "KITE-7 is graded B. EAGLE-SIGINT intermittent = C.",
        examples=["A", "B", "C", "D", "E", "F"],
    )
    information_grade: str = Field(
        ...,
        description="Information content grade 1–6 (1=confirmed, 6=cannot be judged). "
                    "Used with reliability to form NATO STANAG source grading.",
        examples=["1", "2", "3", "4", "5", "6"],
    )
    summary: str = Field(
        ...,
        description="One-sentence summary of what this source reported, in plain language.",
    )


class CivilianConsideration(BaseModel):
    """
    Civilian presence and collateral damage assessment for a target.
    Populated by Target Nomination agent; reviewed by Commander agent.
    """
    cde_tier: CDETier = Field(
        ...,
        description="CDE tier per ROE Card Alpha-7 Section 5. Determines engagement authority.",
    )
    civilian_presence_assessed: bool = Field(
        ...,
        description="Whether civilians are assessed to be present at or near the target.",
    )
    civilian_count_estimate: Optional[int] = Field(
        None,
        description="Estimated civilian count if present. None = not assessed / zero confirmed.",
    )
    nsl_proximity_metres: Optional[float] = Field(
        None,
        description="Distance to nearest NSL object in metres. "
                    "HESSEK Mosque Complex and MORRUSK Hospital are NSL objects.",
    )
    proportionality_statement: str = Field(
        ...,
        description="Plain-language proportionality assessment: expected collateral harm vs "
                    "anticipated military advantage. Must satisfy AJP-3.9 and ROE Alpha-7.",
    )
    precautionary_measures: List[str] = Field(
        default_factory=list,
        description="List of precautionary measures taken or recommended, e.g. "
                    "['Wait for OILCAN civilian absence window 2200–0300', "
                    "'Use precision munition to minimise blast radius']",
    )


class ROEChecklist(BaseModel):
    """
    Mandatory ROE compliance checklist per ROE Card Alpha-7.
    Target Nomination agent completes this; Commander agent reviews it.
    All four LOAC principles must be satisfied for engagement to be lawful.
    """
    military_necessity_met: bool = Field(
        ...,
        description="Confirms the target offers definite military advantage. "
                    "Every target nominated must contribute to attaining the commander's objectives (FM 3-60 §1-4).",
    )
    distinction_confirmed: bool = Field(
        ...,
        description="Confirms the target is a legitimate military objective, "
                    "distinguished from civilians and civilian objects per LOAC.",
    )
    proportionality_satisfied: bool = Field(
        ...,
        description="Confirms expected CIVCAS/collateral damage is not excessive "
                    "relative to anticipated concrete and direct military advantage.",
    )
    precaution_applied: bool = Field(
        ...,
        description="Confirms all feasible precautionary measures have been considered "
                    "and applied per AJP-3.9 and ROE Alpha-7 Section 1.",
    )
    pid_standard_met: bool = Field(
        ...,
        description="Confirms Positive Identification has been achieved. "
                    "For personality targets: dual-source, 72-hour POL minimum (KESTREL standard).",
    )
    not_on_nsl: bool = Field(
        ...,
        description="Confirms the target is NOT on the No-Strike List. "
                    "NSL includes MORRUSK Hospital, HESSEK Mosque, UN-flagged facilities.",
    )
    rtl_constraints_noted: Optional[str] = Field(
        None,
        description="If target is on the Restricted Target List, describes constraints. "
                    "E.g. OILCAN: 'Engage only 2200–0500 local with confirmed civilian absence; "
                    "no incendiary effects; precision munitions only.'",
    )
    cde_completed: bool = Field(
        ...,
        description="Confirms CDE has been completed where mandatory (all VICTOR-5/6 engagements). "
                    "CDE is not required for STONEPILE (outside VICTOR-5/6, rural).",
    )
    engagement_authority_confirmed: EngagementAuthority = Field(
        ...,
        description="The engagement authority that applies to this target per ROE Alpha-7 and AGM. "
                    "HVI and TST: COMKJTF. STONEPILE: TF KESTREL CDR.",
    )
    legal_review_required: bool = Field(
        False,
        description="Whether JAG / legal review is required before engagement authority is granted. "
                    "Mandatory for CDE 6 and all dual-use facilities with civilian presence.",
    )

    @model_validator(mode="after")
    def all_loac_principles_checked(self) -> "ROEChecklist":
        """All four LOAC principles must be explicitly assessed."""
        # DESIGN DECISION: Model validator enforces that all four LOAC fields are
        # present (Pydantic guarantees this for non-Optional bools), but does NOT
        # enforce that all are True — because a TNP may legitimately be submitted
        # documenting that ROE is NOT met, so the Commander can formally deny it.
        return self


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — REPORT BASE
# ═══════════════════════════════════════════════════════════════════════════════


class ReportBase(BaseModel):
    """
    Common fields inherited by all agent-produced reports.
    Provides traceability, classification, and cycle linkage.
    """
    report_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique report identifier (UUID4). Auto-generated.",
    )
    classification: ClassificationMarking = Field(
        default=ClassificationMarking.COSMIC_INDIGO_REL,
        description="Exercise classification marking. All simulation outputs default to "
                    "COSMIC INDIGO // REL KESTREL COALITION.",
    )
    exercise_serial: str = Field(
        default="COPPERCLAW-SIM-001",
        description="Exercise serial identifier.",
    )
    cycle_id: str = Field(
        ...,
        description="Identifier for the F3EAD cycle this report belongs to. "
                    "Format: CYCLE-NNNN, e.g. CYCLE-0001. Injected by LangGraph orchestrator.",
        examples=["CYCLE-0001", "CYCLE-0002"],
    )
    phase: CyclePhase = Field(
        ...,
        description="The F3EAD phase during which this report was produced.",
    )
    producing_agent: str = Field(
        ...,
        description="The agent role that produced this report. "
                    "E.g. 'ISR-TASKING', 'COLLECTION', 'ALL-SOURCE-ANALYST'.",
        examples=["ISR-TASKING", "COLLECTION", "ALL-SOURCE-ANALYST",
                  "TARGET-NOMINATION", "COMMANDER", "EXECUTION", "BDA", "DEVELOP"],
    )
    timestamp_zulu: datetime = Field(
        default_factory=datetime.utcnow,
        description="Report production timestamp in Zulu time.",
    )
    target_id: TargetID = Field(
        ...,
        description="The primary HPTL target this report addresses.",
    )
    narrative: str = Field(
        ...,
        description="Plain-language narrative summary of this report. "
                    "Must be parseable by a downstream agent and renderable in the frontend panel. "
                    "Write in the voice of the producing agent's role.",
        min_length=20,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — REPORT TYPES (agent-to-agent message schemas)
# ═══════════════════════════════════════════════════════════════════════════════


class ISRTaskingOrder(ReportBase):
    """
    ISR Tasking agent → Collection agent.

    Produced by the ISR Tasking agent (J2 collection manager) to direct a
    named ISR asset against a specific PIR and target. This is the first
    message in the F3EAD cycle — it initiates the FIND phase.

    Agent guidance: Generate one tasking order per PIR per cycle. If multiple
    assets are available, task the most appropriate by capability and endurance.
    RAVEN-1 is currently on PIR-001 (VARNAK). RAVEN-2 is reserve.
    """
    phase: CyclePhase = CyclePhase.FIND

    pir_addressed: List[PIRNumber] = Field(
        ...,
        description="PIR(s) this collection task is designed to answer. "
                    "E.g. [PIR-001] for VARNAK location development.",
        min_length=1,
    )
    asset_tasked: ISRAsset = Field(
        ...,
        description="Named ISR asset being tasked. Must be available and appropriate "
                    "to the collection requirement.",
    )
    collection_window: TimeWindow = Field(
        ...,
        description="The Zulu time window during which collection should occur.",
    )
    target_area: GridReference = Field(
        ...,
        description="Primary collection area. For PIR-001 (VARNAK): "
                    "VICTOR-5-KILO-229-447 and adjacent grids in HESSEK District.",
    )
    collection_method: IntelSourceType = Field(
        ...,
        description="The intelligence discipline this asset will employ, e.g. IMINT for RAVEN-1.",
    )
    specific_indicators: List[str] = Field(
        default_factory=list,
        description="Specific indicators the collection asset should look for. "
                    "E.g. ['Civilian vehicles changing route pattern', "
                    "'Activity at three HESSEK safe house grids', "
                    "'Courier foot movement between VICTOR-5-KILO-229-447 and 218-461']",
    )
    priority: int = Field(
        ...,
        description="Collection priority 1–5 (1=highest). Drives asset deconfliction.",
        ge=1,
        le=5,
    )
    retask_from_previous: bool = Field(
        False,
        description="Whether this is a retask of an asset from a previous collection line. "
                    "If True, previous_task_id should be populated.",
    )
    previous_task_id: Optional[str] = Field(
        None,
        description="report_id of the ISRTaskingOrder this replaces, if retasking.",
    )


class CollectionReport(ReportBase):
    """
    Collection agent → All-Source Analyst agent.

    The Collection agent simulates the output of a sensor or platform
    executing an ISRTaskingOrder. This report carries the raw intelligence
    gathered during the collection window, before all-source fusion.

    Agent guidance: Generate realistic but synthetic collection results.
    Maintain consistency with the COPPERCLAW initial intelligence state.
    VARNAK POL is 48hrs complete — a new RAVEN-1 collection report should
    advance this toward the 72hr PID standard. Do not confirm PID yet.
    """
    phase: CyclePhase = CyclePhase.FIX

    tasking_order_id: str = Field(
        ...,
        description="report_id of the ISRTaskingOrder that generated this collection.",
    )
    asset_id: ISRAsset = Field(
        ...,
        description="The ISR asset that conducted this collection.",
    )
    pir_addressed: List[PIRNumber] = Field(
        ...,
        description="PIR(s) this report partially or fully answers.",
    )
    collection_start_zulu: str = Field(
        ...,
        description="Collection window start in HHMM Zulu.",
        examples=["0600", "2200", "1430"],
    )
    collection_end_zulu: str = Field(
        ...,
        description="Collection window end in HHMM Zulu.",
        examples=["0800", "2300", "1600"],
    )
    source_type: IntelSourceType = Field(
        ...,
        description="Intelligence discipline of this collection.",
    )
    raw_intelligence: str = Field(
        ...,
        description="The raw intelligence product in plain language — what the sensor "
                    "observed, intercepted, or reported. Written in the voice of the "
                    "platform/source. Not yet fused or assessed. "
                    "E.g. 'RAVEN-1 EO confirms vehicle activity at VICTOR-5-KILO-229-447 "
                    "consistent with previous POL observation. One adult male departed "
                    "compound at 0643Z on foot, heading toward VICTOR-5-KILO-218-461.'",
        min_length=30,
    )
    location_confirmed: Optional[GridReference] = Field(
        None,
        description="If the collection confirmed a target location, the grid. None if not confirmed.",
    )
    pol_hours_added: Optional[float] = Field(
        None,
        description="For personality targets: additional hours of pattern-of-life observation "
                    "this collection contributes. VARNAK needs 24 more hours to reach 72hr standard.",
        ge=0,
    )
    pol_total_hours: Optional[float] = Field(
        None,
        description="Running total of POL hours accumulated against this personality target. "
                    "VARNAK baseline: 48hrs. PID requires 72hrs.",
        ge=0,
    )
    negative_information: Optional[str] = Field(
        None,
        description="What the collection did NOT find, where relevant. "
                    "Negative information is valid intelligence (FM 3-60 §2-10).",
    )
    follow_on_collection_required: bool = Field(
        ...,
        description="Whether additional collection is needed before PID standard can be met.",
    )
    confidence: ConfidenceLevel = Field(
        ...,
        description="Confidence in the accuracy of this collection report.",
    )


class IntelligenceAssessment(ReportBase):
    """
    All-Source Analyst agent → Target Nomination agent.

    The All-Source Analyst fuses multiple CollectionReports and existing
    intelligence holdings into a comprehensive target assessment. This is
    the intelligence product that the Target Nomination agent will use to
    build the TNP.

    Agent guidance: Synthesise all available collection against this target.
    Assess confidence, identify intelligence gaps, and make explicit whether
    the KESTREL PID standard (dual-source, 72hr POL) has been met.
    If PID standard is not met, state this clearly — the TNP cannot proceed.
    """
    phase: CyclePhase = CyclePhase.FIX

    source_reports: List[str] = Field(
        ...,
        description="List of report_ids of CollectionReports fused in this assessment.",
        min_length=1,
    )
    sources: List[IntelSource] = Field(
        ...,
        description="Structured source list with reliability and information grades.",
        min_length=1,
    )
    target_type: TargetType = Field(
        ...,
        description="Target category per FM 3-60. Personality for HVI; NODE for IRONBOX; "
                    "DUAL_USE for OILCAN; FIRE_POSITION for STONEPILE.",
    )
    target_codename: TargetCodename = Field(
        ...,
        description="HPTL codename for this target.",
    )
    siv_component: ComponentID = Field(
        ...,
        description="Which SLV component this target belongs to.",
    )
    confirmed_location: Optional[GridReference] = Field(
        None,
        description="Current confirmed location. None if location not yet confirmed.",
    )
    location_confidence: ConfidenceLevel = Field(
        ...,
        description="Confidence in the confirmed location.",
    )
    pol_hours_complete: Optional[float] = Field(
        None,
        description="For personality targets: total POL hours accumulated. "
                    "KESTREL standard = 72hr minimum. VARNAK baseline: 48hr.",
    )
    pid_standard_met: bool = Field(
        ...,
        description="Whether KESTREL PID standard is met: dual-source confirmation AND "
                    "72-hour pattern of life for personality targets. "
                    "This field gates whether a TNP can be generated.",
    )
    pid_shortfall: Optional[str] = Field(
        None,
        description="If pid_standard_met=False, describes what is missing. "
                    "E.g. 'VARNAK POL is 56hrs complete; 16hrs additional observation required.'",
    )
    intelligence_gaps: List[str] = Field(
        default_factory=list,
        description="Remaining intelligence gaps for this target. "
                    "E.g. ['KAZMER precise location unconfirmed — ISR lapse 72hrs', "
                    "'RASK identity unconfirmed', "
                    "'OILCAN civilian absence window — KITE-7 report required']",
    )
    exploitation_value: str = Field(
        ...,
        description="Assessment of intelligence exploitation value if target is engaged. "
                    "VARNAK and KAZMER are CRITICAL. IRONBOX is MEDIUM.",
        examples=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    )
    threat_to_friendly_forces: Optional[str] = Field(
        None,
        description="If the target poses a direct threat to friendly forces, describe it. "
                    "STONEPILE poses mortar threat to FOB GREYSTONE.",
    )
    recommended_action: str = Field(
        ...,
        description="All-Source Analyst's recommended next action. "
                    "E.g. 'Continue RAVEN-1 POL for 16 additional hours then generate TNP' "
                    "or 'IRONBOX PID met — recommend TNP generation for COMKJTF review.'",
    )
    overall_confidence: ConfidenceLevel = Field(
        ...,
        description="Overall assessment confidence across all sources.",
    )


class TargetNominationPackage(ReportBase):
    """
    Target Nomination agent → Commander agent.

    The formal targeting package nominating a target for engagement authority.
    The Target Nomination agent applies ROE Card Alpha-7 and CDE methodology
    to construct this package. The Commander agent reviews it and issues
    either an EngagementAuthorization or a hold decision.

    Agent guidance: You are the targeting officer. You must satisfy all four
    LOAC principles and the full ROE checklist. If any element is not satisfied,
    submit the TNP anyway but mark it as ROE_NOT_MET and explain why.
    Never omit the ROE checklist. Never omit the CDE.
    """
    phase: CyclePhase = CyclePhase.FINISH

    assessment_id: str = Field(
        ...,
        description="report_id of the IntelligenceAssessment this TNP is based on.",
    )
    target_codename: TargetCodename = Field(
        ...,
        description="HPTL codename for this target.",
    )
    target_type: TargetType = Field(
        ...,
        description="Target type category.",
    )
    target_location: GridReference = Field(
        ...,
        description="Confirmed target location at time of nomination.",
    )
    desired_effect: EffectType = Field(
        ...,
        description="The desired effect from FM 3-60 §1-6 vocabulary. "
                    "HVI targets: REMOVE. IRONBOX: DESTROY. OILCAN: DISRUPT. STONEPILE: NEUTRALISE.",
    )
    recommended_execution_method: ExecutionMethod = Field(
        ...,
        description="Recommended method of engagement. Must be appropriate to target type and ROE. "
                    "HVI (capture preferred): SOF_DIRECT_ACTION. STONEPILE: ARTILLERY_FIRE.",
    )
    alternative_execution_methods: List[ExecutionMethod] = Field(
        default_factory=list,
        description="Alternative execution methods if recommended method is unavailable.",
    )
    engagement_window: Optional[TimeWindow] = Field(
        None,
        description="Recommended engagement window. Mandatory for OILCAN (2200–0300 local, "
                    "civilian absence). Optional for other targets.",
    )
    roe_checklist: ROEChecklist = Field(
        ...,
        description="Completed ROE compliance checklist per ROE Card Alpha-7. "
                    "All fields must be populated. Commander agent will review each field.",
    )
    civilian_consideration: CivilianConsideration = Field(
        ...,
        description="CDE and civilian presence assessment.",
    )
    is_tst: bool = Field(
        ...,
        description="Whether this target is designated as a Time-Sensitive Target. "
                    "TST: VARNAK (TGT-ECHO-001) and KAZMER (TGT-ECHO-002) only.",
    )
    tst_justification: Optional[str] = Field(
        None,
        description="If is_tst=True, the justification for TST designation. "
                    "Required per JP 3-60: target must present fleeting opportunity or imminent threat.",
    )
    exploitation_plan: str = Field(
        ...,
        description="Plan for exploitation following Finish action. "
                    "VARNAK: 'KSOF to conduct DOMEX of all devices and documents on site; "
                    "tactical questioning if captured.' IRONBOX: 'EOD and SIGINT exploitation "
                    "of comms equipment if accessible.'",
    )
    requesting_authority: str = Field(
        default="J2/J3 TF KESTREL",
        description="The authority requesting this engagement.",
    )
    roe_compliance_summary: str = Field(
        ...,
        description="Plain-language summary of ROE compliance assessment. "
                    "Written for COMKJTF review. Must address all four LOAC principles explicitly.",
    )


class EngagementAuthorization(ReportBase):
    """
    Commander agent → Execution agent.

    The Commander agent (voice of COMKJTF) reviews the TNP and issues either
    an authorization or a hold. This is the human-in-the-loop node.

    In the simulation, the Commander agent may be:
    (a) Acting autonomously based on the TNP and ROE, OR
    (b) Reflecting a real operator decision via the Operator LLM layer.

    If the operator has issued an 'authorize_target' or 'hold_target' tool call,
    that decision is injected into this agent's context and must be honoured.

    Agent guidance: You are COMKJTF. Review the TNP as a senior commander.
    Apply the ROE checklist. Check CDE tier vs your authority level.
    Add commander's guidance to constrain or shape the execution.
    """
    phase: CyclePhase = CyclePhase.FINISH

    tnp_id: str = Field(
        ...,
        description="report_id of the TargetNominationPackage being actioned.",
    )
    target_codename: TargetCodename = Field(
        ...,
        description="HPTL codename.",
    )
    authorized: bool = Field(
        ...,
        description="Whether engagement is authorized. "
                    "True = execute. False = hold (see hold_reason).",
    )
    hold_reason: Optional[HoldReason] = Field(
        None,
        description="If authorized=False, the reason for holding. Must be populated.",
    )
    hold_explanation: Optional[str] = Field(
        None,
        description="If authorized=False, plain-language explanation of the hold decision.",
    )
    authority_level: EngagementAuthority = Field(
        ...,
        description="The engagement authority being exercised.",
    )
    authorized_execution_method: Optional[ExecutionMethod] = Field(
        None,
        description="If authorized=True, the approved execution method. "
                    "May differ from TNP recommendation.",
    )
    authorized_engagement_window: Optional[TimeWindow] = Field(
        None,
        description="If authorized=True, the approved engagement window. "
                    "Commander may constrain the window further than TNP recommended.",
    )
    commanders_guidance: str = Field(
        ...,
        description="Commander's guidance to the Execution agent. "
                    "E.g. 'Capture VARNAK if possible; lethal authority granted only if capture "
                    "is not feasible and force protection requires it. JTAC to confirm PID on "
                    "approach. DOMEX team to be pre-positioned.' "
                    "Or if hold: 'Return when POL reaches 72 hours. Do not engage until then.'",
    )
    operator_injected: bool = Field(
        False,
        description="Whether this decision reflects a real operator input via the Operator LLM layer. "
                    "If True, the operator's exact instruction is preserved in operator_instruction.",
    )
    operator_instruction: Optional[str] = Field(
        None,
        description="The operator's natural-language instruction that drove this decision, "
                    "if operator_injected=True.",
    )
    civcas_threshold: Optional[str] = Field(
        None,
        description="Commander's explicit CIVCAS threshold for this engagement. "
                    "E.g. 'Zero CIVCAS — abort if any civilian presence confirmed on target.' "
                    "Mandatory for OILCAN and any CDE 5+ engagement.",
    )


class ExecutionReport(ReportBase):
    """
    Execution agent → BDA agent.

    The Execution agent simulates the fires/effects action authorised by
    the EngagementAuthorization. It produces a report of what occurred,
    including any observed immediate effects. This feeds the BDA agent.

    Agent guidance: You are the fires/effects simulator. Execute the
    authorized method against the confirmed grid. Generate a realistic
    execution narrative. If execution was a SOF direct action, describe
    the approach, breach, and immediate outcome. If fires, describe the
    engagement sequence. Do not pre-judge BDA — that is the BDA agent's role.
    Note any CIVCAS immediately per ROE Alpha-7 Section 7.
    """
    phase: CyclePhase = CyclePhase.EXPLOIT

    authorization_id: str = Field(
        ...,
        description="report_id of the EngagementAuthorization that directed this execution.",
    )
    target_codename: TargetCodename = Field(
        ...,
        description="HPTL codename of the target engaged.",
    )
    execution_method_used: ExecutionMethod = Field(
        ...,
        description="The execution method actually used (may differ from authorization if "
                    "circumstances required adaptation).",
    )
    method_deviation: Optional[str] = Field(
        None,
        description="If execution method differed from authorization, explain why.",
    )
    engagement_time_zulu: str = Field(
        ...,
        description="Time of engagement in HHMM Zulu.",
        examples=["0215", "1437", "2248"],
    )
    engagement_grid: GridReference = Field(
        ...,
        description="Grid at which the engagement occurred.",
    )
    execution_narrative: str = Field(
        ...,
        description="Detailed narrative of the execution. Written in the voice of the "
                    "fires/effects simulator. Describe the sequence of events from "
                    "initiation through immediate effects observation.",
        min_length=50,
    )
    immediate_effects_observed: str = Field(
        ...,
        description="Immediate effects observed at time of engagement — before BDA assessment. "
                    "E.g. 'Two secondary explosions observed, structure partially collapsed.' "
                    "Or for SOF: 'Primary target secured; one SLV combatant KIA during breach.'",
    )
    civcas_observed: bool = Field(
        ...,
        description="Whether any actual or suspected civilian casualties were observed. "
                    "If True, immediate reporting to COMKJTF is mandatory per ROE Alpha-7 §7.",
    )
    civcas_detail: Optional[str] = Field(
        None,
        description="If civcas_observed=True, detail of observed CIVCAS. Mandatory.",
    )
    exploitation_opportunity: bool = Field(
        ...,
        description="Whether the execution created exploitation opportunities "
                    "(accessible site, captured persons, recoverable material).",
    )
    exploitation_description: Optional[str] = Field(
        None,
        description="If exploitation_opportunity=True, what is available for exploitation. "
                    "E.g. 'Primary target VARNAK in custody; three electronic devices recovered; "
                    "document cache accessible at grid VICTOR-5-KILO-229-447.'",
    )
    follow_on_isr_required: bool = Field(
        ...,
        description="Whether ISR tasking is needed immediately post-execution "
                    "(e.g. for BDA collection).",
    )


class BDAReport(ReportBase):
    """
    BDA agent → Develop agent.

    The Battle Damage Assessment agent assesses the effect of the execution
    against the desired effect stated in the TNP. This report determines
    whether the targeting objective has been achieved and what further
    action is required. It feeds directly into the Develop phase.

    Agent guidance: You are the BDA cell. Assess effects against the desired
    effect from the TNP. Use available ISR collection (RAVEN-1/2, JTAC report)
    to assess physical and functional damage. For personality targets, confirm
    removal from network. State clearly whether the target requires
    re-engagement or has been satisfactorily serviced.
    """
    phase: CyclePhase = CyclePhase.ASSESS

    execution_report_id: str = Field(
        ...,
        description="report_id of the ExecutionReport this BDA assesses.",
    )
    target_codename: TargetCodename = Field(
        ...,
        description="HPTL codename of the assessed target.",
    )
    desired_effect: EffectType = Field(
        ...,
        description="The desired effect from the TNP against which this BDA assesses.",
    )
    bda_outcome: BDAOutcome = Field(
        ...,
        description="Assessment of whether the desired effect was achieved.",
    )
    physical_damage_assessment: str = Field(
        ...,
        description="Assessment of physical damage or status. "
                    "For materiel: describe structural/functional damage. "
                    "For personality: confirmed status (captured/KIA/escaped/unknown). "
                    "For dual-use: operational status of the facility.",
    )
    functional_damage_assessment: str = Field(
        ...,
        description="Assessment of functional damage — has the target's military function been degraded? "
                    "E.g. 'IRONBOX C2 function assessed destroyed — GAMMA unable to coordinate "
                    "at formation level for estimated 72–96hrs.'",
    )
    network_effect_assessment: str = Field(
        ...,
        description="Assessment of the effect on the broader SLV network. "
                    "E.g. 'VARNAK removal degrades ECHO command by approximately 60%; "
                    "network will likely attempt reconstitution within 48–72hrs.'",
    )
    civcas_confirmed: bool = Field(
        ...,
        description="Whether civilian casualties are confirmed in BDA. "
                    "If True, CIVCAS reporting chain must be triggered.",
    )
    civcas_count: Optional[int] = Field(
        None,
        description="Confirmed or estimated CIVCAS count. Exercise use only.",
    )
    re_engagement_required: bool = Field(
        ...,
        description="Whether the target requires re-engagement to achieve the desired effect.",
    )
    re_engagement_rationale: Optional[str] = Field(
        None,
        description="If re_engagement_required=True, the rationale.",
    )
    exploitation_results: Optional[str] = Field(
        None,
        description="Summary of exploitation results from the Finish phase that inform BDA. "
                    "E.g. 'DOMEX of VARNAK's device yielded 3 new contact names and "
                    "a partial courier route map.'",
    )
    bda_collection_gaps: List[str] = Field(
        default_factory=list,
        description="Collection gaps remaining in the BDA — what could not be assessed. "
                    "E.g. ['Secondary vehicle park not visible to RAVEN-1 due to obscuration', "
                    "'KAZMER co-location unconfirmed']",
    )
    assessment_confidence: ConfidenceLevel = Field(
        ...,
        description="Confidence in this BDA assessment.",
    )


class DevelopLead(ReportBase):
    """
    Develop agent → ISR Tasking agent (closes the F3EAD loop).

    The Develop agent processes DOMEX products, BDA results, and exploitation
    intelligence to generate new leads and updated requirements. This is the
    'D' in F3EAD — it closes the loop back to Find and re-initiates the cycle.

    Agent guidance: You are the DOMEX/lead generation cell. Extract every
    actionable lead from the BDA and exploitation products. Generate new PIRs.
    Update the network picture. Determine whether the cycle should continue
    against the same target (re-engagement) or pivot to a new target.
    Prioritise leads that develop the ECHO courier network — this is the
    commander's strategic priority.
    """
    phase: CyclePhase = CyclePhase.DEVELOP

    bda_report_id: str = Field(
        ...,
        description="report_id of the BDAReport that generated these leads.",
    )
    source_target: TargetCodename = Field(
        ...,
        description="The HPTL target from whose exploitation these leads derive.",
    )
    new_leads: List[str] = Field(
        default_factory=list,
        description="List of new intelligence leads generated by DOMEX and exploitation. "
                    "Each lead should be a specific, actionable item. "
                    "E.g. ['New contact name GREGOR identified in VARNAK device — assess as "
                    "ECHO courier network node', 'Financial transfer record to account "
                    "associated with DELTA PRENN facilitator GORNIK', "
                    "'Courier route map fragment yields two additional HESSEK safe house grids']",
    )
    new_pir_requirements: List[str] = Field(
        default_factory=list,
        description="New Priority Intelligence Requirements generated by the Develop phase. "
                    "These will be formalised by the ISR Tasking agent in the next cycle. "
                    "E.g. ['Confirm GREGOR identity and location — HESSEK District north', "
                    "'Assess DELTA financial nexus between GORNIK and PRENN Energy accounts']",
    )
    network_update: str = Field(
        ...,
        description="Updated assessment of the SLV target network following this cycle. "
                    "Describe changes in network structure, identified gaps, and remaining nodes.",
    )
    recommended_next_target: Optional[TargetID] = Field(
        None,
        description="Recommended HPTL target for the next cycle, based on lead analysis. "
                    "If a new target not on the current HPTL is identified, set to None "
                    "and describe in new_target_nomination.",
    )
    new_target_nomination: Optional[str] = Field(
        None,
        description="If a new target not on the current HPTL is identified, "
                    "describe it here for J2 development. E.g. 'GREGOR — new ECHO courier "
                    "network node; requires HUMINT development and ISR tasking before "
                    "formal HPTL nomination.'",
    )
    cycle_recommendation: str = Field(
        ...,
        description="Develop agent's recommendation for next cycle action. "
                    "E.g. 'INITIATE new cycle against TGT-ECHO-002 (KAZMER) — "
                    "VARNAK device yields likely Kazmer contact pattern.' "
                    "Or: 'RE-ENGAGE TGT-DELTA-001 (OILCAN) — disruption effect partial, "
                    "logistic function resumed within 24hrs.'",
    )
    domex_products: List[str] = Field(
        default_factory=list,
        description="List of DOMEX products generated (documents, devices, media). "
                    "E.g. ['Encrypted mobile device — sent for technical exploitation', "
                    "'Hand-written courier schedule — photographed and disseminated', "
                    "'SIM card — SIGINT tasking generated against associated numbers']",
    )
    dissemination_list: List[str] = Field(
        default_factory=list,
        description="Agencies and cells to which DOMEX products and leads are disseminated. "
                    "E.g. ['J2 TF KESTREL', 'SHADOW COMMS (SIGINT exploitation)', "
                    "'KJTF J2X (national-level development)', 'VALDORIAN Intelligence Service (sanitised)']",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — OPERATOR LAYER TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class TargetCycleStatus(BaseModel):
    """
    Status of a single target within the current cycle.
    Embedded in CycleState.
    """
    target_id: TargetID
    codename: TargetCodename
    current_phase: CyclePhase
    pid_met: bool
    pol_hours_complete: Optional[float] = None
    last_report_id: Optional[str] = None
    last_report_type: Optional[str] = None
    authorized: Optional[bool] = None
    bda_outcome: Optional[BDAOutcome] = None
    on_hold: bool = False
    hold_reason: Optional[HoldReason] = None
    notes: Optional[str] = None


class ISRAssetStatus(BaseModel):
    """Current status of a named ISR asset."""
    asset_id: ISRAsset
    currently_tasked: bool
    current_task_target: Optional[TargetID] = None
    current_pir: Optional[PIRNumber] = None
    available_from_zulu: Optional[str] = None
    endurance_hours_remaining: Optional[float] = None
    notes: Optional[str] = None


class CycleState(BaseModel):
    """
    Full current state of the F3EAD simulation cycle.
    Injected as context into the Operator LLM on every turn.
    Also used as the primary data structure for the frontend operational display.

    This is the authoritative real-time picture of the simulation.
    """
    classification: ClassificationMarking = ClassificationMarking.COSMIC_INDIGO_REL
    exercise_serial: str = "COPPERCLAW-SIM-001"
    cycle_id: str = Field(
        ...,
        description="Current cycle identifier, e.g. CYCLE-0001.",
    )
    cycle_sequence: int = Field(
        ...,
        description="Monotonically increasing cycle counter.",
        ge=1,
    )
    timestamp_zulu: datetime = Field(default_factory=datetime.utcnow)
    overall_phase: CyclePhase = Field(
        ...,
        description="The current dominant phase of the cycle. Individual targets may "
                    "be in different phases within the same cycle.",
    )
    commander_priority_target: TargetID = Field(
        default=TargetID.ECHO_001,
        description="Current commander's priority target. Default: TGT-ECHO-001 (VARNAK).",
    )
    target_statuses: List[TargetCycleStatus] = Field(
        ...,
        description="Status of each HPTL target in the current cycle.",
    )
    isr_asset_statuses: List[ISRAssetStatus] = Field(
        default_factory=list,
        description="Current status of each named ISR asset.",
    )
    active_pirs: List[PIRNumber] = Field(
        default_factory=list,
        description="PIRs currently active and driving collection.",
    )
    latest_report_ids: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of producing_agent → latest report_id for that agent in this cycle. "
                    "E.g. {'COLLECTION': 'uuid...', 'ALL-SOURCE-ANALYST': 'uuid...'}",
    )
    pending_commander_decision: Optional[str] = Field(
        None,
        description="report_id of a TargetNominationPackage awaiting Commander decision. "
                    "Non-null signals the frontend to render the Commander decision UI.",
    )
    cycle_events: List[str] = Field(
        default_factory=list,
        description="Ordered list of significant cycle events as plain-language strings. "
                    "E.g. ['0643Z: RAVEN-1 confirms VARNAK movement at VICTOR-5-KILO-229-447', "
                    "'0712Z: All-Source Assessment complete — PID not yet met (56/72hrs)', "
                    "'0715Z: ISR retask issued — RAVEN-1 continue PIR-001']",
    )
    operator_guidance_active: Optional[str] = Field(
        None,
        description="Any active operator guidance injected via inject_commander_guidance tool. "
                    "Displayed in the frontend and injected into agent context.",
    )
    simulation_warnings: List[str] = Field(
        default_factory=list,
        description="Non-blocking warnings surfaced by agents (e.g. ISR asset endurance low, "
                    "CIVCAS risk elevated, stale intelligence).",
    )


class CommanderLogEntry(BaseModel):
    """
    A single entry in the append-only Commander's Log maintained by the Operator LLM.
    The log provides chronological accountability for all decisions in the simulation.
    """
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_zulu: datetime = Field(default_factory=datetime.utcnow)
    cycle_id: str
    entry_type: Literal[
        "OPERATOR_COMMAND",
        "AGENT_EVENT",
        "ENGAGEMENT_AUTHORIZED",
        "ENGAGEMENT_HELD",
        "CIVCAS_REPORT",
        "CYCLE_START",
        "CYCLE_COMPLETE",
        "ISR_RETASK",
        "OPERATOR_GUIDANCE",
        "SYSTEM_NOTE",
    ] = Field(
        ...,
        description="Category of this log entry for filtering and display.",
    )
    actor: str = Field(
        ...,
        description="Who or what generated this entry. "
                    "E.g. 'OPERATOR', 'COMKJTF', 'ISR-TASKING', 'COLLECTION', 'SYSTEM'.",
    )
    subject_target: Optional[TargetID] = Field(
        None,
        description="Target this entry relates to, if applicable.",
    )
    content: str = Field(
        ...,
        description="The log entry content in plain language. Written in chronological "
                    "operational voice. E.g. 'COMKJTF AUTHORIZED engagement of VARNAK "
                    "(TGT-ECHO-001) via SOF direct action. Capture preferred. "
                    "JTAC confirmation required on approach.'",
    )
    related_report_id: Optional[str] = Field(
        None,
        description="report_id of the agent report this entry relates to, for traceability.",
    )
    classification: ClassificationMarking = ClassificationMarking.COSMIC_INDIGO_REL


# ─── Operator Tool Calls ──────────────────────────────────────────────────────

# DESIGN DECISION: Each tool call is modelled as a Union-discriminated Pydantic
# model with a 'tool_name' literal field. This allows the FastAPI endpoint to
# deserialise any tool call into the correct type without a separate endpoint
# per tool. The OperatorToolCall union covers all six tool types.


class CycleStartTool(BaseModel):
    """
    Operator tool: cycle_start
    Initiates a new F3EAD targeting cycle.
    The operator may specify the priority target; defaults to COMKJTF priority.
    """
    tool_name: Literal["cycle_start"] = "cycle_start"
    priority_target: TargetID = Field(
        default=TargetID.ECHO_001,
        description="Target to prioritise in this cycle.",
    )
    operator_intent: Optional[str] = Field(
        None,
        description="Optional plain-language operator intent statement to inject into agent context.",
    )


class RetaskISRTool(BaseModel):
    """
    Operator tool: retask_isr
    Redirects a named ISR asset to a new target/PIR.
    """
    tool_name: Literal["retask_isr"] = "retask_isr"
    asset: ISRAsset = Field(..., description="The ISR asset to retask.")
    new_target: TargetID = Field(..., description="The target to task the asset against.")
    new_pir: PIRNumber = Field(..., description="The PIR the retasked collection will address.")
    operator_rationale: str = Field(
        ...,
        description="Operator's rationale for the retask.",
    )


class AuthorizeTargetTool(BaseModel):
    """
    Operator tool: authorize_target
    Injects a COMKJTF engagement authorization decision into the Commander agent.
    This reflects an actual operator decision in the human-in-the-loop node.
    """
    tool_name: Literal["authorize_target"] = "authorize_target"
    target_id: TargetID = Field(..., description="The target being authorized.")
    tnp_id: str = Field(..., description="report_id of the TNP being actioned.")
    authorized: bool = Field(..., description="Whether engagement is authorized.")
    commanders_guidance: str = Field(
        ...,
        description="COMKJTF's guidance to the Execution agent.",
    )
    civcas_threshold: Optional[str] = Field(
        None,
        description="CIVCAS threshold constraint for this engagement.",
    )


class HoldTargetTool(BaseModel):
    """
    Operator tool: hold_target
    Places a target on hold, preventing the cycle from proceeding to Finish.
    """
    tool_name: Literal["hold_target"] = "hold_target"
    target_id: TargetID = Field(..., description="The target to place on hold.")
    hold_reason: HoldReason = Field(..., description="Reason for the hold.")
    hold_explanation: str = Field(..., description="Plain-language hold explanation.")
    resume_condition: Optional[str] = Field(
        None,
        description="Condition under which the hold should be lifted. "
                    "E.g. 'Resume when VARNAK POL reaches 72 hours.'",
    )


class RequestBDATool(BaseModel):
    """
    Operator tool: request_bda
    Directs the BDA agent to produce an immediate assessment of a target
    following execution, outside of the normal cycle cadence.
    """
    tool_name: Literal["request_bda"] = "request_bda"
    target_id: TargetID = Field(..., description="The target requiring BDA.")
    execution_report_id: str = Field(
        ...,
        description="report_id of the ExecutionReport to assess.",
    )
    urgency: Literal["IMMEDIATE", "PRIORITY", "ROUTINE"] = Field(
        default="PRIORITY",
        description="BDA urgency. IMMEDIATE = within 1hr. PRIORITY = within 6hrs. ROUTINE = next cycle.",
    )


class InjectCommanderGuidanceTool(BaseModel):
    """
    Operator tool: inject_commander_guidance
    Injects plain-language COMKJTF guidance into the cycle state and all
    subsequent agent contexts. Does not directly authorize or hold —
    it provides intent that agents must incorporate into their reasoning.
    """
    tool_name: Literal["inject_commander_guidance"] = "inject_commander_guidance"
    guidance: str = Field(
        ...,
        description="COMKJTF guidance in plain language. Will be injected into cycle state "
                    "and all subsequent agent system contexts. "
                    "E.g. 'Prioritise capture over lethal action for all ECHO personnel — "
                    "exploitation value is the strategic priority.'",
    )
    applies_to: Optional[List[TargetID]] = Field(
        None,
        description="If guidance applies to specific targets only, list them. "
                    "None = guidance applies to all targets in the cycle.",
    )


# Union of all operator tool call types
OperatorToolCall = Union[
    CycleStartTool,
    RetaskISRTool,
    AuthorizeTargetTool,
    HoldTargetTool,
    RequestBDATool,
    InjectCommanderGuidanceTool,
]


class OperatorToolResult(BaseModel):
    """
    What the FastAPI backend returns to the Operator LLM after processing a tool call.
    The Operator LLM uses this to confirm the action was taken and update its context.
    """
    tool_name: str = Field(
        ...,
        description="The tool call that was processed.",
    )
    success: bool = Field(
        ...,
        description="Whether the tool call was successfully processed.",
    )
    message: str = Field(
        ...,
        description="Plain-language result message for the Operator LLM context. "
                    "E.g. 'RAVEN-1 retasked from PIR-001 to PIR-002 (KAZMER / HESSEK north). "
                    "New collection window: 0600–0800Z. ISRTaskingOrder generated: CYCLE-0001-TASK-002.'",
    )
    affected_cycle_id: str = Field(
        ...,
        description="The cycle_id of the cycle affected by this tool call.",
    )
    generated_report_id: Optional[str] = Field(
        None,
        description="If the tool call generated a new report, its report_id.",
    )
    updated_cycle_state: Optional[CycleState] = Field(
        None,
        description="Updated CycleState snapshot following the tool call. "
                    "Injected into operator context for next turn.",
    )
    error_detail: Optional[str] = Field(
        None,
        description="If success=False, the error detail.",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — SSE EVENT ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════


class SSEEvent(BaseModel):
    """
    Server-Sent Event envelope for streaming agent state to the frontend.
    The FastAPI SSE endpoint wraps every state change in this envelope.
    The frontend uses event_type to route to the correct panel.

    DESIGN DECISION: Using a single SSE envelope type rather than typed
    event streams, because the React frontend routes on event_type string
    and the data field carries the full serialised report. This avoids
    the need for the frontend to maintain separate EventSource listeners
    per agent.
    """
    event_type: Literal[
        "cycle_state_update",
        "isr_tasking_order",
        "collection_report",
        "intelligence_assessment",
        "target_nomination_package",
        "engagement_authorization",
        "execution_report",
        "bda_report",
        "develop_lead",
        "commander_log_entry",
        "operator_tool_result",
        "simulation_error",
    ] = Field(
        ...,
        description="Event type string used by the frontend to route the payload.",
    )
    cycle_id: str
    timestamp_zulu: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(
        ...,
        description="The full serialised payload — a ReportBase subclass or CycleState, "
                    "serialised with model.model_dump().",
    )
    sequence: int = Field(
        ...,
        description="Monotonically increasing sequence number within the cycle. "
                    "Frontend uses this to detect missed events.",
        ge=0,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — CONVENIENCE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

# Map from event_type string → Pydantic model class.
# Used by both backend (serialisation) and frontend type-checking utilities.

REPORT_TYPE_REGISTRY: Dict[str, type] = {
    "isr_tasking_order": ISRTaskingOrder,
    "collection_report": CollectionReport,
    "intelligence_assessment": IntelligenceAssessment,
    "target_nomination_package": TargetNominationPackage,
    "engagement_authorization": EngagementAuthorization,
    "execution_report": ExecutionReport,
    "bda_report": BDAReport,
    "develop_lead": DevelopLead,
    "cycle_state": CycleState,
    "commander_log_entry": CommanderLogEntry,
    "sse_event": SSEEvent,
}

OPERATOR_TOOL_REGISTRY: Dict[str, type] = {
    "cycle_start": CycleStartTool,
    "retask_isr": RetaskISRTool,
    "authorize_target": AuthorizeTargetTool,
    "hold_target": HoldTargetTool,
    "request_bda": RequestBDATool,
    "inject_commander_guidance": InjectCommanderGuidanceTool,
}


# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN DECISIONS — FOR ARCHITECT REVIEW
# ═══════════════════════════════════════════════════════════════════════════════
#
# DD-001: ISRTaskingOrder added as an explicit schema type.
#         The original brief specified CollectionReport as the first report
#         type (Collection → All-Source). An ISRTaskingOrder (ISR Tasking →
#         Collection) was implied but not listed. It has been added as the
#         first step in the chain so that the Collection agent has a typed
#         input to act on. This is consistent with FM 3-60 collection
#         management doctrine.
#
# DD-002: ReportBase carries both target_id and narrative.
#         All reports inherit target_id (mandatory) and narrative (mandatory,
#         min 20 chars). This ensures the frontend can always render a
#         meaningful summary for any report type without type-specific logic.
#
# DD-003: ROEChecklist uses bool fields rather than an overall pass/fail.
#         Each of the four LOAC principles is a separate bool field. This
#         allows the Commander agent to see exactly which principle is
#         not satisfied, rather than a single gating boolean. The TNP
#         may be submitted with some bools=False — the Commander agent
#         decides whether to hold or deny.
#
# DD-004: EngagementAuthorization carries operator_injected flag.
#         This allows the LangGraph graph to distinguish between autonomous
#         Commander agent decisions and operator-driven decisions, preserving
#         accountability in the Commander's Log.
#
# DD-005: SSEEvent uses a single data: Dict field rather than typed unions.
#         Frontend receives event_type and routes accordingly. The dict is
#         the model_dump() of the relevant Pydantic model. This keeps the
#         SSE schema stable regardless of report type additions.
#
# DD-006: CycleState.pending_commander_decision drives frontend UI state.
#         When non-null, the frontend renders the Commander decision panel
#         (approve/deny/request-more). When null, it is hidden. This is a
#         clean signal without requiring the frontend to poll for TNPs.
#
# DD-007: DevelopLead.recommended_next_target may be None.
#         If the Develop agent identifies a new target not on the HPTL,
#         it sets this to None and populates new_target_nomination.
#         The ISR Tasking agent handles both cases in the next cycle.
#
# DD-008: TargetCycleStatus and ISRAssetStatus are embedded in CycleState
#         rather than being top-level report types. They are operational
#         tracking objects, not intelligence reports. This distinction
#         keeps the report type registry clean.
#
# DD-009: TimeWindow.confirmed field added.
#         The OILCAN RTL requires confirmed civilian absence. A TimeWindow
#         with confirmed=False means the window is assessed but not yet
#         verified by collection. This gates the OILCAN engagement.
#
# DD-010: CollectionReport.pol_hours_added and pol_total_hours added.
#         POL accumulation tracking is critical for KESTREL PID standard.
#         These fields allow the All-Source Analyst to compute PID status
#         without re-reading the full history of collection reports.
#
# ═══════════════════════════════════════════════════════════════════════════════
