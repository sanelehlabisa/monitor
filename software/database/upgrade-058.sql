-- Manual, one-time additive upgrade from the audited pre-058 schema.
-- Rehearsed on a copy only; applying to the current DB needs separate approval.
-- Run with psql -v ON_ERROR_STOP=1. Never run schema.sql or seed.sql here.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

ALTER TABLE monitor.users
    ADD COLUMN type TEXT NOT NULL DEFAULT 'user',
    ADD CONSTRAINT users_type_valid CHECK (type IN ('user', 'admin'));

CREATE TABLE monitor.user_meters (
    user_id BIGINT NOT NULL REFERENCES monitor.users (id) ON DELETE CASCADE,
    meter_id UUID NOT NULL REFERENCES monitor.meters (id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, meter_id)
);
CREATE INDEX user_meters_meter_user_idx ON monitor.user_meters (meter_id, user_id);

INSERT INTO monitor.user_meters (user_id, meter_id)
SELECT user_id, id FROM monitor.meters;

-- No existing-admin promotion, seeds, history rewrites or removal of owner fields.
-- At sharing cutover, repeat this backfill with ON CONFLICT DO NOTHING to cover
-- meters created while the owner-only application was still active.
COMMIT;
