package com.redhat.copperclaw.state;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/api/state")
public class StateResource {

    @Inject
    CycleStateStore store;

    @GET
    @Path("/current")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getCurrent() {
        return Response.ok(store.getCurrentStateJson()).build();
    }

    @GET
    @Path("/{cycleId}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getByCycleId(@PathParam("cycleId") String cycleId) {
        return Response.ok(store.getStateForCycle(cycleId)).build();
    }

    @GET
    @Path("/health")
    @Produces(MediaType.APPLICATION_JSON)
    public java.util.Map<String, String> health() {
        return java.util.Map.of("status", "UP", "service", "state-service");
    }
}
