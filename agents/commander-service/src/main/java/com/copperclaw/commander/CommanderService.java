package com.copperclaw.commander;

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.output.Response;
import dev.langchain4j.data.message.AiMessage;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.copperclaw.shared.records.CommanderLogEntry;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.reactive.messaging.Incoming;
import io.smallrye.reactive.messaging.annotations.Blocking;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.jboss.logging.Logger;

@ApplicationScoped
public class CommanderService {

    private static final Logger LOG = Logger.getLogger(CommanderService.class);

    @Inject
    ObjectMapper objectMapper;

    @Inject
    ChatLanguageModel model;

    @ConfigProperty(name = "copperclaw.agent.system-prompt-path")
    String systemPromptPath;

    @Channel("authorization-out")
    Emitter<String> authorizationEmitter;

    @Channel("cycle-state-out")
    Emitter<String> cycleStateEmitter;

    @Channel("commander-log-out")
    Emitter<String> commanderLogEmitter;

    /**
     * In-memory store of pending LegalReviewAssessments awaiting operator decision.
     * Key: target_id, Value: full LegalReviewAssessment JSON string.
     */
    private final ConcurrentHashMap<String, String> pendingAssessments = new ConcurrentHashMap<>();

    private String systemPrompt;

    private void emitCommanderLog(String cycleId, String entryType, String content, String relatedReportId) {
        try {
            var entry = new CommanderLogEntry(
                "CLG-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase(),
                LocalDateTime.now(),
                cycleId,
                entryType,
                "COMMANDER",
                Optional.empty(),
                content,
                Optional.ofNullable(relatedReportId),
                "UNCLASSIFIED//EXERCISE"
            );
            commanderLogEmitter.send(objectMapper.writeValueAsString(entry));
        } catch (Exception e) {
            LOG.warnf(e, "COMMANDER: Failed to emit commander-log entry");
        }
    }

    private void loadSystemPrompt() {
        try {
            systemPrompt = Files.readString(Path.of(systemPromptPath));
        } catch (Exception e) {
            throw new RuntimeException("Failed to load system prompt from: " + systemPromptPath, e);
        }
    }

    /**
     * Phase 1: LegalReviewAssessment received from legal-review-service.
     * Store it and publish a hold event to cycle-state.
     * Do NOT call Claude. Do NOT emit to authorization-out.
     * The cycle is paused here until the operator provides input.
     */
    @Blocking
    @Incoming("legal-review-in")
    public void processLegalReview(String message) {
        try {
            var lraNode = objectMapper.readTree(message);
            String targetId = lraNode.path("target_id").asText("UNKNOWN");
            String tnpId = lraNode.path("tnp_id").asText("UNKNOWN");
            String targetCodename = lraNode.path("target_codename").asText("UNKNOWN");
            String cycleId = lraNode.path("cycle_id").asText("UNKNOWN");
            boolean legalCleared = lraNode.path("legal_cleared").asBoolean(false);

            // Store LegalReviewAssessment awaiting operator decision
            pendingAssessments.put(targetId, message);

            LOG.infof("COMMANDER: LegalReviewAssessment received for %s (%s). Legal cleared: %b. Cycle paused.",
                targetId, targetCodename, legalCleared);

            emitCommanderLog(cycleId, "HOLD_ISSUED",
                "Legal review complete for " + targetCodename + " (" + targetId + "). Legal cleared: " + legalCleared
                + ". Cycle paused pending COMKJTF authorization.",
                tnpId);

            String holdEvent = objectMapper.writeValueAsString(Map.of(
                "event_type", "pending_commander_decision",
                "producing_agent", "COMMANDER",
                "cycle_id", cycleId,
                "target_id", targetId,
                "target_codename", targetCodename,
                "tnp_id", tnpId,
                "legal_cleared", legalCleared,
                "status", "AWAITING_OPERATOR_INPUT",
                "message", "Legal review complete. Cycle paused. Awaiting COMKJTF authorization via operator interface."
            ));
            cycleStateEmitter.send(holdEvent);

        } catch (Exception e) {
            LOG.errorf(e, "COMMANDER: Error storing LegalReviewAssessment");
        }
    }

    /**
     * Phase 2: Operator command received (AuthorizeTargetTool or HoldTargetTool).
     * Retrieve pending LegalReviewAssessment, call Claude, emit EngagementAuthorization.
     */
    @Blocking
    @Incoming("operator-commands-in")
    public void processOperatorCommand(String message) {
        try {
            var commandNode = objectMapper.readTree(message);
            String commandType = commandNode.path("tool_name").asText(
                commandNode.path("command_type").asText("UNKNOWN")
            );

            if (!commandType.contains("authorize") && !commandType.contains("hold") &&
                !commandType.contains("AUTHORIZE") && !commandType.contains("HOLD")) {
                LOG.debugf("COMMANDER: Ignoring non-authorization command: %s", commandType);
                return;
            }

            String targetId = commandNode.path("target_id").asText(
                commandNode.path("input").path("target_id").asText("UNKNOWN")
            );

            String pendingAssessment = pendingAssessments.get(targetId);
            if (pendingAssessment == null) {
                LOG.warnf("COMMANDER: No pending LegalReviewAssessment for target_id=%s. Ignoring.", targetId);
                return;
            }

            if (systemPrompt == null) loadSystemPrompt();

            String prompt = """
                You are processing a COMKJTF engagement authorization decision.

                LEGAL REVIEW ASSESSMENT (JSON):
                %s

                OPERATOR COMMAND (JSON):
                %s

                Based on the legal review and the operator's command, produce an EngagementAuthorization JSON object.
                The operator_injected field MUST be true.
                If the command is an authorization (authorized=true), produce a full authorization with commanders_guidance.
                If the command is a hold (authorized=false), produce a hold with hold_reason and hold_explanation.
                No prose, no markdown, no preamble. JSON only.
                """.formatted(pendingAssessment, message);

            Response<AiMessage> response = model.generate(
                SystemMessage.from(systemPrompt),
                UserMessage.from(prompt)
            );

            String output = response.content().text()
                .replaceAll("(?s)```json\\s*", "")
                .replaceAll("(?s)```\\s*", "")
                .trim();

            objectMapper.readTree(output); // validate JSON
            authorizationEmitter.send(output);
            pendingAssessments.remove(targetId);

            var outputNode = objectMapper.readTree(output);
            String cycleId = outputNode.path("cycle_id").asText("UNKNOWN");
            boolean authorized = outputNode.path("authorized").asBoolean(false);
            String entryType = authorized ? "AUTHORIZATION_ISSUED" : "HOLD_ORDER";
            String guidance = outputNode.path("commanders_guidance").asText(
                outputNode.path("hold_explanation").asText(""));
            emitCommanderLog(cycleId, entryType,
                (authorized ? "Engagement authorized for target " : "Hold order issued for target ")
                + targetId + ". " + guidance,
                null);

            cycleStateEmitter.send(objectMapper.writeValueAsString(Map.of(
                "event_type", "agent_output",
                "producing_agent", "COMMANDER",
                "cycle_id", cycleId,
                "status", "COMPLETE"
            )));

        } catch (Exception e) {
            LOG.errorf(e, "COMMANDER: Error processing operator command");
            try {
                cycleStateEmitter.send(objectMapper.writeValueAsString(Map.of(
                    "event_type", "agent_error",
                    "producing_agent", "COMMANDER",
                    "error", e.getMessage() != null ? e.getMessage() : "unknown"
                )));
            } catch (Exception ignored) {}
        }
    }
}
