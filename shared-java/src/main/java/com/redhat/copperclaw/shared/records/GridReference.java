package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;

public record GridReference(
    @JsonProperty("zone") String zone,
    @JsonProperty("sector") String sector,
    @JsonProperty("easting") String easting,
    @JsonProperty("northing") String northing
) {}
