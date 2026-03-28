"""
Comprehensive tests for copperclaw_shared package.
All report types are instantiated with valid minimal data and validated.
"""
from __future__ import annotations

import uuid
import pytest

from copperclaw_shared import (
    # enums
    ClassificationMarking,
    TargetID,
    TargetCodename,
    ComponentID,
    ISRAsset,
    PIRNumber,
    EngagementAuthority,
    CyclePhase,
    ConfidenceLevel,
    CDETier,
    EffectType,
    IntelSourceType,
    TargetType,
    ExecutionMethod,
    BDAOutcome,
    HoldReason,
    # base_types
    GridReference,
    TimeWindow,
    IntelSource,
    CivilianConsideration,
    ROEChecklist,
    ReportBase,
    # reports
    ISRTaskingOrder,
    CollectionReport,
    IntelligenceAssessment,
    TargetNominationPackage,
    EngagementAuthorization,
    ExecutionReport,
    BDAReport,
    DevelopLead,
    # operator
    TargetCycleStatus,
    ISRAssetStatus,
    CycleState,
    CommanderLogEntry,
    CycleStartTool,
    RetaskISRTool,
    AuthorizeTargetTool,
    HoldTargetTool,
    RequestBDATool,
    InjectCommanderGuidanceTool,
    OperatorToolCall,
    OperatorToolResult,
    # sse
    SSEEvent,
    REPORT_TYPE_REGISTRY,
    OPERATOR_TOOL_REGISTRY,
    # kafka
    KafkaTopics,
)


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

CYCLE_ID = "CYCLE-0001"
PRODUCING_AGENT = "ISR-TASKING"
TARGET_ID = TargetID.ECHO_001
NARRATIVE = "Test narrative for unit testing purposes only."

GRID = GridReference(zone="VICTOR-5", sector="KILO", easting="229", northing="447")
WINDOW = TimeWindow(start_zulu="0600", end_zulu="0800")
INTEL_SOURCE = IntelSource(
    source_type=IntelSourceType.IMINT,
    report_age_hours=6.0,
    reliability_grade="B",
    information_grade="2",
    summary="Test source summary.",
)
CIVILIAN_CONSIDERATION = CivilianConsideration(
    cde_tier=CDETier.CDE_2,
    civilian_presence_assessed=False,
    proportionality_statement="No civilians assessed.",
)
ROE = ROEChecklist(
    military_necessity_met=True,
    distinction_confirmed=True,
    proportionality_satisfied=True,
    precaution_applied=True,
    pid_standard_met=True,
    not_on_nsl=True,
    cde_completed=True,
    engagement_authority_confirmed=EngagementAuthority.COMKJTF,
)

BASE_KWARGS = dict(
    cycle_id=CYCLE_ID,
    producing_agent=PRODUCING_AGENT,
    target_id=TARGET_ID,
    narrative=NARRATIVE,
)


# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------

class TestEnums:
    def test_classification_marking_values(self):
        assert ClassificationMarking.COSMIC_INDIGO == "COSMIC INDIGO"
        assert ClassificationMarking.COSMIC_INDIGO_REL == "COSMIC INDIGO // REL KESTREL COALITION"
        assert ClassificationMarking.UNCLASSIFIED_EXERCISE == "UNCLASSIFIED // EXERCISE"

    def test_target_id_values(self):
        assert TargetID.ECHO_001 == "TGT-ECHO-001"
        assert TargetID.ECHO_002 == "TGT-ECHO-002"
        assert len(TargetID) == 5

    def test_cycle_phase_values(self):
        phases = {p.value for p in CyclePhase}
        assert "FIND" in phases
        assert "FIX" in phases
        assert "FINISH" in phases
        assert "EXPLOIT" in phases
        assert "ASSESS" in phases
        assert "DEVELOP" in phases
        assert "HOLD" in phases
        assert "COMPLETE" in phases

    def test_hold_reason_values(self):
        assert HoldReason.PID_INSUFFICIENT == "PID-INSUFFICIENT"
        assert len(HoldReason) == 8

    def test_bda_outcome_values(self):
        assert BDAOutcome.TARGET_DESTROYED == "TARGET-DESTROYED"
        assert BDAOutcome.CIVCAS_ASSESSED == "CIVCAS-ASSESSED"


