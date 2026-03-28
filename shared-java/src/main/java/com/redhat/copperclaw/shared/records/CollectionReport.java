package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.redhat.copperclaw.shared.enums.ConfidenceLevel;
import com.redhat.copperclaw.shared.enums.CyclePhase;
import com.redhat.copperclaw.shared.enums.IntelSourceType;
import com.redhat.copperclaw.shared.enums.IsrAsset;
import com.redhat.copperclaw.shared.enums.PirNumber;
import com.redhat.copperclaw.shared.enums.TargetId;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public record CollectionReport(
    @JsonProperty("report_id") String reportId,
    @JsonProperty("classification") String classification,
    @JsonProperty("exercise_serial") String exerciseSerial,
    @JsonProperty("cycle_id") String cycleId,
    @JsonProperty("phase") CyclePhase phase,
    @JsonProperty("producing_agent") String producingAgent,
    @JsonProperty("timestamp_zulu") LocalDateTime timestampZulu,
    @JsonProperty("target_id") TargetId targetId,
    @JsonProperty("narrative") String narrative,
    @JsonProperty("tasking_order_id") String taskingOrderId,
    @JsonProperty("asset_id") IsrAsset assetId,
    @JsonProperty("pir_addressed") List<PirNumber> pirAddressed,
    @JsonProperty("collection_start_zulu") String collectionStartZulu,
    @JsonProperty("collection_end_zulu") String collectionEndZulu,
    @JsonProperty("source_type") IntelSourceType sourceType,
    @JsonProperty("raw_intelligence") String rawIntelligence,
    @JsonProperty("location_confirmed") Optional<GridReference> locationConfirmed,
    @JsonProperty("pol_hours_added") Optional<Double> polHoursAdded,
    @JsonProperty("pol_total_hours") Optional<Double> polTotalHours,
    @JsonProperty("negative_information") Optional<String> negativeInformation,
    @JsonProperty("follow_on_collection_required") boolean followOnCollectionRequired,
    @JsonProperty("confidence") ConfidenceLevel confidence
) {}
