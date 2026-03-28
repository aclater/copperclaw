from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from .enums import *


class GridReference(BaseModel):
    zone: str = Field(..., description="Grid zone, e.g. 'VICTOR-5'", examples=["VICTOR-5", "VICTOR-4", "VICTOR-6"])
    sector: str = Field(..., description="Sector letter within zone, e.g. 'KILO', 'LIMA', 'NOVEMBER'", examples=["KILO", "LIMA", "NOVEMBER", "OSCAR"])
    easting: str = Field(..., description="3-digit easting within sector", examples=["229", "312", "088"])
    northing: str = Field(..., description="3-digit northing within sector", examples=["447", "509", "271"])

    @property
    def full_grid(self) -> str:
        return f"{self.zone}-{self.sector}-{self.easting}-{self.northing}"

    def __str__(self) -> str:
        return self.full_grid


class TimeWindow(BaseModel):
    start_zulu: str = Field(..., description="Window start time in HHMM Zulu, e.g. '2200' for OILCAN civilian absence", examples=["2200", "0600", "1200"])
    end_zulu: str = Field(..., description="Window end time in HHMM Zulu", examples=["0300", "1800", "2359"])
    duration_hours: Optional[float] = Field(None, description="Duration in hours, computed or supplied")
    confirmed: bool = Field(False, description="Whether this window has been confirmed by collection (e.g. KITE-7 OILCAN window)")


class IntelSource(BaseModel):
    source_type: IntelSourceType = Field(..., description="Intelligence discipline of this source")
    asset_id: Optional[ISRAsset] = Field(None, description="Named ISR asset if applicable, e.g. RAVEN-1, KITE-7")
    report_age_hours: float = Field(..., description="Age of this source's reporting in hours at time of assessment. KESTREL standard: >72hr is considered stale for personality targets.", examples=[0.5, 6.0, 36.0, 48.0, 72.0])
    reliability_grade: str = Field(..., description="Source reliability grade A–F (A=completely reliable, F=reliability unknown). KITE-7 is graded B. EAGLE-SIGINT intermittent = C.", examples=["A", "B", "C", "D", "E", "F"])
    information_grade: str = Field(..., description="Information content grade 1–6 (1=confirmed, 6=cannot be judged). Used with reliability to form NATO STANAG source grading.", examples=["1", "2", "3", "4", "5", "6"])
    summary: str = Field(..., description="One-sentence summary of what this source reported, in plain language.")


class CivilianConsideration(BaseModel):
    cde_tier: CDETier = Field(..., description="CDE tier per ROE Card Alpha-7 Section 5. Determines engagement authority.")
    civilian_presence_assessed: bool = Field(..., description="Whether civilians are assessed to be present at or near the target.")
    civilian_count_estimate: Optional[int] = Field(None, description="Estimated civilian count if present. None = not assessed / zero confirmed.")
    nsl_proximity_metres: Optional[float] = Field(None, description="Distance to nearest NSL object in metres. HESSEK Mosque Complex and MORRUSK Hospital are NSL objects.")
    proportionality_statement: str = Field(..., description="Plain-language proportionality assessment: expected collateral harm vs anticipated military advantage. Must satisfy AJP-3.9 and ROE Alpha-7.")
    precautionary_measures: List[str] = Field(default_factory=list, description="List of precautionary measures taken or recommended.")


class ROEChecklist(BaseModel):
    military_necessity_met: bool = Field(..., description="Confirms the target offers definite military advantage. Every target nominated must contribute to attaining the commander's objectives (FM 3-60 §1-4).")
    distinction_confirmed: bool = Field(..., description="Confirms the target is a legitimate military objective, distinguished from civilians and civilian objects per LOAC.")
    proportionality_satisfied: bool = Field(..., description="Confirms expected CIVCAS/collateral damage is not excessive relative to anticipated concrete and direct military advantage.")
    precaution_applied: bool = Field(..., description="Confirms all feasible precautionary measures have been considered and applied per AJP-3.9 and ROE Alpha-7 Section 1.")
    pid_standard_met: bool = Field(..., description="Confirms Positive Identification has been achieved. For personality targets: dual-source, 72-hour POL minimum (KESTREL standard).")
    not_on_nsl: bool = Field(..., description="Confirms the target is NOT on the No-Strike List. NSL includes MORRUSK Hospital, HESSEK Mosque, UN-flagged facilities.")
    rtl_constraints_noted: Optional[str] = Field(None, description="If target is on the Restricted Target List, describes constraints. E.g. OILCAN: 'Engage only 2200–0500 local with confirmed civilian absence; no incendiary effects; precision munitions only.'")
    cde_completed: bool = Field(..., description="Confirms CDE has been completed where mandatory (all VICTOR-5/6 engagements). CDE is not required for STONEPILE (outside VICTOR-5/6, rural).")
    engagement_authority_confirmed: EngagementAuthority = Field(..., description="The engagement authority that applies to this target per ROE Alpha-7 and AGM. HVI and TST: COMKJTF. STONEPILE: TF KESTREL CDR.")
    legal_review_required: bool = Field(False, description="Whether JAG / legal review is required before engagement authority is granted. Mandatory for CDE 6 and all dual-use facilities with civilian presence.")

    @model_validator(mode="after")
    def all_loac_principles_checked(self) -> "ROEChecklist":
        """All four LOAC principles must be explicitly assessed."""
        return self


class ReportBase(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique report identifier (UUID4). Auto-generated.")
    classification: ClassificationMarking = Field(default=ClassificationMarking.COSMIC_INDIGO_REL, description="Exercise classification marking. All simulation outputs default to COSMIC INDIGO // REL KESTREL COALITION.")
    exercise_serial: str = Field(default="COPPERCLAW-SIM-001", description="Exercise serial identifier.")
    cycle_id: str = Field(..., description="Identifier for the F3EAD cycle this report belongs to. Format: CYCLE-NNNN, e.g. CYCLE-0001. Injected by LangGraph orchestrator.", examples=["CYCLE-0001", "CYCLE-0002"])
    phase: CyclePhase = Field(..., description="The F3EAD phase during which this report was produced.")
    producing_agent: str = Field(..., description="The agent role that produced this report. E.g. 'ISR-TASKING', 'COLLECTION', 'ALL-SOURCE-ANALYST'.", examples=["ISR-TASKING", "COLLECTION", "ALL-SOURCE-ANALYST", "TARGET-NOMINATION", "COMMANDER", "EXECUTION", "BDA", "DEVELOP"])
    timestamp_zulu: datetime = Field(default_factory=datetime.utcnow, description="Report production timestamp in Zulu time.")
    target_id: TargetID = Field(..., description="The primary HPTL target this report addresses.")
    narrative: str = Field(..., description="Plain-language narrative summary of this report. Must be parseable by a downstream agent and renderable in the frontend panel. Write in the voice of the producing agent's role.", min_length=20)
