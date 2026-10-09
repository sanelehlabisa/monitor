CREATE TABLE monitor.top_up_entries (
    id UUID PRIMARY KEY,
    meter_id UUID NOT NULL REFERENCES monitor.meters (id) ON DELETE CASCADE,
    top_up_kwh NUMERIC(12, 3) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT top_up_entries_kwh_positive CHECK (top_up_kwh > 0)
);

CREATE INDEX top_up_entries_meter_time_idx
    ON monitor.top_up_entries (meter_id, occurred_at DESC, id DESC);
