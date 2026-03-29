package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum EffectType {
    DESTROY("DESTROY"),
    NEUTRALISE("NEUTRALISE"),
    DISRUPT("DISRUPT"),
    DEGRADE("DEGRADE"),
    DENY("DENY"),
    SUPPRESS("SUPPRESS"),
    DECEIVE("DECEIVE"),
    DELAY("DELAY"),
    INTERDICT("INTERDICT"),
    REMOVE("REMOVE"),
    EXPLOIT("EXPLOIT");

    private final String value;
    EffectType(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
