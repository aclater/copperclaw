package com.redhat.copperclaw.legal;

import dev.langchain4j.model.anthropic.AnthropicChatModel;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.output.Response;
import dev.langchain4j.data.message.AiMessage;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.reactive.messaging.Incoming;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.jboss.logging.Logger;

@ApplicationScoped
public class LegalReviewService {

    private static final Logger LOG = Logger.getLogger(LegalReviewService.class);

    @Inject
    ObjectMapper objectMapper;

    @Inject
    AnthropicChatModel model;

    @ConfigProperty(name = "copperclaw.agent.system-prompt-path")
    String systemPromptPath;

    @Channel("legal-review-out")
    Emitter<String> legalReviewEmitter;

    @Channel("cycle-state-out")
    Emitter<String> cycleStateEmitter;

    private String systemPrompt;

    private void loadSystemPrompt() {
        try {
            systemPrompt = Files.readString(Path.of(systemPromptPath));
        } catch (Exception e) {
            throw new RuntimeException("Failed to load system prompt from: " + systemPromptPath, e);
        }
    }

    @Incoming("nomination-in")
    public void processTnp(String message) {
        try {
            if (systemPrompt == null) loadSystemPrompt();

            var tnp = objectMapper.readTree(message);
            String cycleId = tnp.path("cycle_id").asText("UNKNOWN");
            String targetId = tnp.path("target_id").asText("UNKNOWN");
            String targetCodename = tnp.path("target_codename").asText("UNKNOWN");
            String tnpId = tnp.path("report_id").asText("UNKNOWN");

            LOG.infof("LEGAL-REVIEW: Processing TNP for %s (%s)", targetId, targetCodename);

            // --- Rule-based ROE/LOAC checklist ---
            List<String> blockingIssues = new ArrayList<>();
            List<String> warnings = new ArrayList<>();

            // 1. Check all four LOAC principles in ROE checklist
            var roe = tnp.path("roe_checklist");
            if (!roe.path("military_necessity_met").asBoolean(false))
                blockingIssues.add("ROE Alpha-7: military necessity not confirmed in TNP ROE checklist");
            if (!roe.path("distinction_confirmed").asBoolean(false))
                blockingIssues.add("ROE Alpha-7: distinction not confirmed — target legitimacy unverified");
            if (!roe.path("proportionality_satisfied").asBoolean(false))
                blockingIssues.add("ROE Alpha-7: proportionality not satisfied — CIVCAS/collateral risk unacceptable");
            if (!roe.path("precaution_applied").asBoolean(false))
                blockingIssues.add("ROE Alpha-7: precautionary measures not confirmed applied");
            if (!roe.path("pid_standard_met").asBoolean(false))
                blockingIssues.add("PID standard not met — dual-source confirmation and 72hr POL required");
            if (!roe.path("not_on_nsl").asBoolean(false))
                blockingIssues.add("CRITICAL: target may be on No-Strike List — engagement prohibited");
            if (!roe.path("cde_completed").asBoolean(false))
                warnings.add("CDE not confirmed complete — verify CDE requirement applicability");

            // 2. RTL check for OILCAN (TGT-DELTA-001)
            if ("TGT-DELTA-001".equals(targetId)) {
                var window = tnp.path("engagement_window");
                if (window.isMissingNode() || window.isNull() || !window.path("confirmed").asBoolean(false))
                    blockingIssues.add("OILCAN RTL: civilian absence window (2200–0300 local) not confirmed by current KITE-7 report");
                var rtl = roe.path("rtl_constraints_noted");
                if (rtl.isNull() || rtl.isMissingNode() || rtl.asText("").isBlank())
                    warnings.add("OILCAN RTL: rtl_constraints_noted field unpopulated in ROE checklist");
            }

            // 3. TST check — VARNAK/KAZMER require TST justification
            boolean isTst = tnp.path("is_tst").asBoolean(false);
            if (isTst) {
                var tstJustification = tnp.path("tst_justification");
                if (tstJustification.isNull() || tstJustification.isMissingNode() || tstJustification.asText("").isBlank())
                    blockingIssues.add("TST designation requires populated tst_justification per JP 3-60");
            }

            // 4. CDE tier check — CDE 6 requires legal review flag
            var civilianConsideration = tnp.path("civilian_consideration");
            String cdeTier = civilianConsideration.path("cde_tier").asText("CDE_1");
            if ("CDE_6".equals(cdeTier) && !roe.path("legal_review_required").asBoolean(false))
                blockingIssues.add("CDE Tier 6 engagement requires legal_review_required=true in ROE checklist");

            boolean legalCleared = blockingIssues.isEmpty();
            boolean rtlConfirmed = "TGT-DELTA-001".equals(targetId)
                && !tnp.path("engagement_window").isMissingNode()
                && tnp.path("engagement_window").path("confirmed").asBoolean(false);

            // --- Claude: generate legal narrative ---
            String blockingJson = objectMapper.writeValueAsString(blockingIssues);
            String warningsJson = objectMapper.writeValueAsString(warnings);

            String prompt = """
                You are the JAG legal advisor for Task Force KESTREL.

                TARGET NOMINATION PACKAGE (JSON):
                %s

                RULE-BASED ROE CHECKLIST RESULTS:
                - Legal cleared: %b
                - Blocking issues: %s
                - Warnings: %s

                Write a LegalReviewAssessment JSON object. Your legal_narrative must:
                1. Assess all four LOAC principles (military necessity, distinction, proportionality, precautions)
                2. Address any RTL constraints for OILCAN targets
                3. Address CIVCAS risk and CDE tier findings
                4. State clearly whether the target is cleared for execution
                5. Reference ROE Card Alpha-7 and applicable doctrine (AJP-3.9, FM 3-60)

                The following fields must exactly match the rule-based results:
                - legal_cleared: %b
                - blocking_issues: %s
                - rtl_constraints_confirmed: %b

                Populate all other fields. No prose, no markdown, no preamble. JSON only.
                Output must include: report_id (UUID4), classification ("COSMIC INDIGO // REL KESTREL COALITION"),
                exercise_serial ("COPPERCLAW-SIM-001"), cycle_id ("%s"), phase ("FINISH"),
                producing_agent ("LEGAL-REVIEW"), timestamp_zulu (ISO 8601), target_id ("%s"),
                target_codename ("%s"), tnp_id ("%s", legal_narrative, and all other LegalReviewAssessment fields.
                """.formatted(
                    message, legalCleared, blockingJson, warningsJson,
                    legalCleared, blockingJson, rtlConfirmed,
                    cycleId, targetId, targetCodename, tnpId
                );

            Response<AiMessage> response = model.generate(
                SystemMessage.from(systemPrompt),
                UserMessage.from(prompt)
            );

            String output = response.content().text()
                .replaceAll("(?s)```json\\s*", "")
                .replaceAll("(?s)```\\s*", "")
                .trim();

            objectMapper.readTree(output); // validate JSON
            legalReviewEmitter.send(output);

            cycleStateEmitter.send(objectMapper.writeValueAsString(Map.of(
                "event_type", "agent_output",
                "producing_agent", "LEGAL-REVIEW",
                "cycle_id", cycleId,
                "status", "COMPLETE",
                "legal_cleared", legalCleared
            )));

            LOG.infof("LEGAL-REVIEW: Assessment complete for %s. Cleared: %b. Blocking: %d. Warnings: %d",
                targetCodename, legalCleared, blockingIssues.size(), warnings.size());

        } catch (Exception e) {
            LOG.errorf(e, "LEGAL-REVIEW: Error processing TNP");
            try {
                cycleStateEmitter.send(objectMapper.writeValueAsString(Map.of(
                    "event_type", "agent_error",
                    "producing_agent", "LEGAL-REVIEW",
                    "error", e.getMessage() != null ? e.getMessage() : "unknown"
                )));
            } catch (Exception ignored) {}
        }
    }
}
