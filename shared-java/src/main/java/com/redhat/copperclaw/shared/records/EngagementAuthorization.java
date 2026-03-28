package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.redhat.copperclaw.shared.enums.CyclePhase;
import com.redhat.copperclaw.shared.enums.EngagementAuthority;
import com.redhat.copperclaw.shared.enums.ExecutionMethod;
import com.redhat.copperclaw.shared.enums.HoldReason;
import com.redhat.copperclaw.shared.enums.TargetId;
import java.time.LocalDateTime;
import java.util.Optional;

public record EngagementAuthorization(
    @JsonProperty("report_id") String reportId,
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("phase") CyclePhase phase,
    @JsonProperty("producing_agent") String producingAgent,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("narrative") String narrative,
    @JsonProperty("tnp_id") String tnpId,
    @JsonProperty("target_codename") String targetCodename,
    @JsonProperty("authorized") boolean authorized,
    @JsonProperty("hold_reason") Optional<HoldReason> holdReason,
    @JsonProperty("hold_explanation") Optional<String> holdExplanation,
    @JsonProperty("authority_level") EngagementAuthority authorityLevel,
    @JsonProperty("authorized_execution_method") Optional<ExecutionMethod> authorizedExecutionMethod,
    @JsonProperty("authorized_engagement_window") Optional<TimeWindow> authorizedEngagementWindow,
    @JsonProperty("commanders_guidance") String commandersGuidance,
    @JsonProperty("operator_injected") boolean operatorInjected,
    @JsonProperty("operator_instruction") Optional<String> operatorInstruction,
    @JsonProperty("civcas_threshold") Optional<String> civcasThreshold
) {}
