package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.copperclaw.shared.enums.TargetId;
import java.time.LocalDateTime;
import java.util.Optional;

public record CommanderLogEntry(
    @JsonProperty("entry_id") String entryId,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("entry_type") String entryType,
    @JsonProperty("actor") String actor,
    @JsonProperty("subject_target") Optional<TargetId> subjectTarget,
    @JsonProperty("content") String content,
    @JsonProperty("related_report_id") Optional<String> relatedReportId,
    @JsonProperty("classification") String classification
) {}