# ---------------------------------------------------------------------------
# Base type tests
# ---------------------------------------------------------------------------

class TestBaseTypes:
    def test_grid_reference(self):
        g = GridReference(zone="VICTOR-5", sector="KILO", easting="229", northing="447")
        assert g.full_grid == "VICTOR-5-KILO-229-447"
        assert str(g) == "VICTOR-5-KILO-229-447"

    def test_time_window(self):
        w = TimeWindow(start_zulu="2200", end_zulu="0300")
        assert w.start_zulu == "2200"
        assert w.confirmed is False

    def test_time_window_confirmed(self):
        w = TimeWindow(start_zulu="0600", end_zulu="0800", confirmed=True, duration_hours=2.0)
        assert w.confirmed is True
        assert w.duration_hours == 2.0

    def test_intel_source(self):
        src = IntelSource(
            source_type=IntelSourceType.SIGINT,
            report_age_hours=12.0,
            reliability_grade="C",
            information_grade="3",
            summary="SIGINT intercept of voice communications.",
        )
        assert src.source_type == IntelSourceType.SIGINT
        assert src.asset_id is None

    def test_civilian_consideration(self):
        cc = CivilianConsideration(
            cde_tier=CDETier.CDE_3,
            civilian_presence_assessed=True,
            civilian_count_estimate=5,
            proportionality_statement="Collateral harm is proportionate to military advantage.",
        )
        assert cc.civilian_count_estimate == 5

    def test_roe_checklist(self):
        assert ROE.military_necessity_met is True
        assert ROE.engagement_authority_confirmed == EngagementAuthority.COMKJTF
        assert ROE.legal_review_required is False


# ---------------------------------------------------------------------------
# Report type instantiation tests
# ---------------------------------------------------------------------------

class TestISRTaskingOrder:
    def test_instantiate(self):
        report = ISRTaskingOrder(
            **BASE_KWARGS,
            phase=CyclePhase.FIND,
            pir_addressed=[PIRNumber.PIR_001],
            asset_tasked=ISRAsset.RAVEN_1,
            collection_window=WINDOW,
            target_area=GRID,
            collection_method=IntelSourceType.IMINT,
            priority=1,
        )
        assert report.phase == CyclePhase.FIND
        assert report.asset_tasked == ISRAsset.RAVEN_1
        assert report.priority == 1
        assert report.retask_from_previous is False
        assert report.report_id  # auto-generated UUID

    def test_retask_fields(self):
        prev_id = str(uuid.uuid4())
        report = ISRTaskingOrder(
            **BASE_KWARGS,
            phase=CyclePhase.FIND,
            pir_addressed=[PIRNumber.PIR_001],
            asset_tasked=ISRAsset.KITE_7,
            collection_window=WINDOW,
            target_area=GRID,
            collection_method=IntelSourceType.IMINT,
            priority=2,
            retask_from_previous=True,
            previous_task_id=prev_id,
        )
        assert report.retask_from_previous is True
        assert report.previous_task_id == prev_id


class TestCollectionReport:
    def test_instantiate(self):
        tasking_id = str(uuid.uuid4())
        report = CollectionReport(
            **BASE_KWARGS,
            phase=CyclePhase.FIX,
            tasking_order_id=tasking_id,
            asset_id=ISRAsset.RAVEN_1,
            pir_addressed=[PIRNumber.PIR_001],
            collection_start_zulu="0600",
            collection_end_zulu="0800",
            source_type=IntelSourceType.IMINT,
            raw_intelligence="RAVEN-1 conducted imagery of VICTOR-5-KILO-229-447. A structure consistent with safe house was observed with two vehicles in compound.",
            follow_on_collection_required=False,
            confidence=ConfidenceLevel.MODERATE,
        )
        assert report.asset_id == ISRAsset.RAVEN_1
        assert report.confidence == ConfidenceLevel.MODERATE
        assert report.location_confirmed is None


