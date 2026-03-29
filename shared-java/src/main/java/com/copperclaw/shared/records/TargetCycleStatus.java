package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.copperclaw.shared.enums.BdaOutcome;
import com.copperclaw.shared.enums.CyclePhase;
import com.copperclaw.shared.enums.HoldReason;
import com.copperclaw.shared.enums.TargetId;
import java.util.Optional;

public record TargetCycleStatus(
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("codename") String codename,
    @JsonProperty("current_phase") CyclePhase currentPhase,
    @JsonProperty("pid_met") boolean pidMet,
    @JsonProperty("pol_hours_complete") Optional<Double> polHoursComplete,
    @JsonProperty("last_report_id") Optional<String> lastReportId,
    @JsonProperty("last_report_type") Optional<String> lastReportType,
    @JsonProperty("authorized") Optional<Boolean> authorized,
    @JsonProperty("bda_outcome") Optional<BdaOutcome> bdaOutcome,
    @JsonProperty("on_hold") boolean onHold,
    @JsonProperty("hold_reason") Optional<HoldReason> holdReason,
    @JsonProperty("notes") Optional<String> notes
) {}
