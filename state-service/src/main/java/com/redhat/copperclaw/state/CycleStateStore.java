package com.redhat.copperclaw.state;

import io.agroal.api.AgroalDataSource;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Inject;
import io.quarkus.runtime.StartupEvent;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import org.jboss.logging.Logger;

@ApplicationScoped
public class CycleStateStore {

    private static final Logger LOG = Logger.getLogger(CycleStateStore.class);

    @Inject
    AgroalDataSource dataSource;

    @Inject
    ObjectMapper objectMapper;

    void initDb(@Observes StartupEvent ev) {
        try (Connection conn = dataSource.getConnection();
             var stmt = conn.createStatement()) {
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS cycle_state (
                    cycle_id   TEXT PRIMARY KEY,
                    state_json JSONB NOT NULL DEFAULT '{}',
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """);
            LOG.info("CycleStateStore: schema initialised");
        } catch (SQLException e) {
            throw new RuntimeException("CycleStateStore: schema init failed", e);
        }
    }

    /**
     * Upsert a new agent report into the cycle's state_json using JSONB merge (|| operator).
     * The incoming message JSON is merged into the existing state, keyed by the agent name.
     */
    public void upsert(String messageJson, String agentKey) {
        String agentPatch;
        try {
            // Build a patch: {"AGENT_KEY": <full message node>}
            var msgNode = objectMapper.readTree(messageJson);
            agentPatch = objectMapper.writeValueAsString(
                objectMapper.createObjectNode().set(agentKey, msgNode)
            );
        } catch (Exception e) {
            LOG.warnf("CycleStateStore.upsert: could not parse message JSON for agent %s, storing as string", agentKey);
            agentPatch = "{\"" + agentKey + "\": {\"raw\": \"unparseable\"}}";
        }

        String cycleId = extractCycleId(messageJson);

        String sql = """
            INSERT INTO cycle_state (cycle_id, state_json, updated_at)
            VALUES (?, ?::jsonb, NOW())
            ON CONFLICT (cycle_id) DO UPDATE
              SET state_json = cycle_state.state_json || ?::jsonb,
                  updated_at = NOW()
            """;

        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cycleId);
            ps.setString(2, agentPatch);
            ps.setString(3, agentPatch);
            ps.executeUpdate();
        } catch (SQLException e) {
            LOG.errorf(e, "CycleStateStore.upsert failed for cycle %s agent %s", cycleId, agentKey);
        }
    }

    public String getCurrentStateJson() {
        String sql = "SELECT state_json FROM cycle_state ORDER BY updated_at DESC LIMIT 1";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            if (rs.next()) return rs.getString(1);
        } catch (SQLException e) {
            LOG.errorf(e, "CycleStateStore.getCurrentStateJson failed");
        }
        return "{}";
    }

    public String getStateForCycle(String cycleId) {
        String sql = "SELECT state_json FROM cycle_state WHERE cycle_id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cycleId);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) return rs.getString(1);
            }
        } catch (SQLException e) {
            LOG.errorf(e, "CycleStateStore.getStateForCycle failed for cycle %s", cycleId);
        }
        return "{}";
    }

    private String extractCycleId(String json) {
        try {
            return objectMapper.readTree(json).path("cycle_id").asText("CYCLE-UNKNOWN");
        } catch (Exception e) {
            return "CYCLE-UNKNOWN";
        }
    }
}
