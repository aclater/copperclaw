package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.redhat.copperclaw.shared.enums.CyclePhase;
import com.redhat.copperclaw.shared.enums.IntelSourceType;
import com.redhat.copperclaw.shared.enums.IsrAsset;
import com.redhat.copperclaw.shared.enums.PirNumber;
import com.redhat.copperclaw.shared.enums.TargetId;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public record IsrTaskingOrder(
    @JsonProperty("report_id") String reportId,
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("phase") CyclePhase phase,
    @JsonProperty("producing_agent") String producingAgent,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("narrative") String narrative,
    @JsonProperty("pir_addressed") List<PirNumber> pirAddressed,
    @JsonProperty("asset_tasked") IsrAsset assetTasked,
    @JsonProperty("collection_window") TimeWindow collectionWindow,
    @JsonProperty("target_area") GridReference targetArea,
    @JsonProperty("collection_method") IntelSourceType collectionMethod,
    @JsonProperty("specific_indicators") List<String> specificIndicators,
    @JsonProperty("priority") int priority,
    @JsonProperty("retask_from_previous") boolean retaskFromPrevious,
    @JsonProperty("previous_task_id") Optional<String> previousTaskId
) {}
