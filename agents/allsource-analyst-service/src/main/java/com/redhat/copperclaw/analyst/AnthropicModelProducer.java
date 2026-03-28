package com.redhat.copperclaw.analyst;

import dev.langchain4j.model.anthropic.AnthropicChatModel;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@ApplicationScoped
public class AnthropicModelProducer {

    @ConfigProperty(name = "langchain4j.anthropic.api-key")
    String apiKey;

    @ConfigProperty(name = "langchain4j.anthropic.model-name", defaultValue = "claude-sonnet-4-20250514")
    String modelName;

    @Produces
    @ApplicationScoped
    public AnthropicChatModel anthropicChatModel() {
        return AnthropicChatModel.builder()
            .apiKey(apiKey)
            .modelName(modelName)
            .maxTokens(4096)
            .build();
    }
}
