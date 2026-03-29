package com.copperclaw.bda;

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.anthropic.AnthropicChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import java.time.Duration;
import java.util.Optional;

@ApplicationScoped
public class LlmModelProducer {

    @ConfigProperty(name = "llm.backend", defaultValue = "ramalama")
    String backend;

    @ConfigProperty(name = "llm.model", defaultValue = "qwen2.5:14b")
    String model;

    @ConfigProperty(name = "ramalama.base-url", defaultValue = "http://localhost:8080/v1")
    String ramalamaBaseUrl;

    @ConfigProperty(name = "anthropic.api-key")
    Optional<String> anthropicApiKey;

    @Produces
    @ApplicationScoped
    public ChatLanguageModel chatLanguageModel() {
        if ("anthropic".equalsIgnoreCase(backend)) {
            return AnthropicChatModel.builder()
                .apiKey(anthropicApiKey.orElseThrow(() ->
                    new IllegalStateException(
                        "ANTHROPIC_API_KEY required when LLM_BACKEND=anthropic")))
                .modelName(model.isBlank() ? "claude-sonnet-4-20250514" : model)
                .maxTokens(4096)
                .timeout(Duration.ofSeconds(60))
                .build();
        }
        return OpenAiChatModel.builder()
            .baseUrl(ramalamaBaseUrl)
            .apiKey("ramalama")
            .modelName(model)
            .maxTokens(4096)
            .timeout(Duration.ofSeconds(120))
            .logRequests(false)
            .logResponses(false)
            .build();
    }
}
