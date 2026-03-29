package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum ComponentId {
    GAMMA("GAMMA"),
    DELTA("DELTA"),
    ECHO("ECHO"),
    UNKNOWN("UNKNOWN");

    private final String value;
    ComponentId(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
