package com.redhat.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum TargetId {
    ECHO_001("TGT-ECHO-001"),
    ECHO_002("TGT-ECHO-002"),
    GAMMA_001("TGT-GAMMA-001"),
    DELTA_001("TGT-DELTA-001"),
    GAMMA_002("TGT-GAMMA-002");

    private final String value;
    TargetId(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
