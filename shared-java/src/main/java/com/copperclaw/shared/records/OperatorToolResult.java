package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Optional;

public record OperatorToolResult(
    @JsonProperty("tool_name") String toolName,
    @JsonProperty("success") boolean success,
    @JsonProperty("message") String message,
    @JsonProperty("affected_cycle_id") String affectedCycleId,
    @JsonProperty("generated_report_id") Optional<String> generatedReportId,
    @JsonProperty("updated_cycle_state") Optional<CycleState> updatedCycleState,
    @JsonProperty("error_detail") Optional<String> errorDetail
) {}
