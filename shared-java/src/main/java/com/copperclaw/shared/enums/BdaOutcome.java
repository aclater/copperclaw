package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum BdaOutcome {
    TARGET_DESTROYED("TARGET-DESTROYED"),
    TARGET_NEUTRALISED("TARGET-NEUTRALISED"),
    TARGET_DISRUPTED("TARGET-DISRUPTED"),
    EFFECT_NOT_ACHIEVED("EFFECT-NOT-ACHIEVED"),
    PARTIAL_EFFECT("PARTIAL-EFFECT"),
    UNKNOWN("UNKNOWN"),
    CIVCAS_ASSESSED("CIVCAS-ASSESSED");

    private final String value;
    BdaOutcome(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
