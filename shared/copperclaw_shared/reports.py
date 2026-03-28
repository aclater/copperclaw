from __future__ import annotations
from typing import List, Optional

from pydantic import Field

from .base_types import *
from .enums import *


class ISRTaskingOrder(ReportBase):
    phase: CyclePhase = CyclePhase.FIND
    pir_addressed: List[PIRNumber] = Field(..., description="PIR(s) this collection task is designed to answer. E.g. [PIR-001] for VARNAK location development.", min_length=1)
    asset_tasked: ISRAsset = Field(..., description="Named ISR asset being tasked. Must be available and appropriate to the collection requirement.")
    collection_window: TimeWindow = Field(..., description="The Zulu time window during which collection should occur.")
    target_area: GridReference = Field(..., description="Primary collection area. For PIR-001 (VARNAK): VICTOR-5-KILO-229-447 and adjacent grids in HESSEK District.")
    collection_method: IntelSourceType = Field(..., description="The intelligence discipline this asset will employ, e.g. IMINT for RAVEN-1.")
    specific_indicators: List[str] = Field(default_factory=list, description="Specific indicators the collection asset should look for.")
    priority: int = Field(..., description="Collection priority 1–5 (1=highest). Drives asset deconfliction.", ge=1, le=5)
    retask_from_previous: bool = Field(False, description="Whether this is a retask of an asset from a previous collection line. If True, previous_task_id should be populated.")
    previous_task_id: Optional[str] = Field(None, description="report_id of the ISRTaskingOrder this replaces, if retasking.")


class CollectionReport(ReportBase):
    phase: CyclePhase = CyclePhase.FIX
    tasking_order_id: str = Field(..., description="report_id of the ISRTaskingOrder that generated this collection.")
    asset_id: ISRAsset = Field(..., description="The ISR asset that conducted this collection.")
    pir_addressed: List[PIRNumber] = Field(..., description="PIR(s) this report partially or fully answers.")
    collection_start_zulu: str = Field(..., description="Collection window start in HHMM Zulu.", examples=["0600", "2200", "1430"])
    collection_end_zulu: str = Field(..., description="Collection window end in HHMM Zulu.", examples=["0800", "2300", "1600"])
    source_type: IntelSourceType = Field(..., description="Intelligence discipline of this collection.")
    raw_intelligence: str = Field(..., description="The raw intelligence product in plain language — what the sensor observed, intercepted, or reported. Written in the voice of the platform/source. Not yet fused or assessed.", min_length=30)
    location_confirmed: Optional[GridReference] = Field(None, description="If the collection confirmed a target location, the grid. None if not confirmed.")
    pol_hours_added: Optional[float] = Field(None, description="For personality targets: additional hours of pattern-of-life observation this collection contributes. VARNAK needs 24 more hours to reach 72hr standard.", ge=0)
    pol_total_hours: Optional[float] = Field(None, description="Running total of POL hours accumulated against this personality target. VARNAK baseline: 48hrs. PID requires 72hrs.", ge=0)
    negative_information: Optional[str] = Field(None, description="What the collection did NOT find, where relevant. Negative information is valid intelligence (FM 3-60 §2-10).")
    follow_on_collection_required: bool = Field(..., description="Whether additional collection is needed before PID standard can be met.")
    confidence: ConfidenceLevel = Field(..., description="Confidence in the accuracy of this collection report.")


class IntelligenceAssessment(ReportBase):
    phase: CyclePhase = CyclePhase.FIX
    source_reports: List[str] = Field(..., description="List of report_ids of CollectionReports fused in this assessment.", min_length=1)
    sources: List[IntelSource] = Field(..., description="Structured source list with reliability and information grades.", min_length=1)
    target_type: TargetType = Field(..., description="Target category per FM 3-60. Personality for HVI; NODE for IRONBOX; DUAL_USE for OILCAN; FIRE_POSITION for STONEPILE.")
    target_codename: TargetCodename = Field(..., description="HPTL codename for this target.")
    siv_component: ComponentID = Field(..., description="Which SLV component this target belongs to.")
    confirmed_location: Optional[GridReference] = Field(None, description="Current confirmed location. None if location not yet confirmed.")
    location_confidence: ConfidenceLevel = Field(..., description="Confidence in the confirmed location.")
    pol_hours_complete: Optional[float] = Field(None, description="For personality targets: total POL hours accumulated. KESTREL standard = 72hr minimum. VARNAK baseline: 48hr.")
    pid_standard_met: bool = Field(..., description="Whether KESTREL PID standard is met: dual-source confirmation AND 72-hour pattern of life for personality targets. This field gates whether a TNP can be generated.")
    pid_shortfall: Optional[str] = Field(None, description="If pid_standard_met=False, describes what is missing. E.g. 'VARNAK POL is 56hrs complete; 16hrs additional observation required.'")
    intelligence_gaps: List[str] = Field(default_factory=list, description="Remaining intelligence gaps for this target.")
    exploitation_value: str = Field(..., description="Assessment of intelligence exploitation value if target is engaged. VARNAK and KAZMER are CRITICAL. IRONBOX is MEDIUM.", examples=["CRITICAL", "HIGH", "MEDIUM", "LOW"])
    threat_to_friendly_forces: Optional[str] = Field(None, description="If the target poses a direct threat to friendly forces, describe it. STONEPILE poses mortar threat to FOB GREYSTONE.")
    recommended_action: str = Field(..., description="All-Source Analyst's recommended next action.")
    overall_confidence: ConfidenceLevel = Field(..., description="Overall assessment confidence across all sources.")


