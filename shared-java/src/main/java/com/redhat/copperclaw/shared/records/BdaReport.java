package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.redhat.copperclaw.shared.enums.BdaOutcome;
import com.redhat.copperclaw.shared.enums.ConfidenceLevel;
import com.redhat.copperclaw.shared.enums.CyclePhase;
import com.redhat.copperclaw.shared.enums.EffectType;
import com.redhat.copperclaw.shared.enums.TargetId;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public record BdaReport(
    @JsonProperty("report_id") String reportId,
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("phase") CyclePhase phase,
    @JsonProperty("producing_agent") String producingAgent,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("narrative") String narrative,
    @JsonProperty("execution_report_id") String executionReportId,
    @JsonProperty("target_codename") String targetCodename,
    @JsonProperty("desired_effect") EffectType desiredEffect,
    @JsonProperty("bda_outcome") BdaOutcome bdaOutcome,
    @JsonProperty("physical_damage_assessment") String physicalDamageAssessment,
    @JsonProperty("functional_damage_assessment") String functionalDamageAssessment,
    @JsonProperty("network_effect_assessment") String networkEffectAssessment,
    @JsonProperty("civcas_confirmed") boolean civcasConfirmed,
    @JsonProperty("civcas_count") Optional<Integer> civcasCount,
    @JsonProperty("re_engagement_required") boolean reEngagementRequired,
    @JsonProperty("re_engagement_rationale") Optional<String> reEngagementRationale,
    @JsonProperty("exploitation_results") Optional<String> exploitationResults,
    @JsonProperty("bda_collection_gaps") List<String> bdaCollectionGaps,
    @JsonProperty("assessment_confidence") ConfidenceLevel assessmentConfidence
) {}
