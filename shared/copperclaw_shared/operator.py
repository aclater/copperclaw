from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .enums import *
from .base_types import *
from .reports import *


class TargetCycleStatus(BaseModel):
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
    asset_id: ISRAsset
    currently_tasked: bool
    current_task_target: Optional[TargetID] = None
    current_pir: Optional[PIRNumber] = None
    available_from_zulu: Optional[str] = None
    endurance_hours_remaining: Optional[float] = None
    notes: Optional[str] = None


class CycleState(BaseModel):
    classification: ClassificationMarking = ClassificationMarking.COSMIC_INDIGO_REL
    exercise_serial: str = "COPPERCLAW-SIM-001"
    cycle_id: str = Field(..., description="Current cycle identifier, e.g. CYCLE-0001.")
    cycle_sequence: int = Field(..., description="Monotonically increasing cycle counter.", ge=1)
    timestamp_zulu: datetime = Field(default_factory=datetime.utcnow)
    overall_phase: CyclePhase = Field(..., description="The current dominant phase of the cycle. Individual targets may be in different phases within the same cycle.")
    commander_priority_target: TargetID = Field(default=TargetID.ECHO_001, description="Current commander's priority target. Default: TGT-ECHO-001 (VARNAK).")
    target_statuses: List[TargetCycleStatus] = Field(..., description="Status of each HPTL target in the current cycle.")
    isr_asset_statuses: List[ISRAssetStatus] = Field(default_factory=list, description="Current status of each named ISR asset.")
    active_pirs: List[PIRNumber] = Field(default_factory=list, description="PIRs currently active and driving collection.")
    latest_report_ids: Dict[str, str] = Field(default_factory=dict, description="Map of producing_agent → latest report_id for that agent in this cycle.")
    pending_commander_decision: Optional[str] = Field(None, description="report_id of a TargetNominationPackage awaiting Commander decision. Non-null signals the frontend to render the Commander decision UI.")
    cycle_events: List[str] = Field(default_factory=list, description="Ordered list of significant cycle events as plain-language strings.")
    operator_guidance_active: Optional[str] = Field(None, description="Any active operator guidance injected via inject_commander_guidance tool. Displayed in the frontend and injected into agent context.")
    simulation_warnings: List[str] = Field(default_factory=list, description="Non-blocking warnings surfaced by agents.")


class CommanderLogEntry(BaseModel):
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
    ] = Field(..., description="Category of this log entry for filtering and display.")
    actor: str = Field(..., description="Who or what generated this entry. E.g. 'OPERATOR', 'COMKJTF', 'ISR-TASKING', 'COLLECTION', 'SYSTEM'.")
    subject_target: Optional[TargetID] = Field(None, description="Target this entry relates to, if applicable.")
    content: str = Field(..., description="The log entry content in plain language.")
    related_report_id: Optional[str] = Field(None, description="report_id of the agent report this entry relates to, for traceability.")
    classification: ClassificationMarking = ClassificationMarking.COSMIC_INDIGO_REL


class CycleStartTool(BaseModel):
    tool_name: Literal["cycle_start"] = "cycle_start"
    priority_target: TargetID = Field(default=TargetID.ECHO_001, description="Target to prioritise in this cycle.")
    operator_intent: Optional[str] = Field(None, description="Optional plain-language operator intent statement to inject into agent context.")


class RetaskISRTool(BaseModel):
    tool_name: Literal["retask_isr"] = "retask_isr"
    asset: ISRAsset = Field(..., description="The ISR asset to retask.")
    new_target: TargetID = Field(..., description="The target to task the asset against.")
    new_pir: PIRNumber = Field(..., description="The PIR the retasked collection will address.")
    operator_rationale: str = Field(..., description="Operator's rationale for the retask.")


class AuthorizeTargetTool(BaseModel):
    tool_name: Literal["authorize_target"] = "authorize_target"
    target_id: TargetID = Field(..., description="The target being authorized.")
    tnp_id: str = Field(..., description="report_id of the TNP being actioned.")
    authorized: bool = Field(..., description="Whether engagement is authorized.")
    commanders_guidance: str = Field(..., description="COMKJTF's guidance to the Execution agent.")
    civcas_threshold: Optional[str] = Field(None, description="CIVCAS threshold constraint for this engagement.")


class HoldTargetTool(BaseModel):
    tool_name: Literal["hold_target"] = "hold_target"
    target_id: TargetID = Field(..., description="The target to place on hold.")
    hold_reason: HoldReason = Field(..., description="Reason for the hold.")
    hold_explanation: str = Field(..., description="Plain-language hold explanation.")
    resume_condition: Optional[str] = Field(None, description="Condition under which the hold should be lifted.")


class RequestBDATool(BaseModel):
    tool_name: Literal["request_bda"] = "request_bda"
    target_id: TargetID = Field(..., description="The target requiring BDA.")
    execution_report_id: str = Field(..., description="report_id of the ExecutionReport to assess.")
    urgency: Literal["IMMEDIATE", "PRIORITY", "ROUTINE"] = Field(default="PRIORITY", description="BDA urgency. IMMEDIATE = within 1hr. PRIORITY = within 6hrs. ROUTINE = next cycle.")


class InjectCommanderGuidanceTool(BaseModel):
    tool_name: Literal["inject_commander_guidance"] = "inject_commander_guidance"
    guidance: str = Field(..., description="COMKJTF guidance in plain language. Will be injected into cycle state and all subsequent agent system contexts.")
    applies_to: Optional[List[TargetID]] = Field(None, description="If guidance applies to specific targets only, list them. None = guidance applies to all targets in the cycle.")


OperatorToolCall = Union[
    CycleStartTool,
    RetaskISRTool,
    AuthorizeTargetTool,
    HoldTargetTool,
    RequestBDATool,
    InjectCommanderGuidanceTool,
]


class OperatorToolResult(BaseModel):
    tool_name: str = Field(..., description="The tool call that was processed.")
    success: bool = Field(..., description="Whether the tool call was successfully processed.")
    message: str = Field(..., description="Plain-language result message for the Operator LLM context.")
    affected_cycle_id: str = Field(..., description="The cycle_id of the cycle affected by this tool call.")
    generated_report_id: Optional[str] = Field(None, description="If the tool call generated a new report, its report_id.")
    updated_cycle_state: Optional[CycleState] = Field(None, description="Updated CycleState snapshot following the tool call. Injected into operator context for next turn.")
    error_detail: Optional[str] = Field(None, description="If success=False, the error detail.")
