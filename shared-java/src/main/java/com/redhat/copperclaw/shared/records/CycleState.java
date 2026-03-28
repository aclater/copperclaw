package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.redhat.copperclaw.shared.enums.CyclePhase;
import com.redhat.copperclaw.shared.enums.PirNumber;
import com.redhat.copperclaw.shared.enums.TargetId;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public record CycleState(
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("cycle_sequence") int cycleSequence,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("overall_phase") CyclePhase overallPhase,
    @JsonProperty("commander_priority_target") TargetId commanderPriorityTarget,
    @JsonProperty("target_statuses") List<TargetCycleStatus> targetStatuses,
    @JsonProperty("isr_asset_statuses") List<IsrAssetStatus> isrAssetStatuses,
    @JsonProperty("active_pirs") List<PirNumber> activePirs,
    @JsonProperty("latest_report_ids") Map<String, String> latestReportIds,
    @JsonProperty("pending_commander_decision") Optional<String> pendingCommanderDecision,
    @JsonProperty("cycle_events") List<String> cycleEvents,
    @JsonProperty("operator_guidance_active") Optional<String> operatorGuidanceActive,
    @JsonProperty("simulation_warnings") List<String> simulationWarnings
) {}
