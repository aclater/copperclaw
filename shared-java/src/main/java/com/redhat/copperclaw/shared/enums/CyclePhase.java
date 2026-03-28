package com.redhat.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum CyclePhase {
    FIND("FIND"),
    FIX("FIX"),
    FINISH("FINISH"),
    EXPLOIT("EXPLOIT"),
    ASSESS("ASSESS"),
    DEVELOP("DEVELOP"),
    HOLD("HOLD"),
    COMPLETE("COMPLETE");

    private final String value;
    CyclePhase(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
