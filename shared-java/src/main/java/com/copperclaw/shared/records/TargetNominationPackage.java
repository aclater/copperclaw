package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.copperclaw.shared.enums.CyclePhase;
import com.copperclaw.shared.enums.EffectType;
import com.copperclaw.shared.enums.ExecutionMethod;
import com.copperclaw.shared.enums.TargetId;
import com.copperclaw.shared.enums.TargetType;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public record TargetNominationPackage(
    @JsonProperty("report_id") String reportId,
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("phase") CyclePhase phase,
    @JsonProperty("producing_agent") String producingAgent,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("narrative") String narrative,
    @JsonProperty("assessment_id") String assessmentId,
    @JsonProperty("target_codename") String targetCodename,
    @JsonProperty("target_type") TargetType targetType,
    @JsonProperty("target_location") GridReference targetLocation,
    @JsonProperty("desired_effect") EffectType desiredEffect,
    @JsonProperty("recommended_execution_method") ExecutionMethod recommendedExecutionMethod,
    @JsonProperty("alternative_execution_methods") List<ExecutionMethod> alternativeExecutionMethods,
    @JsonProperty("engagement_window") Optional<TimeWindow> engagementWindow,
    @JsonProperty("roe_checklist") RoeChecklist roeChecklist,
    @JsonProperty("civilian_consideration") CivilianConsideration civilianConsideration,
    @JsonProperty("is_tst") boolean isTst,
    @JsonProperty("tst_justification") Optional<String> tstJustification,
    @JsonProperty("exploitation_plan") String exploitationPlan,
    @JsonProperty("requesting_authority") String requestingAuthority,
    @JsonProperty("roe_compliance_summary") String roeComplianceSummary
) {}
