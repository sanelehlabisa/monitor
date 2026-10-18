-- Reviewed Task 063 transition: rehearse on an isolated current-data copy only.
-- Live execution requires separate approval. Use psql -v ON_ERROR_STOP=1.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

LOCK TABLE monitor.meters, monitor.user_meters IN SHARE ROW EXCLUSIVE MODE;

-- Cover interim owner-only creations, not creators who left a shared meter.
INSERT INTO monitor.user_meters (user_id, meter_id)
SELECT meters.user_id, meters.id
FROM monitor.meters AS meters
WHERE NOT EXISTS (
    SELECT 1 FROM monitor.user_meters AS members WHERE members.meter_id = meters.id
)
ON CONFLICT DO NOTHING;

ALTER TABLE monitor.meters
    DROP CONSTRAINT meters_user_id_fkey,
    ADD CONSTRAINT meters_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES monitor.users (id) ON DELETE RESTRICT;

ALTER TABLE monitor.user_meters
    DROP CONSTRAINT user_meters_user_id_fkey,
    ADD CONSTRAINT user_meters_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES monitor.users (id) ON DELETE RESTRICT;

-- Preserve creator metadata, all records/roles/history and meter-deletion cascades.
COMMIT;
