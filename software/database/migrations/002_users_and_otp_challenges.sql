CREATE TABLE monitor.users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_email_normalized CHECK (
        email <> '' AND email = LOWER(BTRIM(email))
    )
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
    CONSTRAINT otp_digest_is_sha256_hex CHECK (
        code_digest ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT otp_expiry_after_creation CHECK (expires_at > created_at),
    CONSTRAINT otp_attempts_valid CHECK (
        max_attempts > 0
        AND attempt_count >= 0
        AND attempt_count <= max_attempts
    )
);

CREATE INDEX otp_challenges_email_created_idx
    ON monitor.otp_challenges (email, created_at DESC);
