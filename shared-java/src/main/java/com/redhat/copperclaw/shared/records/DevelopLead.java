package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.redhat.copperclaw.shared.enums.CyclePhase;
import com.redhat.copperclaw.shared.enums.TargetId;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public record DevelopLead(
    @JsonProperty("report_id") String reportId,
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("phase") CyclePhase phase,
    @JsonProperty("producing_agent") String producingAgent,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("narrative") String narrative,
    @JsonProperty("bda_report_id") String bdaReportId,
    @JsonProperty("source_target") String sourceTarget,
    @JsonProperty("new_leads") List<String> newLeads,
    @JsonProperty("new_pir_requirements") List<String> newPirRequirements,
    @JsonProperty("network_update") String networkUpdate,
    @JsonProperty("recommended_next_target") Optional<TargetId> recommendedNextTarget,
    @JsonProperty("new_target_nomination") Optional<String> newTargetNomination,
    @JsonProperty("cycle_recommendation") String cycleRecommendation,
    @JsonProperty("domex_products") List<String> domexProducts,
    @JsonProperty("dissemination_list") List<String> disseminationList
) {}