class TargetNominationPackage(ReportBase):
    phase: CyclePhase = CyclePhase.FINISH
    assessment_id: str = Field(..., description="report_id of the IntelligenceAssessment this TNP is based on.")
    target_codename: TargetCodename = Field(..., description="HPTL codename for this target.")
    target_type: TargetType = Field(..., description="Target type category.")
    target_location: GridReference = Field(..., description="Confirmed target location at time of nomination.")
    desired_effect: EffectType = Field(..., description="The desired effect from FM 3-60 §1-6 vocabulary. HVI targets: REMOVE. IRONBOX: DESTROY. OILCAN: DISRUPT. STONEPILE: NEUTRALISE.")
    recommended_execution_method: ExecutionMethod = Field(..., description="Recommended method of engagement. Must be appropriate to target type and ROE. HVI (capture preferred): SOF_DIRECT_ACTION. STONEPILE: ARTILLERY_FIRE.")
    alternative_execution_methods: List[ExecutionMethod] = Field(default_factory=list, description="Alternative execution methods if recommended method is unavailable.")
    engagement_window: Optional[TimeWindow] = Field(None, description="Recommended engagement window. Mandatory for OILCAN (2200–0300 local, civilian absence). Optional for other targets.")
    roe_checklist: ROEChecklist = Field(..., description="Completed ROE compliance checklist per ROE Card Alpha-7. All fields must be populated. Commander agent will review each field.")
    civilian_consideration: CivilianConsideration = Field(..., description="CDE and civilian presence assessment.")
    is_tst: bool = Field(..., description="Whether this target is designated as a Time-Sensitive Target. TST: VARNAK (TGT-ECHO-001) and KAZMER (TGT-ECHO-002) only.")
    tst_justification: Optional[str] = Field(None, description="If is_tst=True, the justification for TST designation. Required per JP 3-60: target must present fleeting opportunity or imminent threat.")
    exploitation_plan: str = Field(..., description="Plan for exploitation following Finish action.")
    requesting_authority: str = Field(default="J2/J3 TF KESTREL", description="The authority requesting this engagement.")
    roe_compliance_summary: str = Field(..., description="Plain-language summary of ROE compliance assessment. Written for COMKJTF review. Must address all four LOAC principles explicitly.")


class EngagementAuthorization(ReportBase):
    phase: CyclePhase = CyclePhase.FINISH
    tnp_id: str = Field(..., description="report_id of the TargetNominationPackage being actioned.")
    target_codename: TargetCodename = Field(..., description="HPTL codename.")
    authorized: bool = Field(..., description="Whether engagement is authorized. True = execute. False = hold (see hold_reason).")
    hold_reason: Optional[HoldReason] = Field(None, description="If authorized=False, the reason for holding. Must be populated.")
    hold_explanation: Optional[str] = Field(None, description="If authorized=False, plain-language explanation of the hold decision.")
    authority_level: EngagementAuthority = Field(..., description="The engagement authority being exercised.")
    authorized_execution_method: Optional[ExecutionMethod] = Field(None, description="If authorized=True, the approved execution method. May differ from TNP recommendation.")
    authorized_engagement_window: Optional[TimeWindow] = Field(None, description="If authorized=True, the approved engagement window. Commander may constrain the window further than TNP recommended.")
    commanders_guidance: str = Field(..., description="Commander's guidance to the Execution agent.")
    operator_injected: bool = Field(False, description="Whether this decision reflects a real operator input via the Operator LLM layer. If True, the operator's exact instruction is preserved in operator_instruction.")
    operator_instruction: Optional[str] = Field(None, description="The operator's natural-language instruction that drove this decision, if operator_injected=True.")
    civcas_threshold: Optional[str] = Field(None, description="Commander's explicit CIVCAS threshold for this engagement. E.g. 'Zero CIVCAS — abort if any civilian presence confirmed on target.' Mandatory for OILCAN and any CDE 5+ engagement.")


