package com.redhat.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum TargetType {
    PERSONALITY("PERSONALITY"),
    MATERIEL("MATERIEL"),
    NODE("NODE"),
    DUAL_USE("DUAL_USE"),
    FIRE_POSITION("FIRE_POSITION"),
    NETWORK("NETWORK");

    private final String value;
    TargetType(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
