package com.copperclaw.state;

/**
 * Plain POJO for carrying cycle state data — no JPA/Hibernate.
 * State persistence is handled by CycleStateStore via plain JDBC.
 */
public record CycleStateEntity(String cycleId, String stateJson, java.time.Instant updatedAt) {}