class TestIntelligenceAssessment:
    def test_instantiate(self):
        report_ref = str(uuid.uuid4())
        report = IntelligenceAssessment(
            **BASE_KWARGS,
            phase=CyclePhase.FIX,
            source_reports=[report_ref],
            sources=[INTEL_SOURCE],
            target_type=TargetType.PERSONALITY,
            target_codename=TargetCodename.VARNAK,
            siv_component=ComponentID.ECHO,
            location_confidence=ConfidenceLevel.MODERATE,
            pid_standard_met=False,
            pid_shortfall="VARNAK POL is 56hrs complete; 16hrs additional observation required.",
            exploitation_value="CRITICAL",
            recommended_action="Continue collection to reach 72hr POL standard.",
            overall_confidence=ConfidenceLevel.MODERATE,
        )
        assert report.pid_standard_met is False
        assert report.target_codename == TargetCodename.VARNAK
        assert report.siv_component == ComponentID.ECHO


class TestTargetNominationPackage:
    def test_instantiate(self):
        assessment_id = str(uuid.uuid4())
        report = TargetNominationPackage(
            **BASE_KWARGS,
            phase=CyclePhase.FINISH,
            assessment_id=assessment_id,
            target_codename=TargetCodename.VARNAK,
            target_type=TargetType.PERSONALITY,
            target_location=GRID,
            desired_effect=EffectType.REMOVE,
            recommended_execution_method=ExecutionMethod.SOF_DIRECT_ACTION,
            roe_checklist=ROE,
            civilian_consideration=CIVILIAN_CONSIDERATION,
            is_tst=True,
            tst_justification="VARNAK presents fleeting opportunity; target confirmed at location.",
            exploitation_plan="Conduct DOMEX of captured materials and devices.",
            roe_compliance_summary="All four LOAC principles satisfied. Military necessity confirmed. Distinction confirmed. Proportionality assessed acceptable. Precautions applied.",
        )
        assert report.desired_effect == EffectType.REMOVE
        assert report.is_tst is True
        assert report.requesting_authority == "J2/J3 TF KESTREL"


class TestEngagementAuthorization:
    def test_authorized(self):
        tnp_id = str(uuid.uuid4())
        report = EngagementAuthorization(
            **BASE_KWARGS,
            phase=CyclePhase.FINISH,
            tnp_id=tnp_id,
            target_codename=TargetCodename.VARNAK,
            authorized=True,
            authority_level=EngagementAuthority.COMKJTF,
            authorized_execution_method=ExecutionMethod.SOF_DIRECT_ACTION,
            authorized_engagement_window=WINDOW,
            commanders_guidance="Execute direct action capture. Zero CIVCAS threshold applies.",
        )
        assert report.authorized is True
        assert report.hold_reason is None

    def test_held(self):
        tnp_id = str(uuid.uuid4())
        report = EngagementAuthorization(
            **BASE_KWARGS,
            phase=CyclePhase.FINISH,
            tnp_id=tnp_id,
            target_codename=TargetCodename.OILCAN,
            authorized=False,
            hold_reason=HoldReason.CDE_UNACCEPTABLE,
            hold_explanation="CDE assessment indicates unacceptable collateral damage risk.",
            authority_level=EngagementAuthority.COMKJTF,
            commanders_guidance="Hold pending revised CDE and precautionary measure review.",
        )
        assert report.authorized is False
        assert report.hold_reason == HoldReason.CDE_UNACCEPTABLE


