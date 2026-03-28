package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Optional;

public record TimeWindow(
    @JsonProperty("start_zulu") String startZulu,
    @JsonProperty("end_zulu") String endZulu,
    @JsonProperty("duration_hours") Optional<Double> durationHours,
    @JsonProperty("confirmed") boolean confirmed
) {}
