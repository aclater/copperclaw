package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.copperclaw.shared.enums.IntelSourceType;
import com.copperclaw.shared.enums.IsrAsset;
import java.util.Optional;

public record IntelSource(
    @JsonProperty("source_type") IntelSourceType sourceType,
    @JsonProperty("asset_id") Optional<IsrAsset> assetId,
    @JsonProperty("report_age_hours") double reportAgeHours,
    @JsonProperty("reliability_grade") String reliabilityGrade,
    @JsonProperty("information_grade") String informationGrade,
    @JsonProperty("summary") String summary
) {}