class TestExecutionReport:
    def test_instantiate(self):
        auth_id = str(uuid.uuid4())
        report = ExecutionReport(
            **BASE_KWARGS,
            phase=CyclePhase.EXPLOIT,
            authorization_id=auth_id,
            target_codename=TargetCodename.VARNAK,
            execution_method_used=ExecutionMethod.SOF_DIRECT_ACTION,
            engagement_time_zulu="0215",
            engagement_grid=GRID,
            execution_narrative="SOF element conducted direct action at VICTOR-5-KILO-229-447. Target building was breached and secured within four minutes. No resistance encountered on entry.",
            immediate_effects_observed="Target structure secured. Two individuals detained for processing.",
            civcas_observed=False,
            exploitation_opportunity=True,
            exploitation_description="Two mobile devices and one laptop recovered. Document cache identified.",
            follow_on_isr_required=True,
        )
        assert report.civcas_observed is False
        assert report.exploitation_opportunity is True
        assert report.engagement_time_zulu == "0215"


class TestBDAReport:
    def test_instantiate(self):
        exec_id = str(uuid.uuid4())
        report = BDAReport(
            **BASE_KWARGS,
            phase=CyclePhase.ASSESS,
            execution_report_id=exec_id,
            target_codename=TargetCodename.VARNAK,
            desired_effect=EffectType.REMOVE,
            bda_outcome=BDAOutcome.TARGET_NEUTRALISED,
            physical_damage_assessment="Target individual detained and removed from the battlefield.",
            functional_damage_assessment="VARNAK's operational coordination role within the SLV network is disrupted.",
            network_effect_assessment="ECHO component of SLV network has lost primary coordinator.",
            civcas_confirmed=False,
            re_engagement_required=False,
            assessment_confidence=ConfidenceLevel.HIGH,
        )
        assert report.bda_outcome == BDAOutcome.TARGET_NEUTRALISED
        assert report.civcas_confirmed is False
        assert report.re_engagement_required is False


class TestDevelopLead:
    def test_instantiate(self):
        bda_id = str(uuid.uuid4())
        report = DevelopLead(
            **BASE_KWARGS,
            phase=CyclePhase.DEVELOP,
            bda_report_id=bda_id,
            source_target=TargetCodename.VARNAK,
            network_update="SLV ECHO component disrupted. GAMMA component remains active.",
            cycle_recommendation="Initiate next cycle against TGT-ECHO-002 (KAZMER).",
            new_leads=["Document references to KAZMER safe house location in VICTOR-6."],
            domex_products=["Two mobile devices", "One laptop", "Document cache"],
        )
        assert report.source_target == TargetCodename.VARNAK
        assert len(report.domex_products) == 3
        assert report.recommended_next_target is None


# ---------------------------------------------------------------------------
# Operator model tests
# ---------------------------------------------------------------------------

