package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.copperclaw.shared.enums.IsrAsset;
import com.copperclaw.shared.enums.PirNumber;
import com.copperclaw.shared.enums.TargetId;
import java.util.Optional;

public record IsrAssetStatus(
    @JsonProperty("asset_id") IsrAsset assetId,
    @JsonProperty("currently_tasked") boolean currentlyTasked,
    @JsonProperty("current_task_target") Optional<TargetId> currentTaskTarget,
    @JsonProperty("current_pir") Optional<PirNumber> currentPir,
    @JsonProperty("available_from_zulu") Optional<String> availableFromZulu,
    @JsonProperty("endurance_hours_remaining") Optional<Double> enduranceHoursRemaining,
    @JsonProperty("notes") Optional<String> notes
) {}
