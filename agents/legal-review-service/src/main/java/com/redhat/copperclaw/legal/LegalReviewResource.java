package com.redhat.copperclaw.legal;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.util.Map;

@Path("/legal-review")
public class LegalReviewResource {

    @GET
    @Path("/status")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> status() {
        return Map.of(
            "service", "legal-review-service",
            "status", "UP",
            "role", "LEGAL-REVIEW",
            "pipeline_position", "nomination->legal-review->commander"
        );
    }
}
