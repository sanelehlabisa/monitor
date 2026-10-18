-- Fresh empty databases only. Existing data uses the separately approved upgrade.
BEGIN;
CREATE SCHEMA monitor;

CREATE TABLE monitor.users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    type TEXT NOT NULL DEFAULT 'user',
    CONSTRAINT users_email_normalized CHECK (
        email <> '' AND email = LOWER(BTRIM(email))
    ),
    CONSTRAINT users_type_valid CHECK (type IN ('user', 'admin'))
);

CREATE TABLE monitor.otp_challenges (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL,
    code_digest TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    attempt_count SMALLINT NOT NULL DEFAULT 0,
    max_attempts SMALLINT NOT NULL DEFAULT 5,
    used_at TIMESTAMPTZ,
    invalidated_at TIMESTAMPTZ,
    CONSTRAINT otp_email_normalized CHECK (
        email <> '' AND email = LOWER(BTRIM(email))
    ),
    CONSTRAINT otp_digest_is_sha256_hex CHECK (code_digest ~ '^[0-9a-f]{64}$'),
    CONSTRAINT otp_expiry_after_creation CHECK (expires_at > created_at),
    CONSTRAINT otp_attempts_valid CHECK (
        max_attempts > 0 AND attempt_count >= 0 AND attempt_count <= max_attempts
    )
);
CREATE INDEX otp_challenges_email_created_idx
    ON monitor.otp_challenges (email, created_at DESC);

CREATE TABLE monitor.user_sessions (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES monitor.users(id) ON DELETE CASCADE,
    token_digest TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    CONSTRAINT user_sessions_digest_is_sha256_hex CHECK (token_digest ~ '^[0-9a-f]{64}$'),
    CONSTRAINT user_sessions_expiry_after_creation CHECK (expires_at > created_at),
    CONSTRAINT user_sessions_revocation_after_creation CHECK (
        revoked_at IS NULL OR revoked_at >= created_at
    )
);
CREATE INDEX user_sessions_user_created_idx
    ON monitor.user_sessions (user_id, created_at DESC);

CREATE TABLE monitor.meters (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES monitor.users (id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT meters_name_valid CHECK (
        name = BTRIM(name) AND CHAR_LENGTH(name) BETWEEN 1 AND 80
    )
);
CREATE UNIQUE INDEX meters_user_name_unique_idx ON monitor.meters (user_id, LOWER(name));
CREATE INDEX meters_user_created_idx ON monitor.meters (user_id, created_at, id);

-- Staged only: owner-based API access remains until the sharing implementation.
CREATE TABLE monitor.user_meters (
    user_id BIGINT NOT NULL REFERENCES monitor.users (id) ON DELETE CASCADE,
    meter_id UUID NOT NULL REFERENCES monitor.meters (id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, meter_id)
);
CREATE INDEX user_meters_meter_user_idx ON monitor.user_meters (meter_id, user_id);

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

CREATE TABLE monitor.reminder_settings (
    meter_id UUID PRIMARY KEY REFERENCES monitor.meters (id) ON DELETE CASCADE,
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

CREATE TABLE monitor.reminder_deliveries (
    id UUID PRIMARY KEY,
    meter_id UUID NOT NULL REFERENCES monitor.meters (id) ON DELETE CASCADE,
    reminder_type TEXT NOT NULL,
    dedupe_key TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    claimed_at TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reminder_delivery_type_valid CHECK (reminder_type IN ('monthly', 'low_balance')),
    CONSTRAINT reminder_delivery_key_valid CHECK (
        dedupe_key = BTRIM(dedupe_key) AND CHAR_LENGTH(dedupe_key) BETWEEN 1 AND 32
    ),
    CONSTRAINT reminder_delivery_status_valid CHECK (status IN ('pending', 'sent')),
    CONSTRAINT reminder_delivery_sent_state_valid CHECK (
        (status = 'pending' AND sent_at IS NULL) OR (status = 'sent' AND sent_at IS NOT NULL)
    ),
    UNIQUE (meter_id, reminder_type, dedupe_key)
);
CREATE INDEX reminder_deliveries_pending_idx ON monitor.reminder_deliveries (status, claimed_at);
COMMIT;
