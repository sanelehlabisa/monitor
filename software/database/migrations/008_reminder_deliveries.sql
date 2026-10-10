CREATE TABLE monitor.reminder_deliveries (
    id UUID PRIMARY KEY,
    meter_id UUID NOT NULL REFERENCES monitor.meters (id) ON DELETE CASCADE,
    reminder_type TEXT NOT NULL,
    dedupe_key TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    claimed_at TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reminder_delivery_type_valid CHECK (
        reminder_type IN ('monthly', 'low_balance')
    ),
    CONSTRAINT reminder_delivery_key_valid CHECK (
        dedupe_key = BTRIM(dedupe_key)
        AND CHAR_LENGTH(dedupe_key) BETWEEN 1 AND 32
    ),
    CONSTRAINT reminder_delivery_status_valid CHECK (
        status IN ('pending', 'sent')
    ),
    CONSTRAINT reminder_delivery_sent_state_valid CHECK (
        (status = 'pending' AND sent_at IS NULL)
        OR (status = 'sent' AND sent_at IS NOT NULL)
    ),
    UNIQUE (meter_id, reminder_type, dedupe_key)
);

CREATE INDEX reminder_deliveries_pending_idx
    ON monitor.reminder_deliveries (status, claimed_at);
