CREATE TABLE monitor.balance_entries (
    id UUID PRIMARY KEY,
    meter_id UUID NOT NULL REFERENCES monitor.meters (id) ON DELETE CASCADE,
    balance_kwh NUMERIC(12, 3) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT balance_entries_kwh_non_negative CHECK (balance_kwh >= 0),
    CONSTRAINT balance_entries_meter_time_unique UNIQUE (meter_id, occurred_at)
);

CREATE INDEX balance_entries_meter_time_idx
    ON monitor.balance_entries (meter_id, occurred_at DESC, id DESC);
