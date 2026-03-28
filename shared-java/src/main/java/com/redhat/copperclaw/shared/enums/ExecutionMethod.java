package com.redhat.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum ExecutionMethod {
    PRECISION_STRIKE("PRECISION-STRIKE"),
    ARTILLERY_FIRE("ARTILLERY-FIRE"),
    ATTACK_AVIATION("ATTACK-AVIATION"),
    SOF_DIRECT_ACTION("SOF-DIRECT-ACTION"),
    NON_KINETIC_EW("NON-KINETIC-EW"),
    NON_KINETIC_INFLUENCE("NON-KINETIC-INFLUENCE"),
    SURVEILLANCE_ONLY("SURVEILLANCE-ONLY");

    private final String value;
    ExecutionMethod(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
