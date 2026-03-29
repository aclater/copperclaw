package com.copperclaw.shared.records;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * LegalReviewAssessment — produced by legal-review-service, consumed by commander-service.
 * Sits between TargetNominationPackage and EngagementAuthorization in the F3EAD pipeline.
 */
public record LegalReviewAssessment(
    @JsonProperty("report_id")               String reportId,
    @JsonProperty("classification")          String classification,
    @JsonProperty("exercise_serial")         String exerciseSerial,
    @JsonProperty("cycle_id")                String cycleId,
    @JsonProperty("phase")                   String phase,
    @JsonProperty("producing_agent")         String producingAgent,
    @JsonProperty("timestamp_zulu")          String timestampZulu,
    @JsonProperty("target_id")              String targetId,
    @JsonProperty("narrative")               String narrative,
    @JsonProperty("tnp_id")                  String tnpId,
    @JsonProperty("target_codename")         String targetCodename,
    @JsonProperty("legal_cleared")           boolean legalCleared,
    @JsonProperty("blocking_issues")         List<String> blockingIssues,
    @JsonProperty("warnings")               List<String> warnings,
    @JsonProperty("military_necessity_assessment") String militaryNecessityAssessment,
    @JsonProperty("distinction_assessment")  String distinctionAssessment,
    @JsonProperty("proportionality_assessment") String proportionalityAssessment,
    @JsonProperty("precautions_assessment")  String precautionsAssessment,
    @JsonProperty("roe_compliance_verified") boolean roeComplianceVerified,
    @JsonProperty("rtl_constraints_confirmed") boolean rtlConstraintsConfirmed,
    @JsonProperty("legal_narrative")         String legalNarrative
) {}
