package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.copperclaw.shared.enums.ComponentId;
import com.copperclaw.shared.enums.ConfidenceLevel;
import com.copperclaw.shared.enums.CyclePhase;
import com.copperclaw.shared.enums.TargetId;
import com.copperclaw.shared.enums.TargetType;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public record IntelligenceAssessment(
    @JsonProperty("report_id") String reportId,
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("phase") CyclePhase phase,
    @JsonProperty("producing_agent") String producingAgent,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("narrative") String narrative,
    @JsonProperty("source_reports") List<String> sourceReports,
    @JsonProperty("sources") List<IntelSource> sources,
    @JsonProperty("target_type") TargetType targetType,
    @JsonProperty("target_codename") String targetCodename,
    @JsonProperty("siv_component") ComponentId sivComponent,
    @JsonProperty("confirmed_location") Optional<GridReference> confirmedLocation,
    @JsonProperty("location_confidence") ConfidenceLevel locationConfidence,
    @JsonProperty("pol_hours_complete") Optional<Double> polHoursComplete,
    @JsonProperty("pid_standard_met") boolean pidStandardMet,
    @JsonProperty("pid_shortfall") Optional<String> pidShortfall,
    @JsonProperty("intelligence_gaps") List<String> intelligenceGaps,
    @JsonProperty("exploitation_value") String exploitationValue,
    @JsonProperty("threat_to_friendly_forces") Optional<String> threatToFriendlyForces,
    @JsonProperty("recommended_action") String recommendedAction,
    @JsonProperty("overall_confidence") ConfidenceLevel overallConfidence
) {}