class ExecutionReport(ReportBase):
    phase: CyclePhase = CyclePhase.EXPLOIT
    authorization_id: str = Field(..., description="report_id of the EngagementAuthorization that directed this execution.")
    target_codename: TargetCodename = Field(..., description="HPTL codename of the target engaged.")
    execution_method_used: ExecutionMethod = Field(..., description="The execution method actually used (may differ from authorization if circumstances required adaptation).")
    method_deviation: Optional[str] = Field(None, description="If execution method differed from authorization, explain why.")
    engagement_time_zulu: str = Field(..., description="Time of engagement in HHMM Zulu.", examples=["0215", "1437", "2248"])
    engagement_grid: GridReference = Field(..., description="Grid at which the engagement occurred.")
    execution_narrative: str = Field(..., description="Detailed narrative of the execution. Written in the voice of the fires/effects simulator.", min_length=50)
    immediate_effects_observed: str = Field(..., description="Immediate effects observed at time of engagement — before BDA assessment.")
    civcas_observed: bool = Field(..., description="Whether any actual or suspected civilian casualties were observed. If True, immediate reporting to COMKJTF is mandatory per ROE Alpha-7 §7.")
    civcas_detail: Optional[str] = Field(None, description="If civcas_observed=True, detail of observed CIVCAS. Mandatory.")
    exploitation_opportunity: bool = Field(..., description="Whether the execution created exploitation opportunities (accessible site, captured persons, recoverable material).")
    exploitation_description: Optional[str] = Field(None, description="If exploitation_opportunity=True, what is available for exploitation.")
    follow_on_isr_required: bool = Field(..., description="Whether ISR tasking is needed immediately post-execution (e.g. for BDA collection).")


class BDAReport(ReportBase):
    phase: CyclePhase = CyclePhase.ASSESS
    execution_report_id: str = Field(..., description="report_id of the ExecutionReport this BDA assesses.")
    target_codename: TargetCodename = Field(..., description="HPTL codename of the assessed target.")
    desired_effect: EffectType = Field(..., description="The desired effect from the TNP against which this BDA assesses.")
    bda_outcome: BDAOutcome = Field(..., description="Assessment of whether the desired effect was achieved.")
    physical_damage_assessment: str = Field(..., description="Assessment of physical damage or status.")
    functional_damage_assessment: str = Field(..., description="Assessment of functional damage — has the target's military function been degraded?")
    network_effect_assessment: str = Field(..., description="Assessment of the effect on the broader SLV network.")
    civcas_confirmed: bool = Field(..., description="Whether civilian casualties are confirmed in BDA. If True, CIVCAS reporting chain must be triggered.")
    civcas_count: Optional[int] = Field(None, description="Confirmed or estimated CIVCAS count. Exercise use only.")
    re_engagement_required: bool = Field(..., description="Whether the target requires re-engagement to achieve the desired effect.")
    re_engagement_rationale: Optional[str] = Field(None, description="If re_engagement_required=True, the rationale.")
    exploitation_results: Optional[str] = Field(None, description="Summary of exploitation results from the Finish phase that inform BDA.")
    bda_collection_gaps: List[str] = Field(default_factory=list, description="Collection gaps remaining in the BDA — what could not be assessed.")
    assessment_confidence: ConfidenceLevel = Field(..., description="Confidence in this BDA assessment.")


class DevelopLead(ReportBase):
    phase: CyclePhase = CyclePhase.DEVELOP
    bda_report_id: str = Field(..., description="report_id of the BDAReport that generated these leads.")
    source_target: TargetCodename = Field(..., description="The HPTL target from whose exploitation these leads derive.")
    new_leads: List[str] = Field(default_factory=list, description="List of new intelligence leads generated by DOMEX and exploitation.")
    new_pir_requirements: List[str] = Field(default_factory=list, description="New Priority Intelligence Requirements generated by the Develop phase.")
    network_update: str = Field(..., description="Updated assessment of the SLV target network following this cycle.")
    recommended_next_target: Optional[TargetID] = Field(None, description="Recommended HPTL target for the next cycle, based on lead analysis.")
    new_target_nomination: Optional[str] = Field(None, description="If a new target not on the current HPTL is identified, describe it here for J2 development.")
    cycle_recommendation: str = Field(..., description="Develop agent's recommendation for next cycle action.")
    domex_products: List[str] = Field(default_factory=list, description="List of DOMEX products generated (documents, devices, media).")
    dissemination_list: List[str] = Field(default_factory=list, description="Agencies and cells to which DOMEX products and leads are disseminated.")
