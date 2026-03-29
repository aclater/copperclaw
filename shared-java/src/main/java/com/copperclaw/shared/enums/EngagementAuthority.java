package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum EngagementAuthority {
    COMKJTF("COMKJTF"),
    TF_KESTREL_CDR("TF-KESTREL-CDR"),
    J3_FIRES("J3-FIRES"),
    DENIED("DENIED"),
    PENDING("PENDING");

    private final String value;
    EngagementAuthority(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
