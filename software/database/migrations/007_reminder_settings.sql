CREATE TABLE monitor.reminder_settings (
    meter_id UUID PRIMARY KEY
        REFERENCES monitor.meters (id) ON DELETE CASCADE,
    monthly_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    monthly_day SMALLINT NOT NULL DEFAULT 1,
    low_balance_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    low_balance_days NUMERIC(4,2) NOT NULL DEFAULT 3.00,
    timezone TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reminder_monthly_day_valid CHECK (monthly_day BETWEEN 1 AND 28),
    CONSTRAINT reminder_low_balance_days_valid CHECK (
        low_balance_days > 0 AND low_balance_days <= 30
    ),
    CONSTRAINT reminder_timezone_valid CHECK (
        timezone = BTRIM(timezone) AND CHAR_LENGTH(timezone) BETWEEN 1 AND 64
    )
);
