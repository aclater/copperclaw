package com.redhat.copperclaw.sse;

import io.smallrye.mutiny.Multi;
import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.util.Map;
import org.jboss.resteasy.reactive.RestStreamElementType;

@Path("/api")
public class SseBridgeResource {

    @Inject
    SseBridgeService sseBridgeService;

    @GET
    @Path("/stream")
    @Produces(MediaType.SERVER_SENT_EVENTS)
    @RestStreamElementType(MediaType.APPLICATION_JSON)
    public Multi<String> stream() {
        return sseBridgeService.stream();
    }

    @GET
    @Path("/stream/health")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> health() {
        return Map.of("status", "UP", "service", "sse-bridge-service");
    }
}
