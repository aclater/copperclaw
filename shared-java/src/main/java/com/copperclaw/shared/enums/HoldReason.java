package com.copperclaw.shared.enums;

import com.fasterxml.jackson.annotation.JsonValue;

public enum HoldReason {
    PID_INSUFFICIENT("PID-INSUFFICIENT"),
    CDE_UNACCEPTABLE("CDE-UNACCEPTABLE"),
    NSL_PROXIMITY("NSL-PROXIMITY"),
    ROE_NOT_MET("ROE-NOT-MET"),
    INTEL_STALE("INTEL-STALE"),
    LEGAL_REVIEW_REQUIRED("LEGAL-REVIEW-REQUIRED"),
    COMMANDER_DISCRETION("COMMANDER-DISCRETION"),
    AWAIT_CIVILIAN_WINDOW("AWAIT-CIVILIAN-WINDOW");

    private final String value;
    HoldReason(String value) { this.value = value; }
    @JsonValue public String getValue() { return value; }
}
