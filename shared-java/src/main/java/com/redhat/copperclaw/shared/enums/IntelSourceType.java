package com.redhat.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum IntelSourceType {
    SIGINT("SIGINT"),
    HUMINT("HUMINT"),
    IMINT("IMINT"),
    OSINT("OSINT"),
    DOMEX("DOMEX"),
    ACOUSTIC("ACOUSTIC"),
    FUSION("FUSION");

    private final String value;
    IntelSourceType(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
