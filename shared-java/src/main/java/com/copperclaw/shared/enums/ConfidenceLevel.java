package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum ConfidenceLevel {
    HIGH("HIGH"),
    MODERATE("MODERATE"),
    LOW("LOW"),
    UNCONFIRMED("UNCONFIRMED");

    private final String value;
    ConfidenceLevel(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
