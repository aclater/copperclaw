package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum IsrAsset {
    RAVEN_1("RAVEN-1"),
    RAVEN_2("RAVEN-2"),
    KITE_7("KITE-7"),
    EAGLE_SIGINT("EAGLE-SIGINT"),
    SHADOW_COMMS("SHADOW-COMMS"),
    JTAC_TEAM("JTAC-TEAM");

    private final String value;
    IsrAsset(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
