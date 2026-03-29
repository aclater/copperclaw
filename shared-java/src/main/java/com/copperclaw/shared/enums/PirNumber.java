package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum PirNumber {
    PIR_001("PIR-001"),
    PIR_002("PIR-002"),
    PIR_003("PIR-003"),
    PIR_004("PIR-004"),
    PIR_NEW("PIR-NEW");

    private final String value;
    PirNumber(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