class TestOperatorModels:
    def test_target_cycle_status(self):
        status = TargetCycleStatus(
            target_id=TargetID.ECHO_001,
            codename=TargetCodename.VARNAK,
            current_phase=CyclePhase.FIND,
            pid_met=False,
        )
        assert status.on_hold is False
        assert status.authorized is None

    def test_isr_asset_status(self):
        status = ISRAssetStatus(
            asset_id=ISRAsset.RAVEN_1,
            currently_tasked=True,
            current_task_target=TargetID.ECHO_001,
            current_pir=PIRNumber.PIR_001,
        )
        assert status.currently_tasked is True

    def test_cycle_state(self):
        target_status = TargetCycleStatus(
            target_id=TargetID.ECHO_001,
            codename=TargetCodename.VARNAK,
            current_phase=CyclePhase.FIND,
            pid_met=False,
        )
        state = CycleState(
            cycle_id=CYCLE_ID,
            cycle_sequence=1,
            overall_phase=CyclePhase.FIND,
            target_statuses=[target_status],
        )
        assert state.cycle_sequence == 1
        assert state.classification == ClassificationMarking.COSMIC_INDIGO_REL
        assert len(state.target_statuses) == 1

    def test_commander_log_entry(self):
        entry = CommanderLogEntry(
            cycle_id=CYCLE_ID,
            entry_type="CYCLE_START",
            actor="SYSTEM",
            content="Cycle CYCLE-0001 initiated. Priority target: TGT-ECHO-001 (VARNAK).",
        )
        assert entry.entry_type == "CYCLE_START"
        assert entry.entry_id  # auto-generated

    def test_cycle_start_tool(self):
        tool = CycleStartTool(priority_target=TargetID.ECHO_001, operator_intent="Focus on VARNAK this cycle.")
        assert tool.tool_name == "cycle_start"

    def test_retask_isr_tool(self):
        tool = RetaskISRTool(
            asset=ISRAsset.RAVEN_2,
            new_target=TargetID.ECHO_002,
            new_pir=PIRNumber.PIR_002,
            operator_rationale="Shift collection to develop KAZMER lead.",
        )
        assert tool.tool_name == "retask_isr"

    def test_authorize_target_tool(self):
        tool = AuthorizeTargetTool(
            target_id=TargetID.ECHO_001,
            tnp_id=str(uuid.uuid4()),
            authorized=True,
            commanders_guidance="Execute as planned.",
        )
        assert tool.tool_name == "authorize_target"
        assert tool.authorized is True

    def test_hold_target_tool(self):
        tool = HoldTargetTool(
            target_id=TargetID.DELTA_001,
            hold_reason=HoldReason.ROE_NOT_MET,
            hold_explanation="ROE conditions have not been met for engagement.",
        )
        assert tool.tool_name == "hold_target"

    def test_request_bda_tool(self):
        tool = RequestBDATool(
            target_id=TargetID.ECHO_001,
            execution_report_id=str(uuid.uuid4()),
        )
        assert tool.tool_name == "request_bda"
        assert tool.urgency == "PRIORITY"

    def test_inject_commander_guidance_tool(self):
        tool = InjectCommanderGuidanceTool(
            guidance="Prioritise VARNAK capture over lethal action.",
            applies_to=[TargetID.ECHO_001],
        )
        assert tool.tool_name == "inject_commander_guidance"

    def test_operator_tool_result(self):
        target_status = TargetCycleStatus(
            target_id=TargetID.ECHO_001,
            codename=TargetCodename.VARNAK,
            current_phase=CyclePhase.FIND,
            pid_met=False,
        )
        state = CycleState(
            cycle_id=CYCLE_ID,
            cycle_sequence=1,
            overall_phase=CyclePhase.FIND,
            target_statuses=[target_status],
        )
        result = OperatorToolResult(
            tool_name="cycle_start",
            success=True,
            message="Cycle CYCLE-0001 started successfully.",
            affected_cycle_id=CYCLE_ID,
            updated_cycle_state=state,
        )
        assert result.success is True
        assert result.error_detail is None


# ---------------------------------------------------------------------------
# SSE model tests
# ---------------------------------------------------------------------------

class TestSSEEvent:
    def test_instantiate(self):
        event = SSEEvent(
            event_type="cycle_state_update",
            cycle_id=CYCLE_ID,
            data={"cycle_id": CYCLE_ID, "overall_phase": "FIND"},
            sequence=0,
        )
        assert event.event_type == "cycle_state_update"
        assert event.sequence == 0


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

class TestRegistries:
    def test_report_type_registry_has_12_keys(self):
        assert len(REPORT_TYPE_REGISTRY) == 12

    def test_report_type_registry_keys(self):
        expected_keys = {
            "isr_tasking_order",
            "collection_report",
            "intelligence_assessment",
            "target_nomination_package",
            "engagement_authorization",
            "execution_report",
            "bda_report",
            "develop_lead",
            "cycle_state",
            "commander_log_entry",
            "sse_event",
            "operator_tool_result",
        }
        assert set(REPORT_TYPE_REGISTRY.keys()) == expected_keys

    def test_operator_tool_registry_has_6_keys(self):
        assert len(OPERATOR_TOOL_REGISTRY) == 6

    def test_operator_tool_registry_keys(self):
        expected_keys = {
            "cycle_start",
            "retask_isr",
            "authorize_target",
            "hold_target",
            "request_bda",
            "inject_commander_guidance",
        }
        assert set(OPERATOR_TOOL_REGISTRY.keys()) == expected_keys

    def test_report_type_registry_values_are_classes(self):
        for key, cls in REPORT_TYPE_REGISTRY.items():
            assert isinstance(cls, type), f"{key} should map to a class"

    def test_operator_tool_registry_values_are_classes(self):
        for key, cls in OPERATOR_TOOL_REGISTRY.items():
            assert isinstance(cls, type), f"{key} should map to a class"


