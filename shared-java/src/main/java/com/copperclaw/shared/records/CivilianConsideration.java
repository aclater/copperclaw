package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.copperclaw.shared.enums.CdeTier;
import java.util.List;
import java.util.Optional;

public record CivilianConsideration(
    @JsonProperty("cde_tier") CdeTier cdeTier,
    @JsonProperty("civilian_presence_assessed") boolean civilianPresenceAssessed,
    @JsonProperty("civilian_count_estimate") Optional<Integer> civilianCountEstimate,
    @JsonProperty("nsl_proximity_metres") Optional<Double> nslProximityMetres,
    @JsonProperty("proportionality_statement") String proportionalityStatement,
    @JsonProperty("precautionary_measures") List<String> precautionaryMeasures
) {}
