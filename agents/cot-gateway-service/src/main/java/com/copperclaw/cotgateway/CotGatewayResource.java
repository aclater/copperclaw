package com.copperclaw.cotgateway;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.util.Map;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import jakarta.inject.Inject;

@Path("/cot-gateway")
public class CotGatewayResource {

    @ConfigProperty(name = "copperclaw.cot.simulation.enabled", defaultValue = "true")
    boolean simulationEnabled;

    @GET
    @Path("/status")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> status() {
        return Map.of(
            "service", "cot-gateway-service",
            "status", "UP",
            "mode", simulationEnabled ? "SIMULATION" : "MULTICAST"
        );
    }
}