# ---------------------------------------------------------------------------
# KafkaTopics tests
# ---------------------------------------------------------------------------

class TestKafkaTopics:
    def test_has_11_topic_constants(self):
        topic_attrs = [
            attr for attr in dir(KafkaTopics)
            if not attr.startswith("_")
        ]
        assert len(topic_attrs) == 11

    def test_topic_values(self):
        assert KafkaTopics.ISR_TASKING == "copperclaw.isr-tasking"
        assert KafkaTopics.COLLECTION == "copperclaw.collection"
        assert KafkaTopics.ASSESSMENT == "copperclaw.assessment"
        assert KafkaTopics.NOMINATION == "copperclaw.nomination"
        assert KafkaTopics.AUTHORIZATION == "copperclaw.authorization"
        assert KafkaTopics.EXECUTION == "copperclaw.execution"
        assert KafkaTopics.BDA == "copperclaw.bda"
        assert KafkaTopics.DEVELOP == "copperclaw.develop"
        assert KafkaTopics.CYCLE_STATE == "copperclaw.cycle-state"
        assert KafkaTopics.COMMANDER_LOG == "copperclaw.commander-log"
        assert KafkaTopics.OPERATOR_COMMANDS == "copperclaw.operator-commands"

    def test_all_topics_start_with_copperclaw(self):
        topic_attrs = [attr for attr in dir(KafkaTopics) if not attr.startswith("_")]
        for attr in topic_attrs:
            value = getattr(KafkaTopics, attr)
            assert value.startswith("copperclaw."), f"{attr} should start with 'copperclaw.'"


# ---------------------------------------------------------------------------
# Default values / auto-generation tests
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_report_base_defaults(self):
        report = ISRTaskingOrder(
            **BASE_KWARGS,
            phase=CyclePhase.FIND,
            pir_addressed=[PIRNumber.PIR_001],
            asset_tasked=ISRAsset.RAVEN_1,
            collection_window=WINDOW,
            target_area=GRID,
            collection_method=IntelSourceType.IMINT,
            priority=1,
        )
        assert report.classification == ClassificationMarking.COSMIC_INDIGO_REL
        assert report.exercise_serial == "COPPERCLAW-SIM-001"
        assert report.report_id  # UUID was generated

    def test_report_ids_are_unique(self):
        kwargs = dict(
            **BASE_KWARGS,
            phase=CyclePhase.FIND,
            pir_addressed=[PIRNumber.PIR_001],
            asset_tasked=ISRAsset.RAVEN_1,
            collection_window=WINDOW,
            target_area=GRID,
            collection_method=IntelSourceType.IMINT,
            priority=1,
        )
        r1 = ISRTaskingOrder(**kwargs)
        r2 = ISRTaskingOrder(**kwargs)
        assert r1.report_id != r2.report_id

    def test_cycle_state_defaults(self):
        target_status = TargetCycleStatus(
            target_id=TargetID.ECHO_001,
            codename=TargetCodename.VARNAK,
            current_phase=CyclePhase.FIND,
            pid_met=False,
        )
        state = CycleState(
            cycle_id=CYCLE_ID,
            cycle_sequence=1,
            overall_phase=CyclePhase.FIND,
            target_statuses=[target_status],
        )
        assert state.commander_priority_target == TargetID.ECHO_001
        assert state.exercise_serial == "COPPERCLAW-SIM-001"
        assert state.isr_asset_statuses == []
        assert state.active_pirs == []
        assert state.latest_report_ids == {}
        assert state.cycle_events == []
        assert state.simulation_warnings == []
