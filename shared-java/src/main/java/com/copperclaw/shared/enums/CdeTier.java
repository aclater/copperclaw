package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum CdeTier {
    CDE_1("CDE-1"),
    CDE_2("CDE-2"),
    CDE_3("CDE-3"),
    CDE_4("CDE-4"),
    CDE_5("CDE-5"),
    CDE_6("CDE-6"),
    NOT_REQUIRED("NOT-REQUIRED");

    private final String value;
    CdeTier(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
