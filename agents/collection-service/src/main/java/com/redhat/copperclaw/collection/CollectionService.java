package com.redhat.copperclaw.collection;

import dev.langchain4j.model.anthropic.AnthropicChatModel;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.output.Response;
import dev.langchain4j.data.message.AiMessage;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.reactive.messaging.Incoming;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.jboss.logging.Logger;

@ApplicationScoped
public class CollectionService {

    private static final Logger LOG = Logger.getLogger(CollectionService.class);

    @Inject
    ObjectMapper objectMapper;

    @Inject
    AnthropicChatModel model;

    @ConfigProperty(name = "copperclaw.agent.system-prompt-path")
    String systemPromptPath;

    @Channel("collection-out")
    Emitter<String> outputEmitter;

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

    @Incoming("isr-tasking-in")
    public void process(String message) {
        try {
            if (systemPrompt == null) loadSystemPrompt();

            String prompt = buildPrompt(message);

            Response<AiMessage> response = model.generate(
                SystemMessage.from(systemPrompt),
                UserMessage.from(prompt)
            );

            String output = response.content().text();

            // Validate output is parseable JSON before emitting
            objectMapper.readTree(output);

            outputEmitter.send(output);

            String cycleStateUpdate = buildCycleStateUpdate(message, output);
            cycleStateEmitter.send(cycleStateUpdate);

        } catch (Exception e) {
            LOG.errorf(e, "COLLECTION processing error");
            publishError(message, e);
        }
    }

    private String buildPrompt(String incomingMessage) {
        return """
            You are processing the following input message from the COPPERCLAW targeting cycle.

            INPUT MESSAGE (JSON):
            %s

            Produce your output as a single valid JSON object matching your output schema.
            No prose, no markdown, no preamble. JSON only.
            """.formatted(incomingMessage);
    }

    private String buildCycleStateUpdate(String input, String output) {
        try {
            var inputNode = objectMapper.readTree(input);
            String cycleId = inputNode.path("cycle_id").asText("UNKNOWN");
            return objectMapper.writeValueAsString(Map.of(
                "event_type", "agent_output",
                "producing_agent", "COLLECTION",
                "cycle_id", cycleId,
                "status", "COMPLETE"
            ));
        } catch (Exception e) {
            return "{\"event_type\":\"agent_error\",\"producing_agent\":\"COLLECTION\"}";
        }
    }

    private void publishError(String input, Exception e) {
        try {
            String errorEvent = objectMapper.writeValueAsString(Map.of(
                "event_type", "agent_error",
                "producing_agent", "COLLECTION",
                "error", e.getMessage() != null ? e.getMessage() : "unknown"
            ));
            cycleStateEmitter.send(errorEvent);
        } catch (Exception ignored) {}
    }
}
