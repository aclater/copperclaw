from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .enums import *
from .reports import *
from .operator import *


class SSEEvent(BaseModel):
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
    ] = Field(..., description="Event type string used by the frontend to route the payload.")
    cycle_id: str
    timestamp_zulu: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(..., description="The full serialised payload — a ReportBase subclass or CycleState, serialised with model.model_dump().")
    sequence: int = Field(..., description="Monotonically increasing sequence number within the cycle. Frontend uses this to detect missed events.", ge=0)


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
    "operator_tool_result": OperatorToolResult,
}

OPERATOR_TOOL_REGISTRY: Dict[str, type] = {
    "cycle_start": CycleStartTool,
    "retask_isr": RetaskISRTool,
    "authorize_target": AuthorizeTargetTool,
    "hold_target": HoldTargetTool,
    "request_bda": RequestBDATool,
    "inject_commander_guidance": InjectCommanderGuidanceTool,
}
