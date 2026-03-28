-- OPERATION COPPERCLAW — initial database schema
-- Table is created by Hibernate; this script runs after schema creation.
-- Seed a default cycle state record.
INSERT INTO cycle_state (cycle_id, state_json, updated_at)
VALUES ('CYCLE-0000', '{"cycle_id":"CYCLE-0000","status":"INITIALISED","targets":[]}', NOW())
ON CONFLICT (cycle_id) DO NOTHING;
