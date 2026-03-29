package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.copperclaw.shared.enums.CyclePhase;
import com.copperclaw.shared.enums.ExecutionMethod;
import com.copperclaw.shared.enums.TargetId;
import java.time.LocalDateTime;
import java.util.Optional;

public record ExecutionReport(
    @JsonProperty("report_id") String reportId,
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("phase") CyclePhase phase,
    @JsonProperty("producing_agent") String producingAgent,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("narrative") String narrative,
    @JsonProperty("authorization_id") String authorizationId,
    @JsonProperty("target_codename") String targetCodename,
    @JsonProperty("execution_method_used") ExecutionMethod executionMethodUsed,
    @JsonProperty("method_deviation") Optional<String> methodDeviation,
    @JsonProperty("engagement_time_zulu") String engagementTimeZulu,
    @JsonProperty("engagement_grid") GridReference engagementGrid,
    @JsonProperty("execution_narrative") String executionNarrative,
    @JsonProperty("immediate_effects_observed") String immediateEffectsObserved,
    @JsonProperty("civcas_observed") boolean civcasObserved,
    @JsonProperty("civcas_detail") Optional<String> civcasDetail,
    @JsonProperty("exploitation_opportunity") boolean exploitationOpportunity,
    @JsonProperty("exploitation_description") Optional<String> exploitationDescription,
    @JsonProperty("follow_on_isr_required") boolean followOnIsrRequired
) {}
