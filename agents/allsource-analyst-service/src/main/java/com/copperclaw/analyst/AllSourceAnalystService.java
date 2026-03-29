package com.copperclaw.analyst;

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.output.Response;
import dev.langchain4j.data.message.AiMessage;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.reactive.messaging.Incoming;
import io.smallrye.reactive.messaging.annotations.Blocking;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.jboss.logging.Logger;

@ApplicationScoped
public class AllSourceAnalystService {

    private static final Logger LOG = Logger.getLogger(AllSourceAnalystService.class);

    @Inject
    ObjectMapper objectMapper;

    @Inject
    ChatLanguageModel model;

    @ConfigProperty(name = "copperclaw.agent.system-prompt-path")
    String systemPromptPath;

    @ConfigProperty(name = "copperclaw.analyst.flush-interval-seconds", defaultValue = "10")
    long flushIntervalSeconds;

    @Channel("assessment-out")
    Emitter<String> outputEmitter;

    @Channel("cycle-state-out")
    Emitter<String> cycleStateEmitter;

    /** Key: cycle_id, Value: list of raw CollectionReport JSON strings */
    private final ConcurrentHashMap<String, List<String>> pending = new ConcurrentHashMap<>();

    private String systemPrompt;
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    // Called by Quarkus after injection
    void onStart(@jakarta.enterprise.event.Observes io.quarkus.runtime.StartupEvent ev) {
        scheduler.scheduleAtFixedRate(this::flushAll, flushIntervalSeconds, flushIntervalSeconds, TimeUnit.SECONDS);
        LOG.infof("ALL-SOURCE-ANALYST: accumulator flush scheduled every %d seconds", flushIntervalSeconds);
    }

    private void loadSystemPrompt() {
        try {
            systemPrompt = Files.readString(Path.of(systemPromptPath));
        } catch (Exception e) {
            throw new RuntimeException("Failed to load system prompt from: " + systemPromptPath, e);
        }
    }

    @Blocking
    @Incoming("collection-in")
    public void onCollectionReport(String message) {
        try {
            var node = objectMapper.readTree(message);
            String cycleId = node.path("cycle_id").asText("UNKNOWN");
            pending.computeIfAbsent(cycleId, k -> new ArrayList<>()).add(message);
            LOG.infof("ALL-SOURCE-ANALYST: queued CollectionReport for cycle %s (total queued: %d)",
                cycleId, pending.get(cycleId).size());
        } catch (Exception e) {
            LOG.errorf(e, "ALL-SOURCE-ANALYST: failed to queue CollectionReport");
        }
    }

    private void flushAll() {
        for (String cycleId : pending.keySet()) {
            List<String> reports = pending.remove(cycleId);
            if (reports != null && !reports.isEmpty()) {
                flush(cycleId, reports);
            }
        }
    }

    private void flush(String cycleId, List<String> reports) {
        try {
            if (systemPrompt == null) loadSystemPrompt();

            String combined = String.join(",\n", reports);
            String prompt = """
                You are fusing the following CollectionReport(s) from the COPPERCLAW targeting cycle.
                Cycle ID: %s

                COLLECTION REPORTS (JSON array elements — one or more):
                [
                %s
                ]

                Fuse these reports into a single IntelligenceAssessment JSON object.
                No prose, no markdown, no preamble. JSON only.
                """.formatted(cycleId, combined);

            Response<AiMessage> response = model.generate(
                SystemMessage.from(systemPrompt),
                UserMessage.from(prompt)
            );

            String output = response.content().text()
                .replaceAll("(?s)```json\\s*", "")
                .replaceAll("(?s)```\\s*", "")
                .trim();

            objectMapper.readTree(output); // validate JSON
            outputEmitter.send(output);

            cycleStateEmitter.send(objectMapper.writeValueAsString(Map.of(
                "event_type", "agent_output",
                "producing_agent", "ALL-SOURCE-ANALYST",
                "cycle_id", cycleId,
                "status", "COMPLETE",
                "reports_fused", reports.size()
            )));

            LOG.infof("ALL-SOURCE-ANALYST: fused %d reports for cycle %s", reports.size(), cycleId);

        } catch (Exception e) {
            LOG.errorf(e, "ALL-SOURCE-ANALYST: flush failed for cycle %s", cycleId);
            try {
                cycleStateEmitter.send(objectMapper.writeValueAsString(Map.of(
                    "event_type", "agent_error",
                    "producing_agent", "ALL-SOURCE-ANALYST",
                    "cycle_id", cycleId,
                    "error", e.getMessage() != null ? e.getMessage() : "unknown"
                )));
            } catch (Exception ignored) {}
        }
    }
}
