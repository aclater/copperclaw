package com.redhat.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.redhat.copperclaw.shared.enums.EngagementAuthority;
import java.util.Optional;

public record RoeChecklist(
    @JsonProperty("military_necessity_met") boolean militaryNecessityMet,
    @JsonProperty("distinction_confirmed") boolean distinctionConfirmed,
    @JsonProperty("proportionality_satisfied") boolean proportionalitySatisfied,
    @JsonProperty("precaution_applied") boolean precautionApplied,
    @JsonProperty("pid_standard_met") boolean pidStandardMet,
    @JsonProperty("not_on_nsl") boolean notOnNsl,
    @JsonProperty("rtl_constraints_noted") Optional<String> rtlConstraintsNoted,
    @JsonProperty("cde_completed") boolean cdeCompleted,
    @JsonProperty("engagement_authority_confirmed") EngagementAuthority engagementAuthorityConfirmed,
    @JsonProperty("legal_review_required") boolean legalReviewRequired
) {}
